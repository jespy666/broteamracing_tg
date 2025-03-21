from typing import TYPE_CHECKING

from .routes import simple_router, booking_router
from .commands import set_commands

if TYPE_CHECKING:
    from aiogram import Dispatcher


def register_routes(dp: "Dispatcher") -> None:
    """
    Регистрация всех маршрутов бота.
    """

    dp.include_router(simple_router)
    dp.include_router(booking_router)


__all__ = ("register_routes", "set_commands")
