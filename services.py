
from database import get_authenticated_supabase


def search_services(access_token, industry="all", keyword=""):
    """Find published, approved professional services."""

    supabase = get_authenticated_supabase(access_token)

    query = (
        supabase.table("services")
        .select(
            "id, worker_id, title, description, industry, "
            "price, duration_minutes"
        )
        .eq("is_published", True)
        .eq("eligibility_status", "approved")
    )

    if industry != "all":
        query = query.eq("industry", industry)

    response = query.limit(100).execute()
    services = response.data or []

    if keyword.strip():
        keyword = keyword.strip().lower()
        services = [
            service for service in services
            if keyword in service["title"].lower()
            or keyword in service["description"].lower()
        ]

    return services
