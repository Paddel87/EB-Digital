"""Async-Repositories für die Auth-Subjekte (PlatformAdmin / Dispatcher / Carer).

Drei separate Tabellen, ein gemeinsamer Login-Pfad: ``find_by_username`` sucht
in einer deterministischen Reihenfolge und liefert das erste Match als
``AuthSubject`` — eine schmale typisierte Container-Klasse, die das Login-API
und der Session-Helper konsumieren, ohne ORM-Klassen direkt zu kennen.

**Suchreihenfolge:** ``platform_admin`` → ``dispatcher`` → ``carer``. Bei
gleichem Username in mehreren Tabellen gewinnt PlatformAdmin (höchste
Privileg-Stufe). Phase 1 hat ``platform_admin.username`` als globally
unique definiert; Dispatcher- und Carer-Usernames sind jeweils nur pro
Mandant unique. ``find_by_username`` liefert den ersten Treffer — bei
Mehrdeutigkeit über verschiedene Mandanten hinweg trifft das den
ältesten Eintrag (deterministisch über ``created_at ASC, id ASC``).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Final, Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth.models import Carer, Dispatcher, PlatformAdmin

SubjectKind = Literal["platform_admin", "dispatcher", "carer"]

KIND_PLATFORM_ADMIN: Final[SubjectKind] = "platform_admin"
KIND_DISPATCHER: Final[SubjectKind] = "dispatcher"
KIND_CARER: Final[SubjectKind] = "carer"


@dataclass(frozen=True, slots=True)
class AuthSubject:
    """Login-relevante Felder eines authentifizierten Subjekts.

    Wird vom Login-API und Session-Helper als opaker Container behandelt; die
    konkrete ORM-Klasse bleibt im Repository gekapselt.
    """

    kind: SubjectKind
    id: uuid.UUID
    username: str
    password_hash: str
    is_active: bool
    tenant_id: uuid.UUID | None  # PlatformAdmin: None; Dispatcher/Carer: Mandanten-FK


async def find_by_username(session: AsyncSession, username: str) -> AuthSubject | None:
    """Sucht ``username`` in den drei Auth-Tabellen, liefert den ersten Treffer.

    Reihenfolge: PlatformAdmin → Dispatcher → Carer (siehe Modul-Docstring).
    Bei Mehrfach-Treffern in Dispatcher/Carer (gleicher Username in
    verschiedenen Mandanten) gewinnt der älteste Eintrag pro Tabelle.
    """
    admin_stmt = select(PlatformAdmin).where(PlatformAdmin.username == username)
    admin = (await session.execute(admin_stmt)).scalar_one_or_none()
    if admin is not None:
        # PlatformAdmin hat im Phase-1-Schema kein ``is_active`` (immer aktiv).
        return AuthSubject(
            kind=KIND_PLATFORM_ADMIN,
            id=admin.id,
            username=admin.username,
            password_hash=admin.password_hash,
            is_active=True,
            tenant_id=None,
        )

    dispatcher_stmt = (
        select(Dispatcher)
        .where(Dispatcher.username == username)
        .order_by(Dispatcher.created_at.asc(), Dispatcher.id.asc())
        .limit(1)
    )
    dispatcher = (await session.execute(dispatcher_stmt)).scalar_one_or_none()
    if dispatcher is not None:
        return AuthSubject(
            kind=KIND_DISPATCHER,
            id=dispatcher.id,
            username=dispatcher.username,
            password_hash=dispatcher.password_hash,
            is_active=dispatcher.is_active,
            tenant_id=dispatcher.tenant_id,
        )

    carer_stmt = (
        select(Carer)
        .where(Carer.username == username)
        .order_by(Carer.created_at.asc(), Carer.id.asc())
        .limit(1)
    )
    carer = (await session.execute(carer_stmt)).scalar_one_or_none()
    if carer is not None:
        return AuthSubject(
            kind=KIND_CARER,
            id=carer.id,
            username=carer.username,
            password_hash=carer.password_hash,
            is_active=carer.is_active,
            tenant_id=carer.tenant_id,
        )

    return None


__all__ = [
    "KIND_CARER",
    "KIND_DISPATCHER",
    "KIND_PLATFORM_ADMIN",
    "AuthSubject",
    "SubjectKind",
    "find_by_username",
]
