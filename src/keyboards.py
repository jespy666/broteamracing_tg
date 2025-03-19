from typing import TYPE_CHECKING, Dict, List, Union

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    KeyboardButton,
)
from aiogram.types import ReplyKeyboardMarkup

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


def get_cancel_button() -> "InlineKeyboardMarkup":
    """
    Кнопка отмены.
    """
    keyboard = InlineKeyboardBuilder()
    button = InlineKeyboardButton(
        text="Отмена",
        callback_data="cancel-dialogue",
    )
    keyboard.add(button).adjust(1)

    return keyboard.as_markup()


def get_inline_menu(buttons: Dict[str, str]) -> "InlineKeyboardMarkup":
    """
    Инлайн меню.
    """
    keyboard = InlineKeyboardBuilder()
    for item, callback in buttons.items():
        keyboard.button(
            text=item,
            callback_data=callback,
        )
    keyboard.adjust(2)
    return keyboard.as_markup()


def get_reply_markup(buttons: List[Union[str, int]]) -> "ReplyKeyboardMarkup":
    """
    Разметка на клавиатуре.
    """
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(btn)) for btn in buttons]],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
