"""URL-Token-Generator und -Validator für die Einsatzkraft-URL.

Die einsatzspezifische URL trägt einen ``itsdangerous.URLSafeSerializer``-
signierten Token, der die Operation-UUID als Payload enthält. Vorteile gegen-
über reinen Zufalls-Tokens:

  • **Signatur-Vor-Check ohne DB-Hit:** Verfälschte oder erfundene Tokens
    werden anhand der Signatur abgewiesen, bevor das Backend in die Datenbank
    schaut. Reduziert die Angriffsfläche für URL-Fuzzing.
  • **Context-Separation via Salt:** Der Salt ``operation-url-token`` schützt
    davor, dass ein für einen anderen Kontext signierter Wert (z. B. später ein
    Email-Reset-Token) als gültiger Operation-Token interpretiert wird.

Der Token wird beim Operation-Anlegen erzeugt und in ``operation.url_token``
gespeichert (Spalte ist seit Schritt 2.3 ``String(255)``; itsdangerous-Tokens
sind ~80-100 Zeichen lang). Der Lookup geht über die im Token enthaltene
Operation-UUID; das DB-Feld bleibt als Anti-Replay-/Rotations-Anker.
"""

from __future__ import annotations

import uuid
from typing import Final

from itsdangerous import BadData, URLSafeSerializer

URL_TOKEN_SALT: Final[str] = "eb-digital.operation-url-token"  # noqa: S105 — Context-Salt, kein Secret


def _serializer(secret: str) -> URLSafeSerializer:
    """Baut einen ``URLSafeSerializer`` mit dem produktiven Salt."""
    return URLSafeSerializer(secret_key=secret, salt=URL_TOKEN_SALT)


def generate_url_token(operation_id: uuid.UUID, secret: str) -> str:
    """Erzeuge einen signierten URL-Token für die Operation.

    Payload ist die UUID als String; der Empfänger validiert die Signatur und
    rekonstruiert daraus die UUID per ``verify_url_token``.
    """
    return _serializer(secret).dumps(str(operation_id))


def verify_url_token(token: str, secret: str) -> uuid.UUID | None:
    """Liefert die Operation-UUID, falls Token-Signatur und Payload gültig sind.

    Bei ungültiger Signatur, kaputter Payload oder kaputtem UUID-String wird
    ``None`` zurückgegeben — die Aufrufer (Endpoints) reagieren mit 404/410,
    nie mit einer 5xx-Exception.
    """
    try:
        payload = _serializer(secret).loads(token)
    except BadData:
        # ``BadData`` ist die gemeinsame Oberklasse von ``BadSignature`` (HMAC
        # passt nicht), ``BadPayload`` (Base64-Decoder schlägt fehl) und
        # weiteren itsdangerous-Validierungs-Fehlern. Alle landen einheitlich
        # in ``None``, damit der Endpoint mit 404/410 antworten kann.
        return None
    if not isinstance(payload, str):
        return None
    try:
        return uuid.UUID(payload)
    except (ValueError, TypeError):
        return None


__all__ = [
    "URL_TOKEN_SALT",
    "generate_url_token",
    "verify_url_token",
]
