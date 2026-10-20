# ============================================================
# SmartBook AI — Authentication Module
# ============================================================
# Features:
# - Register new client accounts
# - Redirect confirmation emails to the correct app URL
# - Authenticate users with Supabase Auth
# - Restore sessions using access and refresh tokens
# - Sign out authenticated sessions
#
# Security:
# - Signup always assigns client metadata
# - Metadata alone does not grant worker privileges
# - Supabase Auth manages passwords
# - Session tokens must be handled securely
# ============================================================

import os

from dotenv import load_dotenv
from supabase import create_client


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Set APP_URL in Streamlit Cloud Secrets or local .env.
# Cloud example: https://your-app-name.streamlit.app
# Local example: http://localhost:8501
APP_URL = os.getenv("APP_URL", "").strip().rstrip("/")


# ------------------------------------------------------------
# Create Authentication Client
# ------------------------------------------------------------

def get_auth_client():
    """Create a Supabase client for authentication."""

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Check SUPABASE_URL and SUPABASE_KEY "
            "in your environment configuration."
        )

    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ------------------------------------------------------------
# Signup
# ------------------------------------------------------------

def signup_user(email, password, full_name, role="client"):
    """
    Register a client account and configure the email
    confirmation redirect when APP_URL is available.

    Returns:
        (True, message) on success.
        (False, error_message) on failure.
    """

    email = (email or "").strip()
    full_name = (full_name or "").strip()

    if not email:
        return False, "Please enter your email address."

    if not password:
        return False, "Please enter a password."

    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    if not full_name:
        return False, "Please enter your full name."

    try:
        supabase = get_auth_client()

        options = {
            "data": {
                "full_name": full_name,
                # Informational metadata only.
                # Enforce authorization in trusted database logic.
                "role": "client",
            }
        }

        # Supabase uses this URL after email confirmation.
        # Add the same URL to Supabase Auth Redirect URLs.
        if APP_URL:
            options["email_redirect_to"] = APP_URL

        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": options,
        })

        if response.user is None:
            return False, "Signup failed. Please try again."

        return True, (
            "Account created successfully. "
            "Check your email to confirm your account. "
            "After confirmation, return to SmartBook AI and log in."
        )

    except Exception as error:
        return False, str(error)


# ------------------------------------------------------------
# Login
# ------------------------------------------------------------

def login_user(email, password):
    """Authenticate an existing user with Supabase Auth."""

    email = (email or "").strip()

    if not email or not password:
        return False, "Please enter your email and password."

    try:
        supabase = get_auth_client()

        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        if response.user is None or response.session is None:
            return False, "Login failed. Please try again."

        return True, response

    except Exception as error:
        return False, str(error)


# ------------------------------------------------------------
# Restore Session
# ------------------------------------------------------------

def restore_user_session(access_token, refresh_token):
    """Restore a session using access and refresh tokens."""

    if not access_token or not refresh_token:
        raise ValueError("Both session tokens are required.")

    supabase = get_auth_client()

    response = supabase.auth.set_session(
        access_token,
        refresh_token,
    )

    if response.user is None or response.session is None:
        raise ValueError("Could not restore the saved session.")

    return response


# ------------------------------------------------------------
# Logout
# ------------------------------------------------------------

def logout_user(access_token, refresh_token):
    """Sign out the authenticated Supabase session."""

    try:
        if not access_token or not refresh_token:
            return False, "No valid session was provided."

        supabase = get_auth_client()

        supabase.auth.set_session(
            access_token,
            refresh_token,
        )

        supabase.auth.sign_out()

        return True, "Logged out successfully."

    except Exception as error:
        return False, str(error)


# ============================================================
# End of auth.py
# ============================================================
