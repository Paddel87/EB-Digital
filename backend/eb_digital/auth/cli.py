"""CLI-Subcommand für Plattform-Administrator-Bootstrap (ADR-004, Schritt 1.6).

Aufruf: ``python -m eb_digital admin create --username <name>``.
Passwort wird interaktiv über ``getpass.getpass()`` gelesen — niemals als
CLI-Argument, niemals in Logs, niemals im Klartext gespeichert.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import sys
from typing import TYPE_CHECKING

from sqlalchemy import select

from eb_digital.auth.hashing import PASSWORD_MIN_LENGTH, hash_password
from eb_digital.auth.models import CREATED_VIA_BOOTSTRAP_CLI, PlatformAdmin
from eb_digital.logging import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

_logger = get_logger("eb_digital.auth.cli")


class AdminCreationError(Exception):
    """Vorhersehbarer, nutzerseitiger Fehler beim Bootstrap (z. B. Duplikat)."""


USERNAME_MIN_LENGTH: int = 3


async def create_platform_admin(
    session: AsyncSession,
    *,
    username: str,
    password: str,
    created_via: str = CREATED_VIA_BOOTSTRAP_CLI,
) -> PlatformAdmin:
    """Plattform-Admin anlegen oder ``AdminCreationError`` werfen.

    Der Klartext-Passwort-Parameter wird ausschließlich an
    :func:`hash_password` weitergereicht und sofort verworfen.
    """
    cleaned = username.strip()
    if not cleaned:
        raise AdminCreationError("username darf nicht leer sein")
    if any(c.isspace() for c in cleaned):
        raise AdminCreationError("username darf keine Leerzeichen enthalten")
    if len(cleaned) < USERNAME_MIN_LENGTH:
        raise AdminCreationError(
            f"username muss mindestens {USERNAME_MIN_LENGTH} Zeichen lang sein"
        )
    if len(password) < PASSWORD_MIN_LENGTH:
        raise AdminCreationError(
            f"Passwort muss mindestens {PASSWORD_MIN_LENGTH} Zeichen lang sein"
        )

    existing = await session.scalar(select(PlatformAdmin).where(PlatformAdmin.username == cleaned))
    if existing is not None:
        raise AdminCreationError(f"Username '{cleaned}' existiert bereits")

    admin = PlatformAdmin(
        username=cleaned,
        password_hash=hash_password(password),
        created_via=created_via,
    )
    session.add(admin)
    await session.flush()

    _logger.info(
        "platform_admin_created",
        extra={
            "username": admin.username,
            "created_via": admin.created_via,
            "at": admin.created_at.isoformat(),
        },
    )
    return admin


def _read_password_interactively() -> str:
    """getpass-Wrapper, in Tests monkey-patchbar."""
    return getpass.getpass("Passwort: ")


async def _run_create(username: str, password: str) -> int:
    from eb_digital.db import create_db_engine, create_session_factory
    from eb_digital.settings import get_settings

    settings = get_settings()
    engine = create_db_engine(settings.database_url)
    factory = create_session_factory(engine)
    try:
        async with factory() as session, session.begin():
            admin = await create_platform_admin(session, username=username, password=password)
        sys.stdout.write(f"created admin user: {admin.username}\n")
        return 0
    except AdminCreationError as exc:
        sys.stderr.write(f"Fehler: {exc}\n")
        return 1
    finally:
        await engine.dispose()


def cmd_admin_create(args: argparse.Namespace) -> int:
    """Argparse-Handler für ``admin create --username NAME``."""
    username = str(args.username).strip()
    if not username:
        sys.stderr.write("Fehler: --username darf nicht leer sein\n")
        return 1

    password = _read_password_interactively()
    if not password:
        sys.stderr.write("Fehler: Passwort darf nicht leer sein\n")
        return 1

    return asyncio.run(_run_create(username=username, password=password))


__all__ = [
    "AdminCreationError",
    "cmd_admin_create",
    "create_platform_admin",
]
