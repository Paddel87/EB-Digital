"""Tests for the platform-admin bootstrap CLI (Schritt 1.6)."""

from __future__ import annotations

import argparse
import logging
from typing import Any

import pytest

from eb_digital.auth import cli as auth_cli
from eb_digital.auth.cli import (
    AdminCreationError,
    cmd_admin_create,
    create_platform_admin,
)
from eb_digital.auth.models import PlatformAdmin


class _FakeSession:
    """Minimal AsyncSession stand-in: scalar/add/flush only.

    ``flush`` applies SQLAlchemy column defaults the way the real engine would
    on INSERT. That keeps the assertion ``admin.created_at`` / ``admin.id`` not
    None without a live database round-trip.
    """

    def __init__(self, *, existing: PlatformAdmin | None = None) -> None:
        self._existing = existing
        self.added: list[PlatformAdmin] = []
        self.flushed = False

    async def scalar(self, _stmt: object) -> PlatformAdmin | None:
        return self._existing

    def add(self, obj: PlatformAdmin) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushed = True
        for obj in self.added:
            for col in obj.__table__.c:
                if getattr(obj, col.name, None) is None and col.default is not None:
                    arg = col.default.arg
                    value = arg(None) if callable(arg) else arg
                    setattr(obj, col.name, value)


# ─── create_platform_admin ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_platform_admin_inserts_new_row() -> None:
    session = _FakeSession()
    admin = await create_platform_admin(
        session,  # type: ignore[arg-type]
        username="patrick",
        password="correcthorsebattery",
    )
    assert session.added == [admin]
    assert session.flushed is True
    assert admin.username == "patrick"
    assert admin.password_hash.startswith("$argon2id$")
    assert admin.created_via == "bootstrap_cli"
    assert admin.id is not None
    assert admin.created_at is not None


@pytest.mark.asyncio
async def test_create_platform_admin_strips_username_whitespace() -> None:
    session = _FakeSession()
    admin = await create_platform_admin(
        session,  # type: ignore[arg-type]
        username="  patrick  ",
        password="correcthorsebattery",
    )
    assert admin.username == "patrick"


@pytest.mark.asyncio
async def test_create_platform_admin_supports_admin_cli_role() -> None:
    session = _FakeSession()
    admin = await create_platform_admin(
        session,  # type: ignore[arg-type]
        username="patrick",
        password="correcthorsebattery",
        created_via="admin_cli",
    )
    assert admin.created_via == "admin_cli"


@pytest.mark.asyncio
async def test_create_platform_admin_rejects_empty_username() -> None:
    session = _FakeSession()
    with pytest.raises(AdminCreationError, match="username darf nicht leer sein"):
        await create_platform_admin(
            session,  # type: ignore[arg-type]
            username="   ",
            password="correcthorsebattery",
        )
    assert session.added == []


@pytest.mark.asyncio
async def test_create_platform_admin_rejects_username_with_internal_whitespace() -> None:
    session = _FakeSession()
    with pytest.raises(AdminCreationError, match="keine Leerzeichen"):
        await create_platform_admin(
            session,  # type: ignore[arg-type]
            username="pat rick",
            password="correcthorsebattery",
        )
    assert session.added == []


@pytest.mark.asyncio
async def test_create_platform_admin_rejects_too_short_username() -> None:
    session = _FakeSession()
    with pytest.raises(AdminCreationError, match="mindestens 3 Zeichen"):
        await create_platform_admin(
            session,  # type: ignore[arg-type]
            username="pa",
            password="correcthorsebattery",
        )
    assert session.added == []


@pytest.mark.asyncio
async def test_create_platform_admin_rejects_short_password() -> None:
    session = _FakeSession()
    with pytest.raises(AdminCreationError, match="mindestens 12 Zeichen"):
        await create_platform_admin(
            session,  # type: ignore[arg-type]
            username="patrick",
            password="short",
        )
    assert session.added == []


@pytest.mark.asyncio
async def test_create_platform_admin_rejects_duplicate_username() -> None:
    existing = PlatformAdmin(
        username="patrick",
        password_hash="$argon2id$placeholder",
        created_via="bootstrap_cli",
    )
    session = _FakeSession(existing=existing)
    with pytest.raises(AdminCreationError, match="existiert bereits"):
        await create_platform_admin(
            session,  # type: ignore[arg-type]
            username="patrick",
            password="correcthorsebattery",
        )
    assert session.added == []


@pytest.mark.asyncio
async def test_create_platform_admin_logs_event_without_password_or_hash(
    caplog: pytest.LogCaptureFixture,
) -> None:
    session = _FakeSession()
    with caplog.at_level(logging.INFO, logger="eb_digital.auth.cli"):
        await create_platform_admin(
            session,  # type: ignore[arg-type]
            username="patrick",
            password="correcthorsebattery-secret",
        )
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.message == "platform_admin_created"
    # No leak of the plaintext password or the hash into the log payload.
    record_dict = record.__dict__
    assert "correcthorsebattery-secret" not in str(record_dict)
    assert "password_hash" not in record_dict
    assert record_dict.get("username") == "patrick"
    assert record_dict.get("created_via") == "bootstrap_cli"
    assert "at" in record_dict


# ─── cmd_admin_create + _run_create ──────────────────────────────────────────


def test_cmd_admin_create_rejects_empty_username(
    capsys: pytest.CaptureFixture[str],
) -> None:
    args = argparse.Namespace(username="   ")
    code = cmd_admin_create(args)
    assert code == 1
    assert "username darf nicht leer sein" in capsys.readouterr().err


def test_cmd_admin_create_rejects_empty_password(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(auth_cli, "_read_password_interactively", lambda: "")
    args = argparse.Namespace(username="patrick")
    code = cmd_admin_create(args)
    assert code == 1
    assert "Passwort darf nicht leer sein" in capsys.readouterr().err


def test_cmd_admin_create_invokes_run_create_with_parsed_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def fake_run_create(*, username: str, password: str) -> int:
        captured["username"] = username
        captured["password"] = password
        return 0

    monkeypatch.setattr(auth_cli, "_read_password_interactively", lambda: "correcthorsebattery")
    monkeypatch.setattr(auth_cli, "_run_create", fake_run_create)

    args = argparse.Namespace(username="patrick")
    assert cmd_admin_create(args) == 0
    assert captured == {"username": "patrick", "password": "correcthorsebattery"}


@pytest.mark.asyncio
async def test_run_create_happy_path_disposes_engine(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    disposed = {"called": False}

    class _FakeEngine:
        async def dispose(self) -> None:
            disposed["called"] = True

    fake_session = _FakeSession()

    class _FakeFactory:
        def __call__(self) -> _FakeSessionContext:
            return _FakeSessionContext(fake_session)

    class _FakeSessionContext:
        def __init__(self, session: _FakeSession) -> None:
            self._session = session
            self.tx = _FakeTxContext()

        async def __aenter__(self) -> _FakeSession:
            return self._session

        async def __aexit__(self, *_exc: object) -> None:
            return None

    class _FakeTxContext:
        async def __aenter__(self) -> None:
            return None

        async def __aexit__(self, *_exc: object) -> None:
            return None

    # session.begin() returns a transaction context manager — patch on the
    # FakeSession instance.
    fake_session.begin = lambda: _FakeTxContext()  # type: ignore[attr-defined]

    monkeypatch.setattr("eb_digital.db.create_db_engine", lambda _url: _FakeEngine())
    monkeypatch.setattr("eb_digital.db.create_session_factory", lambda _engine: _FakeFactory())

    code = await auth_cli._run_create(username="patrick", password="correcthorsebattery")
    assert code == 0
    assert disposed["called"] is True
    assert len(fake_session.added) == 1
    assert fake_session.added[0].username == "patrick"
    out = capsys.readouterr().out
    assert "created admin user: patrick" in out


@pytest.mark.asyncio
async def test_run_create_returns_1_on_admin_creation_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    disposed = {"called": False}

    class _FakeEngine:
        async def dispose(self) -> None:
            disposed["called"] = True

    existing = PlatformAdmin(
        username="patrick",
        password_hash="$argon2id$placeholder",
        created_via="bootstrap_cli",
    )
    fake_session = _FakeSession(existing=existing)

    class _FakeTxContext:
        async def __aenter__(self) -> None:
            return None

        async def __aexit__(self, *_exc: object) -> None:
            return None

    fake_session.begin = lambda: _FakeTxContext()  # type: ignore[attr-defined]

    class _FakeFactory:
        def __call__(self) -> _FakeSessionContext:
            return _FakeSessionContext(fake_session)

    class _FakeSessionContext:
        def __init__(self, session: _FakeSession) -> None:
            self._session = session

        async def __aenter__(self) -> _FakeSession:
            return self._session

        async def __aexit__(self, *_exc: object) -> None:
            return None

    monkeypatch.setattr("eb_digital.db.create_db_engine", lambda _url: _FakeEngine())
    monkeypatch.setattr("eb_digital.db.create_session_factory", lambda _engine: _FakeFactory())

    code = await auth_cli._run_create(username="patrick", password="correcthorsebattery")
    assert code == 1
    assert disposed["called"] is True
    assert "existiert bereits" in capsys.readouterr().err


def test_read_password_interactively_delegates_to_getpass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    def fake_getpass(prompt: str) -> str:
        captured["prompt"] = prompt
        return "from-getpass"

    monkeypatch.setattr("eb_digital.auth.cli.getpass.getpass", fake_getpass)
    assert auth_cli._read_password_interactively() == "from-getpass"
    assert captured["prompt"] == "Passwort: "
