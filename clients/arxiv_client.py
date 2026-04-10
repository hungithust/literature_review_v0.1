"""
arXiv API client.

Fetches papers from the arXiv API and normalizes results
into the same PaperMetadata schema used by Semantic Scholar client.
"""

import httpx
import xmltodict

from config import ARXIV_API_URL, ARXIV_TIMEOUT
from schemas import PaperMetadata
from utils.logger import get_logger
from utils.helpers import clean_text

logger = get_logger(__name__)


def search_papers(
    query: str,
    limit: int = 15,
) -> list[PaperMetadata]:
    """Search arXiv for papers matching a query.

    Args:
        query: Search query string.
        limit: Maximum number of papers to return.

    Returns:
        List of normalized PaperMetadata objects.
    """
    logger.info("Searching arXiv: query='%s', limit=%d", query, limit)

    # arXiv API uses 'search_query' param with prefix like 'all:'
    params: dict = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": min(limit, 50),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    try:
        response = httpx.get(
            ARXIV_API_URL,
            params=params,
            timeout=ARXIV_TIMEOUT,
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        logger.error("arXiv API timeout for query: '%s'", query)
        return []
    except httpx.HTTPStatusError as err:
        logger.error("arXiv API HTTP error %d for query: '%s'", err.response.status_code, query)
        return []
    except httpx.RequestError as err:
        logger.error("arXiv API request error: %s", err)
        return []

    try:
        parsed = xmltodict.parse(response.text)
    except Exception as err:
        logger.error("Failed to parse arXiv XML response: %s", err)
        return []

    feed = parsed.get("feed", {})
    entries = feed.get("entry", [])

    # Handle single result (xmltodict returns dict instead of list)
    if isinstance(entries, dict):
        entries = [entries]

    if not entries:
        logger.warning("No papers returned from arXiv for query: '%s'", query)
        return []

    logger.info("arXiv returned %d papers for query: '%s'", len(entries), query)

    papers: list[PaperMetadata] = []
    for entry in entries:
        paper = _normalize_paper(entry)
        if paper:
            papers.append(paper)

    logger.info("Normalized %d papers from arXiv", len(papers))
    return papers


def _normalize_paper(entry: dict) -> PaperMetadata | None:
    """Normalize a raw arXiv entry to PaperMetadata.

    Args:
        entry: Parsed XML entry dict from arXiv API.

    Returns:
        PaperMetadata object, or None if essential fields are missing.
    """
    title = entry.get("title")
    arxiv_id = entry.get("id", "")

    if not title or not arxiv_id:
        logger.debug("Skipping arXiv entry with missing title or id")
        return None

    # Extract arXiv ID from URL (e.g., "http://arxiv.org/abs/2401.12345v1")
    short_id = arxiv_id.split("/abs/")[-1] if "/abs/" in arxiv_id else arxiv_id

    # Extract authors
    authors_raw = entry.get("author", [])
    if isinstance(authors_raw, dict):
        authors_raw = [authors_raw]
    authors = [a.get("name", "Unknown") for a in authors_raw if isinstance(a, dict)]

    # Extract abstract
    abstract = clean_text(entry.get("summary", "") or "")

    # Extract publication date
    published = entry.get("published", "")
    date_str = published[:10] if published else None  # YYYY-MM-DD
    year = int(date_str[:4]) if date_str and len(date_str) >= 4 else None

    # Build paper URL
    url = arxiv_id if arxiv_id.startswith("http") else f"https://arxiv.org/abs/{short_id}"

    return PaperMetadata(
        paper_id=f"arxiv:{short_id}",
        title=clean_text(title),
        abstract=abstract if abstract else None,
        authors=authors,
        year=year,
        date=date_str,
        url=url,
        source="arxiv",
    )
