
# ============================================================
# SmartBook AI — Worker Applications
# ============================================================
# ## Purpose
# Manage professional applications for workers who want to
# offer services through SmartBook AI.
#
# ## Features
# 1. Retrieve the logged-in user's application.
# 2. Validate application information.
# 3. Check qualification requirements.
# 4. Prevent duplicate application submissions.
# 5. Submit applications with a pending status.
#
# ## Supported Industries
# - Healthcare
# - Tutoring
# - Consulting
#
# ## Security
# - The user must be authenticated.
# - RLS must enforce application ownership.
# - Approval must be performed through a trusted process.
# - Healthcare credentials require independent verification.
# - An evidence URL alone does not prove a credential is valid.
# ============================================================

from database import get_authenticated_supabase
from qualifications import assess_qualification_application


# ------------------------------------------------------------
# ## Configuration
# ------------------------------------------------------------

SUPPORTED_INDUSTRIES = {
    "healthcare",
    "tutoring",
    "consulting",
}


# ------------------------------------------------------------
# ## Get My Application
# ------------------------------------------------------------

def get_my_application(access_token, user_id):
    """
    Retrieve the current user's worker application.

    Parameters:
        access_token: Authenticated Supabase access token.
        user_id: ID of the authenticated user.

    Returns:
        The application dictionary, or None if not found.
    """

    if not access_token or not user_id:
        raise ValueError("Please log in to view your application.")

    supabase = get_authenticated_supabase(access_token)

    response = (
        supabase.table("worker_applications")
        .select(
            "id, user_id, business_name, industry, "
            "professional_description, evidence_url, status, "
            "credential_verified, created_at"
        )
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    applications = response.data or []

    return applications[0] if applications else None


# ------------------------------------------------------------
# ## Submit Worker Application
# ------------------------------------------------------------

def submit_worker_application(
    access_token,
    user_id,
    business_name,
    industry,
    professional_description,
    evidence_url="",
):
    """
    Validate and submit a worker application for review.

    New applications remain pending until a trusted reviewer
    approves them.

    Returns:
        (True, success_message) when submission succeeds.
        (False, error_message) when validation or submission fails.
    """

    # Step 1: Check authentication.
    if not access_token or not user_id:
        return False, "Please log in before submitting an application."

    # Step 2: Clean the submitted information.
    business_name = (business_name or "").strip()
    professional_description = (
        professional_description or ""
    ).strip()
    industry = (industry or "").strip().lower()
    evidence_url = (evidence_url or "").strip()

    # Step 3: Validate required fields.
    if not business_name:
        return False, "Please enter your business or professional name."

    if industry not in SUPPORTED_INDUSTRIES:
        return False, "Please select a supported industry."

    if len(professional_description) < 30:
        return False, (
            "Please provide at least 30 characters describing "
            "your qualifications and services."
        )

    # Step 4: Require evidence for healthcare applications.
    if industry == "healthcare" and not evidence_url:
        return False, (
            "Healthcare applications require credential evidence "
            "for independent verification."
        )

    # Step 5: Assess application completeness.
    # This assessment does not independently verify credentials.
    assessment = assess_qualification_application(
        industry=industry,
        description=professional_description,
        evidence_url=evidence_url,
    )

    # Support a dictionary-based assessment result.
    if not assessment.get("complete", False):
        return False, assessment.get(
            "message",
            "Please complete the application requirements."
        )

    # Step 6: Connect using the user's authenticated session.
    supabase = get_authenticated_supabase(access_token)

    # Step 7: Check for an existing application.
    existing = (
        supabase.table("worker_applications")
        .select("id, status")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if existing.data:
        current_status = existing.data[0].get("status", "pending")

        return False, (
            "You already have an application "
            f"(status: {current_status}). Please check its status "
            "instead of submitting another application."
        )

    # Step 8: Prepare the application for database insertion.
    application_data = {
        "user_id": user_id,
        "business_name": business_name,
        "industry": industry,
        "professional_description": professional_description,
        "evidence_url": evidence_url or None,
        "status": "pending",
    }

    # Step 9: Save the application.
    response = (
        supabase.table("worker_applications")
        .insert(application_data)
        .execute()
    )

    # Step 10: Return the submission result.
    if response.data:
        return True, (
            "Your application was submitted successfully. "
            "It must be reviewed before you can offer services."
        )

    return False, "The application could not be submitted."


# ============================================================
# End of worker_applications.py
# ============================================================
