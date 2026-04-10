"""
Tests for the Filter agent.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from schemas import PaperMetadata, FilterResult
from agents.filter import select_top_papers, _fallback_scores
from utils.validators import safe_parse_json, validate_filter_result


def test_select_top_papers():
    """Should select papers above min score, limited to top_k."""
    results = [
        FilterResult(paper_id="1", relevance_score=90, confidence=80, reason="Great fit"),
        FilterResult(paper_id="2", relevance_score=75, confidence=70, reason="Good fit"),
        FilterResult(paper_id="3", relevance_score=60, confidence=60, reason="OK fit"),
        FilterResult(paper_id="4", relevance_score=20, confidence=40, reason="Poor fit"),
        FilterResult(paper_id="5", relevance_score=10, confidence=30, reason="Irrelevant"),
    ]
    top = select_top_papers(results, top_k=3, min_score=30)
    assert len(top) == 3
    assert top[0].paper_id == "1"
    assert top[2].paper_id == "3"


def test_select_top_papers_none_above_threshold():
    """Should return empty if no papers above min score."""
    results = [
        FilterResult(paper_id="1", relevance_score=10, confidence=20, reason="Bad"),
    ]
    top = select_top_papers(results, top_k=5, min_score=50)
    assert len(top) == 0


def test_fallback_scores():
    """Fallback should assign default score to all papers."""
    papers = [
        PaperMetadata(paper_id="1", title="Paper A", source="ss"),
        PaperMetadata(paper_id="2", title="Paper B", source="ss"),
    ]
    results = _fallback_scores(papers)
    assert len(results) == 2
    assert all(r.relevance_score == 25 for r in results)


def test_safe_parse_json_valid():
    """Should parse valid JSON."""
    result = safe_parse_json('{"score": 90}')
    assert result == {"score": 90}


def test_safe_parse_json_markdown_wrapped():
    """Should parse JSON wrapped in markdown code blocks."""
    text = '```json\n{"score": 90}\n```'
    result = safe_parse_json(text)
    assert result == {"score": 90}


def test_safe_parse_json_invalid():
    """Should return None for invalid JSON."""
    result = safe_parse_json("not json at all")
    assert result is None


def test_validate_filter_result_valid():
    """Should validate correct filter result."""
    data = {"relevance_score": 85, "confidence": 70, "reason": "Good match"}
    result = validate_filter_result(data)
    assert result is not None
    assert result["relevance_score"] == 85


def test_validate_filter_result_missing_fields():
    """Should handle missing fields with defaults."""
    data = {"relevance_score": 50}
    result = validate_filter_result(data)
    assert result is not None
    assert result["confidence"] == 50
    assert result["reason"] == "No reason provided"


if __name__ == "__main__":
    test_select_top_papers()
    test_select_top_papers_none_above_threshold()
    test_fallback_scores()
    test_safe_parse_json_valid()
    test_safe_parse_json_markdown_wrapped()
    test_safe_parse_json_invalid()
    test_validate_filter_result_valid()
    test_validate_filter_result_missing_fields()
    print("[PASS] All filter tests passed!")
