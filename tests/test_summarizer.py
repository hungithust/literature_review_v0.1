"""
Tests for the Summarizer agent.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from schemas import PaperMetadata
from agents.summarizer import _fallback_summary
from utils.validators import validate_summary_result


def test_fallback_summary_with_abstract():
    """Fallback should use abstract as problem."""
    paper = PaperMetadata(
        paper_id="1",
        title="Test Paper",
        abstract="This paper studies transformers for text classification.",
        source="ss",
    )
    result = _fallback_summary(paper)
    assert result.paper_id == "1"
    assert "transformers" in result.problem.lower() or "classification" in result.problem.lower()
    assert "unavailable" in result.method.lower()


def test_fallback_summary_no_abstract():
    """Fallback with no abstract should give clear message."""
    paper = PaperMetadata(
        paper_id="2",
        title="Test Paper No Abstract",
        abstract=None,
        source="arxiv",
    )
    result = _fallback_summary(paper)
    assert "unavailable" in result.problem.lower() or "unable" in result.problem.lower()


def test_validate_summary_result_valid():
    """Should validate correct summary data."""
    data = {
        "problem": "Text classification is hard",
        "method": "We use transformers",
        "key_result": "95% accuracy",
    }
    result = validate_summary_result(data)
    assert result is not None
    assert result["problem"] == "Text classification is hard"


def test_validate_summary_result_missing_fields():
    """Should handle missing fields with defaults."""
    data = {"problem": "Something"}
    result = validate_summary_result(data)
    assert result is not None
    assert result["method"] == "Not specified"
    assert result["key_result"] == "Not specified"


def test_validate_summary_result_invalid_type():
    """Should return None for non-dict input."""
    result = validate_summary_result("not a dict")
    assert result is None


if __name__ == "__main__":
    test_fallback_summary_with_abstract()
    test_fallback_summary_no_abstract()
    test_validate_summary_result_valid()
    test_validate_summary_result_missing_fields()
    test_validate_summary_result_invalid_type()
    print("[PASS] All summarizer tests passed!")
