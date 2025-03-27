from typing import TYPE_CHECKING

from aiogram.types import BotCommand

if TYPE_CHECKING:
    from aiogram import Bot


async def set_commands(bot: "Bot") -> None:
    """
    Установка команд для бота.
    """
    commands = [
        BotCommand(
            command="start",
            description="Главное меню",
        ),
        BotCommand(
            command="prices",
            description="Цены",
        ),
        BotCommand(
            command="help",
            description="Справка",
        ),
        BotCommand(
            command="booking",
            description="Запись на прокат",
        ),
        BotCommand(
            command="cancel",
            description="Отменить запись на прокат",
        ),
    ]

    await bot.set_my_commands(commands)
