
# ============================================================
# SmartBook AI — User Profiles
# ============================================================
# ## Purpose
# Retrieve the authenticated user's profile from Supabase.
#
# ## Security
# - Uses the user's access token.
# - Does not accept a user_id from the UI.
# - Relies on Supabase Row Level Security (RLS) to restrict access.
# ============================================================

# ------------------------------------------------------------
# ## Imports
# ------------------------------------------------------------

from database import get_authenticated_supabase


# ------------------------------------------------------------
# ## Get Current User Profile
# ------------------------------------------------------------

def get_user_profile(access_token):
    """
    Fetch the authenticated user's profile.

    Args:
        access_token: The current Supabase access token.

    Returns:
        Profile dictionary if found, otherwise None.

    Raises:
        ValueError: If the access token is missing.
    """

    # ## Validate the Session Token
    if not access_token or not isinstance(access_token, str):
        raise ValueError("A valid access token is required.")

    # ## Create an Authenticated Supabase Client
    supabase = get_authenticated_supabase(access_token)

    # ## Fetch the Profile
    response = (
        supabase.table("profiles")
        .select("user_id, full_name, role, created_at")
        .maybe_single()
        .execute()
    )

    # ## Return the Profile
    return response.data


# ============================================================
# End of profiles.py
# ============================================================
