MENU = {
    'Записаться': 'book',
    'Помощь': 'help',
    'Регистрация': 'create',
    'Сброс пароля': 'reset',
    'Отмена записи': 'cancel',
    'Изменить запись': 'edit',
}


def read_template(title: str) -> str:
    """
    Read template for reply message.

    Args:
        title (str): Template title.
    Returns:
        Message template as string.
    """
    with open(f'src/utils/templates/{title}', 'r') as file:
        return file.read()
