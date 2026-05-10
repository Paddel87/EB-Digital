"""AccessCode-Generator und -Verifier (ADR-005, Regel-006).

**Format:** Sechs Zeichen aus dem kanonischen Crockford-Base32-Alphabet
``0-9`` plus ``A-Z`` ohne die verwechselbaren Zeichen ``I/L/O/U`` — also
``0123456789ABCDEFGHJKMNPQRSTVWXYZ`` (32 Symbole, 32**6 ≈ 1.07 Mrd.
Möglichkeiten, ausreichend Brute-Force-Reserve).

**Hinweis zur ADR-005-Wortlaut-Diskrepanz:** ADR-005 spricht von „Crockford-
Base32 ohne O/0/I/1/L" — diese parenthetische Glosse ist sprachlich ungenau
(klassisches Crockford-Base32 lässt 0 und 1 zu und schließt I/L/O/U aus). Die
maßgebliche Spec ist der ADR-Name selbst („Crockford-Base32") und die regex-
präzise Festlegung in ``architecture.md`` Abschnitt 4 Schnittstelle S2
(``^[0-9A-HJ-KM-NP-TV-Z]{6}$``). Diese Implementierung folgt der Schnittstellen-
Spec.

**Hashing-Disziplin (Regel-006):**
  • Klartext-Codes erscheinen weder in DB, Logs noch Fehlermeldungen.
  • ``hash_access_code`` produziert einen Argon2id-PHC-Hash mit
    library-Default-Parametern (gleiches Profil wie ``auth/hashing``).
  • ``verify_access_code`` ist Konstantzeit-Vergleich.
  • ``verify_dummy_access_code`` deckt den „kein Code aktiviert" /
    „operation hat keinen Hash"-Pfad ab, damit die Antwortzeit nicht
    verrät, ob ein Code überhaupt existiert.
"""

from __future__ import annotations

import contextlib
import re
import secrets
from typing import Final

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

ACCESS_CODE_LENGTH: Final[int] = 6
ACCESS_CODE_ALPHABET: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
ACCESS_CODE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[0-9A-HJ-KM-NP-TV-Z]{6}$")

_hasher: Final[PasswordHasher] = PasswordHasher()

# Modul-Ladezeit-Aufwand ca. 50 ms — einmalig. Wird in ``verify_dummy_access_code``
# benutzt, um den Argon2-Verify-Aufwand bei „kein Hash zu prüfen"-Pfaden zu
# simulieren (Timing-Schutz).
_DUMMY_HASH: Final[str] = _hasher.hash("dummy-not-a-real-access-code")  # nosec B106


def generate_access_code() -> str:
    """Erzeuge einen 6-Zeichen-Crockford-Base32-Code via CSPRNG.

    ``secrets.choice`` ist kryptographisch stark; jeder Aufruf liefert
    unabhängige Werte.
    """
    return "".join(secrets.choice(ACCESS_CODE_ALPHABET) for _ in range(ACCESS_CODE_LENGTH))


def hash_access_code(code: str) -> str:
    """Argon2id-PHC-Hash des Codes.

    Salt wird argon2-cffi-intern erzeugt; identische Codes erzeugen
    unterschiedliche Hashes (verhindert Hash-Reuse-Erkennung).
    """
    return _hasher.hash(code)


def verify_access_code(stored_hash: str, code: str) -> bool:
    """Konstantzeit-Vergleich.

    Liefert ``False`` bei kaputtem Hash, Mismatch oder anderen Argon2-
    Verifikations-Fehlern; andere Exceptions propagieren.
    """
    try:
        return _hasher.verify(stored_hash, code)
    except (VerifyMismatchError, InvalidHash):
        return False


def verify_dummy_access_code(code: str) -> bool:
    """Liefert immer ``False`` — gleicher CPU-Aufwand wie ``verify_access_code``.

    Im ``POST /session``-Pfad nach Lookup einer Operation **ohne** Hash
    (``access_code_hash IS NULL``) bzw. bei sonstigen Pfaden, die ohne
    Argon2-Verify zu 401 führen würden. Verhindert Timing-Hinweise auf den
    Operation-Hash-Zustand.
    """
    with contextlib.suppress(VerifyMismatchError, InvalidHash):
        _hasher.verify(_DUMMY_HASH, code)
    return False


__all__ = [
    "ACCESS_CODE_ALPHABET",
    "ACCESS_CODE_LENGTH",
    "ACCESS_CODE_PATTERN",
    "generate_access_code",
    "hash_access_code",
    "verify_access_code",
    "verify_dummy_access_code",
]
