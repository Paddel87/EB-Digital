"""Plausibilitäts-Algorithmus (ADR-017).

Hülle-Distanz + dynamische GPS-Toleranz ``2·accuracy_m`` mit dreistufiger
Konfigurations-Hierarchie:

1. **Plattform-Konstanten** (in dieser Datei): Accuracy-Cutoff
   ``ACCURACY_TOO_LOW_M = 500`` (Bestellungen mit größerer Ungenauigkeit
   landen automatisch in Moderation), Min/Max-Threshold-Range
   ``THRESHOLD_MIN_M = 50`` / ``THRESHOLD_MAX_M = 50000``.
2. **Tenant-Default** (``tenant.plausibility_default_threshold_m``): 5 000 m.
3. **Operation-Override** (``operation.plausibility_threshold_m``): optional.

Outcome (ADR-017):

* ``ACCEPTED`` — GPS vorhanden, Hülle-Distanz ≤ Toleranz + Schwellenwert.
* ``MODERATION_NO_GPS`` — kein GPS, nur Text-Standort.
* ``MODERATION_ACCURACY_TOO_LOW`` — accuracy > 500 m (Cell-Tower-only-
  Locating).
* ``MODERATION_OUT_OF_RANGE`` — GPS vorhanden, aber Hülle-Distanz > Toleranz
  + Schwellenwert.

Geometrie-Berechnung über Shapely 2.x (ADR-020 — GEOS LGPL-Ausnahme).
Hülle-Distanz heißt: Punkt liegt **außerhalb** des Polygons → kürzester
Abstand zur Polygon-Hülle; **innerhalb** → 0. Das bildet das real beobachtete
Verhalten ab (eine Person am Rand eines länglichen Einsatzraums ist
plausibel, eine im Mittelpunkt aber 750 m außerhalb der Hülle nicht — siehe
Spike-I-Test-Datensatz Osterdeich).

Algorithmus läuft synchron in O(N·K) (N = Polygon-Vertices, K = Anzahl
Areas). Für Phase 1 (wenige Areas pro Einsatz, kleine Polygone) ist das
unproblematisch (<1 ms typisch). Bounding-Box-Pre-Filter ist nicht nötig.

Audit-relevante Felder im Ergebnis: ``outcome``, ``distance_m`` (None bei
NO_GPS / ACCURACY_TOO_LOW), ``threshold_m`` (wirksamer Wert nach Hierarchie-
Auflösung), ``variant`` (Algorithmus-Label, aktuell nur
``dynamic_2_accuracy``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, cast

from shapely.geometry import Point, Polygon

# Plattform-Konstanten (ADR-017). Erste Stufe der Konfigurations-Hierarchie.
# Bestellungen mit accuracy > 500 m werden automatisch moderiert
# (Cell-Tower-only-Locating, Werte sind operativ nicht belastbar).
ACCURACY_TOO_LOW_M: Final[float] = 500.0
# Range, in dem sich Tenant-Defaults und Operation-Overrides bewegen dürfen.
# DB-CHECK-Constraints in tenant/operation spiegeln diese Werte.
THRESHOLD_MIN_M: Final[int] = 50
THRESHOLD_MAX_M: Final[int] = 50_000
# Multiplikator für GPS-Toleranz (ADR-017): ``2·accuracy`` ≈ 95 %-Konfidenz
# unter Annahme accuracy = 1-Sigma-Radius.
ACCURACY_TOLERANCE_MULTIPLIER: Final[float] = 2.0

# Algorithmus-Label für Audit-Spur. Wird identisch in
# ``CustomerOrder.plausibility_variant`` persistiert.
PLAUSIBILITY_VARIANT: Final[str] = "dynamic_2_accuracy"

# Outcome-Strings (identisch zu Konstanten in ``operations.models``).
OUTCOME_ACCEPTED: Final[str] = "ACCEPTED"
OUTCOME_MODERATION_NO_GPS: Final[str] = "MODERATION_NO_GPS"
OUTCOME_MODERATION_ACCURACY_TOO_LOW: Final[str] = "MODERATION_ACCURACY_TOO_LOW"
OUTCOME_MODERATION_OUT_OF_RANGE: Final[str] = "MODERATION_OUT_OF_RANGE"


@dataclass(frozen=True, slots=True)
class OrderLocation:
    """Eingabe-Standort einer Order.

    ``lat`` + ``lng`` müssen gemeinsam vorhanden oder gemeinsam ``None``
    sein (DB-CHECK ``location_lat_lng_both_or_none`` durchgesetzt; im
    App-Layer hier als Vorbedingung). ``accuracy_m`` ist nur sinnvoll,
    wenn GPS vorhanden ist; bei reinem Text-Standort ist sie ``None``.
    """

    lat: float | None
    lng: float | None
    accuracy_m: float | None
    text: str | None


@dataclass(frozen=True, slots=True)
class PlausibilityThresholds:
    """Aufgelöste Konfigurations-Hierarchie für einen Einsatz.

    ``effective_threshold_m`` ist der wirksame Schwellenwert, der bereits
    aus Plattform-Konstanten, Tenant-Default und ggf. Operation-Override
    abgeleitet wurde — der Algorithmus nutzt nur diesen einen Wert.
    """

    effective_threshold_m: int


@dataclass(frozen=True, slots=True)
class PlausibilityResult:
    """Resultat des Plausibilitäts-Checks (ADR-017-Audit-Felder).

    ``distance_m`` ist die Hülle-Distanz in Metern, gerundet auf 1 m;
    ``None`` bei Outcomes ohne sinnvolle Distanz (NO_GPS, ACCURACY_TOO_LOW).
    ``threshold_m`` ist der wirksame Schwellenwert. ``variant`` ist das
    Algorithmus-Label für künftige A/B-Vergleiche im Audit-Log.
    """

    outcome: str
    distance_m: float | None
    threshold_m: int
    variant: str

    @property
    def accepted(self) -> bool:
        return self.outcome == OUTCOME_ACCEPTED


def resolve_threshold(
    *,
    tenant_default_m: int,
    operation_override_m: int | None,
) -> PlausibilityThresholds:
    """Löst die dreistufige Hierarchie zu einem effektiven Wert auf.

    Operation-Override (falls vorhanden) schlägt Tenant-Default. Plattform-
    Min/Max-Constraint wird hier defensiv noch einmal angewendet (auch wenn
    DB-CHECKs das Schema-seitig garantieren), damit Algorithmus-Eingaben
    immer im erwarteten Bereich liegen.
    """
    chosen = operation_override_m if operation_override_m is not None else tenant_default_m
    # Defense-in-Depth gegen Eingangs-Fehlkonfiguration.
    clamped = max(THRESHOLD_MIN_M, min(THRESHOLD_MAX_M, chosen))
    return PlausibilityThresholds(effective_threshold_m=clamped)


def _hull_distance_meters(
    *,
    lat: float,
    lng: float,
    polygon_geojson: dict[str, Any],
) -> float:
    """Hülle-Distanz Punkt ⇄ Polygon in Metern (approximierte Web-Mercator-Skala).

    Wir berechnen die Distanz im **lokalen ENU-Approximations-Modell**: in
    Grad bei dem gegebenen Breitengrad entspricht 1° Breite ≈ 111 320 m,
    1° Länge ≈ 111 320 m · cos(lat). Für Distanzen unter 50 km und
    Polygone in derselben Größenordnung ist der Fehler vernachlässigbar
    (< 0,5 %). Bremen liegt bei 53° N → cos ≈ 0,602; die App-Layer-Distanz
    bleibt ausreichend genau für Plausibility-Schwellen ab 50 m.

    GeoJSON-Polygon ist orientiert ``[lng, lat]``-Paare; wir konvertieren
    in lokale Meter-Koordinaten, bauen ein Shapely-Polygon und nutzen
    ``polygon.distance(point)``.
    """
    from math import cos, radians

    # Lokale Meter-Skala um den Punkt.
    meters_per_degree_lat = 111_320.0
    meters_per_degree_lng = 111_320.0 * cos(radians(lat))

    coords = polygon_geojson["coordinates"][0]
    poly_xy = [
        (
            (pt[0] - lng) * meters_per_degree_lng,
            (pt[1] - lat) * meters_per_degree_lat,
        )
        for pt in coords
    ]
    polygon = Polygon(poly_xy)
    point = Point(0.0, 0.0)
    # Shapely ``distance`` liefert 0, wenn der Punkt innerhalb (oder auf
    # der Hülle) ist; sonst die kürzeste euklidische Distanz zur Hülle.
    return float(polygon.distance(point))


def check_plausibility(
    *,
    location: OrderLocation,
    polygons_geojson: list[dict[str, Any]],
    thresholds: PlausibilityThresholds,
) -> PlausibilityResult:
    """Wertet den Plausibilitäts-Algorithmus aus (ADR-017).

    ``polygons_geojson`` ist die Liste aller ``OperationArea.polygon``-
    Werte für die Operation. Distanz wird zu **dem nächstgelegenen
    Polygon** gemessen; das ist sinnvoll, weil eine Bestellung von einer
    beliebigen Stelle in einem beliebigen Einsatzraum legitim ist.

    Reihenfolge der Checks (so steht es in ADR-017 / Spike-I-Spec):

    1. Kein GPS und Text-Standort → ``MODERATION_NO_GPS``.
    2. accuracy nicht plausibel (None oder > 500 m) → ``MODERATION_ACCURACY_TOO_LOW``.
    3. Hülle-Distanz > (Schwellenwert + 2·accuracy) → ``MODERATION_OUT_OF_RANGE``.
    4. sonst → ``ACCEPTED``.
    """
    threshold_m = thresholds.effective_threshold_m
    variant = PLAUSIBILITY_VARIANT

    has_gps = location.lat is not None and location.lng is not None
    if not has_gps:
        return PlausibilityResult(
            outcome=OUTCOME_MODERATION_NO_GPS,
            distance_m=None,
            threshold_m=threshold_m,
            variant=variant,
        )

    accuracy = location.accuracy_m
    if accuracy is None or accuracy > ACCURACY_TOO_LOW_M:
        return PlausibilityResult(
            outcome=OUTCOME_MODERATION_ACCURACY_TOO_LOW,
            distance_m=None,
            threshold_m=threshold_m,
            variant=variant,
        )

    # mypy: nach ``has_gps``-Check sind lat/lng garantiert nicht None —
    # aber der Checker sieht das nicht. Wir greifen die Werte einmalig
    # ab und casten — kein ``assert`` (bandit B101) nötig.
    lat = cast(float, location.lat)
    lng = cast(float, location.lng)

    if not polygons_geojson:
        # Defensiv: ohne Areas keine sinnvolle Hülle. Wir behandeln das wie
        # einen Out-of-Range-Fall, weil keine zulässige Aufenthaltsregion
        # definiert ist. Operativ sollte das nicht passieren — Operation
        # wird mit mindestens einer Area eröffnet — aber Defense-in-Depth.
        return PlausibilityResult(
            outcome=OUTCOME_MODERATION_OUT_OF_RANGE,
            distance_m=None,
            threshold_m=threshold_m,
            variant=variant,
        )

    nearest_distance_m = min(
        _hull_distance_meters(
            lat=lat,
            lng=lng,
            polygon_geojson=poly,
        )
        for poly in polygons_geojson
    )
    tolerance_m = ACCURACY_TOLERANCE_MULTIPLIER * accuracy
    if nearest_distance_m > threshold_m + tolerance_m:
        return PlausibilityResult(
            outcome=OUTCOME_MODERATION_OUT_OF_RANGE,
            distance_m=round(nearest_distance_m, 1),
            threshold_m=threshold_m,
            variant=variant,
        )
    return PlausibilityResult(
        outcome=OUTCOME_ACCEPTED,
        distance_m=round(nearest_distance_m, 1),
        threshold_m=threshold_m,
        variant=variant,
    )


__all__ = [
    "ACCURACY_TOLERANCE_MULTIPLIER",
    "ACCURACY_TOO_LOW_M",
    "OUTCOME_ACCEPTED",
    "OUTCOME_MODERATION_ACCURACY_TOO_LOW",
    "OUTCOME_MODERATION_NO_GPS",
    "OUTCOME_MODERATION_OUT_OF_RANGE",
    "PLAUSIBILITY_VARIANT",
    "THRESHOLD_MAX_M",
    "THRESHOLD_MIN_M",
    "OrderLocation",
    "PlausibilityResult",
    "PlausibilityThresholds",
    "check_plausibility",
    "resolve_threshold",
]
