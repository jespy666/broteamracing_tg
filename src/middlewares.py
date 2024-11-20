from typing import TYPE_CHECKING, Callable, Dict, Any, Awaitable

import aiohttp

from aiogram import BaseMiddleware
from aiogram.types import Message

from src import settings
from src.utils import exceptions as exc

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery, TelegramObject


class AccessMiddleware(BaseMiddleware):
    """
    Middleware checks, if user is authenticated.
    """

    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[["TelegramObject", Dict[str, Any]], Awaitable[Any]],
        event: "TelegramObject",
        data: Dict[str, Any],
    ) -> Any:
        async with aiohttp.ClientSession() as session:
            if isinstance(event, Message):
                message = event
            elif isinstance(event, CallbackQuery):
                message = event.message  # type: ignore
            else:
                raise TypeError("Non authorized event")

            user_id: int = message.from_user.id  # type: ignore
            body = {"tg_id": user_id}
            response = await session.post(
                settings.TG_USER_CHECK_URL, json=body
            )
            match response.status:
                case 200:
                    data["user"] = response.json()
                case 404:
                    raise exc.APIConnectionError
                case _:
                    data["has_access"] = False
        return await handler(event, data)
