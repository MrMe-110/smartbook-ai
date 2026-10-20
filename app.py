# ============================================================
# SmartBook AI — Main Application
# ============================================================
# Features:
# - Signup and login
# - Cookie-based session restoration
# - Supabase profile management
# - Client service discovery and appointment booking
# - Worker applications and dashboard
# - LangChain AI booking assistant
#
# Security:
# - New accounts begin as clients
# - Authenticated sessions are required
# - Database RLS must enforce data ownership
# - Worker approval must use a trusted review process
# ============================================================

import json

import streamlit as st
import extra_streamlit_components as stx
from dotenv import load_dotenv

from auth import (
    signup_user,
    login_user,
    logout_user,
    restore_user_session,
)
from profiles import get_user_profile
from worker_applications import (
    get_my_application,
    submit_worker_application,
)
from qualifications import assess_qualification_application
from worker_dashboard import show_worker_dashboard
from client_dashboard import show_client_dashboard
from chat_ui import show_ai_booking_assistant


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="SmartBook AI",
    page_icon="📅",
    layout="wide",
)

st.title("📅 SmartBook AI")
st.caption(
    "Discover professional services, manage appointments, "
    "and use AI to find available services."
)


# ------------------------------------------------------------
# Cookie Setup
# ------------------------------------------------------------

cookies = stx.CookieManager(key="smartbook_cookie_manager")


# ------------------------------------------------------------
# Session State
# ------------------------------------------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None


def save_session(user, session):
    """Save authenticated session information."""

    st.session_state.user = user
    st.session_state.access_token = session.access_token
    st.session_state.refresh_token = session.refresh_token

    cookies.set(
        "sb_session",
        json.dumps({
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }),
    )


def clear_session():
    """Clear the current session and saved cookie."""

    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.refresh_token = None

    try:
        cookies.delete("sb_session")
    except Exception:
        pass


# ------------------------------------------------------------
# Restore Session
# ------------------------------------------------------------

if st.session_state.user is None:
    saved_session = cookies.get("sb_session")

    if saved_session:
        try:
            tokens = json.loads(saved_session)

            restored = restore_user_session(
                tokens["access_token"],
                tokens["refresh_token"],
            )

            if (
                restored
                and restored.user
                and restored.session
            ):
                save_session(
                    restored.user,
                    restored.session,
                )
            else:
                clear_session()

        except Exception:
            clear_session()


# ------------------------------------------------------------
# Login and Signup
# ------------------------------------------------------------

if st.session_state.user is None:

    login_tab, signup_tab = st.tabs([
        "🔑 Login",
        "📝 Create Account",
    ])

    # -------------------- Login -----------------------------

    with login_tab:
        st.subheader("Welcome back")

        with st.form("login_form"):
            login_email = st.text_input("Email")

            login_password = st.text_input(
                "Password",
                type="password",
            )

            login_submitted = st.form_submit_button(
                "Login",
                use_container_width=True,
            )

        if login_submitted:
            if (
                not login_email.strip()
                or not login_password
            ):
                st.warning(
                    "Please enter your email and password."
                )
            else:
                try:
                    success, result = login_user(
                        login_email.strip(),
                        login_password,
                    )

                    if success and result.session:
                        save_session(
                            result.user,
                            result.session,
                        )
                        st.success("Login successful!")
                        st.rerun()

                    elif success:
                        st.info(
                            "Check your email if confirmation "
                            "is required, then log in."
                        )

                    else:
                        st.error(f"Login failed: {result}")

                except Exception:
                    st.error(
                        "Login failed. Please check your "
                        "credentials and try again."
                    )

    # -------------------- Signup ----------------------------

    with signup_tab:
        st.subheader("Create an account")

        st.write(
            "New accounts begin as clients. You can apply "
            "to become a professional after signing in."
        )

        with st.form("signup_form"):
            full_name = st.text_input("Full name")
            signup_email = st.text_input("Email address")

            signup_password = st.text_input(
                "Password",
                type="password",
            )

            signup_submitted = st.form_submit_button(
                "Create Account",
                use_container_width=True,
            )

        if signup_submitted:
            if not full_name.strip():
                st.warning("Please enter your name.")

            elif (
                not signup_email.strip()
                or not signup_password
            ):
                st.warning(
                    "Please enter your email and password."
                )

            elif len(signup_password) < 6:
                st.warning(
                    "Use a password with at least 6 characters."
                )

            else:
                try:
                    success, message = signup_user(
                        signup_email.strip(),
                        signup_password,
                        full_name.strip(),
                        "client",
                    )

                    if success:
                        st.success(message)
                    else:
                        st.error(message)

                except Exception:
                    st.error(
                        "Account creation failed. Please try again."
                    )

    st.stop()


# ------------------------------------------------------------
# Validate Authenticated Session
# ------------------------------------------------------------

user = st.session_state.user
access_token = st.session_state.access_token
user_id = getattr(user, "id", None)

if not user_id or not access_token:
    clear_session()
    st.warning(
        "Your session is incomplete. Please log in again."
    )
    st.rerun()


# ------------------------------------------------------------
# Sidebar and Logout
# ------------------------------------------------------------

st.sidebar.title("SmartBook AI")

st.sidebar.write(
    f"**Email:** {getattr(user, 'email', 'Not available')}"
)

st.sidebar.success("Logged in")

if st.sidebar.button(
    "Logout",
    use_container_width=True,
):
    try:
        logout_user(
            st.session_state.access_token,
            st.session_state.refresh_token,
        )
    finally:
        clear_session()

    st.rerun()


# ------------------------------------------------------------
# Load User Profile
# ------------------------------------------------------------

st.header("👤 Your Account")

try:
    profile = get_user_profile(access_token)

    if not profile:
        st.error(
            "Your account profile could not be found."
        )
        st.stop()

except Exception:
    st.error("Could not load your account profile.")
    st.stop()


st.write(
    f"**Name:** {profile.get('full_name') or 'Not provided'}"
)

role = profile.get("role", "client")

st.write(f"**Role:** {role.title()}")


# ============================================================
# Client Dashboard and Worker Application
# ============================================================

if role == "client":

    st.divider()

    show_client_dashboard(
        access_token=access_token,
        user_id=user_id,
    )

    st.divider()
    st.header("🏢 Become a Professional")

    try:
        application = get_my_application(
            access_token,
            user_id,
        )

        if application:
            st.info(
                "Worker application status: "
                f"**{application.get('status', 'pending').title()}**"
            )

            st.write(
                f"**Industry:** "
                f"{application.get('industry', '').title()}"
            )

            st.write(
                "**Description:** "
                f"{application.get('professional_description', '')}"
            )

            if application.get("evidence_url"):
                st.write(
                    f"**Evidence:** {application['evidence_url']}"
                )

            st.caption(
                "Applications require trusted review. Evidence "
                "links alone do not establish verified qualifications."
            )

        else:
            st.write(
                "Apply to offer healthcare, tutoring, or "
                "consulting services on SmartBook AI."
            )

            with st.form("worker_application_form"):
                business_name = st.text_input(
                    "Business or professional name",
                    placeholder="Enter your professional name",
                )

                industry = st.selectbox(
                    "Industry",
                    [
                        "tutoring",
                        "consulting",
                        "healthcare",
                    ],
                )

                description = st.text_area(
                    "Professional description",
                    placeholder=(
                        "Describe your services, experience, "
                        "and relevant expertise..."
                    ),
                    height=130,
                )

                evidence_url = st.text_input(
                    "Qualification or evidence link",
                    placeholder="https://...",
                )

                application_submitted = st.form_submit_button(
                    "Submit Worker Application",
                    use_container_width=True,
                )

            if application_submitted:
                assessment = assess_qualification_application(
                    industry=industry,
                    description=description,
                    evidence_url=evidence_url,
                )

                if not business_name.strip():
                    st.error(
                        "Please enter your business or "
                        "professional name."
                    )

                elif not assessment.get("complete", False):
                    st.error(assessment["message"])

                else:
                    success, message = submit_worker_application(
                        access_token=access_token,
                        user_id=user_id,
                        business_name=business_name,
                        industry=industry,
                        professional_description=description,
                        evidence_url=evidence_url,
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    except Exception:
        st.error(
            "Could not load the worker application section."
        )


# ============================================================
# Worker Dashboard
# ============================================================

elif role == "worker":

    show_worker_dashboard(
        access_token=access_token,
        user_id=user_id,
    )


# ============================================================
# AI Booking Assistant
# ============================================================

st.divider()

show_ai_booking_assistant(
    access_token=access_token,
    user_id=user_id,
)


# ============================================================
# End of app.py
# ============================================================
