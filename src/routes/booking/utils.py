from datetime import datetime, timedelta

from typing import Dict, List, Union


def render_bookings(bookings: List[Dict[str, Union[str, int]]]) -> str:
    """
    Рендер в HTML список записей на прокат.
    """
    html_bookings = [
        (
            f"🔘 <strong>{booking["id"]}</strong>: <em>{booking["date"]} |"
            f" {booking["start"]} - {booking["end"]}</em>"
        )
        for booking in bookings
    ]
    return "\n\n".join(html_bookings)


def validate_booking_id(
    booking_id: str,
    bookings: List[Dict[str, Union[str, int]]],
) -> bool:
    """
    Валидация Типа booking_id и ее вхождение в список записей.
    """
    try:
        return int(booking_id) in [booking["id"] for booking in bookings]
    except ValueError:
        return False
