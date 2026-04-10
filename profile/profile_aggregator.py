"""
Profile aggregator.

Combines data from Google Scholar, LinkedIn, and user description
into a unified PersonalResearchProfile using LLM-powered classification.

Weighting: Scholar (0.6) > User Input (0.3) > LinkedIn (0.1)
"""

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
from schemas import ScholarData, LinkedInData, PersonalResearchProfile
from prompts import PROFILE_AGGREGATION_PROMPT
from utils.logger import get_logger
from utils.validators import safe_parse_json

logger = get_logger(__name__)


def _collect_raw_keywords(
    scholar_data: ScholarData | None,
    linkedin_data: LinkedInData | None,
    user_description: str,
) -> dict:
    """Collect all raw signals from the three sources.

    Args:
        scholar_data: Parsed Google Scholar data.
        linkedin_data: Parsed LinkedIn data.
        user_description: User's research description text.

    Returns:
        Dict with categorized raw signals for the LLM.
    """
    signals = {
        "scholar_keywords": [],
        "scholar_areas": [],
        "scholar_paper_titles": [],
        "linkedin_headline": "",
        "linkedin_roles": [],
        "linkedin_skills": [],
        "user_description": user_description.strip(),
    }

    if scholar_data:
        signals["scholar_keywords"] = scholar_data.keywords[:20]
        signals["scholar_areas"] = scholar_data.top_areas
        signals["scholar_paper_titles"] = [
            p.get("title", "") for p in scholar_data.papers[:15]
        ]

    if linkedin_data:
        signals["linkedin_headline"] = linkedin_data.headline
        signals["linkedin_roles"] = linkedin_data.roles
        signals["linkedin_skills"] = linkedin_data.skills

    return signals


def aggregate_profile(
    scholar_data: ScholarData | None,
    linkedin_data: LinkedInData | None,
    user_description: str,
) -> PersonalResearchProfile:
    """Aggregate multi-source data into a unified research profile.

    Uses LLM to intelligently classify and merge keywords from
    Scholar, LinkedIn, and user input with appropriate weighting.

    Args:
        scholar_data: Data from Google Scholar parser.
        linkedin_data: Data from LinkedIn parser.
        user_description: User's own research description.

    Returns:
        PersonalResearchProfile with classified and merged data.
    """
    logger.info("Aggregating profile from %s sources",
                sum([bool(scholar_data), bool(linkedin_data), bool(user_description)]))

    signals = _collect_raw_keywords(scholar_data, linkedin_data, user_description)

    # If we have barely any data, create a minimal profile
    if not any([
        signals["scholar_keywords"],
        signals["linkedin_skills"],
        signals["user_description"],
    ]):
        logger.warning("Insufficient data for profile aggregation")
        return PersonalResearchProfile(research_description=user_description)

    # Use LLM to classify and merge
    prompt = PROFILE_AGGREGATION_PROMPT.format(
        scholar_keywords=", ".join(signals["scholar_keywords"]),
        scholar_areas=", ".join(signals["scholar_areas"]),
        paper_titles="\n".join(f"- {t}" for t in signals["scholar_paper_titles"]),
        linkedin_headline=signals["linkedin_headline"],
        linkedin_roles=", ".join(signals["linkedin_roles"]),
        linkedin_skills=", ".join(signals["linkedin_skills"]),
        user_description=signals["user_description"],
    )

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=OPENAI_TEMPERATURE,
        )
        content = response.choices[0].message.content or ""
    except Exception as err:
        logger.error("LLM profile aggregation failed: %s", err)
        return _fallback_aggregation(signals)

    parsed = safe_parse_json(content)
    if not isinstance(parsed, dict):
        logger.warning("LLM returned invalid profile data, using fallback")
        return _fallback_aggregation(signals)

    logger.info("Profile aggregation complete: %d topics, %d methods, %d keywords",
                len(parsed.get("core_topics", [])),
                len(parsed.get("methods", [])),
                len(parsed.get("keywords", [])))

    return PersonalResearchProfile(
        core_topics=[str(t) for t in parsed.get("core_topics", [])],
        methods=[str(m) for m in parsed.get("methods", [])],
        applications=[str(a) for a in parsed.get("applications", [])],
        keywords=[str(k) for k in parsed.get("keywords", [])],
        query_hints=[str(q) for q in parsed.get("query_hints", [])],
        scholar_url=scholar_data.top_areas[0] if scholar_data and scholar_data.top_areas else "",
        research_description=user_description,
    )


def _fallback_aggregation(signals: dict) -> PersonalResearchProfile:
    """Create a basic profile without LLM when API fails.

    Uses raw keywords directly without classification.

    Args:
        signals: Raw signals dict from _collect_raw_keywords.

    Returns:
        Basic PersonalResearchProfile with uncategorized keywords.
    """
    logger.warning("Using fallback profile aggregation")

    all_keywords = list(set(
        signals["scholar_keywords"]
        + signals["linkedin_skills"]
    ))

    return PersonalResearchProfile(
        core_topics=signals["scholar_areas"][:5],
        methods=[],
        applications=[],
        keywords=all_keywords[:20],
        query_hints=signals["scholar_keywords"][:5],
        research_description=signals["user_description"],
    )
