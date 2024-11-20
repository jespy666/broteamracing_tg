from typing import Union, TYPE_CHECKING, cast

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.utils import read_template, MENU
from src.utils.keyboards import get_inline_menu

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

simple_router = Router()


@simple_router.message(Command("start"))
@simple_router.callback_query(F.data == "start")
async def start(event: Union[Message, CallbackQuery]) -> None:
    """
    Handle start command.
    """
    message: Message = (
        event if isinstance(event, Message) else cast(Message, event.message)
    )

    if message.reply_markup:
        await message.edit_reply_markup(reply_markup=None)

    menu = MENU.copy()
    menu["Цены"] = "prices"
    markup: "InlineKeyboardMarkup" = get_inline_menu(menu)

    text: str = read_template("start.txt")
    await message.answer(text, reply_markup=markup, parse_mode="HTML")


@simple_router.message(Command("prices"))
@simple_router.callback_query(F.data == "prices")
async def handle_prices(event: Union[Message, CallbackQuery]) -> None:
    """
    Message and Callback handler for prices.
    """
    message: Message = (
        event if isinstance(event, Message) else cast(Message, event.message)
    )

    if message.reply_markup:
        await message.edit_reply_markup(reply_markup=None)

    menu = MENU.copy()
    menu["Главная"] = "start"
    markup: "InlineKeyboardMarkup" = get_inline_menu(menu)

    text: str = read_template("prices.txt")
    await message.answer(text, reply_markup=markup, parse_mode="HTML")


@simple_router.message(Command("help"))
@simple_router.callback_query(F.data == "help")
async def handle_help(event: Union[Message, CallbackQuery]) -> None:
    """
    Message and Callback handler for help.
    """
    message: Message = (
        event if isinstance(event, Message) else cast(Message, event.message)
    )

    menu = MENU.copy()
    menu["Цены"] = "prices"
    markup: "InlineKeyboardMarkup" = get_inline_menu(menu)

    text: str = read_template("help.txt")
    await message.answer(text, reply_markup=markup, parse_mode="HTML")
