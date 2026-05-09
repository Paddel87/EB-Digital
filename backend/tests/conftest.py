"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from eb_digital.settings import get_settings


@pytest.fixture(autouse=True)
def _reset_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Provide a fully populated env for every test.

    pydantic-settings prefers explicit env vars over .env file entries, so
    setting them here overrides any developer-local .env. The Settings
    cache is cleared so each test sees these values.
    """
    monkeypatch.setenv("ENVIRONMENT", "dev")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-not-for-production")
    monkeypatch.setenv("SESSION_COOKIE_NAME", "eb_session")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://eb:eb@localhost:5432/eb_test")
    monkeypatch.setenv("VALKEY_URL", "valkey://localhost:6379/0")
    monkeypatch.setenv("TOMTOM_API_KEY", "test-tomtom-key")
    monkeypatch.setenv("MAPTILER_API_KEY", "test-maptiler-key")
    monkeypatch.setenv("TILE_PROXY_BASE", "http://tile-proxy:80")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
