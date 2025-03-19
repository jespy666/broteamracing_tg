from typing import Optional


class APIError(Exception):
    """
    Ошибка взаимодействия с API приложения.
    """

    def __init__(self, status_code: int, detail: Optional[str] = None) -> None:
        self.detail = detail or f"Unknown error: {status_code}"
        super().__init__(detail)
