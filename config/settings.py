from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки бота.
    """

    BOT_TOKEN: str
    API_TOKEN: str
    BASE_API_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore