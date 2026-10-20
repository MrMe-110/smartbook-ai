
import json
import logging

from langchain.tools import tool

from services import search_services
from availability import get_available_slots
from bookings import get_my_bookings

logger = logging.getLogger(__name__)


def get_booking_tools(access_token):
    """Create booking tools scoped to the authenticated session."""

    if not access_token:
        raise ValueError("An authenticated access token is required.")

    @tool
    def find_services(
        industry: str = "all",
        keyword: str = ""
    ) -> str:
        """Search published and approved services.

        Industry options: all, healthcare, tutoring, consulting.
        Keyword searches service titles and descriptions.
        """
        allowed = {
            "all",
            "healthcare",
            "tutoring",
            "consulting"
        }

        selected_industry = industry.strip().lower()
        keyword = keyword.strip()

        if selected_industry not in allowed:
            return (
                "Invalid industry. Choose all, healthcare, "
                "tutoring, or consulting."
            )

        try:
            results = search_services(
                access_token,
                selected_industry,
                keyword
            )

            if not results:
                return "No matching approved services were found."

            return json.dumps(results, default=str)

        except Exception:
            logger.exception("Service search tool failed")
            return "Service search is temporarily unavailable. Please try again."

    @tool
    def check_availability(service_id: int) -> str:
        """Find available future appointment slots for a service ID.

        Use the service ID returned by find_services.
        """
        if service_id <= 0:
            return "Please provide a valid service ID."

        try:
            slots = get_available_slots(
                access_token,
                service_id
            )

            if not slots:
                return (
                    "No available future slots were found "
                    "for this service."
                )

            return json.dumps(slots, default=str)

        except Exception:
            logger.exception("Availability tool failed")
            return "Availability could not be checked. Please try again."

    @tool
    def view_my_bookings() -> str:
        """View bookings belonging to the authenticated user.

        Never request another person's user ID.
        """
        try:
            bookings = get_my_bookings(access_token)

            if not bookings:
                return "You do not have any bookings yet."

            return json.dumps(bookings, default=str)

        except Exception:
            logger.exception("Booking history tool failed")
            return "Your bookings could not be retrieved. Please try again."

    return [
        find_services,
        check_availability,
        view_my_bookings
    ]
