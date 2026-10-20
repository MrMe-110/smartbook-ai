
# ============================================================
# SmartBook AI — Booking Operations
# ============================================================
# Features:
# 1. View the authenticated user's bookings.
# 2. Create a booking using the secure Supabase RPC.
# 3. Cancel a booking using the secure Supabase RPC.
# 4. Retrieve available slots for an approved service.
#
# Security:
# - Uses the current user's access token.
# - Never accepts another user's identity from the UI or AI.
# - Booking conflicts are enforced by Supabase.
# ============================================================


# -------------------- IMPORTS -------------------------------

from database import get_authenticated_supabase


# -------------------- VIEW MY BOOKINGS ----------------------

def get_my_bookings(access_token):
    """
    Return bookings visible to the authenticated user.

    RLS should restrict clients to their own bookings and
    workers to bookings assigned to them.
    """

    supabase = get_authenticated_supabase(access_token)

    response = (
        supabase.table("bookings")
        .select(
            "id, status, created_at, "
            "services(title, industry, price, duration_minutes), "
            "availability_slots(starts_at, ends_at)"
        )
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )

    if response is None or response.data is None:
        return []

    return response.data


# -------------------- GET AVAILABLE SLOTS -------------------

def get_available_slots(access_token, service_id):
    """
    Retrieve future available slots for an approved service.

    The database function must validate publication,
    approval, time, and booking status.
    """

    if not service_id or int(service_id) <= 0:
        raise ValueError("Please provide a valid service ID.")

    supabase = get_authenticated_supabase(access_token)

    response = supabase.rpc(
        "get_available_slots",
        {"p_service_id": int(service_id)},
    ).execute()

    if response is None or response.data is None:
        return []

    return response.data


# -------------------- CREATE BOOKING ------------------------

def create_booking(access_token, service_id, slot_id):
    """
    Create a booking through the secure database function.

    The database checks the authenticated user, service,
    slot ownership, future time, and booking conflicts.
    """

    if int(service_id) <= 0 or int(slot_id) <= 0:
        return {
            "success": False,
            "message": "Please select a valid service and time slot.",
        }

    supabase = get_authenticated_supabase(access_token)

    response = supabase.rpc(
        "create_booking",
        {
            "p_service_id": int(service_id),
            "p_slot_id": int(slot_id),
        },
    ).execute()

    if response is None or response.data is None:
        return {
            "success": False,
            "message": "The booking could not be confirmed.",
        }

    result = response.data

    # The SQL function returns JSONB.
    if isinstance(result, dict):
        return result

    return {
        "success": False,
        "message": "Unexpected booking response from the database.",
    }


# -------------------- CANCEL BOOKING -----------------------

def cancel_booking(access_token, booking_id):
    """
    Cancel a confirmed booking through the database function.

    The database verifies that the current user is allowed
    to cancel the selected booking.
    """

    if int(booking_id) <= 0:
        return {
            "success": False,
            "message": "Please provide a valid booking ID.",
        }

    supabase = get_authenticated_supabase(access_token)

    response = supabase.rpc(
        "cancel_booking",
        {"p_booking_id": int(booking_id)},
    ).execute()

    if response is None or response.data is None:
        return {
            "success": False,
            "message": "The cancellation could not be completed.",
        }

    result = response.data

    if isinstance(result, dict):
        return result

    return {
        "success": False,
        "message": "Unexpected cancellation response from the database.",
    }


# -------------------- END OF FILE ---------------------------
