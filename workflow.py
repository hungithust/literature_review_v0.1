"""
Workflow orchestrator for AI SOTA Radar.

Connects all pipeline stages: search → filter → summarize → combine.
Provides logging, timing, and error handling for each step.
"""

import time
from typing import Any

from schemas import PaperMetadata, FilterResult, SummaryResult, FinalPaperCard
from agents import searcher, filter as filter_agent, summarizer
from utils.logger import get_logger

logger = get_logger(__name__)


def run_pipeline(
    profile: str,
    progress_callback: Any = None,
) -> list[FinalPaperCard]:
    """Run the full paper discovery pipeline end-to-end.

    Steps:
    1. Search: Generate queries and fetch papers
    2. Filter: Score relevance and select top papers
    3. Summarize: Create structured summaries
    4. Combine: Merge all results into FinalPaperCard objects

    Args:
        profile: Research profile description text.
        progress_callback: Optional callable(step_name, step_number, total_steps)
                          for UI progress updates.

    Returns:
        List of FinalPaperCard objects, sorted by relevance score.
    """
    total_steps = 4
    pipeline_start = time.time()

    logger.info("=" * 60)
    logger.info("PIPELINE START — Profile: '%s'", profile[:100])
    logger.info("=" * 60)

    # --- Step 1: Search ---
    _notify_progress(progress_callback, "🔍 Searching for papers...", 1, total_steps)
    step_start = time.time()

    try:
        papers = searcher.search(profile)
    except Exception as err:
        logger.error("Search step failed: %s", err)
        return []

    step_time = time.time() - step_start
    logger.info("Step 1 DONE — Found %d papers (%.1fs)", len(papers), step_time)

    if not papers:
        logger.warning("No papers found — pipeline ending early")
        return []

    # --- Step 2: Filter ---
    _notify_progress(progress_callback, "🎯 Scoring relevance...", 2, total_steps)
    step_start = time.time()

    try:
        scored_results = filter_agent.score_papers(profile, papers)
        top_results = filter_agent.select_top_papers(scored_results)
    except Exception as err:
        logger.error("Filter step failed: %s", err)
        return []

    step_time = time.time() - step_start
    logger.info("Step 2 DONE — Selected %d top papers (%.1fs)", len(top_results), step_time)

    if not top_results:
        logger.warning("No papers passed filtering — pipeline ending early")
        return []

    # Get full metadata for top papers
    papers_map = {p.paper_id: p for p in papers}
    top_papers = [papers_map[r.paper_id] for r in top_results if r.paper_id in papers_map]

    # --- Step 3: Summarize ---
    _notify_progress(progress_callback, "📝 Summarizing top papers...", 3, total_steps)
    step_start = time.time()

    try:
        summaries = summarizer.summarize_papers(top_papers)
    except Exception as err:
        logger.error("Summarize step failed: %s", err)
        summaries = []

    step_time = time.time() - step_start
    logger.info("Step 3 DONE — Summarized %d papers (%.1fs)", len(summaries), step_time)

    # --- Step 4: Combine ---
    _notify_progress(progress_callback, "📊 Preparing results...", 4, total_steps)
    step_start = time.time()

    final_cards = _combine_results(top_papers, top_results, summaries)

    step_time = time.time() - step_start
    total_time = time.time() - pipeline_start
    logger.info("Step 4 DONE — Combined %d final cards (%.1fs)", len(final_cards), step_time)
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE — %d results in %.1fs", len(final_cards), total_time)
    logger.info("=" * 60)

    return final_cards


def _combine_results(
    papers: list[PaperMetadata],
    filter_results: list[FilterResult],
    summaries: list[SummaryResult],
) -> list[FinalPaperCard]:
    """Combine paper metadata, filter results, and summaries into final cards.

    Args:
        papers: List of paper metadata.
        filter_results: List of relevance scores.
        summaries: List of paper summaries.

    Returns:
        List of FinalPaperCard objects sorted by relevance score.
    """
    # Build lookup maps
    filter_map = {r.paper_id: r for r in filter_results}
    summary_map = {s.paper_id: s for s in summaries}

    cards: list[FinalPaperCard] = []

    for paper in papers:
        filter_result = filter_map.get(paper.paper_id)
        summary = summary_map.get(paper.paper_id)

        card = FinalPaperCard(
            paper_id=paper.paper_id,
            title=paper.title,
            abstract=paper.abstract,
            authors=paper.authors,
            year=paper.year,
            date=paper.date,
            url=paper.url,
            source=paper.source,
            relevance_score=filter_result.relevance_score if filter_result else 0,
            confidence=filter_result.confidence if filter_result else 0,
            relevance_reason=filter_result.reason if filter_result else "",
            problem=summary.problem if summary else "",
            method=summary.method if summary else "",
            key_result=summary.key_result if summary else "",
        )
        cards.append(card)

    # Sort by relevance score
    cards.sort(key=lambda c: c.relevance_score, reverse=True)

    return cards


def _notify_progress(
    callback: Any,
    message: str,
    step: int,
    total: int,
) -> None:
    """Notify progress callback if provided.

    Args:
        callback: Optional progress callback function.
        message: Progress message.
        step: Current step number.
        total: Total step count.
    """
    if callback:
        try:
            callback(message, step, total)
        except Exception:
            pass  # Don't let UI errors break the pipeline
