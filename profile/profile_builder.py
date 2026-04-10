"""
Profile builder — orchestrator.

Single entry point that chains:
Scholar parser → LinkedIn parser → Profile aggregator
to produce a complete PersonalResearchProfile.
"""

from schemas import ScholarData, LinkedInData, PersonalResearchProfile
from profile.scholar_parser import parse_scholar_profile
from profile.linkedin_parser import parse_linkedin_from_text, parse_linkedin_from_form
from profile.profile_aggregator import aggregate_profile
from utils.logger import get_logger

logger = get_logger(__name__)


def build_profile(
    scholar_url: str = "",
    linkedin_text: str = "",
    linkedin_headline: str = "",
    linkedin_roles: list[str] | None = None,
    linkedin_skills: list[str] | None = None,
    user_description: str = "",
) -> PersonalResearchProfile:
    """Build a complete PersonalResearchProfile from multiple sources.

    Orchestrates the full profile building flow:
    1. Parse Google Scholar profile (if URL provided)
    2. Parse LinkedIn data (from text or manual form)
    3. Aggregate into unified profile

    Each step is independent — if one fails, the others still proceed.

    Args:
        scholar_url: Google Scholar profile URL (optional).
        linkedin_text: Raw LinkedIn profile text for LLM extraction (optional).
        linkedin_headline: Manual headline input (optional).
        linkedin_roles: Manual roles input (optional).
        linkedin_skills: Manual skills input (optional).
        user_description: Free-text research description (recommended).

    Returns:
        PersonalResearchProfile with aggregated data from all sources.
    """
    logger.info("Building profile — Scholar: %s, LinkedIn text: %s, Description: %s",
                bool(scholar_url), bool(linkedin_text), bool(user_description))

    # --- Step 1: Google Scholar ---
    scholar_data = None
    if scholar_url and scholar_url.strip():
        try:
            logger.info("Step 1: Parsing Google Scholar...")
            scholar_data = parse_scholar_profile(scholar_url.strip())
            if scholar_data and scholar_data.papers:
                logger.info("Scholar: found %d papers, %d keywords",
                            len(scholar_data.papers), len(scholar_data.keywords))
            else:
                logger.warning("Scholar: no papers found")
                scholar_data = None
        except Exception as err:
            logger.error("Scholar parsing failed (non-fatal): %s", err)
            scholar_data = None
    else:
        logger.info("Step 1: Skipping Scholar (no URL)")

    # --- Step 2: LinkedIn ---
    linkedin_data = None
    if linkedin_text and linkedin_text.strip():
        try:
            logger.info("Step 2: Extracting LinkedIn from pasted text...")
            linkedin_data = parse_linkedin_from_text(linkedin_text.strip())
            logger.info("LinkedIn: headline='%s', %d roles, %d skills",
                        linkedin_data.headline[:30],
                        len(linkedin_data.roles),
                        len(linkedin_data.skills))
        except Exception as err:
            logger.error("LinkedIn text extraction failed (non-fatal): %s", err)
            linkedin_data = None
    elif linkedin_headline or linkedin_roles or linkedin_skills:
        logger.info("Step 2: Creating LinkedIn from manual form...")
        linkedin_data = parse_linkedin_from_form(
            headline=linkedin_headline,
            roles=linkedin_roles,
            skills=linkedin_skills,
        )
    else:
        logger.info("Step 2: Skipping LinkedIn (no input)")

    # --- Step 3: Aggregate ---
    logger.info("Step 3: Aggregating profile...")
    profile = aggregate_profile(
        scholar_data=scholar_data,
        linkedin_data=linkedin_data,
        user_description=user_description,
    )

    # Attach scholar URL to profile
    if scholar_url:
        profile.scholar_url = scholar_url.strip()

    logger.info("Profile built: %d topics, %d methods, %d keywords, %d query hints",
                len(profile.core_topics), len(profile.methods),
                len(profile.keywords), len(profile.query_hints))

    return profile
