
# ============================================================
# SmartBook AI — Worker Dashboard
# ============================================================
# ## Features
# 1. Create professional services.
# 2. View services and their approval status.
# 3. Add future appointment availability.
# 4. View bookings assigned to the worker.
#
# ## Security
# - Database RLS must enforce record ownership.
# - New services are pending and unpublished by default.
# - Approval is a separate trusted operation.
# - Only the appropriate form's submit button triggers its insert.
# ============================================================


# -------------------- IMPORTS -------------------------------

from datetime import datetime, time, timedelta, timezone

import streamlit as st

from database import get_authenticated_supabase


# -------------------- CONFIGURATION -------------------------

# Pakistan Standard Time (UTC+05:00)
PAKISTAN_TZ = timezone(timedelta(hours=5))

INDUSTRIES = ["tutoring", "consulting", "healthcare"]


# -------------------- HELPER FUNCTIONS ----------------------

# ## Get Worker Services

def get_worker_services(access_token, user_id):
    """Return services belonging to the current worker."""

    supabase = get_authenticated_supabase(access_token)

    response = (
        supabase.table("services")
        .select(
            "id, title, description, industry, price, "
            "duration_minutes, eligibility_status, "
            "is_published, created_at"
        )
        .eq("worker_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


# ## Get Worker Availability

def get_worker_slots(access_token, user_id):
    """Return availability slots belonging to the current worker."""

    supabase = get_authenticated_supabase(access_token)

    response = (
        supabase.table("availability_slots")
        .select("id, starts_at, ends_at")
        .eq("worker_id", user_id)
        .order("starts_at", desc=False)
        .limit(100)
        .execute()
    )

    return response.data or []


# ## Get Worker Bookings

def get_worker_bookings(access_token, user_id):
    """Return bookings assigned to the current worker."""

    supabase = get_authenticated_supabase(access_token)

    response = (
        supabase.table("bookings")
        .select(
            "id, status, created_at, "
            "services(title, industry), "
            "availability_slots(starts_at, ends_at)"
        )
        .eq("worker_id", user_id)
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )

    return response.data or []


# -------------------- CREATE SERVICE ------------------------

# ## Insert a New Service

def create_worker_service(
    access_token,
    user_id,
    title,
    description,
    industry,
    price,
    duration_minutes,
):
    """Create a service that awaits trusted approval."""

    if not access_token or not user_id:
        return False, "Please log in again."

    if not title or not title.strip():
        return False, "Please enter a service title."

    if not description or not description.strip():
        return False, "Please describe your service."

    if industry not in INDUSTRIES:
        return False, "Please select a valid industry."

    if price < 0:
        return False, "Price cannot be negative."

    if not 15 <= int(duration_minutes) <= 480:
        return False, "Duration must be between 15 and 480 minutes."

    supabase = get_authenticated_supabase(access_token)

    service_data = {
        "worker_id": user_id,
        "title": title.strip(),
        "description": description.strip(),
        "industry": industry,
        "price": float(price),
        "duration_minutes": int(duration_minutes),
        "eligibility_status": "pending",
        "is_published": False,
    }

    response = (
        supabase.table("services")
        .insert(service_data)
        .execute()
    )

    if response is not None and response.data:
        return True, (
            "Service created successfully. It is pending review "
            "and is not visible to clients yet."
        )

    return False, "The service could not be created."


# -------------------- CREATE AVAILABILITY -------------------

# ## Insert an Availability Slot

def create_availability_slot(
    access_token,
    user_id,
    slot_date,
    start_time,
    end_time,
):
    """Add a future availability slot for the worker."""

    if not access_token or not user_id:
        return False, "Please log in again."

    start_dt = datetime.combine(
        slot_date,
        start_time,
        tzinfo=PAKISTAN_TZ,
    )

    end_dt = datetime.combine(
        slot_date,
        end_time,
        tzinfo=PAKISTAN_TZ,
    )

    now = datetime.now(PAKISTAN_TZ)

    if start_dt <= now:
        return False, "Choose a future appointment time."

    if end_dt <= start_dt:
        return False, "The end time must be after the start time."

    supabase = get_authenticated_supabase(access_token)

    # ## Check for Existing Overlapping Slots
    existing_slots = get_worker_slots(access_token, user_id)

    for slot in existing_slots:
        try:
            existing_start = datetime.fromisoformat(
                slot["starts_at"].replace("Z", "+00:00")
            )

            existing_end = datetime.fromisoformat(
                slot["ends_at"].replace("Z", "+00:00")
            )

            if (
                start_dt < existing_end
                and end_dt > existing_start
            ):
                return False, (
                    "This time overlaps with one of your existing "
                    "availability slots."
                )

        except (ValueError, TypeError, KeyError, AttributeError):
            # Ignore malformed records here; database constraints
            # should independently protect booking integrity.
            continue

    slot_data = {
        "worker_id": user_id,
        "starts_at": start_dt.isoformat(),
        "ends_at": end_dt.isoformat(),
    }

    response = (
        supabase.table("availability_slots")
        .insert(slot_data)
        .execute()
    )

    if response is not None and response.data:
        return True, "Availability slot added successfully."

    return False, "The availability slot could not be saved."


# -------------------- DASHBOARD UI -------------------------

# ## Main Worker Dashboard

def show_worker_dashboard(access_token, user_id):
    """Render the worker dashboard."""

    st.header("🧑‍💼 Worker Dashboard")

    st.write(
        "Manage your professional services, appointment "
        "availability, and bookings."
    )

    # ## Load Dashboard Data

    try:
        services = get_worker_services(access_token, user_id)
        slots = get_worker_slots(access_token, user_id)
        bookings = get_worker_bookings(access_token, user_id)

    except Exception as error:
        st.error("Could not load your worker dashboard.")
        st.caption(str(error))
        return

    # ## Summary Metrics

    total_services = len(services)

    approved_services = sum(
        1
        for service in services
        if service.get("eligibility_status") == "approved"
        and service.get("is_published") is True
    )

    pending_services = sum(
        1
        for service in services
        if service.get("eligibility_status") == "pending"
    )

    confirmed_bookings = sum(
        1
        for booking in bookings
        if booking.get("status") == "confirmed"
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric("My Services", total_services)
    metric2.metric("Published", approved_services)
    metric3.metric("Pending Review", pending_services)
    metric4.metric("Confirmed Bookings", confirmed_bookings)

    # ## Dashboard Tabs

    services_tab, availability_tab, bookings_tab = st.tabs(
        [
            "🛠️ My Services",
            "🗓️ Availability",
            "📋 My Bookings",
        ]
    )

    # ========================================================
    # ## TAB 1 — SERVICES
    # ========================================================

    with services_tab:

        st.subheader("Create a Service")

        # All service inputs belong to this form.
        # No service is created outside its submit handler.

        with st.form(
            "create_worker_service_form",
            clear_on_submit=True,
        ):

            service_title = st.text_input(
                "Service title",
                placeholder="Example: Python Programming Tutoring",
            )

            service_industry = st.selectbox(
                "Industry",
                INDUSTRIES,
            )

            service_description = st.text_area(
                "Service description",
                placeholder=(
                    "Explain what clients will receive from this service."
                ),
                height=120,
            )

            col1, col2 = st.columns(2)

            with col1:
                service_price = st.number_input(
                    "Price",
                    min_value=0.0,
                    value=0.0,
                    step=100.0,
                    help="Enter the price in your chosen currency.",
                )

            with col2:
                service_duration = st.number_input(
                    "Duration (minutes)",
                    min_value=15,
                    max_value=480,
                    value=60,
                    step=15,
                )

            service_submitted = st.form_submit_button(
                "Create Service",
                use_container_width=True,
            )

        # This block executes only when this form is submitted.
        if service_submitted:

            try:
                success, message = create_worker_service(
                    access_token=access_token,
                    user_id=user_id,
                    title=service_title,
                    description=service_description,
                    industry=service_industry,
                    price=service_price,
                    duration_minutes=service_duration,
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

            except Exception as error:
                st.error("Could not create the service.")
                st.caption(str(error))

        st.divider()
        st.subheader("My Existing Services")

        if services:

            for service in services:

                with st.container(border=True):

                    st.markdown(f"**{service['title']}**")

                    st.write(service.get("description", ""))

                    st.caption(
                        f"Industry: {service.get('industry', '').title()} "
                        f"| Price: {service.get('price')} "
                        f"| Duration: "
                        f"{service.get('duration_minutes')} minutes"
                    )

                    status = service.get(
                        "eligibility_status",
                        "pending",
                    )

                    st.write(f"**Review status:** {status.title()}")

                    st.write(
                        "**Published:** "
                        + (
                            "Yes"
                            if service.get("is_published")
                            else "No"
                        )
                    )

        else:
            st.info("You have not created any services yet.")

        st.caption(
            "New services remain unpublished until approved "
            "through the platform's trusted review process."
        )

    # ========================================================
    # ## TAB 2 — AVAILABILITY
    # ========================================================

    with availability_tab:

        st.subheader("Add Appointment Availability")

        st.write(
            "Choose a future date and the start and end times "
            "when clients can book an appointment."
        )

        # This is a separate form from service creation.
        # Submitting it cannot call create_worker_service().

        today = datetime.now(PAKISTAN_TZ).date()

        with st.form(
            "create_availability_form",
            clear_on_submit=False,
        ):

            slot_date = st.date_input(
                "Appointment date",
                value=today,
                min_value=today,
            )

            col1, col2 = st.columns(2)

            with col1:
                slot_start = st.time_input(
                    "Start time",
                    value=time(10, 0),
                )

            with col2:
                slot_end = st.time_input(
                    "End time",
                    value=time(11, 0),
                )

            slot_submitted = st.form_submit_button(
                "Add Availability",
                use_container_width=True,
            )

        # This block executes only when the availability form is submitted.
        if slot_submitted:

            try:
                success, message = create_availability_slot(
                    access_token=access_token,
                    user_id=user_id,
                    slot_date=slot_date,
                    start_time=slot_start,
                    end_time=slot_end,
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

            except Exception as error:
                st.error("Could not add availability.")
                st.caption(str(error))

        st.divider()
        st.subheader("My Availability Slots")

        if slots:

            st.dataframe(
                [
                    {
                        "Slot ID": slot.get("id"),
                        "Starts At": slot.get("starts_at"),
                        "Ends At": slot.get("ends_at"),
                    }
                    for slot in slots
                ],
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.info("You have not added any availability slots.")

    # ========================================================
    # ## TAB 3 — BOOKINGS
    # ========================================================

    with bookings_tab:

        st.subheader("Appointments Assigned to Me")

        if bookings:

            for booking in bookings:

                service = booking.get("services") or {}
                slot = booking.get("availability_slots") or {}

                with st.container(border=True):

                    st.markdown(
                        f"**Booking #{booking.get('id')}**"
                    )

                    st.write(
                        "Service: "
                        f"{service.get('title', 'Unavailable')}"
                    )

                    industry = service.get("industry") or "Unknown"

                    st.write(f"Industry: {industry.title()}")

                    st.write(
                        "Start: "
                        f"{slot.get('starts_at', 'Unavailable')}"
                    )

                    st.write(
                        "End: "
                        f"{slot.get('ends_at', 'Unavailable')}"
                    )

                    status = booking.get("status") or "unknown"

                    st.write(f"Status: {status.title()}")

        else:
            st.info(
                "You do not have any bookings assigned to you yet."
            )


# ============================================================
# End of worker_dashboard.py
# ============================================================
