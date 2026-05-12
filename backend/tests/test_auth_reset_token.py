"""Tests für ``backend/eb_digital/auth/reset_token``."""

from __future__ import annotations

import time
import uuid

import pytest

from eb_digital.auth.reset_token import (
    DEFAULT_TTL_SECONDS,
    RESET_TOKEN_SALT,
    generate_reset_token,
    verify_reset_token,
)
from eb_digital.auth_anonymous.tokens import URL_TOKEN_SALT, generate_url_token

SECRET = "test-secret-not-for-production"


def test_roundtrip_dispatcher() -> None:
    subject_id = uuid.uuid4()
    token = generate_reset_token("dispatcher", subject_id, SECRET)
    assert isinstance(token, str)
    assert token  # non-empty
    result = verify_reset_token(token, SECRET)
    assert result is not None
    kind, recovered_id = result
    assert kind == "dispatcher"
    assert recovered_id == subject_id


def test_roundtrip_carer() -> None:
    subject_id = uuid.uuid4()
    token = generate_reset_token("carer", subject_id, SECRET)
    result = verify_reset_token(token, SECRET)
    assert result == ("carer", subject_id)


def test_wrong_secret_returns_none() -> None:
    subject_id = uuid.uuid4()
    token = generate_reset_token("dispatcher", subject_id, SECRET)
    assert verify_reset_token(token, "different-secret") is None


def test_garbage_token_returns_none() -> None:
    assert verify_reset_token("not-a-token", SECRET) is None
    assert verify_reset_token("", SECRET) is None
    assert verify_reset_token("a.b.c", SECRET) is None


def test_expired_token_returns_none() -> None:
    """``max_age=0`` markiert jeden Token sofort als abgelaufen."""
    subject_id = uuid.uuid4()
    token = generate_reset_token("dispatcher", subject_id, SECRET)
    # 1 Sekunde warten, damit ``max_age=0`` greift (URLSafeTimedSerializer
    # nutzt Sekunden-Auflösung; Token ist genau jetzt 0 s alt).
    time.sleep(1.1)
    assert verify_reset_token(token, SECRET, max_age_seconds=0) is None


def test_long_max_age_accepts_recent_token() -> None:
    subject_id = uuid.uuid4()
    token = generate_reset_token("carer", subject_id, SECRET)
    result = verify_reset_token(token, SECRET, max_age_seconds=DEFAULT_TTL_SECONDS)
    assert result == ("carer", subject_id)


def test_url_token_cannot_be_used_as_reset_token() -> None:
    """Salt-Separation gegen ``auth_anonymous.tokens``.

    Ein für eine Operation signierter URL-Token darf NICHT als Reset-Token
    akzeptiert werden, auch wenn das Secret identisch ist (Detail-Plan-
    Frage 4-A aus 2.3).
    """
    operation_id = uuid.uuid4()
    url_token = generate_url_token(operation_id, SECRET)
    # Gleicher Secret, aber anderer Salt — Verify muss None liefern.
    assert verify_reset_token(url_token, SECRET) is None


def test_salt_constant_is_distinct_from_url_token_salt() -> None:
    """Statisch sichergestellt: Reset-Token-Salt ≠ URL-Token-Salt."""
    assert RESET_TOKEN_SALT != URL_TOKEN_SALT


@pytest.mark.parametrize("kind", ["dispatcher", "carer"])
def test_kind_round_trip(kind: str) -> None:
    subject_id = uuid.uuid4()
    token = generate_reset_token(kind, subject_id, SECRET)  # type: ignore[arg-type]
    result = verify_reset_token(token, SECRET)
    assert result is not None
    assert result[0] == kind


def test_default_ttl_is_24_hours() -> None:
    assert DEFAULT_TTL_SECONDS == 24 * 60 * 60
