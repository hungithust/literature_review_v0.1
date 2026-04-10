"""
Summarizer agent.

Generates structured summaries (problem, method, key_result)
for top papers using an LLM.
"""

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
from schemas import PaperMetadata, SummaryResult
from prompts import SUMMARIZER_PROMPT
from utils.logger import get_logger
from utils.validators import safe_parse_json, validate_summary_result
from utils.helpers import truncate_text

logger = get_logger(__name__)


def summarize_papers(papers: list[PaperMetadata]) -> list[SummaryResult]:
    """Generate structured summaries for a list of papers.

    Each paper is summarized individually to ensure quality.

    Args:
        papers: List of top papers to summarize.

    Returns:
        List of SummaryResult objects.
    """
    logger.info("Summarizing %d papers", len(papers))

    results: list[SummaryResult] = []

    for paper in papers:
        summary = _summarize_single(paper)
        results.append(summary)

    logger.info("Summarization complete: %d papers summarized", len(results))
    return results


def _summarize_single(paper: PaperMetadata) -> SummaryResult:
    """Summarize a single paper using LLM.

    Args:
        paper: Paper metadata with title and abstract.

    Returns:
        SummaryResult with problem, method, and key_result fields.
    """
    abstract = paper.abstract or "No abstract available."
    abstract = truncate_text(abstract, 800)

    prompt = SUMMARIZER_PROMPT.format(
        title=paper.title,
        abstract=abstract,
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
        logger.error("LLM summarization failed for paper '%s': %s", paper.paper_id, err)
        return _fallback_summary(paper)

    parsed = safe_parse_json(content)
    if not isinstance(parsed, dict):
        logger.warning("LLM returned invalid summary JSON for paper '%s'", paper.paper_id)
        return _fallback_summary(paper)

    validated = validate_summary_result(parsed)
    if not validated:
        logger.warning("Summary validation failed for paper '%s'", paper.paper_id)
        return _fallback_summary(paper)

    return SummaryResult(
        paper_id=paper.paper_id,
        problem=validated["problem"],
        method=validated["method"],
        key_result=validated["key_result"],
    )


def _fallback_summary(paper: PaperMetadata) -> SummaryResult:
    """Generate a fallback summary when LLM fails.

    Uses the abstract directly as a minimal summary.

    Args:
        paper: Paper to create fallback summary for.

    Returns:
        SummaryResult with fallback content.
    """
    abstract_preview = truncate_text(paper.abstract or "", 200)

    return SummaryResult(
        paper_id=paper.paper_id,
        problem=abstract_preview if abstract_preview else "Unable to summarize — no abstract available.",
        method="Summary unavailable — LLM processing failed.",
        key_result="Please refer to the original paper for details.",
    )
