from typing import Union, List, Any


MENU = {
    "Записаться": "book",
    "Помощь": "help",
    "Регистрация": "create",
    "Сброс пароля": "reset",
    "Отмена записи": "cancel",
    "Изменить запись": "edit",
}

BIKES = {
    "X-motos": {
        "amount": 2,
        "link": "https://i.ibb.co.com/7WN23CJ/x-motos.png",
    },
    "Pit-Bike": {
        "amount": 1,
        "link": "https://i.ibb.co.com/p0CnFLV/Pit-bike.png",
    },
    "GR-7": {
        "amount": 1,
        "link": "https://i.ibb.co.com/SVN1Gm4/gr-7.png",
    },
    "Progasi": {
        "amount": 2,
        "link": "https://i.ibb.co.com/wcSrWBt/progassi.png",
    },
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
