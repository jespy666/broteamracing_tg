from dataclasses import dataclass
from typing import List, Optional

from aiohttp import ClientSession

from src import settings
from src.utils import exceptions as exc


@dataclass(slots=True)
class APIManager(ClientSession):
    """
    API connect manager for BroTeamRacing.ru
    """

    base_url: str = settings.BASE_API_URL

    async def get_available_slots(self, date: str) -> Optional[List[str]]:
        """
        Get available booking slots.

        Args:
            date: Date string.
        """
        url = f"{self.base_url}/get-slots/"
        payload = {"date": date}
        async with self.post(url, json=payload) as response:
            match response.status:
                case 200:
                    return await response.json()
                case _:
                    raise exc.APIConnectionError
