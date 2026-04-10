"""
LinkedIn profile parser.

Supports two modes:
1. Copy-paste: User pastes raw LinkedIn profile text → LLM extracts info.
2. Manual form: User enters headline, roles, skills directly.
"""

import json

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
from schemas import LinkedInData
from prompts import LINKEDIN_EXTRACTION_PROMPT
from utils.logger import get_logger
from utils.validators import safe_parse_json

logger = get_logger(__name__)


def parse_linkedin_from_text(raw_text: str) -> LinkedInData:
    """Extract LinkedIn info from raw pasted text using LLM.

    The user copies their LinkedIn profile page content and
    pastes it. The LLM then extracts structured fields:
    headline, roles, and skills.

    Args:
        raw_text: Raw text copied from LinkedIn profile.

    Returns:
        LinkedInData with extracted fields.
        Returns minimal data (with raw_text preserved) if extraction fails.
    """
    if not raw_text or not raw_text.strip():
        logger.warning("Empty LinkedIn text provided")
        return LinkedInData()

    logger.info("Extracting LinkedIn info from pasted text (%d chars)", len(raw_text))

    # Truncate very long text to save tokens
    truncated = raw_text[:3000] if len(raw_text) > 3000 else raw_text

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = LINKEDIN_EXTRACTION_PROMPT.format(linkedin_text=truncated)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=OPENAI_TEMPERATURE,
        )
        content = response.choices[0].message.content or ""
    except Exception as err:
        logger.error("LLM LinkedIn extraction failed: %s", err)
        return LinkedInData(raw_text=raw_text)

    parsed = safe_parse_json(content)
    if not isinstance(parsed, dict):
        logger.warning("LLM returned invalid LinkedIn data: %s", content[:200])
        return LinkedInData(raw_text=raw_text)

    logger.info("LinkedIn extraction success: headline='%s'", parsed.get("headline", "")[:50])

    return LinkedInData(
        headline=str(parsed.get("headline", "")),
        roles=[str(r) for r in parsed.get("roles", []) if r],
        skills=[str(s) for s in parsed.get("skills", []) if s],
        raw_text=raw_text,
    )


def parse_linkedin_from_form(
    headline: str = "",
    roles: list[str] | None = None,
    skills: list[str] | None = None,
) -> LinkedInData:
    """Create LinkedInData from manual form input.

    Fallback when user doesn't have LinkedIn or prefers
    to enter information directly.

    Args:
        headline: Job title or professional headline.
        roles: List of job roles/positions.
        skills: List of professional skills.

    Returns:
        LinkedInData from form input.
    """
    clean_roles = [r.strip() for r in (roles or []) if r.strip()]
    clean_skills = [s.strip() for s in (skills or []) if s.strip()]

    logger.info(
        "LinkedIn form input: headline='%s', %d roles, %d skills",
        headline[:50], len(clean_roles), len(clean_skills),
    )

    return LinkedInData(
        headline=headline.strip(),
        roles=clean_roles,
        skills=clean_skills,
    )
