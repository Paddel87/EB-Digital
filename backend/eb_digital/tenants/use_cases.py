"""Use-Case-Schicht für ``backend/tenants``.

Dünne Orchestrierungs-Schicht über dem Repository: Validierung
(Slug/Username), Status-Checks (Tenant muss ``active`` sein für Invites),
Reset-Token-Generierung und Mapping von DB-/Validierungs-Fehlern auf
domain-spezifische Exceptions, die die API-Schicht in HTTP-Status mappt.

**Bewusste Begrenzung:** Use-Cases liefern Domain-Objekte oder werfen
Domain-Exceptions, **keine** HTTP-Status. Sie kennen weder FastAPI noch
Pydantic. Damit bleiben sie test- und wiederverwendbar (z. B. später für
einen CLI-Befehl analog zu ``admin create``).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Final

from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth.hashing import PASSWORD_MIN_LENGTH, hash_password
from eb_digital.auth.models import Carer, Dispatcher
from eb_digital.auth.repositories import KIND_CARER, KIND_DISPATCHER, SubjectKind
from eb_digital.auth.reset_token import (
    DEFAULT_TTL_SECONDS,
    ResetSubjectKind,
    generate_reset_token,
    verify_reset_token,
)
from eb_digital.tenants import repositories as tenants_repo
from eb_digital.tenants.models import (
    TENANT_STATUS_ACTIVE,
    Tenant,
)
from eb_digital.tenants.slug import validate_slug
from eb_digital.tenants.username import validate_username

# Hilfs-Konstanten für Tenant-Namen (vermeidet Magic Numbers in der
# Validierungslogik).
NAME_MIN_LENGTH: Final[int] = 3
NAME_MAX_LENGTH: Final[int] = 120

# Wir wiederverwenden die Slug- und Username-Validierungs-Exceptions als
# Use-Case-Exceptions; sie sind selbst ``ValueError``-Subklassen und
# erfüllen die Use-Case-Konvention (Domain-Fehler, kein HTTP).
__all__ = [
    "InvalidResetTokenError",
    "PasswordTooShortError",
    "ResetTokenIssued",
    "TenantApplicationCreated",
    "TenantNotActiveError",
    "TenantNotFoundError",
    "UserAlreadyActiveError",
    "apply_for_tenant",
    "approve_tenant",
    "complete_password_reset",
    "deactivate_tenant",
    "invite_carer",
    "invite_dispatcher",
]


# ─── Domain-Exceptions ───────────────────────────────────────────────────────


class TenantNotFoundError(Exception):
    """Tenant mit angegebener ID existiert nicht."""

    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(f"Tenant not found: {tenant_id}")
        self.tenant_id = tenant_id


class TenantNotActiveError(Exception):
    """Tenant ist nicht im Status ``active`` — Operation nicht erlaubt."""

    def __init__(self, *, tenant_id: uuid.UUID, status: str) -> None:
        super().__init__(f"Tenant {tenant_id} is in status {status!r}, expected 'active'.")
        self.tenant_id = tenant_id
        self.status = status


class InvalidResetTokenError(Exception):
    """Reset-Token ungültig, abgelaufen oder bereits eingelöst (Replay)."""


class UserAlreadyActiveError(Exception):
    """User wurde bereits aktiviert — Reset-Token-Replay-Schutz."""


class PasswordTooShortError(Exception):
    """Passwort kürzer als ``PASSWORD_MIN_LENGTH``."""


# ─── Antwort-Datenklassen ────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TenantApplicationCreated:
    """Ergebnis von ``apply_for_tenant``."""

    tenant: Tenant


@dataclass(frozen=True, slots=True)
class ResetTokenIssued:
    """Ergebnis eines Invite-Use-Case (Dispatcher oder Carer)."""

    user_id: uuid.UUID
    reset_token: str
    expires_in_seconds: int


# ─── Use-Cases ───────────────────────────────────────────────────────────────


async def apply_for_tenant(
    session: AsyncSession,
    *,
    name: str,
    slug: str,
) -> TenantApplicationCreated:
    """Public Self-Service-Antrag.

    Validiert Slug-Format, prüft Reserved-Liste, mappt Slug-Kollision auf
    ``SlugAlreadyTakenError`` (vom Repository geworfen). Name-Validierung ist
    bewusst dünn (3-120 Zeichen, kein Format-Pattern — Verbandsnamen
    enthalten Sonderzeichen, Leerzeichen, Bindestriche).
    """
    # Name-Validierung (dünn).
    if not isinstance(name, str) or not (NAME_MIN_LENGTH <= len(name.strip()) <= NAME_MAX_LENGTH):
        msg = f"Name muss {NAME_MIN_LENGTH}-{NAME_MAX_LENGTH} Zeichen lang sein."
        raise ValueError(msg)
    name = name.strip()
    # Slug-Validierung (strikt).
    validate_slug(slug)
    tenant = await tenants_repo.create_tenant_application(session, name=name, slug=slug)
    return TenantApplicationCreated(tenant=tenant)


async def approve_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> Tenant:
    """Plattform-Admin-Approve. Idempotent."""
    tenant = await tenants_repo.approve_tenant(session, tenant_id)
    if tenant is None:
        raise TenantNotFoundError(tenant_id)
    return tenant


async def deactivate_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> Tenant:
    """Plattform-Admin-Deaktivierung (DSGVO-Art.-17-Eintrittspunkt)."""
    tenant = await tenants_repo.deactivate_tenant(session, tenant_id)
    if tenant is None:
        raise TenantNotFoundError(tenant_id)
    return tenant


def _ensure_tenant_active(tenant: Tenant) -> None:
    if tenant.status != TENANT_STATUS_ACTIVE:
        raise TenantNotActiveError(tenant_id=tenant.id, status=tenant.status)


async def _invite(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    username: str,
    email: str | None,
    secret: str,
    kind: ResetSubjectKind,
) -> ResetTokenIssued:
    tenant = await tenants_repo.find_tenant_by_id(session, tenant_id)
    if tenant is None:
        raise TenantNotFoundError(tenant_id)
    _ensure_tenant_active(tenant)
    validate_username(username)
    if kind == "dispatcher":
        user: Dispatcher | Carer = await tenants_repo.invite_dispatcher(
            session,
            tenant_id=tenant_id,
            username=username,
            email=email,
        )
    else:
        user = await tenants_repo.invite_carer(
            session,
            tenant_id=tenant_id,
            username=username,
            email=email,
        )
    token = generate_reset_token(kind, user.id, secret)
    return ResetTokenIssued(
        user_id=user.id,
        reset_token=token,
        expires_in_seconds=DEFAULT_TTL_SECONDS,
    )


async def invite_dispatcher(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    username: str,
    email: str | None,
    secret: str,
) -> ResetTokenIssued:
    """Dispatcher-Invite mit Reset-Token. Tenant muss ``active`` sein."""
    return await _invite(
        session,
        tenant_id=tenant_id,
        username=username,
        email=email,
        secret=secret,
        kind="dispatcher",
    )


async def invite_carer(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    username: str,
    email: str | None,
    secret: str,
) -> ResetTokenIssued:
    """Carer-Invite mit Reset-Token. Tenant muss ``active`` sein."""
    return await _invite(
        session,
        tenant_id=tenant_id,
        username=username,
        email=email,
        secret=secret,
        kind="carer",
    )


async def complete_password_reset(
    session: AsyncSession,
    *,
    token: str,
    new_password: str,
    secret: str,
) -> SubjectKind:
    """Verifiziert Reset-Token und setzt das Passwort.

    Liefert den ``SubjectKind`` (für ggf. spätere Audit-/Telemetrie-Zwecke).
    Wirft ``InvalidResetTokenError`` bei ungültigem/abgelaufenem Token,
    ``UserAlreadyActiveError`` bei Replay (User schon aktiv),
    ``PasswordTooShortError`` bei Mindest-Längen-Verstoß.
    """
    if not isinstance(new_password, str) or len(new_password) < PASSWORD_MIN_LENGTH:
        raise PasswordTooShortError
    verified = verify_reset_token(token, secret)
    if verified is None:
        raise InvalidResetTokenError
    kind, subject_id = verified
    password_hash = hash_password(new_password)
    success = await tenants_repo.set_password_and_activate(
        session,
        kind=kind,
        subject_id=subject_id,
        password_hash=password_hash,
    )
    if not success:
        raise UserAlreadyActiveError
    # Map ResetSubjectKind → SubjectKind: ResetSubjectKind ist Subset.
    if kind == "dispatcher":
        return KIND_DISPATCHER
    return KIND_CARER
