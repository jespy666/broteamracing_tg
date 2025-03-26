from contextlib import asynccontextmanager

from datetime import datetime, timedelta

from typing import Union, AsyncGenerator, Any, Dict, List, Literal

from aiohttp import ClientSession

from config import settings
from src import exceptions as exc


class AsyncSession:
    """
    Асинхронная сессия aiohttp.
    """

    def __init__(self) -> None:
        self.client = ClientSession(
            base_url=settings.BASE_API_URL,
            headers={
                "API-KEY": settings.API_TOKEN,
                "Platform": "Telegram",
            },
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[ClientSession, Any]:
        """
        Контекстный менеджер сессии AioHttp.
        """
        async with self.client as session:
            yield session


class APIManager(AsyncSession):
    """
    Менеджер API подключения к основному приложению.
    """

    async def set_telegram_id(
        self,
        user_id: int,
        telegram_id: Union[str, int],
        url: str = "/api/v1/set/telegram_id/",
    ) -> None:
        """
        Установка Telegram ID пользователю на сайт, что-бы получать уведомления.
        """
        payload = {
            "user_id": user_id,
            "telegram_id": telegram_id,
        }
        async with self.get_session() as session:
            async with session.post(url, data=payload) as response:
                if not response.status == 200:
                    raise exc.APIError(
                        detail=response.json().get("detail"),
                        status_code=response.status,
                    )

    async def check_telegram_id(
        self,
        telegram_id: str,
        url: str = "/api/v1/check/telegram_id",
    ) -> bool:
        """
        Проверка, что пользователь привязан к ТГ.
        """
        async with self.get_session() as session:
            url = f"{url}?telegram_id={telegram_id}"
            async with session.get(url) as response:
                return response.status == 200

    async def enable_notifications(
        self,
        telegram_id: str,
        url: str = "/api/v1/notifications/tg/enable/",
    ) -> None:
        """
        Включение уведомлений в Телеграм.
        """
        payload = {"telegram_id": telegram_id}
        async with self.get_session() as session:
            async with session.post(url, data=payload) as response:
                if not response.status == 200:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=response.json().get("detail"),
                    )

    async def load_day_info(
        self,
        date: str,
        url: str = "/api/v1/day_info/",
    ) -> List[Dict[str, Any]]:
        """
        Загрузка данных по дню.
        (Свободные слоты, Доступные байки, Доступные инструкторы).
        """
        payload = {"date": date}
        async with self.get_session() as session:
            async with session.post(url, data=payload) as response:
                data = await response.json()
                if not response.status == 200:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )
                return data

    async def get_available_instructors(
        self,
        date: str,
        start: str,
        duration: int,
        url: str = "api/v1/instructors/available",
    ) -> Dict[str, int]:
        """
        Получение доступных инструкторов.
        """
        start_dt = datetime.strptime(start, "%H:%M")
        end = datetime.strftime(
            (start_dt + timedelta(hours=duration)),
            "%H:%M",
        )
        query_params = f"?date={date}&start={start}&end={end}"
        async with self.get_session() as session:
            async with session.get(f"{url}{query_params}") as response:
                data = await response.json()
                if not response.status == 200:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )
                return data

    async def get_available_bikes(
        self,
        date: str,
        start: str,
        duration: int,
        url: str = "api/v1/bikes/available",
    ) -> Dict[str, int]:
        """
        Получение доступных байков.
        """
        start_dt = datetime.strptime(start, "%H:%M")
        end = datetime.strftime(
            (start_dt + timedelta(hours=duration)),
            "%H:%M",
        )
        query_params = f"?date={date}&start={start}&end={end}"
        async with self.get_session() as session:
            async with session.get(f"{url}{query_params}") as response:
                data = await response.json()
                if not response.status == 200:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )
                return data

    async def make_booking(
        self,
        telegram_id: str,
        date: str,
        start: str,
        end: str,
        duration: int,
        instructor_id: int,
        bikes: Dict[str, int],
        client_phone: str = None,
        url: str = "api/v1/bookings/new/",
    ) -> None:
        """
        Создание записи на прокат.
        """
        payload = {
            "telegram_id": telegram_id,
            "date": date,
            "start": start,
            "end": end,
            "duration": duration,
            "instructor_id": instructor_id,
            "bikes": bikes,
        }
        if client_phone:
            payload["client_phone"] = client_phone

        async with self.get_session() as session:
            async with session.post(url, data=payload) as response:
                data = await response.json()
                if not response.status == 200:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )

    async def get_user_active_bookings(
        self,
        telegram_id: str,
        url: str = "api/v1/bookings/active",
    ) -> List[Dict[str, Any]]:
        """
        Получение всех активных (предстоящих) записей на прокат клиента.
        """
        request_params = f"?telegram_id={telegram_id}"
        async with self.get_session() as session:
            async with session.get(f"{url}{request_params}") as response:
                data = await response.json()
                if not response.status == 200:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )
                return data

    async def cancel_booking(
        self,
        booking_id: int,
        url: str = "api/v1/bookings/cancel/",
    ) -> None:
        """
        Отмена записи на прокат.
        """
        payload = {"booking_id": booking_id}
        async with self.get_session() as session:
            async with session.post(url, data=payload) as response:
                data = await response.json()
                if not response.status == 200:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )

    async def get_instructor_id(
        self,
        telegram_id: str,
        url: str = "api/v1/staff/check",
    ) -> int:
        """
        Проверка прав персонала и получение связанного instructor_id.
        """
        request_params = f"?telegram_id={telegram_id}"
        async with self.get_session() as session:
            async with session.get(f"{url}{request_params}") as response:
                data = await response.json()
                instructor_id: int = data.get("instructor_id")
                if not response.status == 200 or not instructor_id:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )
                return instructor_id

    async def get_bookings(
        self,
        booking_status: Literal["confirmed", "pending"],
        instructor_id: int = None,
        url: str = "api/v1/staff/bookings/list/",
    ) -> List[Dict[str, Union[str, int]]]:
        """
        Получение списка прокатов для взятия их в работу.
        """
        query_params = f"?booking_status={booking_status}"
        if instructor_id:
            query_params += f"&instructor_id={instructor_id}"

        async with self.get_session() as session:
            async with session.get(f"{url}{query_params}") as response:
                data = await response.json()
                if not response.status == 200:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )
                return data

    async def accept_booking(
        self,
        booking_id: int,
        instructor_id: int,
        bike_id: int,
        url: str = "api/v1/staff/bookings/accept/",
    ) -> bool:
        """
        Взять в работу прокат.
        """
        payload = {
            "booking_id": booking_id,
            "instructor_id": instructor_id,
            "bike_id": bike_id,
        }
        async with self.get_session() as session:
            async with session.post(url, data=payload) as response:
                data = await response.json()
                if response.status == 409:
                    return False
                if not response.status in [200, 409]:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )
                return True

    async def decline_booking(
        self,
        booking_id: int,
        telegram_id: str,
        url: str = "api/v1/staff/bookings/decline/",
    ) -> None:
        """
        Отказ от проведения проката.
        """
        payload = {
            "booking_id": booking_id,
            "telegram_id": telegram_id,
        }
        async with self.get_session() as session:
            async with session.post(url, data=payload) as response:
                data = await response.json()
                if not response.status == 200:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )

    async def check_admin(
        self,
        telegram_id: str,
        url: str = "api/v1/admin/check/",
    ) -> bool:
        """
        Проверка прав администратора.
        """
        query_params = f"?telegram_id={telegram_id}"
        async with self.get_session() as session:
            async with session.get(f"{url}{query_params}") as response:
                data = await response.json()
                if not response.status == 200:
                    raise exc.APIError(
                        status_code=response.status,
                        detail=data.get("detail"),
                    )
                return True
