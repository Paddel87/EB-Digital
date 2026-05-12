"""Async-Repositories für ``backend/tenants``.

Drei verzahnte Bereiche:

  • **Tenant-Lifecycle:** Self-Service-Antrag (``status='applied'``) →
    Plattform-Admin-Approve (``status='active'``) → optional Deactivate
    (``status='deactivated'``).
  • **Dispatcher-/Carer-Onboarding:** ``invite_dispatcher`` / ``invite_carer``
    legen Pending-User mit ``is_active=False`` und leerem ``password_hash``
    an. Aktivierung über Reset-Token-Flow (``set_password_and_activate``).
  • **Berechtigungs-Helper:** ``is_dispatcher_of_tenant`` als Berechtigungs-
    Prüfung im Tenant-API für „Dispatcher legt weiteren Dispatcher/Carer
    im eigenen Mandanten an".

DB-Constraint-Verstöße (Slug-Kollision, Username-Kollision) werden hier
abgefangen und auf eigene Domain-Exceptions gemappt — die Use-Case-Schicht
fängt diese und mappt auf API-Status.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Final

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth.models import Carer, Dispatcher
from eb_digital.auth.repositories import KIND_CARER, KIND_DISPATCHER, SubjectKind
from eb_digital.tenants.models import (
    TENANT_STATUS_ACTIVE,
    TENANT_STATUS_APPLIED,
    TENANT_STATUS_DEACTIVATED,
    Tenant,
)

# Sentinel-Hash-Wert für Pending-User. Argon2 erkennt diesen als ungültiges
# PHC-Format und schlägt strukturell beim ``verify_password``-Aufruf fehl;
# zusätzlich blockiert der Login-Pfad solche User über ``is_active=False``.
# Defensive Doppel-Sicherung. Phase-7-Stabilisierung: eigene ``pending=True``-
# Spalte wäre sauberer (Schema-Migration ausgeklammert).
_PENDING_HASH_SENTINEL: Final[str] = ""


class SlugAlreadyTakenError(Exception):
    """Slug ist im ``tenant``-Index bereits vergeben."""

    def __init__(self, slug: str) -> None:
        super().__init__(f"Slug already taken: {slug!r}")
        self.slug = slug


class UsernameTakenInTenantError(Exception):
    """Username existiert im selben Mandanten bereits."""

    def __init__(self, *, tenant_id: uuid.UUID, username: str, kind: SubjectKind) -> None:
        super().__init__(
            f"Username {username!r} already exists for {kind} in tenant {tenant_id}.",
        )
        self.tenant_id = tenant_id
        self.username = username
        self.kind = kind


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ─── Tenant CRUD ─────────────────────────────────────────────────────────────


async def create_tenant_application(
    session: AsyncSession,
    *,
    name: str,
    slug: str,
) -> Tenant:
    """Legt einen neuen Mandanten-Antrag mit ``status='applied'`` an.

    Wird vom Self-Service-Endpoint aufgerufen. Bei Slug-Kollision wird
    ``SlugAlreadyTakenError`` geworfen (DB-Unique-Constraint-Verletzung wird
    abgefangen und auf die Domain-Exception gemappt).
    """
    tenant = Tenant(
        name=name,
        slug=slug,
        status=TENANT_STATUS_APPLIED,
        applied_at=_utcnow(),
    )
    session.add(tenant)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        msg = str(exc.orig) if exc.orig is not None else ""
        # Postgres-spezifische Constraint-Namen aus 2.1-Migration.
        if "uq_tenant_slug" in msg or "tenant_slug" in msg.lower():
            raise SlugAlreadyTakenError(slug) from exc
        raise
    return tenant


async def find_tenant_by_id(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> Tenant | None:
    return (
        await session.execute(select(Tenant).where(Tenant.id == tenant_id))
    ).scalar_one_or_none()


async def find_tenant_by_slug(
    session: AsyncSession,
    slug: str,
) -> Tenant | None:
    return (await session.execute(select(Tenant).where(Tenant.slug == slug))).scalar_one_or_none()


async def list_tenants(
    session: AsyncSession,
    *,
    status_filter: str | None = None,
) -> list[Tenant]:
    """Liefert alle Tenants (Plattform-Admin-Sicht), optional nach Status gefiltert.

    Sortierung: ``applied_at ASC`` — älteste Anträge zuerst, damit der
    Plattform-Admin Anträge in Eingangsreihenfolge abarbeiten kann.
    """
    stmt = select(Tenant).order_by(Tenant.applied_at.asc())
    if status_filter is not None:
        stmt = stmt.where(Tenant.status == status_filter)
    return list((await session.execute(stmt)).scalars().all())


async def approve_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> Tenant | None:
    """Setzt einen Mandanten von ``applied`` auf ``active``.

    Idempotent: bereits aktive Mandanten werden unverändert zurückgegeben.
    Bei Mandanten im Status ``deactivated`` wird **kein** Reaktivierungs-
    Pfad angeboten (das wäre eine eigene Use-Case-Entscheidung; in Phase 1
    bleibt deaktiviert deaktiviert) — der Mandant bleibt unverändert,
    Aufrufer kann am Status-Feld erkennen, dass nichts passiert ist.
    """
    tenant = await find_tenant_by_id(session, tenant_id)
    if tenant is None:
        return None
    if tenant.status == TENANT_STATUS_ACTIVE:
        return tenant
    if tenant.status != TENANT_STATUS_APPLIED:
        return tenant
    tenant.status = TENANT_STATUS_ACTIVE
    tenant.activated_at = _utcnow()
    await session.flush()
    return tenant


async def deactivate_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> Tenant | None:
    """Setzt einen Mandanten auf ``deactivated``.

    Sofortige Folgewirkung: alle Dispatcher-/Carer-Logins des Mandanten
    werden im Login-Pfad geblockt (Tenant-Status-Check). Stammdaten-Löschung
    läuft als separater Procrastinate-Job in ``backend/retention``
    (Phase 6) — in 2.4 wird nur der Status gesetzt.

    Idempotent: bereits deaktivierte Mandanten werden unverändert
    zurückgegeben.
    """
    tenant = await find_tenant_by_id(session, tenant_id)
    if tenant is None:
        return None
    if tenant.status == TENANT_STATUS_DEACTIVATED:
        return tenant
    tenant.status = TENANT_STATUS_DEACTIVATED
    tenant.deactivated_at = _utcnow()
    await session.flush()
    return tenant


# ─── Dispatcher-/Carer-Onboarding ────────────────────────────────────────────


async def invite_dispatcher(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    username: str,
    email: str | None,
) -> Dispatcher:
    """Legt einen Pending-Dispatcher an (``is_active=False``, leerer Hash).

    Aktivierung folgt über Reset-Token-Flow
    (``set_password_and_activate``). Bei Username-Kollision im selben
    Mandanten wird ``UsernameTakenInTenantError`` geworfen.
    """
    dispatcher = Dispatcher(
        tenant_id=tenant_id,
        username=username,
        password_hash=_PENDING_HASH_SENTINEL,
        email=email,
        is_active=False,
    )
    session.add(dispatcher)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        msg = str(exc.orig) if exc.orig is not None else ""
        if "uq_dispatcher_tenant_id_username" in msg:
            raise UsernameTakenInTenantError(
                tenant_id=tenant_id,
                username=username,
                kind=KIND_DISPATCHER,
            ) from exc
        raise
    return dispatcher


async def invite_carer(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    username: str,
    email: str | None,
) -> Carer:
    """Analog ``invite_dispatcher`` für Carer-Accounts."""
    carer = Carer(
        tenant_id=tenant_id,
        username=username,
        password_hash=_PENDING_HASH_SENTINEL,
        email=email,
        is_active=False,
    )
    session.add(carer)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        msg = str(exc.orig) if exc.orig is not None else ""
        if "uq_carer_tenant_id_username" in msg:
            raise UsernameTakenInTenantError(
                tenant_id=tenant_id,
                username=username,
                kind=KIND_CARER,
            ) from exc
        raise
    return carer


async def set_password_and_activate(
    session: AsyncSession,
    *,
    kind: SubjectKind,
    subject_id: uuid.UUID,
    password_hash: str,
) -> bool:
    """Setzt Hash + ``is_active=True`` atomar; Replay-Schutz via aktive Vor-Prüfung.

    Liefert ``True`` bei Erfolg, ``False`` wenn der User schon aktiv ist
    oder gar nicht existiert (Token-Replay-Schutz: ein gültiger Reset-Token
    funktioniert nur einmal). Für PlatformAdmin-Reset (Phase ≥ 7) wäre eine
    eigene Variante nötig — hier explizit nur Dispatcher und Carer.
    """
    if kind == KIND_DISPATCHER:
        stmt = select(Dispatcher).where(Dispatcher.id == subject_id)
        dispatcher = (await session.execute(stmt)).scalar_one_or_none()
        if dispatcher is None or dispatcher.is_active:
            return False
        dispatcher.password_hash = password_hash
        dispatcher.is_active = True
        await session.flush()
        return True
    if kind == KIND_CARER:
        carer_stmt = select(Carer).where(Carer.id == subject_id)
        carer = (await session.execute(carer_stmt)).scalar_one_or_none()
        if carer is None or carer.is_active:
            return False
        carer.password_hash = password_hash
        carer.is_active = True
        await session.flush()
        return True
    return False


async def is_dispatcher_of_tenant(
    session: AsyncSession,
    *,
    dispatcher_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> bool:
    """``True`` wenn Dispatcher zum Mandanten gehört (für Berechtigungs-Check)."""
    stmt = (
        select(func.count())
        .select_from(Dispatcher)
        .where(
            Dispatcher.id == dispatcher_id,
            Dispatcher.tenant_id == tenant_id,
        )
    )
    count = int((await session.execute(stmt)).scalar_one())
    return count > 0


__all__ = [
    "SlugAlreadyTakenError",
    "UsernameTakenInTenantError",
    "approve_tenant",
    "create_tenant_application",
    "deactivate_tenant",
    "find_tenant_by_id",
    "find_tenant_by_slug",
    "invite_carer",
    "invite_dispatcher",
    "is_dispatcher_of_tenant",
    "list_tenants",
    "set_password_and_activate",
]
