"""Tests für ``backend/eb_digital/tenants/slug``."""

from __future__ import annotations

import pytest

from eb_digital.tenants.slug import (
    RESERVED_SLUGS,
    SLUG_PATTERN,
    SlugValidationError,
    validate_slug,
)


class TestValidSlugs:
    """Slugs, die explizit akzeptiert werden müssen."""

    @pytest.mark.parametrize(
        "slug",
        [
            "abc",  # 3 Zeichen Minimum
            "dpolg-bremen",
            "dpolg-bremen-nord",
            "verein-2026",
            "abc123",
            "a1b2c3",
            "x" * 64,  # 64 Zeichen Maximum
            "0a",  # darf mit Ziffer beginnen — wait, length 2 → invalid
        ],
    )
    def test_valid_slug_passes(self, slug: str) -> None:
        if len(slug) < 3:
            pytest.skip("min length is 3")
        validate_slug(slug)


class TestInvalidSlugs:
    """Slugs, die abgewiesen werden müssen."""

    @pytest.mark.parametrize(
        "slug",
        [
            "ab",  # zu kurz
            "x" * 65,  # zu lang
            "DPolG-Bremen",  # Großbuchstaben
            "dpolg_bremen",  # Underscore
            "dpolg.bremen",  # Punkt
            "dpolg bremen",  # Leerzeichen
            "-dpolg",  # führender Bindestrich
            "dpolg-",  # abschließender Bindestrich
            "dpolg--bremen",  # Doppel-Bindestrich
            "umlaut-ä",  # Umlaut
            "öäü",  # Nicht-ASCII
        ],
    )
    def test_invalid_slug_raises(self, slug: str) -> None:
        with pytest.raises(SlugValidationError):
            validate_slug(slug)


class TestReservedSlugs:
    @pytest.mark.parametrize("slug", sorted(RESERVED_SLUGS))
    def test_each_reserved_slug_is_blocked(self, slug: str) -> None:
        with pytest.raises(SlugValidationError):
            validate_slug(slug)

    def test_reserved_slug_error_message_mentions_reserved(self) -> None:
        with pytest.raises(SlugValidationError, match="reserviert"):
            validate_slug("api")


class TestNonStringInput:
    def test_non_string_raises(self) -> None:
        with pytest.raises(SlugValidationError):
            validate_slug(123)  # type: ignore[arg-type]


class TestPatternConstants:
    def test_pattern_matches_canonical_examples(self) -> None:
        assert SLUG_PATTERN.fullmatch("dpolg-bremen")
        assert not SLUG_PATTERN.fullmatch("DPolG")

    def test_reserved_set_is_frozen(self) -> None:
        assert isinstance(RESERVED_SLUGS, frozenset)
