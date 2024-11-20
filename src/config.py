from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )
    BOT_TOKEN: str
    API_TOKEN: str
    BASE_API_URL: str


settings = Settings()  # type: ignore
