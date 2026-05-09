"""Passwort-Hashing-Helper für ``backend/auth``.

Argon2id ist die einzige zulässige Hashing-Variante (``project-context.md``
Abschnitt 6 Sicherheit, ADR-002). Die argon2-cffi-Maintainer pflegen die
Default-Parameter aktiv gegen das aktuelle OWASP-Profil — abweichende
Tunings erfordern einen ADR (Threat-Modelling-Review).

Die Mindest-Passwortlänge entspricht ``project-context.md`` Abschnitt 6:
12 Zeichen, kein Maximum, keine künstlichen Komplexitätsregeln.
"""

from __future__ import annotations

from typing import Final

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

PASSWORD_MIN_LENGTH: Final[int] = 12

_hasher: Final[PasswordHasher] = PasswordHasher()


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


__all__ = [
    "PASSWORD_MIN_LENGTH",
    "hash_password",
    "needs_rehash",
    "verify_password",
]
