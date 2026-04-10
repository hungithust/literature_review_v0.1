"""
Google Scholar profile parser.

Uses the `scholarly` library to extract papers, keywords,
and research areas from a Google Scholar profile URL.
"""

import re
from collections import Counter

from scholarly import scholarly

from config import SCHOLAR_MAX_PAPERS
from schemas import ScholarData
from utils.logger import get_logger

logger = get_logger(__name__)


def _extract_author_id(scholar_url: str) -> str | None:
    """Extract the Google Scholar author ID from a profile URL.

    Supports URLs like:
        https://scholar.google.com/citations?user=AUTHOR_ID
        https://scholar.google.com/citations?user=AUTHOR_ID&hl=en

    Args:
        scholar_url: Google Scholar profile URL.

    Returns:
        Author ID string, or None if not found.
    """
    match = re.search(r"[?&]user=([^&]+)", scholar_url)
    if match:
        return match.group(1)

    # Fallback: if just the ID was passed
    if len(scholar_url.strip()) > 5 and " " not in scholar_url:
        return scholar_url.strip()

    return None


def _extract_keywords_from_titles(titles: list[str], top_n: int = 20) -> list[str]:
    """Extract keywords by word frequency analysis on paper titles.

    Filters common stopwords and short words, returns the most
    frequent meaningful terms.

    Args:
        titles: List of paper title strings.
        top_n: Number of top keywords to return.

    Returns:
        List of keyword strings sorted by frequency.
    """
    stopwords = {
        "a", "an", "the", "of", "in", "for", "and", "or", "to", "on",
        "with", "by", "from", "as", "is", "at", "its", "it", "are",
        "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "will", "would", "could", "should",
        "may", "might", "can", "this", "that", "these", "those",
        "not", "but", "if", "then", "than", "when", "where", "which",
        "who", "whom", "how", "what", "why", "all", "each", "every",
        "both", "few", "more", "most", "other", "some", "such", "no",
        "nor", "only", "own", "same", "so", "very", "using", "based",
        "via", "through", "into", "over", "under", "between", "during",
        "about", "after", "before", "above", "below", "up", "down",
        "out", "off", "further", "once", "here", "there", "new",
        "approach", "method", "study", "paper", "research", "analysis",
        "model", "models", "towards", "toward", "novel", "improved",
    }

    word_counter = Counter()
    for title in titles:
        words = re.findall(r"[a-z]{3,}", title.lower())
        meaningful = [w for w in words if w not in stopwords]
        word_counter.update(meaningful)

    return [word for word, _ in word_counter.most_common(top_n)]


def parse_scholar_profile(scholar_url: str) -> ScholarData:
    """Parse a Google Scholar profile and extract research data.

    Fetches the author's publications (up to SCHOLAR_MAX_PAPERS),
    extracts keywords from titles, and retrieves listed interests.

    Args:
        scholar_url: Google Scholar profile URL or author ID.

    Returns:
        ScholarData with papers, keywords, and top areas.
        Returns empty ScholarData if parsing fails.
    """
    author_id = _extract_author_id(scholar_url)
    if not author_id:
        logger.error("Could not extract author ID from URL: %s", scholar_url)
        return ScholarData()

    logger.info("Parsing Google Scholar profile for author: %s", author_id)

    try:
        # Search for the author by ID
        author = scholarly.search_author_id(author_id)
        if not author:
            logger.warning("Author not found: %s", author_id)
            return ScholarData()

        # Fill in author details (publications, etc.)
        author = scholarly.fill(author, sections=["basics", "publications"])

    except Exception as err:
        logger.error("Scholar API error: %s", err)
        return ScholarData()

    # Extract interests/areas
    top_areas = author.get("interests", [])
    logger.info("Scholar interests: %s", top_areas)

    # Extract papers
    publications = author.get("publications", [])[:SCHOLAR_MAX_PAPERS]
    papers = []
    titles = []

    for pub in publications:
        bib = pub.get("bib", {})
        title = bib.get("title", "")
        if title:
            titles.append(title)
            papers.append({
                "title": title,
                "authors": bib.get("author", "").split(" and ") if isinstance(bib.get("author"), str) else [],
                "year": bib.get("pub_year", None),
            })

    logger.info("Extracted %d papers from Scholar profile", len(papers))

    # Extract keywords from titles
    keywords = _extract_keywords_from_titles(titles)
    logger.info("Extracted %d keywords from titles", len(keywords))

    return ScholarData(
        papers=papers,
        keywords=keywords,
        top_areas=top_areas,
    )
