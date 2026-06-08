"""Tests für ``eb_digital.realtime.redaction`` (Schritt 4.4-5A)."""

from __future__ import annotations

from eb_digital.realtime.redaction import TILE_ZOOM, tile_hash


def test_tile_hash_is_deterministic() -> None:
    assert tile_hash(53.0758, 8.8072) == tile_hash(53.0758, 8.8072)


def test_tile_hash_has_expected_shape() -> None:
    value = tile_hash(53.0758, 8.8072)
    assert value.startswith(f"tile:{TILE_ZOOM}:")
    assert len(value.rsplit(":", 1)[1]) == 16


def test_nearby_coordinates_collapse_to_same_tile() -> None:
    # Zwei sehr nahe Punkte (wenige Meter) landen in derselben Kachel.
    assert tile_hash(53.07580, 8.80720) == tile_hash(53.07581, 8.80721)


def test_distant_coordinates_differ() -> None:
    assert tile_hash(53.0758, 8.8072) != tile_hash(48.1372, 11.5755)


def test_tile_hash_clamps_extreme_latitude() -> None:
    # Pol-nahe Koordinaten dürfen nicht in eine Exception laufen.
    assert tile_hash(89.999999, 0.0).startswith("tile:")
    assert tile_hash(-89.999999, 0.0).startswith("tile:")
