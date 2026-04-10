"""
Profile storage on MongoDB Atlas.

Provides CRUD operations for user profiles stored in a
cloud MongoDB database. Uses singleton connection pattern.
"""

from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.database import Database

from config import MONGODB_URI, MONGODB_DB_NAME
from schemas import PersonalResearchProfile, ScholarData, LinkedInData
from utils.logger import get_logger

logger = get_logger(__name__)

# --- MongoDB Connection Singleton ---
_client: MongoClient | None = None
_db: Database | None = None

COLLECTION_NAME = "user_profiles"


def get_db() -> Database:
    """Get MongoDB database connection (singleton).

    Connects to MongoDB Atlas using the URI from config.
    Reuses the same connection across calls.

    Uses certifi CA bundle for SSL connections, which fixes
    the common TLS handshake error on Windows.

    Returns:
        MongoDB Database instance.

    Raises:
        ValueError: If MONGODB_URI is not configured.
        ConnectionError: If unable to connect to MongoDB Atlas.
    """
    global _client, _db

    if _db is not None:
        return _db

    if not MONGODB_URI:
        raise ValueError(
            "MongoDB URI is not configured. "
            "Please set MONGODB_URI in your .env file."
        )

    try:
        import certifi

        # Try connection with certifi CA bundle first, then fallback
        connection_methods = [
            {"tlsCAFile": certifi.where()},
            {"tls": True, "tlsAllowInvalidCertificates": True},
        ]

        last_error = None
        for tls_opts in connection_methods:
            try:
                _client = MongoClient(
                    MONGODB_URI,
                    serverSelectionTimeoutMS=5000,
                    **tls_opts,
                )
                _client.admin.command("ping")
                _db = _client[MONGODB_DB_NAME]
                logger.info("Connected to MongoDB Atlas: database='%s'", MONGODB_DB_NAME)
                return _db
            except Exception as err:
                last_error = err
                logger.warning("MongoDB connection attempt failed: %s", str(err)[:100])
                continue

        # All connection methods failed
        error_msg = str(last_error)
        if "TLSV1_ALERT_INTERNAL_ERROR" in error_msg:
            raise ConnectionError(
                "MongoDB Atlas SSL handshake failed. "
                "This usually means your IP address is not whitelisted. "
                "Go to MongoDB Atlas → Network Access → Add IP Address → "
                "Add your current IP or '0.0.0.0/0' (allow all) for testing."
            )
        raise ConnectionError(f"Cannot connect to MongoDB: {last_error}")

    except ConnectionError:
        raise
    except Exception as err:
        logger.error("MongoDB connection failed: %s", err)
        raise ConnectionError(f"Cannot connect to MongoDB: {err}") from err


def save_user_profile(
    user_id: str,
    email: str,
    profile: PersonalResearchProfile,
    scholar_data: ScholarData | None = None,
    linkedin_data: LinkedInData | None = None,
) -> bool:
    """Save or update a user profile in MongoDB (upsert).

    Stores the unified profile along with raw source data
    for future reference and profile updates.

    Args:
        user_id: Firebase user ID.
        email: User's email address.
        profile: Unified PersonalResearchProfile.
        scholar_data: Raw Scholar data (optional).
        linkedin_data: Raw LinkedIn data (optional).

    Returns:
        True if save succeeded, False otherwise.
    """
    try:
        db = get_db()
        collection = db[COLLECTION_NAME]

        document = {
            "user_id": user_id,
            "email": email,
            "profile": profile.model_dump(),
            "scholar_data": scholar_data.model_dump() if scholar_data else None,
            "linkedin_data": linkedin_data.model_dump() if linkedin_data else None,
            "updated_at": datetime.now(timezone.utc),
        }

        # Upsert: insert if new, update if exists
        result = collection.update_one(
            {"user_id": user_id},
            {
                "$set": document,
                "$setOnInsert": {"created_at": datetime.now(timezone.utc)},
            },
            upsert=True,
        )

        if result.upserted_id:
            logger.info("Created new profile for user: %s", user_id)
        else:
            logger.info("Updated profile for user: %s", user_id)

        return True

    except Exception as err:
        logger.error("Failed to save profile for user %s: %s", user_id, err)
        return False


def load_user_profile(user_id: str) -> PersonalResearchProfile | None:
    """Load a user's PersonalResearchProfile from MongoDB.

    Args:
        user_id: Firebase user ID.

    Returns:
        PersonalResearchProfile if found, None otherwise.
    """
    try:
        db = get_db()
        collection = db[COLLECTION_NAME]

        doc = collection.find_one({"user_id": user_id})
        if not doc or "profile" not in doc:
            logger.info("No profile found for user: %s", user_id)
            return None

        profile = PersonalResearchProfile(**doc["profile"])
        logger.info("Loaded profile for user: %s (%d keywords)",
                     user_id, len(profile.keywords))
        return profile

    except Exception as err:
        logger.error("Failed to load profile for user %s: %s", user_id, err)
        return None


def profile_exists(user_id: str) -> bool:
    """Check if a user already has a saved profile.

    Args:
        user_id: Firebase user ID.

    Returns:
        True if profile exists in MongoDB.
    """
    try:
        db = get_db()
        collection = db[COLLECTION_NAME]
        return collection.count_documents({"user_id": user_id}, limit=1) > 0
    except Exception as err:
        logger.error("Failed to check profile existence: %s", err)
        return False


def delete_user_profile(user_id: str) -> bool:
    """Delete a user's profile from MongoDB.

    Args:
        user_id: Firebase user ID.

    Returns:
        True if deleted successfully.
    """
    try:
        db = get_db()
        collection = db[COLLECTION_NAME]
        result = collection.delete_one({"user_id": user_id})
        if result.deleted_count > 0:
            logger.info("Deleted profile for user: %s", user_id)
            return True
        logger.warning("No profile found to delete for user: %s", user_id)
        return False
    except Exception as err:
        logger.error("Failed to delete profile for user %s: %s", user_id, err)
        return False


def get_full_user_data(user_id: str) -> dict | None:
    """Get the complete document for a user (profile + raw data).

    Useful for displaying full profile info in the UI.

    Args:
        user_id: Firebase user ID.

    Returns:
        Full MongoDB document dict, or None if not found.
    """
    try:
        db = get_db()
        collection = db[COLLECTION_NAME]
        doc = collection.find_one({"user_id": user_id}, {"_id": 0})
        return doc
    except Exception as err:
        logger.error("Failed to get full data for user %s: %s", user_id, err)
        return None
