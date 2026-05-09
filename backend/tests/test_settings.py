"""Tests for environment-driven settings."""

from __future__ import annotations

import pytest
from pydantic import SecretStr, ValidationError

from eb_digital.settings import Settings, get_settings


def test_get_settings_loads_values_from_environment() -> None:
    settings = get_settings()
    assert settings.environment == "dev"
    assert settings.log_level == "DEBUG"
    assert isinstance(settings.secret_key, SecretStr)
    assert settings.secret_key.get_secret_value() == "test-secret-key-not-for-production"
    assert settings.session_cookie_name == "eb_session"
    assert "asyncpg" in settings.database_url
    assert settings.tile_proxy_base == "http://tile-proxy:80"


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()


def test_missing_required_secret_raises_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SECRET_KEY", raising=False)
    get_settings.cache_clear()
    with pytest.raises(ValidationError) as excinfo:
        Settings(_env_file=None)  # type: ignore[call-arg]
    assert "secret_key" in str(excinfo.value).lower()


def test_invalid_environment_value_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "wat")
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        get_settings()


def test_secret_str_does_not_leak_via_repr() -> None:
    settings = get_settings()
    # Pydantic SecretStr is designed to mask the value in repr/str output.
    assert "test-secret-key" not in repr(settings)
    assert "test-secret-key" not in str(settings)
