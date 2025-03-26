MENU = {
    "Перевести в ожидание": "admin_pending",
    "Принять прокат": "admin_accept",
    "Отменить прокат": "admin_cancel",
    "Сменить инструктора": "admin_change_instructor",
    "Записать стороннего клиента": "admin_side_booking",
}


def validate_phone_number(phone: str) -> bool:
    """
    Валидация номера телефона.
    """
    return phone.isdigit() and len(phone) == 10
