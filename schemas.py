"""
Pydantic schemas for the AI SOTA Radar pipeline.

Defines all data models used across modules to ensure
consistent, typed data flow throughout the system.
"""

from pydantic import BaseModel, Field
from typing import Optional


class PaperMetadata(BaseModel):
    """Normalized metadata for a single research paper."""

    paper_id: str = Field(description="Unique identifier (e.g., Semantic Scholar corpusId or arXiv id)")
    title: str = Field(description="Paper title")
    abstract: Optional[str] = Field(default=None, description="Paper abstract text")
    authors: list[str] = Field(default_factory=list, description="List of author names")
    year: Optional[int] = Field(default=None, description="Publication year")
    date: Optional[str] = Field(default=None, description="Publication date string (YYYY-MM-DD)")
    url: Optional[str] = Field(default=None, description="URL to the paper")
    source: str = Field(description="Data source: 'semantic_scholar' or 'arxiv'")


class FilterResult(BaseModel):
    """Relevance scoring result for a single paper."""

    paper_id: str = Field(description="Matches PaperMetadata.paper_id")
    relevance_score: int = Field(ge=0, le=100, description="Relevance score 0-100")
    confidence: int = Field(ge=0, le=100, description="Confidence in the score 0-100")
    reason: str = Field(description="Brief explanation of the relevance score")


class SummaryResult(BaseModel):
    """Structured summary of a single paper."""

    paper_id: str = Field(description="Matches PaperMetadata.paper_id")
    problem: str = Field(description="What problem does the paper address?")
    method: str = Field(description="What method/approach is proposed?")
    key_result: str = Field(description="What is the key result or finding?")


class FinalPaperCard(BaseModel):
    """Combined result for UI display — one card per paper."""

    paper_id: str
    title: str
    abstract: Optional[str] = None
    authors: list[str] = Field(default_factory=list)
    year: Optional[int] = None
    date: Optional[str] = None
    url: Optional[str] = None
    source: str

    # Filter results
    relevance_score: int = 0
    confidence: int = 0
    relevance_reason: str = ""

    # Summary results
    problem: str = ""
    method: str = ""
    key_result: str = ""


class ResearchProfile(BaseModel):
    """User's research interests description."""

    description: str = Field(description="Free-text description of research interests")
    name: Optional[str] = Field(default=None, description="Optional profile name for display")
