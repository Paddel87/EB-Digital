"""Tests for the Argon2id password-hashing helper (Schritt 1.6)."""

from __future__ import annotations

from eb_digital.auth.hashing import (
    PASSWORD_MIN_LENGTH,
    hash_password,
    needs_rehash,
    verify_dummy,
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


def test_verify_dummy_always_returns_false() -> None:
    # Garantiert ``False``, egal welches Passwort: die Funktion soll nur den
    # Hash-Vergleichs-Aufwand erzeugen, nicht authentifizieren.
    assert verify_dummy("any-password") is False
    assert verify_dummy("") is False
    assert verify_dummy("dummy-not-a-real-password") is False


def test_verify_dummy_consumes_comparable_time_to_real_verify() -> None:
    # Heuristik gegen Username-Enumeration-Timing-Attack: ``verify_dummy``
    # sollte in der gleichen Größenordnung liegen wie ein echter Verify.
    # 0.5x bis 2x ist tolerierbar — exakt gleich ist auf realer Hardware nicht
    # erreichbar, aber Faktoren > 2 würden die Schutzwirkung untergraben.
    import time

    digest = hash_password("correcthorsebattery")
    t0 = time.perf_counter()
    verify_password(digest, "wrong-password")
    real_duration = time.perf_counter() - t0

    t0 = time.perf_counter()
    verify_dummy("any-password")
    dummy_duration = time.perf_counter() - t0

    ratio = dummy_duration / real_duration
    assert 0.5 <= ratio <= 2.0, (
        f"verify_dummy timing diverges from verify_password by factor {ratio:.2f} "
        f"(real={real_duration * 1000:.1f}ms, dummy={dummy_duration * 1000:.1f}ms)"
    )
