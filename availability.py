
from database import get_authenticated_supabase


def get_available_slots(access_token, service_id):
    """Get available future slots for an approved service."""

    supabase = get_authenticated_supabase(access_token)

    response = supabase.rpc(
        "get_available_slots",
        {"p_service_id": service_id}
    ).execute()

    return response.data or []
