"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["dev", "staging", "production"]


class Settings(BaseSettings):
    """Backend application settings.

    Required secrets have no defaults and must be supplied via environment
    variables or a `.env` file. See `.env.example` for the full list.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Environment = "dev"
    log_level: str = "DEBUG"
    secret_key: SecretStr
    session_cookie_name: str = "eb_session"
    database_url: str
    valkey_url: str = "valkey://cache:6379/0"
    tomtom_api_key: SecretStr
    maptiler_api_key: SecretStr
    tile_proxy_base: str = "http://tile-proxy:80"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # All required fields are populated by pydantic-settings from the environment
    # at runtime; mypy cannot see this, hence the targeted suppression.
    return Settings()  # type: ignore[call-arg]
