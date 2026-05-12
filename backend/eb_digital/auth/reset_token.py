"""Signierte Password-Reset-Tokens für Dispatcher-/Carer-Onboarding.

Verwendung in Phase 2:
  • Plattform-Admin oder Mandanten-Dispatcher legt einen neuen Dispatcher
    oder Carer via ``POST /api/tenants/{id}/dispatchers|carers`` an. Der
    User wird mit ``is_active=False`` und leerem ``password_hash``
    gespeichert; der Reset-Token wird in der API-Response zurückgegeben.
  • Der neue User ruft ``POST /api/auth/reset-password`` mit Token und
    selbst gewähltem Passwort auf — der Token wird signaturgeprüft, der
    Hash gesetzt und der User aktiviert.

**Salt-Separation gegenüber 2.3:** Der Salt
``"eb-digital.user-password-reset"`` ist bewusst ein anderer als der
``"eb-digital.operation-url-token"``-Salt aus ``auth_anonymous.tokens`` —
ein für eine Operation signierter URL-Token kann nicht versehentlich als
Reset-Token akzeptiert werden, auch wenn beide Module dasselbe
``settings.secret_key`` benutzen (Detail-Plan-Frage 4-A aus 2.3).

**TTL:** 24 h (Default). Plattform-Admin/Dispatcher hat einen Tag, den
Token an den Empfänger zu übermitteln. Bei Ablauf: Re-Invite (Endpoint
nochmal aufrufen, neuer Token).

**Replay-Schutz:** Der Reset-Token enthält keine Nonce. Replay-Schutz ist
in der Use-Case-Schicht via ``set_password_and_activate`` implementiert
— wenn der User bereits ``is_active=True`` ist, schlägt das atomare
Update fehl und der Endpoint antwortet 410 (siehe
``tenants.repositories.set_password_and_activate``).
"""

from __future__ import annotations

import uuid
from typing import Final, Literal, get_args

from itsdangerous import BadData, SignatureExpired, URLSafeTimedSerializer

ResetSubjectKind = Literal["dispatcher", "carer"]

RESET_TOKEN_SALT: Final[str] = "eb-digital.user-password-reset"  # noqa: S105 — Context-Salt, kein Secret
DEFAULT_TTL_SECONDS: Final[int] = 24 * 60 * 60  # 24 h


def _serializer(secret: str) -> URLSafeTimedSerializer:
    """Baut einen ``URLSafeTimedSerializer`` mit dem produktiven Salt."""
    return URLSafeTimedSerializer(secret_key=secret, salt=RESET_TOKEN_SALT)


def generate_reset_token(
    subject_kind: ResetSubjectKind,
    subject_id: uuid.UUID,
    secret: str,
) -> str:
    """Erzeuge einen zeitbeschränkten signierten Reset-Token.

    Payload: ``{"kind": <subject_kind>, "id": <uuid-as-str>}``. Die TTL wird
    nicht in den Token kodiert — sie wird beim ``loads`` über ``max_age``
    durchgesetzt, damit der Aufrufer beim Verify die TTL flexibel halten
    kann (Default-TTL via ``verify_reset_token`` ohne Override).
    """
    payload: dict[str, str] = {"kind": subject_kind, "id": str(subject_id)}
    return _serializer(secret).dumps(payload)


def verify_reset_token(
    token: str,
    secret: str,
    *,
    max_age_seconds: int = DEFAULT_TTL_SECONDS,
) -> tuple[ResetSubjectKind, uuid.UUID] | None:
    """Liefert ``(kind, subject_id)`` falls Token gültig, sonst ``None``.

    Alle Fehlerklassen (``BadSignature``, ``SignatureExpired``,
    ``BadPayload``, kaputte Payload-Struktur, ungültige UUID, unbekannter
    ``kind``) werden zu ``None`` umgesetzt — die Aufrufer reagieren mit 410
    (Token ungültig oder abgelaufen, kein Info-Leak welche der beiden
    Ursachen).
    """
    try:
        payload = _serializer(secret).loads(token, max_age=max_age_seconds)
    except SignatureExpired:
        return None
    except BadData:
        # ``BadData`` deckt ``BadSignature``, ``BadPayload``, und alle
        # weiteren itsdangerous-Validierungs-Fehler ab.
        return None

    if not isinstance(payload, dict):
        return None
    raw_kind = payload.get("kind")
    raw_id = payload.get("id")
    if raw_kind not in get_args(ResetSubjectKind):
        return None
    if not isinstance(raw_id, str):
        return None
    try:
        subject_id = uuid.UUID(raw_id)
    except (ValueError, TypeError):
        return None
    # Mypy versteht nach ``raw_kind not in get_args(...)``-Check oben nicht
    # automatisch, dass ``raw_kind`` jetzt vom Literal-Typ ist.
    kind: ResetSubjectKind = raw_kind  # type: ignore[assignment]
    return kind, subject_id


__all__ = [
    "DEFAULT_TTL_SECONDS",
    "RESET_TOKEN_SALT",
    "ResetSubjectKind",
    "generate_reset_token",
    "verify_reset_token",
]
