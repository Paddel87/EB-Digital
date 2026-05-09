"""Tests for the Argon2id password-hashing helper (Schritt 1.6)."""

from __future__ import annotations

from eb_digital.auth.hashing import (
    PASSWORD_MIN_LENGTH,
    hash_password,
    needs_rehash,
    verify_password,
)


def test_password_min_length_matches_project_constraint() -> None:
    # project-context.md Abschnitt 6 Sicherheit: minimum 12 Zeichen.
    assert PASSWORD_MIN_LENGTH == 12


def test_hash_password_returns_phc_argon2id_string() -> None:
    digest = hash_password("correcthorsebattery")
    # PHC Modular Crypt Format with the argon2id algorithm marker.
    assert digest.startswith("$argon2id$")


def test_hash_password_uses_per_call_salt() -> None:
    a = hash_password("correcthorsebattery")
    b = hash_password("correcthorsebattery")
    assert a != b, "Each call must produce a different salt → different hash."


def test_verify_password_accepts_correct_password() -> None:
    digest = hash_password("correcthorsebattery")
    assert verify_password(digest, "correcthorsebattery") is True


def test_verify_password_rejects_wrong_password() -> None:
    digest = hash_password("correcthorsebattery")
    assert verify_password(digest, "wrong-password") is False


def test_verify_password_rejects_invalid_hash_input() -> None:
    # An obviously malformed hash must not raise — it must return False so
    # callers can treat it as a normal authentication failure.
    assert verify_password("not-a-valid-argon2-hash", "anything") is False


def test_needs_rehash_returns_false_for_freshly_hashed_password() -> None:
    digest = hash_password("correcthorsebattery")
    assert needs_rehash(digest) is False
