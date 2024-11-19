from typing import TYPE_CHECKING

from aiogram import Router, F
from aiogram.filters import Command

from src.utils import read_template, MENU
from src.utils.keyboards import InlineKeyboard

if TYPE_CHECKING:
    from aiogram.types import Message, CallbackQuery


simple_router = Router()


@simple_router.message(Command('start'))
async def start(message: "Message") -> None:
    """
    Handle start command.
    """
    menu = MENU.copy()
    menu['Цены'] = 'prices'
    kb = InlineKeyboard(menu)

    text: str = read_template('start.txt')
    await message.answer(
        text,
        reply_markup=kb.get_inline_menu(),
        parse_mode='HTML'
    )


@simple_router.callback_query(F.data == 'start')
async def start_callback(callback: "CallbackQuery") -> None:
    """
    Callback handle of start command.
    """
    message: Message = callback.message
    await message.edit_reply_markup(reply_markup=None)

    menu = MENU.copy()
    menu['Цены'] = 'prices'
    kb = InlineKeyboard(menu)

    text: str = read_template('start.txt')
    await message.answer(
        text,
        reply_markup=kb.get_inline_menu(),
        parse_mode='HTML'
    )
