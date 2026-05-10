"""Passwort-Hashing-Helper für ``backend/auth``.

Argon2id ist die einzige zulässige Hashing-Variante (``project-context.md``
Abschnitt 6 Sicherheit, ADR-002). Die argon2-cffi-Maintainer pflegen die
Default-Parameter aktiv gegen das aktuelle OWASP-Profil — abweichende
Tunings erfordern einen ADR (Threat-Modelling-Review).

Die Mindest-Passwortlänge entspricht ``project-context.md`` Abschnitt 6:
12 Zeichen, kein Maximum, keine künstlichen Komplexitätsregeln.
"""

from __future__ import annotations

import contextlib
from typing import Final

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

PASSWORD_MIN_LENGTH: Final[int] = 12

_hasher: Final[PasswordHasher] = PasswordHasher()

# Vor-berechneter Argon2id-Hash für ``verify_dummy()`` (Timing-Attack-Schutz im
# Login-Pfad: nicht existierende Username sollen denselben CPU-Aufwand erzeugen
# wie echte Verifikationen). Modul-Ladezeit-Kosten: einmalig ~50 ms.
_DUMMY_HASH: Final[str] = _hasher.hash("dummy-not-a-real-password")  # nosec B106


def hash_password(password: str) -> str:
    """Argon2id-Hash im PHC-Format zurückgeben.

    Salt wird argon2-cffi-intern erzeugt; jede Aufrufung produziert einen
    anderen Hash, auch bei identischem Input.
    """
    return _hasher.hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
    """``True`` genau dann, wenn ``password`` zu ``stored_hash`` passt.

    ``VerifyMismatchError`` und ``InvalidHash`` werden zu ``False`` umgesetzt;
    alle anderen argon2-Fehler propagieren.
    """
    try:
        return _hasher.verify(stored_hash, password)
    except (VerifyMismatchError, InvalidHash):
        return False


def needs_rehash(stored_hash: str) -> bool:
    """``True``, wenn die Library aktuellere Default-Parameter hat als der Hash."""
    return _hasher.check_needs_rehash(stored_hash)


def verify_dummy(password: str) -> bool:
    """Liefert immer ``False`` — gleicher CPU-Aufwand wie ``verify_password``.

    Im Login-Pfad nach Lookup eines nicht existierenden Usernames aufrufen, um
    die Antwortzeit identisch zur realen Hash-Verifikation zu halten. Sonst
    könnten Angreifer aus einer schnellen 401-Antwort schließen, dass ein
    Username nicht existiert (Username-Enumeration).
    """
    with contextlib.suppress(VerifyMismatchError, InvalidHash):
        _hasher.verify(_DUMMY_HASH, password)
    return False


__all__ = [
    "PASSWORD_MIN_LENGTH",
    "hash_password",
    "needs_rehash",
    "verify_dummy",
    "verify_password",
]
