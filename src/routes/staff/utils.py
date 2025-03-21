from typing import Dict, List


MENU = {
    "Отказаться от проката": "staff_decline",
    "Принять прокат": "staff_accept",
}


def render_bookings_to_accept(bookings: List[Dict[str, str]]) -> str:
    """
    Рендер в HTML списка прокатов для взятия в работу.
    """
    html_bookings = [
        (
            f"🔘 <strong>{booking["id"]}</strong>: <em>{booking["date"]} |"
            f" {booking["start"]} - {booking["end"]} |"
            f" <strong>{booking["instructor"]}</strong></em>"
        )
        for booking in bookings
    ]
    return "\n\n".join(html_bookings)
