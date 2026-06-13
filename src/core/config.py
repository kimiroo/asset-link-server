from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


LogLevelType = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    DATABASE_URL: str = Field(default=...)
    REDIS_HOST: str = Field(default=...)
    REDIS_PORT: int = Field(default=...)

    LOG_LEVEL: LogLevelType = Field(default="INFO")
    IS_DEBUG: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()