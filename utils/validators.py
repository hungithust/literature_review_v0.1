"""
JSON parsing and schema validation utilities.

Provides safe parsing for LLM outputs that may contain
invalid JSON or unexpected formats.
"""

import json
import re
from typing import Any

from utils.logger import get_logger

logger = get_logger(__name__)


def safe_parse_json(text: str) -> Any | None:
    """Safely parse JSON from LLM output.

    Handles common issues:
    - JSON wrapped in markdown code blocks
    - Leading/trailing whitespace
    - Single quotes instead of double quotes

    Args:
        text: Raw text that should contain JSON.

    Returns:
        Parsed JSON object, or None if parsing fails.
    """
    if not text:
        logger.warning("Empty text provided for JSON parsing")
        return None

    # Strip whitespace
    text = text.strip()

    # Remove markdown code block wrapper if present
    if text.startswith("```"):
        # Remove ```json or ``` prefix and ``` suffix
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as err:
        logger.warning("JSON parse error: %s | Text preview: %s", err, text[:200])

        # Try fixing common issues: single quotes
        try:
            fixed = text.replace("'", '"')
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON object/array from text
        json_match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        logger.error("Failed to parse JSON from LLM output: %s", text[:300])
        return None


def validate_filter_result(data: dict) -> dict | None:
    """Validate that a filter result dict has required fields.

    Args:
        data: Dictionary to validate.

    Returns:
        Validated dict with correct types, or None if invalid.
    """
    if not isinstance(data, dict):
        return None

    try:
        return {
            "relevance_score": int(data.get("relevance_score", 0)),
            "confidence": int(data.get("confidence", 50)),
            "reason": str(data.get("reason", "No reason provided")),
        }
    except (ValueError, TypeError) as err:
        logger.warning("Invalid filter result data: %s | Error: %s", data, err)
        return None


def validate_summary_result(data: dict) -> dict | None:
    """Validate that a summary result dict has required fields.

    Args:
        data: Dictionary to validate.

    Returns:
        Validated dict with correct types, or None if invalid.
    """
    if not isinstance(data, dict):
        return None

    return {
        "problem": str(data.get("problem", "Not specified")),
        "method": str(data.get("method", "Not specified")),
        "key_result": str(data.get("key_result", "Not specified")),
    }
