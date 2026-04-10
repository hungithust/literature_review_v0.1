"""
Semantic Scholar API client.

Fetches papers from the Semantic Scholar Academic Graph API
and normalizes results into PaperMetadata objects.
"""

import httpx

from config import (
    SEMANTIC_SCHOLAR_API_KEY,
    SEMANTIC_SCHOLAR_API_URL,
    SEMANTIC_SCHOLAR_FIELDS,
    SEMANTIC_SCHOLAR_TIMEOUT,
)
from schemas import PaperMetadata
from utils.logger import get_logger
from utils.helpers import clean_text

logger = get_logger(__name__)


def search_papers(
    query: str,
    limit: int = 15,
    year_filter: str | None = None,
) -> list[PaperMetadata]:
    """Search Semantic Scholar for papers matching a query.

    Args:
        query: Search query string.
        limit: Maximum number of papers to return.
        year_filter: Optional year filter (e.g., "2024-" for 2024 onwards).

    Returns:
        List of normalized PaperMetadata objects.
    """
    logger.info("Searching Semantic Scholar: query='%s', limit=%d", query, limit)

    params: dict = {
        "query": query,
        "limit": min(limit, 100),
        "fields": SEMANTIC_SCHOLAR_FIELDS,
    }
    if year_filter:
        params["year"] = year_filter

    headers: dict = {}
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY

    try:
        response = httpx.get(
            f"{SEMANTIC_SCHOLAR_API_URL}/paper/search",
            params=params,
            headers=headers,
            timeout=SEMANTIC_SCHOLAR_TIMEOUT,
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        logger.error("Semantic Scholar API timeout for query: '%s'", query)
        return []
    except httpx.HTTPStatusError as err:
        logger.error(
            "Semantic Scholar API HTTP error %d for query: '%s'",
            err.response.status_code,
            query,
        )
        return []
    except httpx.RequestError as err:
        logger.error("Semantic Scholar API request error: %s", err)
        return []

    data = response.json()
    raw_papers = data.get("data", [])

    if not raw_papers:
        logger.warning("No papers returned from Semantic Scholar for query: '%s'", query)
        return []

    logger.info("Semantic Scholar returned %d papers for query: '%s'", len(raw_papers), query)

    papers: list[PaperMetadata] = []
    for raw in raw_papers:
        paper = _normalize_paper(raw)
        if paper:
            papers.append(paper)

    logger.info("Normalized %d papers from Semantic Scholar", len(papers))
    return papers


def _normalize_paper(raw: dict) -> PaperMetadata | None:
    """Normalize a raw Semantic Scholar paper dict to PaperMetadata.

    Args:
        raw: Raw paper data from API response.

    Returns:
        PaperMetadata object, or None if the paper lacks essential fields.
    """
    paper_id = raw.get("paperId")
    title = raw.get("title")

    if not paper_id or not title:
        logger.debug("Skipping paper with missing id or title: %s", raw)
        return None

    # Extract author names
    authors_raw = raw.get("authors", []) or []
    authors = [a.get("name", "Unknown") for a in authors_raw if isinstance(a, dict)]

    # Build URL
    url = raw.get("url")
    if not url and paper_id:
        url = f"https://www.semanticscholar.org/paper/{paper_id}"

    abstract = clean_text(raw.get("abstract", "") or "")

    return PaperMetadata(
        paper_id=f"ss:{paper_id}",
        title=clean_text(title),
        abstract=abstract if abstract else None,
        authors=authors,
        year=raw.get("year"),
        date=raw.get("publicationDate"),
        url=url,
        source="semantic_scholar",
    )
