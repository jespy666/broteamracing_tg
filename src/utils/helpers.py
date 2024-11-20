from datetime import datetime, timedelta

from typing import Union, List, Any

MENU = {
    "Записаться": "book",
    "Помощь": "help",
    "Регистрация": "create",
    "Сброс пароля": "reset",
    "Отмена записи": "cancel",
    "Изменить запись": "edit",
}


def read_template(
    title: str,
    **kwargs: Union[List[Any], str, int],
) -> str:
    """
    Read template for reply message.

    Args:
        title (str): Template title.
        kwargs (str): Variables to format.
    Returns:
        Message template as string.
    """
    with open(f"src/utils/templates/{title}", "r") as file:
        content = file.read()
    return content.format(**kwargs)


def get_start_times(slots: List[str]) -> List[str]:
    """
    Extracts all hourly start times from a list of time slots,
    ensuring intervals are multiples of 1 hour.

    Args:
        slots: List of time slots in the format 'HH:MM-HH:MM'.

    Returns:
        List of start times in the format 'HH:MM',
        broken into 1-hour intervals.
    """
    start_times = []

    for slot in slots:
        start_str, end_str = slot.split("-")

        start_time = datetime.strptime(start_str, "%H:%M")
        end_time = datetime.strptime(end_str, "%H:%M")

        while start_time < end_time:
            start_times.append(start_time.strftime("%H:%M"))
            start_time += timedelta(hours=1)

    return start_times


def get_hours(slots: List[str], time: str) -> List[int]:
    """
    Get a list of available hours for booking.

    Args:
        slots: List of time slots (start, end).
        time: The desired start time in the format 'HH:MM'.

    Returns:
        List of available hours from the start time.
    """
    for slot in slots:
        time_obj = datetime.strptime(time, "%H:%M")

        start_str, end_str = slot.split("-")
        start_time = datetime.strptime(start_str, "%H:%M")
        end_time = datetime.strptime(end_str, "%H:%M")

        if start_time <= time_obj <= end_time:
            time_difference = end_time - time_obj
            result_hours: int = int(time_difference.total_seconds() / 3600)
            return [n + 1 for n, _ in enumerate(range(result_hours))]
