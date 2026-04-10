"""
Tests for the Searcher agent.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.searcher import _fallback_queries, generate_queries
from schemas import PaperMetadata
from utils.helpers import deduplicate_papers


def test_fallback_queries_short_profile():
    """Fallback should return the profile itself for short inputs."""
    result = _fallback_queries("LLMs")
    assert len(result) >= 1
    assert "LLMs" in result[0]


def test_fallback_queries_long_profile():
    """Fallback should split long profiles into 2-3 chunks."""
    profile = "Deep learning for natural language processing large language models retrieval augmented generation instruction tuning prompt engineering"
    result = _fallback_queries(profile)
    assert 1 <= len(result) <= 3
    for query in result:
        assert len(query) > 5


def test_deduplicate_papers():
    """Deduplication should merge papers with same title."""
    papers = [
        PaperMetadata(
            paper_id="ss:1", title="Attention Is All You Need",
            abstract="Long abstract here", authors=["Vaswani"], year=2017,
            source="semantic_scholar",
        ),
        PaperMetadata(
            paper_id="arxiv:2", title="attention is all you need",
            abstract="Short", authors=["Vaswani"], year=2017,
            source="arxiv",
        ),
    ]
    result = deduplicate_papers(papers)
    assert len(result) == 1
    # Should keep the one with longer abstract
    assert "Long abstract" in (result[0].abstract or "")


def test_deduplicate_no_duplicates():
    """Dedup with unique papers should return all."""
    papers = [
        PaperMetadata(paper_id="1", title="Paper A", source="ss"),
        PaperMetadata(paper_id="2", title="Paper B", source="ss"),
    ]
    result = deduplicate_papers(papers)
    assert len(result) == 2


if __name__ == "__main__":
    test_fallback_queries_short_profile()
    test_fallback_queries_long_profile()
    test_deduplicate_papers()
    test_deduplicate_no_duplicates()
    print("[PASS] All searcher tests passed!")
