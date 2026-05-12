"""Slug-Validierung für Mandanten-Self-Service-Antrag.

Der ``slug`` ist der URL-/CLI-taugliche Bezeichner eines Mandanten (z. B.
``dpolg-bremen``). Er wird vom Antragsteller im Self-Service-Antrag gewählt
(Detail-Plan-Frage 1-B aus 2.4): explizite Eingabe statt Auto-Sluggify, um
dem Verband Kontrolle über die URL-Darstellung zu geben.

Format-Regeln:
  • 3-64 Zeichen Länge
  • Beginnt und endet mit Alphanum (``a-z`` oder ``0-9``)
  • Dazwischen sind ``-`` erlaubt, aber kein doppeltes ``--``
  • Großbuchstaben, Umlaute, Sonderzeichen sind verboten

Reservierte Slugs sind technisch belegte Top-Level-Pfad-Anteile (``api``,
``auth``, ``admin``, …) — sie würden mit zukünftigen Routing-Erweiterungen
kollidieren. Die Liste ist konservativ; Abweichungen oder Erweiterungen sind
ADR-pflichtig.
"""

from __future__ import annotations

import re
from typing import Final

# Erlaubt: 3-64 Zeichen, beginnt/endet mit ``[a-z0-9]``, dazwischen
# ``[a-z0-9-]`` ohne Doppel-``-``. Lookahead ``(?!-)`` nach jedem ``-`` ist
# zu fehleranfällig — wir verwenden eine zweistufige Prüfung: erst Pattern,
# dann ``"--" not in value``.
SLUG_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")

# Top-Level-Pfade, die in ``api_router`` oder Caddy-Routing belegt sind oder
# in absehbarer Zukunft belegt werden. Verhindert, dass ein Mandanten-Slug
# wie ``api`` mit einem zukünftigen ``/api/api/...``-Routing kollidiert.
RESERVED_SLUGS: Final[frozenset[str]] = frozenset(
    {
        "admin",
        "api",
        "auth",
        "anon",
        "health",
        "static",
        "assets",
        "ws",
        "openapi",
        "docs",
        "redoc",
    }
)


class SlugValidationError(ValueError):
    """Slug entspricht nicht den Format-Regeln oder ist reserviert."""


def validate_slug(value: str) -> None:
    """Validiert einen Slug, raised ``SlugValidationError`` bei Verstoß.

    Liefert ``None`` bei Erfolg (Convention für reine Validierungs-Funktionen
    in diesem Repo). Aufrufer fangen ``SlugValidationError`` ab und mappen
    auf einen domain-spezifischen API-Status (422 in der Tenant-API).
    """
    if not isinstance(value, str):
        msg = "Slug muss ein String sein."
        raise SlugValidationError(msg)
    if "--" in value:
        msg = f"Slug enthält Doppel-Bindestrich: {value!r}"
        raise SlugValidationError(msg)
    if not SLUG_PATTERN.fullmatch(value):
        msg = (
            f"Slug {value!r} entspricht nicht dem Pattern "
            "^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$ (3-64 Zeichen, Lowercase, "
            "beginnt/endet mit Alphanum, dazwischen optional Bindestrich)."
        )
        raise SlugValidationError(msg)
    if value in RESERVED_SLUGS:
        msg = f"Slug {value!r} ist reserviert (siehe RESERVED_SLUGS)."
        raise SlugValidationError(msg)


__all__ = [
    "RESERVED_SLUGS",
    "SLUG_PATTERN",
    "SlugValidationError",
    "validate_slug",
]
