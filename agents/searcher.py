"""
Searcher agent.

Transforms a Research Profile into search queries,
fetches papers from multiple sources, and returns
a deduplicated list of candidate papers.
"""

import json

from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    SEARCH_PAPERS_PER_QUERY,
    SEARCH_MAX_QUERIES,
    ENABLE_ARXIV_FALLBACK,
    ENABLE_ARXIV_ALWAYS,
)
from schemas import PaperMetadata
from prompts import QUERY_GENERATION_PROMPT
from clients import semantic_scholar_client, arxiv_client
from utils.logger import get_logger
from utils.helpers import deduplicate_papers
from utils.validators import safe_parse_json

logger = get_logger(__name__)


def generate_queries(profile: str, num_queries: int = SEARCH_MAX_QUERIES) -> list[str]:
    """Generate search queries from a research profile using LLM.

    Args:
        profile: Research profile description text.
        num_queries: Number of queries to generate.

    Returns:
        List of search query strings.
    """
    logger.info("Generating %d search queries from profile", num_queries)

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = QUERY_GENERATION_PROMPT.format(
        num_queries=num_queries,
        profile=profile,
    )

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=OPENAI_TEMPERATURE,
        )
        content = response.choices[0].message.content or ""
    except Exception as err:
        logger.error("LLM query generation failed: %s", err)
        # Fallback: use profile keywords directly
        return _fallback_queries(profile)

    queries = safe_parse_json(content)
    if not isinstance(queries, list) or not queries:
        logger.warning("LLM returned invalid queries, using fallback. Output: %s", content[:200])
        return _fallback_queries(profile)

    # Ensure all items are strings
    queries = [str(q) for q in queries if q][:num_queries]
    logger.info("Generated queries: %s", queries)
    return queries


def _fallback_queries(profile: str) -> list[str]:
    """Generate simple fallback queries from profile text.

    Splits the profile into key phrases as a fallback
    when LLM query generation fails.

    Args:
        profile: Research profile text.

    Returns:
        List of 2-3 simple query strings.
    """
    # Take first few meaningful phrases
    words = profile.split()
    if len(words) <= 5:
        return [profile.strip()]

    # Split into chunks of ~5 words
    chunk_size = max(3, len(words) // 3)
    queries = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i : i + chunk_size])
        if len(chunk) > 5:
            queries.append(chunk)
        if len(queries) >= 3:
            break

    return queries[:3]


def search(profile: str) -> list[PaperMetadata]:
    """Execute the full search pipeline for a research profile.

    Steps:
    1. Generate search queries from profile
    2. Fetch papers from Semantic Scholar for each query
    3. Optionally fetch from arXiv (fallback or always)
    4. Merge and deduplicate results

    Args:
        profile: Research profile description text.

    Returns:
        Deduplicated list of PaperMetadata objects.
    """
    logger.info("Starting search for profile: '%s'", profile[:100])

    # Step 1: Generate queries
    queries = generate_queries(profile)
    if not queries:
        logger.error("No queries generated — cannot search")
        return []

    # Step 2: Fetch from Semantic Scholar
    all_papers: list[PaperMetadata] = []

    for query in queries:
        papers = semantic_scholar_client.search_papers(
            query=query,
            limit=SEARCH_PAPERS_PER_QUERY,
        )
        all_papers.extend(papers)

    logger.info(
        "Total papers from Semantic Scholar: %d (across %d queries)",
        len(all_papers),
        len(queries),
    )

    # Step 3: arXiv (fallback or always)
    use_arxiv = ENABLE_ARXIV_ALWAYS or (ENABLE_ARXIV_FALLBACK and len(all_papers) < 10)

    if use_arxiv:
        logger.info("Fetching from arXiv (fallback=%s, always=%s)", ENABLE_ARXIV_FALLBACK, ENABLE_ARXIV_ALWAYS)
        for query in queries[:2]:  # Limit arXiv to 2 queries to save time
            arxiv_papers = arxiv_client.search_papers(
                query=query,
                limit=SEARCH_PAPERS_PER_QUERY,
            )
            all_papers.extend(arxiv_papers)
        logger.info("Total papers after arXiv: %d", len(all_papers))

    # Step 4: Deduplicate
    unique_papers = deduplicate_papers(all_papers)
    logger.info("Papers after deduplication: %d (removed %d duplicates)", len(unique_papers), len(all_papers) - len(unique_papers))

    return unique_papers
