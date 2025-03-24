from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Any,
    Awaitable,
    Union,
)

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.api.manager import APIManager
from src import exceptions as exc

if TYPE_CHECKING:
    from aiogram.types import TelegramObject


class AuthMiddleware(BaseMiddleware):
    """
    Middleware для проверки связывания ТГ аккаунта и Веб приложения.
    """

    async def __call__(
        self,
        handler: Callable[["TelegramObject", Dict[str, Any]], Awaitable[Any]],
        event: "TelegramObject",
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Union[Message, CallbackQuery]):
            raise TypeError("Не поддерживаемый тип события")

        user_id = str(event.from_user.id)
        try:
            api = APIManager()
            data["is_authenticated"] = await api.check_telegram_id(user_id)
        except exc.APIError:
            data["is_authenticated"] = False

        return await handler(event, data)


class StaffMiddleware(BaseMiddleware):
    """
    Middleware для проверки доступа персонала.
    """

    async def __call__(
        self,
        handler: Callable[["TelegramObject", Dict[str, Any]], Awaitable[Any]],
        event: "TelegramObject",
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Union[Message, CallbackQuery]):
            raise TypeError("Не поддерживаемый тип события")

        user_id: int = event.from_user.id
        try:
            api = APIManager()
            data["instructor_id"] = await api.get_instructor_id(str(user_id))
        except exc.APIError:
            data["instructor_id"] = False

        return await handler(event, data)


class AdminMiddleware(BaseMiddleware):
    """
    Middleware для проверки доступа администратора.
    """

    async def __call__(
        self,
        handler: Callable[["TelegramObject", Dict[str, Any]], Awaitable[Any]],
        event: "TelegramObject",
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Union[Message, CallbackQuery]):
            raise TypeError("Не поддерживаемый тип события")

        user_id: int = event.from_user.id
        try:
            api = APIManager()
            data["is_admin"] = await api.check_admin(str(user_id))
        except exc.APIError:
            data["is_admin"] = False

        return await handler(event, data)
