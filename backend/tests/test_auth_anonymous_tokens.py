"""Tests für ``backend/eb_digital/auth_anonymous/tokens``.

URL-Token-Generator und -Validator via ``itsdangerous.URLSafeSerializer``.
"""

from __future__ import annotations

import uuid

from eb_digital.auth_anonymous.tokens import (
    URL_TOKEN_SALT,
    generate_url_token,
    verify_url_token,
)

_SECRET = "test-secret-for-url-tokens"


def test_roundtrip_returns_original_operation_id() -> None:
    op_id = uuid.uuid4()
    token = generate_url_token(op_id, _SECRET)
    assert verify_url_token(token, _SECRET) == op_id


def test_token_is_url_safe_and_within_column_length() -> None:
    """Token fits in ``operation.url_token`` (``String(255)``) and contains
    only URL-safe characters (no ``+`` or ``/``)."""
    op_id = uuid.uuid4()
    token = generate_url_token(op_id, _SECRET)
    assert len(token) <= 255
    forbidden = set("+/")
    assert not (set(token) & forbidden), f"non-URL-safe char in token: {token!r}"


def test_each_call_yields_identical_token_for_same_inputs() -> None:
    """Stateless serializer: gleiche Inputs → gleicher Token (deterministisch).

    Wir verlassen uns nicht auf diese Eigenschaft im Produktivpfad (die
    Tokens werden einmal beim Operation-Anlegen erzeugt und persistiert),
    aber der Test dokumentiert das Verhalten als beobachtete Eigenschaft.
    """
    op_id = uuid.uuid4()
    a = generate_url_token(op_id, _SECRET)
    b = generate_url_token(op_id, _SECRET)
    assert a == b


def test_wrong_secret_returns_none() -> None:
    token = generate_url_token(uuid.uuid4(), _SECRET)
    assert verify_url_token(token, "different-secret") is None


def test_completely_forged_token_returns_none() -> None:
    assert verify_url_token("not-a-real-token", _SECRET) is None
    assert verify_url_function_safely("", _SECRET) is None


def verify_url_function_safely(token: str, secret: str) -> uuid.UUID | None:
    """Hilfsfunktion: leere Strings dürfen nicht zu Exceptions führen."""
    return verify_url_token(token, secret)


def test_tampered_payload_returns_none() -> None:
    """Auch wenn man die Payload manipuliert, schlägt die Signatur fehl."""
    token = generate_url_token(uuid.uuid4(), _SECRET)
    # Tausche einen Buchstaben im Payload-Teil (vor dem Punkt).
    payload, sep, sig = token.partition(".")
    tampered = payload[:-1] + ("A" if payload[-1] != "A" else "B") + sep + sig
    assert verify_url_token(tampered, _SECRET) is None


def test_token_with_non_uuid_payload_returns_none() -> None:
    """Wenn die Payload kein UUID-String ist (anderes Domain-Token mit gleichem
    Secret/Salt-Paar), soll der Token-Validator sauber ``None`` liefern statt
    eine UUID-Exception zu werfen.

    Wir bauen das, indem wir mit demselben Serializer einen anderen String
    signieren — dann ist die Signatur valide, aber die Payload ist keine
    UUID.
    """
    from itsdangerous import URLSafeSerializer

    other_serializer = URLSafeSerializer(secret_key=_SECRET, salt=URL_TOKEN_SALT)
    forged = other_serializer.dumps("not-a-uuid-just-a-string")
    assert verify_url_token(forged, _SECRET) is None


def test_token_with_non_string_payload_returns_none() -> None:
    """itsdangerous akzeptiert JSON-serialisierbare Werte (Dict, List, …) als
    Payload. Unser Validator erwartet ausschließlich Strings; alles andere
    wird zu ``None``.
    """
    from itsdangerous import URLSafeSerializer

    serializer = URLSafeSerializer(secret_key=_SECRET, salt=URL_TOKEN_SALT)
    dict_token = serializer.dumps({"operation_id": "abc"})
    assert verify_url_token(dict_token, _SECRET) is None


def test_salt_isolation_prevents_cross_context_replay() -> None:
    """Ein mit anderem Salt signierter Token wird abgewiesen — Context-Separation
    schützt vor Replay aus z. B. einem späteren Email-Reset-Pfad."""
    from itsdangerous import URLSafeSerializer

    other = URLSafeSerializer(secret_key=_SECRET, salt="some.other.context")
    cross_context_token = other.dumps(str(uuid.uuid4()))
    assert verify_url_token(cross_context_token, _SECRET) is None
