from datetime import datetime, timedelta

from typing import Dict, Any, List


def validate_date(date: str) -> bool:
    """
    Валидация даты формата ГГГГ-ММ-ДД.
    """
    try:
        return datetime.strptime(date, "%Y-%m-%d") >= datetime.today()
    except ValueError:
        return False


def get_start_times(day_info: List[Dict[str, Any]]) -> List[str]:
    """
    Извлечение доступных времен начала проката.
    """
    return [start["start"] for start in day_info]


def get_available_time_range(starts: List[str], start: str) -> List[int]:
    """
    Получение списка доступных часов от времени проката.
    """

    def convert_to_dt(time_str: str) -> datetime:
        return datetime.strptime(time_str, "%H:%M")

    if start not in starts:
        return []

    idx = starts.index(start)
    hours = 1
    current_time = convert_to_dt(starts[idx])

    result = [hours]

    for next_start in starts[idx + 1 :]:
        next_time = convert_to_dt(next_start)

        if next_time != current_time + timedelta(hours=1):
            break

        hours += 1
        result.append(hours)
        current_time = next_time

    return result
