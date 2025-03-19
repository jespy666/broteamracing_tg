import asyncio

import logging

from typing import TYPE_CHECKING

from aiogram import Dispatcher, Bot, F
from aiogram.fsm.storage.memory import MemoryStorage

from src import register_routes, set_commands
from src.utils import read_template, MENU
from src.keyboards import get_inline_menu

from config import settings

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery, InlineKeyboardMarkup
    from aiogram.fsm.context import FSMContext


storage = MemoryStorage()

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=storage)


@dp.callback_query(F.data == "cancel-dialogue")
async def clear_state(callback: "CallbackQuery", state: "FSMContext") -> None:
    """
    Отмена диалога, очистка состояния.
    """
    msg: str = read_template("cancel")
    markup: "InlineKeyboardMarkup" = get_inline_menu(MENU)
    await state.clear()
    await callback.message.answer(msg, reply_markup=markup, parse_mode="HTML")


async def main() -> None:
    register_routes(dp)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s"
        " [%(asctime)s] - %(name)s - %(message)s",
    )
    asyncio.run(main())
