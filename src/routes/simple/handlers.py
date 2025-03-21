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
    try:
        # ID пользователя из приложения
        user_id = int(args)

        telegram_id: Union[str, int] = message.from_user.id
        api = APIManager()

        # Проверка на привязку Телеграм аккаунта
        if not await api.check_telegram_id(user_id):
            await api.set_telegram_id(user_id, telegram_id)
        await message.answer("🆗 Уведомления включены")
    except Exception as e:
        await message.answer(
            f"Произошла ошибка при включении обновлений:\n\n{e}"
        )


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
