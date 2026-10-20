
import streamlit as st

from bookings import (
    get_my_bookings,
    get_available_slots,
    create_booking,
    cancel_booking,
)
from services import search_services


def show_client_dashboard(access_token, user_id):
    st.title("📅 SmartBook AI")
    st.subheader("Your Appointment Dashboard")

    tab_services, tab_bookings = st.tabs(
        ["🔎 Find & Book Services", "📋 My Appointments"]
    )

    # ==================================================
    # TAB 1: FIND AND BOOK SERVICES
    # ==================================================
    with tab_services:
        st.subheader("Find a Service")

        industry = st.selectbox(
            "Choose an industry",
            ["all", "healthcare", "tutoring", "consulting"],
            format_func=lambda x: x.title(),
            key="client_industry",
        )

        keyword = st.text_input(
            "Search by service name or description",
            key="client_keyword",
        )

        if st.button("🔎 Search Services", key="search_services"):
            st.session_state["client_search_requested"] = True

        if st.session_state.get("client_search_requested", False):
            try:
                services = search_services(
                    access_token,
                    industry=industry,
                    keyword=keyword,
                )

                if not services:
                    st.info(
                        "No approved services found. "
                        "Try another industry or search term."
                    )

                for service in services:
                    service_id = int(service["id"])
                    slot_key = f"slots_{service_id}"
                    confirm_key = f"confirm_booking_{service_id}"

                    with st.container(border=True):
                        st.markdown(
                            f"### {service.get('title', 'Service')}"
                        )
                        st.write(service.get("description", ""))

                        st.write(
                            f"**Industry:** "
                            f"{service.get('industry', 'N/A').title()}"
                        )
                        st.write(
                            f"**Price:** "
                            f"{service.get('price', 'Contact provider')}"
                        )
                        st.write(
                            f"**Duration:** "
                            f"{service.get('duration_minutes', 'N/A')} minutes"
                        )

                        # CHECK AVAILABLE TIMES
                        if st.button(
                            "Check Available Times",
                            key=f"check_{service_id}",
                        ):
                            try:
                                slots = get_available_slots(
                                    access_token,
                                    service_id,
                                )
                                st.session_state[slot_key] = slots or []
                                st.session_state.pop(confirm_key, None)

                                if not slots:
                                    st.info(
                                        "No available times for this service."
                                    )

                            except Exception as error:
                                st.error(
                                    f"Could not load available times: {error}"
                                )

                        slots = st.session_state.get(slot_key, [])

                        # DISPLAY AVAILABLE SLOTS
                        if slots:
                            slot_options = {}

                            for slot in slots:
                                slot_id = (
                                    slot.get("slot_id")
                                    or slot.get("id")
                                )
                                starts_at = slot.get("starts_at")
                                ends_at = slot.get("ends_at")

                                if slot_id is not None and starts_at:
                                    label = str(starts_at)

                                    if ends_at:
                                        label += f" — {ends_at}"

                                    slot_options[label] = int(slot_id)

                            if not slot_options:
                                st.warning(
                                    "Slots were returned, but their IDs "
                                    "or start times are missing."
                                )
                            else:
                                selected_label = st.selectbox(
                                    "Select an appointment time",
                                    list(slot_options.keys()),
                                    key=f"slot_select_{service_id}",
                                )

                                if st.button(
                                    "Book This Appointment",
                                    key=f"book_{service_id}",
                                ):
                                    st.session_state[confirm_key] = True

                                # BOOKING CONFIRMATION
                                if st.session_state.get(confirm_key, False):
                                    st.warning(
                                        f"Please confirm: {selected_label}"
                                    )

                                    yes_col, no_col = st.columns(2)

                                    with yes_col:
                                        if st.button(
                                            "Confirm Booking",
                                            key=f"confirm_yes_{service_id}",
                                        ):
                                            try:
                                                result = create_booking(
                                                    access_token,
                                                    service_id,
                                                    slot_options[selected_label],
                                                )

                                                if result.get("success"):
                                                    st.success(
                                                        result.get(
                                                            "message",
                                                            "Appointment booked successfully!",
                                                        )
                                                    )
                                                    st.session_state.pop(
                                                        slot_key, None
                                                    )
                                                    st.session_state.pop(
                                                        confirm_key, None
                                                    )
                                                    st.rerun()
                                                else:
                                                    st.error(
                                                        result.get(
                                                            "message",
                                                            "Booking failed. The slot may no longer be available.",
                                                        )
                                                    )

                                            except Exception as error:
                                                st.error(
                                                    f"Booking failed: {error}"
                                                )

                                    with no_col:
                                        if st.button(
                                            "Go Back",
                                            key=f"confirm_no_{service_id}",
                                        ):
                                            st.session_state.pop(
                                                confirm_key, None
                                            )
                                            st.rerun()

            except Exception as error:
                st.error(f"Could not search services: {error}")

    # ==================================================
    # TAB 2: MY APPOINTMENTS
    # ==================================================
    with tab_bookings:
        st.subheader("My Appointments")

        if st.button("🔄 Refresh Appointments"):
            st.rerun()

        try:
            appointments = get_my_bookings(access_token)

            if not appointments:
                st.info("You don't have any appointments yet.")

            for appointment in appointments:
                booking_id = appointment["id"]
                status = appointment.get("status", "unknown")

                service_data = appointment.get("services") or {}
                slot_data = appointment.get("availability_slots") or {}

                if isinstance(service_data, list):
                    service_data = (
                        service_data[0] if service_data else {}
                    )

                if isinstance(slot_data, list):
                    slot_data = slot_data[0] if slot_data else {}

                with st.container(border=True):
                    st.markdown(
                        f"### {service_data.get('title', 'Appointment')}"
                    )
                    st.write(f"**Booking ID:** {booking_id}")
                    st.write(f"**Status:** {status.title()}")
                    st.write(
                        f"**Industry:** "
                        f"{service_data.get('industry', 'N/A')}"
                    )
                    st.write(
                        f"**Starts:** "
                        f"{slot_data.get('starts_at', 'N/A')}"
                    )
                    st.write(
                        f"**Ends:** "
                        f"{slot_data.get('ends_at', 'N/A')}"
                    )

                    # CANCEL CONFIRMED BOOKINGS
                    if status == "confirmed":
                        confirm_cancel_key = (
                            f"confirm_cancel_{booking_id}"
                        )

                        if st.button(
                            "Cancel Appointment",
                            key=f"cancel_{booking_id}",
                        ):
                            st.session_state[confirm_cancel_key] = True

                        if st.session_state.get(
                            confirm_cancel_key, False
                        ):
                            st.warning(
                                "Are you sure you want to cancel this booking?"
                            )

                            yes_col, no_col = st.columns(2)

                            with yes_col:
                                if st.button(
                                    "Confirm Cancellation",
                                    key=f"cancel_yes_{booking_id}",
                                ):
                                    try:
                                        result = cancel_booking(
                                            access_token,
                                            booking_id,
                                        )

                                        if result.get("success"):
                                            st.success(
                                                result.get(
                                                    "message",
                                                    "Appointment cancelled.",
                                                )
                                            )
                                            st.session_state.pop(
                                                confirm_cancel_key, None
                                            )
                                            st.rerun()
                                        else:
                                            st.error(
                                                result.get(
                                                    "message",
                                                    "Cancellation failed.",
                                                )
                                            )

                                    except Exception as error:
                                        st.error(
                                            f"Cancellation failed: {error}"
                                        )

                            with no_col:
                                if st.button(
                                    "Keep Appointment",
                                    key=f"cancel_no_{booking_id}",
                                ):
                                    st.session_state.pop(
                                        confirm_cancel_key, None
                                    )
                                    st.rerun()

        except Exception as error:
            st.error(
                "Could not load appointments. "
                f"Please check your database policies. Details: {error}"
            )
