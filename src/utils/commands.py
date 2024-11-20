from typing import TYPE_CHECKING

from aiogram.types import BotCommand

if TYPE_CHECKING:
    from aiogram import Bot


async def set_commands(bot: "Bot") -> None:
    """
    Set bot context menu commands.
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
            description="Помощь",
        ),
        BotCommand(
            command="create",
            description="1",
        ),
        BotCommand(
            command="book",
            description="2",
        ),
        BotCommand(
            command="reset",
            description="3",
        ),
        BotCommand(
            command="cancel",
            description="4",
        ),
        BotCommand(
            command="edit",
            description="5",
        ),
    ]
    await bot.set_my_commands(commands)
