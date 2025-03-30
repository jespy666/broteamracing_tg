from typing import Union, TYPE_CHECKING, cast

from aiogram import Router, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message, CallbackQuery

from src.utils import read_template, MENU
from src.keyboards import get_inline_menu
from src.api.manager import APIManager

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


simple_router = Router()


@simple_router.message(CommandStart(deep_link=True))
async def enable_updates(message: Message, command: CommandObject) -> None:
    """
    Установка уведомлений для пользователя в ТГ.
    """
    args = command.args
    # ID пользователя из приложения
    user_id = int(args)
    telegram_id = str(message.from_user.id)

    # Проверка на привязку Телеграм аккаунта
    if not await APIManager().check_telegram_id(telegram_id):
        await APIManager().set_telegram_id(user_id, telegram_id)
        await message.answer("🔗 Аккаунт ТГ связан с веб-приложением!")

    # Включение или выключение Телеграм уведомлений
    state: bool = await APIManager().check_notifications_enabled(user_id)
    if not state:
        await APIManager().switch_notifications(user_id)
        await message.answer("🔔 Уведомления включены")
    else:
        await message.answer("🔔 Уведомления уже включены")


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

    text: str = read_template("start")
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

    text: str = read_template("prices")
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

    text: str = read_template("help")
    await message.answer(text, reply_markup=markup, parse_mode="HTML")
