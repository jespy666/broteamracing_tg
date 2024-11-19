from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    ReplyKeyboardBuilder,
    KeyboardButton
)

if TYPE_CHECKING:
    from aiogram.types import (
        ReplyKeyboardMarkup,
        InlineKeyboardMarkup
)


@dataclass
class Keyboard:
    buttons: Dict[str, str]


@dataclass(slots=True)
class InlineKeyboard(Keyboard):
    keyboard = InlineKeyboardBuilder()

    @property
    def cancel(self) -> "InlineKeyboardMarkup":
        """
        Returns cancel button as markup.
        """
        button = InlineKeyboardButton(
            text='Отмена',
            callback_data=self.buttons['cancel'],
        )
        self.keyboard.add(button)
        self.keyboard.adjust(1)
        return self.keyboard.as_markup()

    def get_inline_menu(self) -> "InlineKeyboardMarkup":
        """
        Returns inline menu as markup.
        """
        for item, callback in self.buttons.items():
            self.keyboard.button(
                text=item,
                callback_data=callback,
            )
        self.keyboard.adjust(2)
        return self.keyboard.as_markup()


@dataclass(slots=True)
class ReplyKeyboard(Keyboard):
    keyboard = ReplyKeyboardBuilder()

    @property
    def markup(self) -> "ReplyKeyboardMarkup":
        """
        Returns reply buttons markup.
        """
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=btn) for btn in self.buttons]],
            one_time_keyboard=True,
            resize_keyboard=True,
        )
