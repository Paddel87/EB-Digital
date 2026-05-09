"""Tests for the Procrastinate job-engine wiring (Schritt 1.5)."""

from __future__ import annotations

import logging

import pytest
from procrastinate import App, PsycopgConnector

from eb_digital.jobs import _to_psycopg_conninfo, make_procrastinate_app, procrastinate_app
from eb_digital.jobs.ping import ping


def test_to_psycopg_conninfo_strips_asyncpg_driver() -> None:
    url = "postgresql+asyncpg://user:pass@db:5432/eb_digital"
    assert _to_psycopg_conninfo(url) == "postgresql://user:pass@db:5432/eb_digital"


def test_to_psycopg_conninfo_keeps_url_without_driver() -> None:
    url = "postgresql://user:pass@host:5432/db"
    assert _to_psycopg_conninfo(url) == url


def test_to_psycopg_conninfo_only_replaces_first_occurrence() -> None:
    # The driver suffix appears once at the URL scheme. Defensive: ensure a
    # later "postgresql+asyncpg://" string in a path/password component would
    # not be touched (very unlikely, but the contract is "replace once").
    url = "postgresql+asyncpg://u:p@h/db?ref=postgresql+asyncpg://other"
    assert _to_psycopg_conninfo(url).startswith("postgresql://u:p@h/db?")


def test_make_procrastinate_app_returns_app_with_psycopg_connector() -> None:
    app = make_procrastinate_app()
    assert isinstance(app, App)
    assert isinstance(app.connector, PsycopgConnector)


def test_module_level_app_has_ping_task_registered() -> None:
    assert "ping" in procrastinate_app.tasks
    assert procrastinate_app.tasks["ping"].name == "ping"


def test_ping_task_object_callable_resolves_to_function() -> None:
    # ``ping`` is a Procrastinate Task wrapper exposing the underlying coroutine.
    assert callable(ping)
    # Call signature has no arguments (Phase-1 sentinel).
    assert ping.func.__name__ == "ping"


@pytest.mark.asyncio
async def test_ping_task_returns_pong_and_logs(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="eb_digital.jobs.ping"):
        result = await ping.func()
    assert result == "pong"
    assert any(
        record.message == "ping_task_executed" and record.levelno == logging.INFO
        for record in caplog.records
    )
