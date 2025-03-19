from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Any,
    Awaitable,
)

from aiogram import BaseMiddleware
from aiogram.types import Message, InaccessibleMessage, CallbackQuery

from src.api.manager import APIManager
from src import exceptions as exc

if TYPE_CHECKING:
    from aiogram.types import TelegramObject


class AccessMiddleware(BaseMiddleware):
    """
    Middleware для проверки связывания ТГ аккаунта и Веб приложения.
    """

    async def __call__(
        self,
        handler: Callable[["TelegramObject", Dict[str, Any]], Awaitable[Any]],
        event: "TelegramObject",
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            if event.message is None:
                raise ValueError("CallbackQuery does not contain a message")
            if isinstance(event.message, InaccessibleMessage):
                raise ValueError(
                    "CallbackQuery contains an inaccessible message"
                )
            message = event.message
        else:
            raise TypeError("Non authorized event")

        if message.from_user is None:
            raise ValueError(
                "Message does not have a sender (from_user is None)"
            )

        try:
            api = APIManager()
            data["has_access"] = await api.check_telegram_id(
                str(message.from_user.id)
            )
        except exc.APIError:
            data["has_access"] = False

        return await handler(event, data)
