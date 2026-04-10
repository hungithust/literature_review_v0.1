"""
Configuration for AI SOTA Radar.

Centralizes all configurable values: API keys, limits, feature flags.
Uses environment variables with sensible defaults.
"""

import os

from dotenv import load_dotenv

load_dotenv()  # Đọc API key từ file .env


# --- OpenAI Configuration ---
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE: float = 0.2

# --- Semantic Scholar Configuration ---
SEMANTIC_SCHOLAR_API_URL: str = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_API_KEY: str = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
SEMANTIC_SCHOLAR_TIMEOUT: int = 15  # seconds
SEMANTIC_SCHOLAR_FIELDS: str = "paperId,title,abstract,authors,year,url,publicationDate"

# --- arXiv Configuration ---
ARXIV_API_URL: str = "https://export.arxiv.org/api/query"
ARXIV_TIMEOUT: int = 15  # seconds

# --- Search Configuration ---
SEARCH_PAPERS_PER_QUERY: int = 15  # papers to fetch per query
SEARCH_MAX_QUERIES: int = 3  # max queries generated per profile
SEARCH_TARGET_PAPERS: int = 30  # target total papers before dedup

# --- Filter Configuration ---
FILTER_TOP_K: int = 5  # number of top papers to select
FILTER_MIN_SCORE: int = 0  # minimum relevance score to include (0 = show all)

# --- Feature Flags ---
ENABLE_ARXIV_FALLBACK: bool = os.getenv("ENABLE_ARXIV_FALLBACK", "true").lower() == "true"
ENABLE_ARXIV_ALWAYS: bool = os.getenv("ENABLE_ARXIV_ALWAYS", "false").lower() == "true"

# --- Firebase Authentication ---
FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")
FIREBASE_AUTH_DOMAIN: str = os.getenv("FIREBASE_AUTH_DOMAIN", "")
FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
FIREBASE_STORAGE_BUCKET: str = os.getenv("FIREBASE_STORAGE_BUCKET", "")
FIREBASE_MESSAGING_SENDER_ID: str = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "")
FIREBASE_APP_ID: str = os.getenv("FIREBASE_APP_ID", "")
FIREBASE_DATABASE_URL: str = os.getenv("FIREBASE_DATABASE_URL", "")
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")

# --- Logging ---
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
