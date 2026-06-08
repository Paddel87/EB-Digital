"""Standort-Redaction für den Realtime-Log-Pfad (Detail-Plan 4.4-5A).

``project-context.md`` §6 (Datenschutz): „Standortdaten in Logs nur als
gehashter Tile-Identifier, nie als Roh-Koordinate." Dieser Helper wandelt
ein Roh-Koordinaten-Paar in einen stabilen, nicht umkehrbaren Tile-Hash um,
der grobe Lokalitäts-Korrelation in Logs erlaubt, ohne die exakte Position
preiszugeben.

GPS-Push selbst (Betreuer-PWA) wird erst in Phase 6 produktiv; der Helper
wird hier bereits angelegt und getestet, damit der Logging-Vertrag des
Moduls von Anfang an steht.
"""

from __future__ import annotations

import hashlib
import math
from typing import Final

# Slippy-Map-Zoom-Stufe für die Tile-Quantisierung. Zoom 14 ≈ 2,4 km Kachel-
# Kantenlänge in mittleren Breiten — grob genug, um keine personenbezogene
# Position zu rekonstruieren, fein genug für Lage-Korrelation in Logs.
TILE_ZOOM: Final[int] = 14


def _tile_xy(lat: float, lng: float, zoom: int) -> tuple[int, int]:
    """Web-Mercator-Slippy-Map-Kachelindex für ``(lat, lng)`` bei ``zoom``."""
    lat_clamped = max(min(lat, 89.9999), -89.9999)
    lat_rad = math.radians(lat_clamped)
    n = 2**zoom
    x = int((lng + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    x = max(0, min(x, n - 1))
    y = max(0, min(y, n - 1))
    return x, y


def tile_hash(lat: float, lng: float, *, zoom: int = TILE_ZOOM) -> str:
    """Nicht umkehrbarer Tile-Identifier-Hash für ein Koordinaten-Paar.

    Zwei Koordinaten in derselben Kachel ergeben denselben Hash; die exakte
    Position ist aus dem Hash nicht rekonstruierbar. Format:
    ``tile:{zoom}:{sha256[:16]}``.
    """
    x, y = _tile_xy(lat, lng, zoom)
    digest = hashlib.sha256(f"{zoom}/{x}/{y}".encode()).hexdigest()
    return f"tile:{zoom}:{digest[:16]}"


__all__ = ["TILE_ZOOM", "tile_hash"]
