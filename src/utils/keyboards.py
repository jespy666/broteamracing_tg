from typing import TYPE_CHECKING, Dict, List

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    KeyboardButton
)

if TYPE_CHECKING:
    from aiogram.types import (
        ReplyKeyboardMarkup,
        InlineKeyboardMarkup
)


def get_cancel_button() -> "InlineKeyboardMarkup":
    """
    Forming inline cancel button.
    """
    keyboard = InlineKeyboardBuilder()
    button = InlineKeyboardButton(
        text='Отмена',
        callback_data='cancel',
    )
    keyboard.add(button).adjust(1)

    return keyboard.as_markup()


def get_inline_menu(buttons: Dict[str, str]) -> "InlineKeyboardMarkup":
    """
    Forming inline menu.
    """
    keyboard = InlineKeyboardBuilder()
    for item, callback in buttons.items():
        keyboard.button(
            text=item,
            callback_data=callback,
        )
    keyboard.adjust(2)
    return keyboard.as_markup()


def get_reply_markup(buttons: List[str]) -> "ReplyKeyboardMarkup":
    """
    Returns reply buttons markup.
    """
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn) for btn in buttons]],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
