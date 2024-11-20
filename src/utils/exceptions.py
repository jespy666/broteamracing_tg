from typing import Optional


class APIConnectionError(Exception):
    """
    If impossible to connect BroTeamRacing API.
    """

    def __init__(self, detail: Optional[str] = None) -> None:
        self.detail = detail or "Error connect to BTR API"
        super().__init__(detail)
