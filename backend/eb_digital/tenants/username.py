"""Username-Validierung für Dispatcher-/Carer-Onboarding.

Username-Regeln (lockerer als Slug, weil Username Tenant-scoped ist —
keine globalen Konflikt-Vektoren):
  • 3-32 Zeichen
  • ``[a-zA-Z0-9_.-]+``
  • Beginnt und endet mit Alphanum (kein führender/abschließender ``_.-``)
  • Keine Reserved-Liste — ``admin`` als Username ist erlaubt, weil er pro
    Mandant unique ist und sich nicht mit einem Routing-Pfad überlappt.
"""

from __future__ import annotations

import re
from typing import Final

USERNAME_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{1,30}[a-zA-Z0-9]$",
)


class UsernameValidationError(ValueError):
    """Username entspricht nicht den Format-Regeln."""


def validate_username(value: str) -> None:
    """Validiert einen Username, raised ``UsernameValidationError`` bei Verstoß."""
    if not isinstance(value, str):
        msg = "Username muss ein String sein."
        raise UsernameValidationError(msg)
    if not USERNAME_PATTERN.fullmatch(value):
        msg = (
            f"Username {value!r} entspricht nicht dem Pattern "
            "^[a-zA-Z0-9][a-zA-Z0-9_.-]{1,30}[a-zA-Z0-9]$ (3-32 Zeichen, "
            "beginnt/endet mit Alphanum, dazwischen optional ``_.-``)."
        )
        raise UsernameValidationError(msg)


__all__ = [
    "USERNAME_PATTERN",
    "UsernameValidationError",
    "validate_username",
]
