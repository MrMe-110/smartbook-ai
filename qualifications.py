
# ============================================================
# SmartBook AI — Qualifications and Eligibility
# ============================================================
# ## Purpose
# Check whether a worker application contains the minimum
# information required for its selected industry.
#
# ## Supported Industries
# 1. Healthcare
# 2. Tutoring
# 3. Consulting
#
# ## Important Security Rule
# These checks do NOT verify professional licenses, degrees,
# certificates, identity, or actual professional competence.
#
# Healthcare credentials require an appropriate external
# verification process before regulated services are published.
# ============================================================


# ------------------------------------------------------------
# ## Industry Requirements
# ------------------------------------------------------------

INDUSTRY_REQUIREMENTS = {
    "healthcare": {
        "name": "Healthcare",
        "description_min_length": 30,
        "evidence_required": True,
        "note": (
            "Appropriate credential and licensing verification "
            "is required before regulated healthcare services "
            "can be published."
        ),
    },
    "tutoring": {
        "name": "Tutoring",
        "description_min_length": 30,
        "evidence_required": False,
        "note": (
            "Education, subject expertise, and experience may "
            "be reviewed before services are approved."
        ),
    },
    "consulting": {
        "name": "Consulting",
        "description_min_length": 30,
        "evidence_required": False,
        "note": (
            "Relevant experience and supporting evidence may "
            "be reviewed before services are approved."
        ),
    },
}


# ------------------------------------------------------------
# ## Get Industry Requirements
# ------------------------------------------------------------

def get_industry_requirements(industry):
    """
    Return the requirements for a supported industry.

    Parameters
    ----------
    industry : str
        healthcare, tutoring, or consulting.

    Returns
    -------
    dict or None
        Industry requirements, or None if the industry is invalid.
    """

    if not industry:
        return None

    return INDUSTRY_REQUIREMENTS.get(industry.strip().lower())


# ------------------------------------------------------------
# ## Assess Qualification Application
# ------------------------------------------------------------

def assess_qualification_application(
    industry,
    description,
    evidence_url="",
):
    """
    Check application completeness and evidence requirements.

    This function performs basic completeness checks only.
    It does not independently verify credentials.

    Returns
    -------
    dict
        complete:
            Whether the minimum submission requirements pass.

        industry:
            Normalized industry name.

        qualification_status:
            Evidence or verification status.

        eligibility_status:
            Application completeness status.

        message:
            Explanation for the applicant.
    """

    # --------------------------------------------------------
    # Step 1: Validate the selected industry
    # --------------------------------------------------------

    industry = industry.strip().lower() if industry else ""

    requirements = get_industry_requirements(industry)

    if requirements is None:
        return {
            "complete": False,
            "industry": industry,
            "qualification_status": "not_required",
            "eligibility_status": "incomplete",
            "message": (
                "Please select healthcare, tutoring, or consulting."
            ),
        }

    # --------------------------------------------------------
    # Step 2: Validate the professional description
    # --------------------------------------------------------

    description = description.strip() if description else ""

    minimum_length = requirements["description_min_length"]

    if len(description) < minimum_length:
        return {
            "complete": False,
            "industry": industry,
            "qualification_status": "pending",
            "eligibility_status": "incomplete",
            "message": (
                f"Please provide at least {minimum_length} characters "
                "describing your professional services and experience."
            ),
        }

    # --------------------------------------------------------
    # Step 3: Check the evidence requirement
    # --------------------------------------------------------

    evidence_url = evidence_url.strip() if evidence_url else ""

    if requirements["evidence_required"] and not evidence_url:
        return {
            "complete": False,
            "industry": industry,
            "qualification_status": "pending",
            "eligibility_status": "incomplete",
            "message": (
                "For healthcare applications, provide an appropriate "
                "credential or licensing evidence link. The link must "
                "still undergo independent verification."
            ),
        }

    # --------------------------------------------------------
    # Step 4: Determine preliminary status
    # --------------------------------------------------------

    if industry == "healthcare":
        qualification_status = "pending"
        eligibility_status = "pending"

        message = (
            "The application meets the basic submission requirements. "
            "Healthcare credentials still require independent "
            "verification and review."
        )

    elif evidence_url:
        qualification_status = "unverified"
        eligibility_status = "pending"

        message = (
            "The application meets the basic completeness checks. "
            "The supplied evidence has not been independently verified, "
            "and the application still requires review."
        )

    else:
        qualification_status = "not_required"
        eligibility_status = "pending"

        message = (
            "The application meets the basic completeness checks. "
            "It still requires review before services can be approved."
        )

    # --------------------------------------------------------
    # Step 5: Return the assessment
    # --------------------------------------------------------

    return {
        "complete": True,
        "industry": industry,
        "qualification_status": qualification_status,
        "eligibility_status": eligibility_status,
        "message": message,
    }


# ============================================================
# End of qualifications.py
# ============================================================
