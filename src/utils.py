from typing import Union, List, Any, Dict, Optional, Tuple

from datetime import datetime, timedelta


MENU = {
    "Записаться": "booking",
    "Помощь": "help",
    "Отмена записи": "cancel",
}


def read_template(
    title: str,
    **kwargs: Union[List[Any], str, int],
) -> str:
    """
    Чтение шаблона ответа для Telegram Message из файла .txt
    """
    with open(f"src/templates/{title}.txt", "r") as file:
        content = file.read()
        return content.format(**kwargs)


def validate_date(date: str) -> bool:
    """
    Валидация даты формата ГГГГ-ММ-ДД и проверка, что дата не в прошлом.
    """
    if len(date) != 10:
        return False
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        return parsed_date >= datetime.now().date()
    except ValueError:
        return False


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


def validate_amount(amount: str, max_value: int) -> bool:
    """
    Валидация количества байков.
    """
    try:
        return int(amount) <= max_value
    except ValueError:
        return False


def has_bike_for_instructor(
    requested_bike: Dict[str, int],
    available_bikes: Dict[str, int],
) -> bool:
    """
    Проверка на остаток байка сопровождения для инструктора.
    """
    # Вычитаем запрошенные байки из доступных
    for bike, count in requested_bike.items():
        if bike in available_bikes:
            available_bikes[bike] -= count
            if available_bikes[bike] <= 0:
                del available_bikes[bike]

    # Проверяем, остался ли хотя бы один байк с количеством >= 1
    return any(count >= 1 for count in available_bikes.values())


def reduce_bike_count(
    requested_bike: Tuple[str, int],
    available_bikes: Dict[str, int],
) -> Union[Dict[str, int], False]:
    """
    Уменьшает кол-во байков, на выбранный байк.
    """
    r_bike, r_amount = requested_bike
    if not r_bike in available_bikes:
        return False
    if len(available_bikes) == 1:
        if r_amount >= available_bikes[r_bike]:
            return False
        else:
            available_bikes[r_bike] -= r_amount
    else:
        if r_amount == available_bikes[r_bike]:
            del available_bikes[r_bike]
        else:
            available_bikes[r_bike] -= r_amount

    return available_bikes


def render_chosen_bikes(bikes: Dict[str, int]) -> str:
    """
    Рендер в HTML формат байки, которые уже выбрал клиент.
    """
    html_bikes = [
        f"🔘 <strong>{title}: <em>{amount}шт</em></strong>"
        for title, amount in bikes.items()
    ]
    return "\n\n".join(html_bikes)


def render_bookings(bookings: List[Dict[str, str]]) -> str:
    """
    Рендер в HTML списка прокатов.
    """
    html_bookings = [
        (
            f"🔘 <strong>#{booking["id"]}</strong>: <em>{booking["date"]} |"
            f" {booking["start"]} - {booking["end"]} |"
            f" <strong>{booking["instructor"]}</strong></em>"
        )
        for booking in bookings
    ]
    return "\n\n".join(html_bookings)


def get_end_time(start: str, duration: int) -> str:
    """
    Получение времени окончания проката.
    """
    start_dt = datetime.strptime(start, "%H:%M")
    return datetime.strftime(
        (start_dt + timedelta(hours=duration)),
        "%H:%M",
    )


def validate_duration(duration: str, durations: List[int]) -> bool:
    """
    Валидация длительности.
    """
    try:
        return int(duration) in durations
    except (ValueError, TypeError):
        return False
