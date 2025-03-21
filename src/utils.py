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
    Чтение шаблона ответа для Telegram Message из файла .txt
    """
    with open(f"src/templates/{title}.txt", "r") as file:
        content = file.read()
        return content.format(**kwargs)
