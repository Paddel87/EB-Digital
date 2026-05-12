"""Tests für ``backend/eb_digital/tenants/username``."""

from __future__ import annotations

import pytest

from eb_digital.tenants.username import (
    USERNAME_PATTERN,
    UsernameValidationError,
    validate_username,
)


@pytest.mark.parametrize(
    "username",
    [
        "abc",  # 3 Zeichen Minimum
        "alice",
        "Alice",  # Großbuchstaben erlaubt
        "alice.dev",
        "alice_99",
        "alice-99",
        "Alice.Dev_99",
        "x" * 32,  # 32 Zeichen Maximum
    ],
)
def test_valid_username_passes(username: str) -> None:
    validate_username(username)


@pytest.mark.parametrize(
    "username",
    [
        "ab",  # zu kurz
        "x" * 33,  # zu lang
        "alice!",  # Sonderzeichen
        "alice space",  # Leerzeichen
        "_alice",  # führender Underscore
        ".alice",  # führender Punkt
        "alice.",  # abschließender Punkt
        "alice-",  # abschließender Bindestrich
        "alice/dev",  # Slash
        "alice@example",  # @
    ],
)
def test_invalid_username_raises(username: str) -> None:
    with pytest.raises(UsernameValidationError):
        validate_username(username)


def test_non_string_raises() -> None:
    with pytest.raises(UsernameValidationError):
        validate_username(123)  # type: ignore[arg-type]


def test_pattern_constant_is_compiled_regex() -> None:
    assert USERNAME_PATTERN.fullmatch("alice")
    assert not USERNAME_PATTERN.fullmatch("a")  # too short
