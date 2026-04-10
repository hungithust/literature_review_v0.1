"""
Helper utilities for text processing and deduplication.
"""

from schemas import PaperMetadata


def deduplicate_papers(papers: list[PaperMetadata]) -> list[PaperMetadata]:
    """Remove duplicate papers based on title similarity.

    Uses normalized (lowercased, stripped) titles to detect duplicates.
    When duplicates are found, keeps the paper with the longer abstract.

    Args:
        papers: List of papers potentially containing duplicates.

    Returns:
        Deduplicated list of papers.
    """
    seen_titles: dict[str, PaperMetadata] = {}

    for paper in papers:
        normalized_title = paper.title.strip().lower()

        if normalized_title in seen_titles:
            existing = seen_titles[normalized_title]
            # Keep the one with a longer abstract
            if len(paper.abstract or "") > len(existing.abstract or ""):
                seen_titles[normalized_title] = paper
        else:
            seen_titles[normalized_title] = paper

    return list(seen_titles.values())


def clean_text(text: str) -> str:
    """Clean and normalize text for processing.

    Removes extra whitespace, newlines, and trims the text.

    Args:
        text: Raw text string.

    Returns:
        Cleaned text string.
    """
    if not text:
        return ""
    # Replace multiple whitespace/newlines with single space
    cleaned = " ".join(text.split())
    return cleaned.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length, adding ellipsis if needed.

    Args:
        text: Text to truncate.
        max_length: Maximum character length.

    Returns:
        Truncated text.
    """
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length].rsplit(" ", 1)[0] + "..."
