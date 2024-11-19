from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
    BOT_TOKEN: str = Field(env='BOT_TOKEN')
    API_TOKEN: str = Field(env='API_TOKEN')


settings = Settings()
