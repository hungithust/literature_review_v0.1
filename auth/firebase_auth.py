"""
Firebase Authentication module.

Handles user sign-in, sign-up, and token verification
using Pyrebase4 for client-side Firebase Auth.
"""

import pyrebase

from config import (
    FIREBASE_API_KEY,
    FIREBASE_AUTH_DOMAIN,
    FIREBASE_PROJECT_ID,
    FIREBASE_STORAGE_BUCKET,
    FIREBASE_MESSAGING_SENDER_ID,
    FIREBASE_APP_ID,
    FIREBASE_DATABASE_URL,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# --- Firebase App Singleton ---
_firebase_app = None
_auth_instance = None


def _get_firebase_config() -> dict:
    """Build Firebase config dict from environment variables."""
    return {
        "apiKey": FIREBASE_API_KEY,
        "authDomain": FIREBASE_AUTH_DOMAIN,
        "projectId": FIREBASE_PROJECT_ID,
        "storageBucket": FIREBASE_STORAGE_BUCKET,
        "messagingSenderId": FIREBASE_MESSAGING_SENDER_ID,
        "appId": FIREBASE_APP_ID,
        "databaseURL": FIREBASE_DATABASE_URL or "https://placeholder.firebaseio.com",
    }


def get_auth():
    """Get Firebase Auth instance (singleton).

    Returns:
        Pyrebase auth instance.

    Raises:
        ValueError: If Firebase API key is not configured.
    """
    global _firebase_app, _auth_instance

    if _auth_instance is not None:
        return _auth_instance

    if not FIREBASE_API_KEY:
        raise ValueError(
            "Firebase API Key is not configured. "
            "Please set FIREBASE_API_KEY in your .env file."
        )

    config = _get_firebase_config()
    _firebase_app = pyrebase.initialize_app(config)
    _auth_instance = _firebase_app.auth()
    logger.info("Firebase Auth initialized successfully")
    return _auth_instance


def sign_up_with_email(email: str, password: str) -> dict:
    """Create a new user account with email and password.

    Args:
        email: User's email address.
        password: User's password (min 6 characters).

    Returns:
        Dict with user_id, email, and token.

    Raises:
        Exception: If sign-up fails (e.g., email already exists).
    """
    auth = get_auth()

    try:
        user = auth.create_user_with_email_and_password(email, password)
        logger.info("User created: %s", email)
        return {
            "user_id": user["localId"],
            "email": user["email"],
            "token": user["idToken"],
            "refresh_token": user["refreshToken"],
        }
    except Exception as err:
        logger.error("Sign-up failed for %s: %s", email, err)
        raise


def sign_in_with_email(email: str, password: str) -> dict:
    """Sign in an existing user with email and password.

    Args:
        email: User's email address.
        password: User's password.

    Returns:
        Dict with user_id, email, and token.

    Raises:
        Exception: If sign-in fails (e.g., wrong password).
    """
    auth = get_auth()

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        logger.info("User signed in: %s", email)
        return {
            "user_id": user["localId"],
            "email": user["email"],
            "token": user["idToken"],
            "refresh_token": user["refreshToken"],
        }
    except Exception as err:
        logger.error("Sign-in failed for %s: %s", email, err)
        raise


def get_account_info(token: str) -> dict | None:
    """Get current user info from a valid token.

    Args:
        token: Firebase ID token.

    Returns:
        Dict with user info, or None if token is invalid.
    """
    auth = get_auth()

    try:
        info = auth.get_account_info(token)
        users = info.get("users", [])
        if users:
            user = users[0]
            return {
                "user_id": user["localId"],
                "email": user.get("email", ""),
            }
        return None
    except Exception as err:
        logger.warning("Token verification failed: %s", err)
        return None


def refresh_token(refresh_token: str) -> dict | None:
    """Refresh an expired ID token.

    Args:
        refresh_token: Firebase refresh token.

    Returns:
        Dict with new token info, or None if refresh fails.
    """
    auth = get_auth()

    try:
        refreshed = auth.refresh(refresh_token)
        return {
            "token": refreshed["idToken"],
            "refresh_token": refreshed["refreshToken"],
            "user_id": refreshed["userId"],
        }
    except Exception as err:
        logger.warning("Token refresh failed: %s", err)
        return None


def sign_in_with_google_token(google_id_token: str) -> dict:
    """Sign in using a Google ID token obtained from frontend OAuth.

    This is used after the user completes Google Sign-In on the frontend.
    The Google ID token is exchanged for a Firebase ID token via
    Firebase's verifyAssertion REST API.

    Args:
        google_id_token: The Google ID token from frontend OAuth flow.

    Returns:
        Dict with user_id, email, token, and refresh_token.

    Raises:
        Exception: If the token exchange fails.
    """
    import requests

    if not FIREBASE_API_KEY:
        raise ValueError("Firebase API Key is not configured.")

    # Firebase REST API: sign in with OAuth credential
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}"

    payload = {
        "postBody": f"id_token={google_id_token}&providerId=google.com",
        "requestUri": "http://localhost",
        "returnIdpCredential": True,
        "returnSecureToken": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        logger.info("Google sign-in successful: %s", data.get("email", ""))
        return {
            "user_id": data["localId"],
            "email": data.get("email", ""),
            "token": data["idToken"],
            "refresh_token": data["refreshToken"],
            "display_name": data.get("displayName", ""),
            "photo_url": data.get("photoUrl", ""),
        }
    except requests.exceptions.HTTPError as err:
        error_data = err.response.json() if err.response else {}
        error_message = error_data.get("error", {}).get("message", str(err))
        logger.error("Google sign-in failed: %s", error_message)
        raise Exception(f"Google sign-in failed: {error_message}") from err
    except Exception as err:
        logger.error("Google sign-in error: %s", err)
        raise

