"""Tests für ``backend/eb_digital/auth_anonymous/access_code``.

AccessCode-Erzeugung (Crockford-Base32) + Argon2id-Hash-Vergleich.
"""

from __future__ import annotations

from eb_digital.auth_anonymous.access_code import (
    ACCESS_CODE_ALPHABET,
    ACCESS_CODE_LENGTH,
    ACCESS_CODE_PATTERN,
    generate_access_code,
    hash_access_code,
    verify_access_code,
    verify_dummy_access_code,
)


def test_alphabet_matches_canonical_crockford_base32() -> None:
    """Alphabet ist 32 Zeichen, ohne I/L/O/U (architecture.md S2-Pattern)."""
    assert len(ACCESS_CODE_ALPHABET) == 32
    assert ACCESS_CODE_ALPHABET == "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    for char in "ILOU":
        assert char not in ACCESS_CODE_ALPHABET


def test_pattern_accepts_canonical_alphabet_only() -> None:
    assert ACCESS_CODE_PATTERN.fullmatch("X7K3PQ") is not None
    assert ACCESS_CODE_PATTERN.fullmatch("000000") is not None
    assert ACCESS_CODE_PATTERN.fullmatch("ZZZZZZ") is not None
    # Verbotene Zeichen.
    assert ACCESS_CODE_PATTERN.fullmatch("IIIIII") is None  # I excluded
    assert ACCESS_CODE_PATTERN.fullmatch("LLLLLL") is None  # L excluded
    assert ACCESS_CODE_PATTERN.fullmatch("OOOOOO") is None  # O excluded
    assert ACCESS_CODE_PATTERN.fullmatch("UUUUUU") is None  # U excluded
    # Falsche Länge.
    assert ACCESS_CODE_PATTERN.fullmatch("X7K3P") is None  # 5 Zeichen
    assert ACCESS_CODE_PATTERN.fullmatch("X7K3PQR") is None  # 7 Zeichen
    # Kleinbuchstaben (Pattern ist case-sensitive).
    assert ACCESS_CODE_PATTERN.fullmatch("x7k3pq") is None


def test_generate_returns_code_of_correct_length() -> None:
    code = generate_access_code()
    assert len(code) == ACCESS_CODE_LENGTH
    assert ACCESS_CODE_PATTERN.fullmatch(code) is not None


def test_generate_only_uses_alphabet_chars() -> None:
    alphabet = set(ACCESS_CODE_ALPHABET)
    for _ in range(50):
        code = generate_access_code()
        assert set(code).issubset(alphabet)


def test_generate_has_enough_entropy_to_avoid_immediate_collision() -> None:
    """100 Codes → keine Kollision erwartet (32**6 ≈ 1 Mrd. Möglichkeiten,
    Geburtstags-Wahrscheinlichkeit für 100 Samples vernachlässigbar)."""
    codes = {generate_access_code() for _ in range(100)}
    assert len(codes) == 100


def test_hash_roundtrip_validates_correct_code() -> None:
    code = generate_access_code()
    hashed = hash_access_code(code)
    assert hashed.startswith("$argon2id$")
    assert verify_access_code(hashed, code) is True


def test_hash_rejects_wrong_code() -> None:
    code = generate_access_code()
    hashed = hash_access_code(code)
    other = generate_access_code()
    # Selbst wenn zufällig identisch, andere Werte sollten nicht matchen.
    if other != code:
        assert verify_access_code(hashed, other) is False


def test_verify_rejects_invalid_hash_input() -> None:
    """Malformed hash → ``False``, kein Exception-Leak in den Endpoint."""
    assert verify_access_code("not-a-valid-argon2-hash", "X7K3PQ") is False


def test_two_hashes_of_same_code_differ_by_salt() -> None:
    code = "X7K3PQ"
    a = hash_access_code(code)
    b = hash_access_code(code)
    assert a != b


def test_verify_dummy_always_returns_false() -> None:
    assert verify_dummy_access_code("X7K3PQ") is False
    assert verify_dummy_access_code("") is False
    assert verify_dummy_access_code("dummy-not-a-real-access-code") is False


def test_verify_dummy_consumes_comparable_time_to_real_verify() -> None:
    """Heuristik gegen Timing-Leak — analog ``test_auth_hashing.py``."""
    import time

    code = generate_access_code()
    hashed = hash_access_code(code)

    t0 = time.perf_counter()
    verify_access_code(hashed, "WRONGW")
    real_duration = time.perf_counter() - t0

    t0 = time.perf_counter()
    verify_dummy_access_code("WRONGW")
    dummy_duration = time.perf_counter() - t0

    ratio = dummy_duration / real_duration
    assert 0.5 <= ratio <= 2.0, (
        f"verify_dummy timing diverges from verify_access_code by factor {ratio:.2f} "
        f"(real={real_duration * 1000:.1f}ms, dummy={dummy_duration * 1000:.1f}ms)"
    )
