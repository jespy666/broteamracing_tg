from typing import TYPE_CHECKING

from .simples.handlers import simple_router
from .utils.commands import set_commands
from .config import settings

if TYPE_CHECKING:
    from aiogram import Dispatcher


def register_routes(dp: "Dispatcher") -> None:
    """
    Register all project routes.
    """
    dp.include_router(simple_router)


__all__ = ('settings', 'register_routes', 'set_commands')
