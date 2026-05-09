"""Shared pytest fixtures."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

# Schritt 1.5 introduces module-level Procrastinate App construction in
# ``eb_digital.jobs`` which loads Settings at import time. pytest collection
# imports test modules before any fixture runs, so test-collection time must
# already see required env vars. ``setdefault`` does not overwrite values a
# developer's local shell might have set.
#
# We deliberately do NOT import ``eb_digital`` at conftest top-level here:
# coverage initialises after conftest is loaded, so a top-level import would
# leave the package out of the coverage report.
_TEST_ENV_DEFAULTS = {
    "ENVIRONMENT": "dev",
    "LOG_LEVEL": "DEBUG",
    "SECRET_KEY": "test-secret-key-not-for-production",
    "SESSION_COOKIE_NAME": "eb_session",
    "DATABASE_URL": "postgresql+asyncpg://eb:eb@localhost:5432/eb_test",
    "VALKEY_URL": "valkey://localhost:6379/0",
    "TOMTOM_API_KEY": "test-tomtom-key",
    "MAPTILER_API_KEY": "test-maptiler-key",
    "TILE_PROXY_BASE": "http://tile-proxy:80",
}
for _key, _value in _TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(_key, _value)


@pytest.fixture(autouse=True)
def _reset_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Provide a fully populated env for every test.

    pydantic-settings prefers explicit env vars over .env file entries, so
    setting them here overrides any developer-local .env. The Settings
    cache is cleared so each test sees these values.
    """
    from eb_digital.settings import get_settings

    for key, value in _TEST_ENV_DEFAULTS.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
