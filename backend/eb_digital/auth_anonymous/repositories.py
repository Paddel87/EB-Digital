"""Async-Repositories für ``backend/auth_anonymous``.

Operations werden über die im URL-Token enthaltene UUID aufgelöst; die
Spalte ``operation.url_token`` bleibt als Anti-Replay-/Rotations-Anker in
der DB, ist aber nicht der Lookup-Schlüssel (Signatur-Verify ersetzt das).

Anonymous-Sessions werden eingefügt und per ``id`` wieder gelesen (z. B.
für die geplanten Order-Endpoints in Phase 4).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth_anonymous.models import AnonymousSession
from eb_digital.operations.models import Operation


async def find_operation_by_id(
    session: AsyncSession,
    operation_id: uuid.UUID,
) -> Operation | None:
    """SELECT auf ``operation.id``; ``None`` wenn nicht vorhanden."""
    stmt = select(Operation).where(Operation.id == operation_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def create_anonymous_session(
    session: AsyncSession,
    *,
    operation_id: uuid.UUID,
) -> AnonymousSession:
    """Lege eine neue ``AnonymousSession`` an und gib sie zurück.

    ``expires_at`` wird vom Model-Default auf ``now + 24h`` gesetzt.
    """
    record = AnonymousSession(operation_id=operation_id)
    session.add(record)
    await session.flush()
    return record


async def find_anonymous_session_by_id(
    session: AsyncSession,
    session_id: uuid.UUID,
) -> AnonymousSession | None:
    """SELECT auf ``anonymous_session.id``; ``None`` wenn nicht vorhanden."""
    stmt = select(AnonymousSession).where(AnonymousSession.id == session_id)
    return (await session.execute(stmt)).scalar_one_or_none()


def is_session_still_valid(record: AnonymousSession, now: datetime | None = None) -> bool:
    """``True`` solange ``expires_at`` in der Zukunft liegt.

    Operation-Status-Check (``closed`` → invalide) erfolgt in der
    aufrufenden Schicht, weil dort die Operation bereits geladen ist.
    """
    return record.expires_at > (now or datetime.now(UTC))


__all__ = [
    "create_anonymous_session",
    "find_anonymous_session_by_id",
    "find_operation_by_id",
    "is_session_still_valid",
]
