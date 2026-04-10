"""
Filter agent.

Scores papers for relevance to a research profile using an LLM
and selects the top papers based on relevance score.
"""

from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    FILTER_TOP_K,
    FILTER_MIN_SCORE,
)
from schemas import PaperMetadata, FilterResult
from prompts import FILTER_BATCH_SCORING_PROMPT
from utils.logger import get_logger
from utils.validators import safe_parse_json, validate_filter_result
from utils.helpers import truncate_text

logger = get_logger(__name__)


def score_papers(
    profile: str,
    papers: list[PaperMetadata],
) -> list[FilterResult]:
    """Score all papers for relevance to the research profile.

    Uses batch scoring to reduce LLM API calls. Falls back
    to individual scoring if batch fails.

    Args:
        profile: Research profile description.
        papers: List of candidate papers.

    Returns:
        List of FilterResult objects with scores, sorted by relevance.
    """
    logger.info("Scoring %d papers for relevance", len(papers))

    if not papers:
        return []

    # Filter out papers without abstracts (can't score them well)
    scorable_papers = [p for p in papers if p.abstract]
    skipped_count = len(papers) - len(scorable_papers)
    if skipped_count > 0:
        logger.warning("Skipping %d papers without abstracts", skipped_count)

    if not scorable_papers:
        logger.warning("No papers with abstracts to score")
        return []

    # Score in batches of 10 to stay within context limits
    batch_size = 10
    all_results: list[FilterResult] = []

    for i in range(0, len(scorable_papers), batch_size):
        batch = scorable_papers[i : i + batch_size]
        batch_results = _score_batch(profile, batch)
        all_results.extend(batch_results)

    # Sort by relevance score descending
    all_results.sort(key=lambda r: r.relevance_score, reverse=True)

    logger.info(
        "Scoring complete. Top score: %d, Lowest score: %d",
        all_results[0].relevance_score if all_results else 0,
        all_results[-1].relevance_score if all_results else 0,
    )

    return all_results


def select_top_papers(
    results: list[FilterResult],
    top_k: int = FILTER_TOP_K,
    min_score: int = FILTER_MIN_SCORE,
) -> list[FilterResult]:
    """Select the top-K papers above the minimum score threshold.

    Args:
        results: Sorted list of FilterResult objects.
        top_k: Maximum number of papers to select.
        min_score: Minimum relevance score to include.

    Returns:
        Top papers that meet the score threshold.
    """
    filtered = [r for r in results if r.relevance_score >= min_score]
    selected = filtered[:top_k]

    logger.info(
        "Selected %d top papers (from %d above min_score=%d)",
        len(selected),
        len(filtered),
        min_score,
    )

    return selected


def _score_batch(
    profile: str,
    papers: list[PaperMetadata],
) -> list[FilterResult]:
    """Score a batch of papers using a single LLM call.

    Args:
        profile: Research profile description.
        papers: Batch of papers to score.

    Returns:
        List of FilterResult objects for the batch.
    """
    # Build papers text for the prompt
    papers_text_parts = []
    for paper in papers:
        abstract_preview = truncate_text(paper.abstract or "No abstract available", 400)
        papers_text_parts.append(
            f"Paper ID: {paper.paper_id}\n"
            f"Title: {paper.title}\n"
            f"Abstract: {abstract_preview}\n"
        )
    papers_text = "\n---\n".join(papers_text_parts)

    prompt = FILTER_BATCH_SCORING_PROMPT.format(
        profile=profile,
        papers_text=papers_text,
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
        logger.error("LLM batch scoring failed: %s", err)
        return _fallback_scores(papers)

    parsed = safe_parse_json(content)
    if not isinstance(parsed, list):
        logger.warning("LLM batch scoring returned non-list, using fallback")
        return _fallback_scores(papers)

    results: list[FilterResult] = []
    # Map parsed results by paper_id
    parsed_map: dict[str, dict] = {}
    for item in parsed:
        if isinstance(item, dict) and "paper_id" in item:
            parsed_map[item["paper_id"]] = item

    for paper in papers:
        raw_result = parsed_map.get(paper.paper_id)
        if raw_result:
            validated = validate_filter_result(raw_result)
            if validated:
                results.append(
                    FilterResult(
                        paper_id=paper.paper_id,
                        relevance_score=validated["relevance_score"],
                        confidence=validated["confidence"],
                        reason=validated["reason"],
                    )
                )
                continue

        # Fallback for papers not in LLM response
        logger.warning("No valid score for paper '%s', assigning default", paper.paper_id)
        results.append(
            FilterResult(
                paper_id=paper.paper_id,
                relevance_score=0,
                confidence=0,
                reason="Scoring failed — no valid result from LLM",
            )
        )

    return results


def _fallback_scores(papers: list[PaperMetadata]) -> list[FilterResult]:
    """Generate fallback scores when LLM scoring fails entirely.

    Assigns a default low score to all papers.

    Args:
        papers: Papers that need fallback scores.

    Returns:
        List of FilterResult with default scores.
    """
    logger.warning("Using fallback scores for %d papers", len(papers))
    return [
        FilterResult(
            paper_id=paper.paper_id,
            relevance_score=25,
            confidence=10,
            reason="Fallback score — LLM scoring unavailable",
        )
        for paper in papers
    ]
