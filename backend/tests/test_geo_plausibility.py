"""Tests für ``backend/geo.plausibility`` (ADR-017).

Spike-I-Testdatensatz (Spike-I-Spec, ``docs/spikes/spike-i-results.md``)
mit Bremen Innenstadt (kompaktes Polygon) und Osterdeich (länglicher Polygon,
1500 m x 200 m). Die Distanz-Berechnung läuft im lokalen ENU-Approximations-
Modell — Fehler < 0.5 % für die hier geprüften Distanzen.

Per-Test-Coverage-Ziel: ≥ 90 % Lines auf ``backend/eb_digital/geo/plausibility``.
"""

from __future__ import annotations

import pytest

from eb_digital.geo.plausibility import (
    ACCURACY_TOO_LOW_M,
    OUTCOME_ACCEPTED,
    OUTCOME_MODERATION_ACCURACY_TOO_LOW,
    OUTCOME_MODERATION_NO_GPS,
    OUTCOME_MODERATION_OUT_OF_RANGE,
    PLAUSIBILITY_VARIANT,
    THRESHOLD_MAX_M,
    THRESHOLD_MIN_M,
    OrderLocation,
    PlausibilityThresholds,
    check_plausibility,
    resolve_threshold,
)

# ─── Test-Polygone ─────────────────────────────────────────────────────────


def _square(lat: float, lng: float, half_size_deg: float = 0.001) -> dict[str, object]:
    """Quadrat mit Mittelpunkt (lat, lng). 0.001° lat ≈ 111 m."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [lng - half_size_deg, lat - half_size_deg],
                [lng + half_size_deg, lat - half_size_deg],
                [lng + half_size_deg, lat + half_size_deg],
                [lng - half_size_deg, lat + half_size_deg],
                [lng - half_size_deg, lat - half_size_deg],
            ]
        ],
    }


BREMEN_INNENSTADT_CENTER_LAT = 53.0793
BREMEN_INNENSTADT_CENTER_LNG = 8.8017
BREMEN_INNENSTADT = _square(BREMEN_INNENSTADT_CENTER_LAT, BREMEN_INNENSTADT_CENTER_LNG)

# Länglicher Osterdeich ≈ 1.5 km x 0.2 km Ost-West-orientiert.
OSTERDEICH_LAT = 53.0697
OSTERDEICH_LNG = 8.8205
OSTERDEICH = {
    "type": "Polygon",
    "coordinates": [
        [
            [OSTERDEICH_LNG - 0.0125, OSTERDEICH_LAT - 0.0009],
            [OSTERDEICH_LNG + 0.0125, OSTERDEICH_LAT - 0.0009],
            [OSTERDEICH_LNG + 0.0125, OSTERDEICH_LAT + 0.0009],
            [OSTERDEICH_LNG - 0.0125, OSTERDEICH_LAT + 0.0009],
            [OSTERDEICH_LNG - 0.0125, OSTERDEICH_LAT - 0.0009],
        ]
    ],
}


DEFAULT_THRESHOLDS = PlausibilityThresholds(effective_threshold_m=500)


# ─── resolve_threshold ─────────────────────────────────────────────────────


def test_resolve_threshold_uses_tenant_default_when_no_override() -> None:
    out = resolve_threshold(tenant_default_m=3000, operation_override_m=None)
    assert out.effective_threshold_m == 3000


def test_resolve_threshold_uses_operation_override_when_present() -> None:
    out = resolve_threshold(tenant_default_m=3000, operation_override_m=750)
    assert out.effective_threshold_m == 750


def test_resolve_threshold_clamps_to_platform_min() -> None:
    out = resolve_threshold(tenant_default_m=10, operation_override_m=None)
    assert out.effective_threshold_m == THRESHOLD_MIN_M


def test_resolve_threshold_clamps_to_platform_max() -> None:
    out = resolve_threshold(tenant_default_m=999_999, operation_override_m=None)
    assert out.effective_threshold_m == THRESHOLD_MAX_M


# ─── Outcome-Pfad NO_GPS ───────────────────────────────────────────────────


def test_no_gps_returns_moderation_no_gps() -> None:
    location = OrderLocation(lat=None, lng=None, accuracy_m=None, text="Hauptmarkt")
    result = check_plausibility(
        location=location, polygons_geojson=[BREMEN_INNENSTADT], thresholds=DEFAULT_THRESHOLDS
    )
    assert result.outcome == OUTCOME_MODERATION_NO_GPS
    assert result.distance_m is None
    assert result.threshold_m == 500
    assert result.variant == PLAUSIBILITY_VARIANT
    assert result.accepted is False


# ─── Outcome-Pfad ACCURACY_TOO_LOW ─────────────────────────────────────────


def test_accuracy_above_cutoff_returns_moderation_accuracy_too_low() -> None:
    location = OrderLocation(
        lat=BREMEN_INNENSTADT_CENTER_LAT,
        lng=BREMEN_INNENSTADT_CENTER_LNG,
        accuracy_m=ACCURACY_TOO_LOW_M + 1.0,
        text=None,
    )
    result = check_plausibility(
        location=location, polygons_geojson=[BREMEN_INNENSTADT], thresholds=DEFAULT_THRESHOLDS
    )
    assert result.outcome == OUTCOME_MODERATION_ACCURACY_TOO_LOW
    assert result.distance_m is None


def test_accuracy_none_returns_moderation_accuracy_too_low() -> None:
    location = OrderLocation(
        lat=BREMEN_INNENSTADT_CENTER_LAT,
        lng=BREMEN_INNENSTADT_CENTER_LNG,
        accuracy_m=None,
        text=None,
    )
    result = check_plausibility(
        location=location, polygons_geojson=[BREMEN_INNENSTADT], thresholds=DEFAULT_THRESHOLDS
    )
    assert result.outcome == OUTCOME_MODERATION_ACCURACY_TOO_LOW


# ─── Outcome-Pfad ACCEPTED (innerhalb Polygon) ─────────────────────────────


def test_inside_polygon_is_accepted() -> None:
    location = OrderLocation(
        lat=BREMEN_INNENSTADT_CENTER_LAT,
        lng=BREMEN_INNENSTADT_CENTER_LNG,
        accuracy_m=10.0,
        text=None,
    )
    result = check_plausibility(
        location=location, polygons_geojson=[BREMEN_INNENSTADT], thresholds=DEFAULT_THRESHOLDS
    )
    assert result.outcome == OUTCOME_ACCEPTED
    assert result.distance_m == 0.0
    assert result.accepted is True


def test_just_outside_polygon_within_threshold_is_accepted() -> None:
    """Person 50 m außerhalb der Hülle mit gutem GPS — innerhalb Schwellenwert."""
    location = OrderLocation(
        lat=BREMEN_INNENSTADT_CENTER_LAT + 0.0014,  # ≈ 156 m nördlich des Centers
        lng=BREMEN_INNENSTADT_CENTER_LNG,
        accuracy_m=10.0,
        text=None,
    )
    result = check_plausibility(
        location=location, polygons_geojson=[BREMEN_INNENSTADT], thresholds=DEFAULT_THRESHOLDS
    )
    # Polygon ist 111 m hoch; Center ist Mitte; 156 m nördlich ≈ 45 m über die
    # Hülle. Mit accuracy=10 ist Toleranz=20. 45 m < 500 + 20 — accepted.
    assert result.outcome == OUTCOME_ACCEPTED


# ─── Outcome-Pfad OUT_OF_RANGE ─────────────────────────────────────────────


def test_far_outside_polygon_is_out_of_range() -> None:
    """Person 5 km nördlich — weit außerhalb Schwellenwert."""
    location = OrderLocation(
        lat=BREMEN_INNENSTADT_CENTER_LAT + 0.05,  # ≈ 5.5 km nördlich
        lng=BREMEN_INNENSTADT_CENTER_LNG,
        accuracy_m=10.0,
        text=None,
    )
    result = check_plausibility(
        location=location, polygons_geojson=[BREMEN_INNENSTADT], thresholds=DEFAULT_THRESHOLDS
    )
    assert result.outcome == OUTCOME_MODERATION_OUT_OF_RANGE
    assert result.distance_m is not None
    assert result.distance_m > 5000


# ─── Dynamische Toleranz ───────────────────────────────────────────────────


def test_borderline_accepted_with_loose_accuracy() -> None:
    """Person 200 m außerhalb mit accuracy=200 — Toleranz 400 m, accepted."""
    location = OrderLocation(
        lat=BREMEN_INNENSTADT_CENTER_LAT + 0.0028,  # ≈ 311 m über Center, ≈ 200 m über Hülle
        lng=BREMEN_INNENSTADT_CENTER_LNG,
        accuracy_m=200.0,
        text=None,
    )
    result = check_plausibility(
        location=location,
        polygons_geojson=[BREMEN_INNENSTADT],
        thresholds=PlausibilityThresholds(effective_threshold_m=50),
    )
    # ≈ 200 m außerhalb der Hülle, Toleranz 2*200 = 400, Schwelle 50 → 200 < 450
    assert result.outcome == OUTCOME_ACCEPTED


def test_strict_accuracy_rejects_what_loose_accepts() -> None:
    """Person 200 m außerhalb mit accuracy=5 (gutes GPS): Toleranz 10, Schwelle 50, out_of_range."""
    location = OrderLocation(
        lat=BREMEN_INNENSTADT_CENTER_LAT + 0.0028,
        lng=BREMEN_INNENSTADT_CENTER_LNG,
        accuracy_m=5.0,
        text=None,
    )
    result = check_plausibility(
        location=location,
        polygons_geojson=[BREMEN_INNENSTADT],
        thresholds=PlausibilityThresholds(effective_threshold_m=50),
    )
    assert result.outcome == OUTCOME_MODERATION_OUT_OF_RANGE


# ─── Mehrere Polygone — Minimum-Distanz ────────────────────────────────────


def test_nearest_polygon_wins() -> None:
    """Bei zwei Polygonen zählt das nähere; Innenstadt-Mitte ist 0 m im Innenstadt-Polygon."""
    location = OrderLocation(
        lat=BREMEN_INNENSTADT_CENTER_LAT,
        lng=BREMEN_INNENSTADT_CENTER_LNG,
        accuracy_m=10.0,
        text=None,
    )
    result = check_plausibility(
        location=location,
        polygons_geojson=[OSTERDEICH, BREMEN_INNENSTADT],
        thresholds=DEFAULT_THRESHOLDS,
    )
    assert result.outcome == OUTCOME_ACCEPTED
    assert result.distance_m == 0.0


# ─── Edge-Case: keine Polygone ─────────────────────────────────────────────


def test_no_polygons_is_out_of_range() -> None:
    location = OrderLocation(
        lat=BREMEN_INNENSTADT_CENTER_LAT,
        lng=BREMEN_INNENSTADT_CENTER_LNG,
        accuracy_m=10.0,
        text=None,
    )
    result = check_plausibility(
        location=location, polygons_geojson=[], thresholds=DEFAULT_THRESHOLDS
    )
    assert result.outcome == OUTCOME_MODERATION_OUT_OF_RANGE
    assert result.distance_m is None


# ─── Property: Variante und Threshold sind im Result ────────────────────────


@pytest.mark.parametrize(
    "outcome_check",
    [
        OUTCOME_ACCEPTED,
        OUTCOME_MODERATION_NO_GPS,
        OUTCOME_MODERATION_ACCURACY_TOO_LOW,
        OUTCOME_MODERATION_OUT_OF_RANGE,
    ],
)
def test_all_outcomes_carry_threshold_and_variant(outcome_check: str) -> None:
    """Trigger jeden Outcome-Pfad und verifiziere, dass threshold + variant
    konsistent gesetzt sind."""
    if outcome_check == OUTCOME_MODERATION_NO_GPS:
        location = OrderLocation(lat=None, lng=None, accuracy_m=None, text="x")
    elif outcome_check == OUTCOME_MODERATION_ACCURACY_TOO_LOW:
        location = OrderLocation(
            lat=BREMEN_INNENSTADT_CENTER_LAT,
            lng=BREMEN_INNENSTADT_CENTER_LNG,
            accuracy_m=ACCURACY_TOO_LOW_M + 1,
            text=None,
        )
    elif outcome_check == OUTCOME_MODERATION_OUT_OF_RANGE:
        location = OrderLocation(
            lat=BREMEN_INNENSTADT_CENTER_LAT + 0.5,
            lng=BREMEN_INNENSTADT_CENTER_LNG,
            accuracy_m=10.0,
            text=None,
        )
    else:  # ACCEPTED
        location = OrderLocation(
            lat=BREMEN_INNENSTADT_CENTER_LAT,
            lng=BREMEN_INNENSTADT_CENTER_LNG,
            accuracy_m=10.0,
            text=None,
        )
    result = check_plausibility(
        location=location, polygons_geojson=[BREMEN_INNENSTADT], thresholds=DEFAULT_THRESHOLDS
    )
    assert result.outcome == outcome_check
    assert result.threshold_m == 500
    assert result.variant == PLAUSIBILITY_VARIANT
