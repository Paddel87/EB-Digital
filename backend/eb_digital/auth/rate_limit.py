"""Valkey-basierter Rate-Limit-Counter (ADR-013).

Implementiert die in ``project-context.md`` Abschnitt 6 fixierte Login-Spec
„5 Fehlversuche pro 15 min pro IP-Adresse plus pro User getrennt" als
zwei gestapelte Counter mit AND-Logik: ein Login-Versuch ist nur dann
erlaubt, wenn beide Counter (IP- und User-Key) unter dem Schwellwert liegen.

**Counter-Reset-Disziplin:** Erfolgreicher Login löscht **nur** den
User-Counter, **nicht** den IP-Counter. Sonst wäre ein Brute-Force-Sweep
„1 falsches Passwort gegen 5 Usernames plus 1 richtiges Login = neuer
IP-Slot" möglich, der die IP-Begrenzung umgeht.

**Atomaritäts-Argument:** ``INCR`` ist atomar (Valkey single-threaded auf der
Command-Loop). ``EXPIRE`` ist eine separate Operation; ein theoretisches
Race-Window „Process A INCR auf neuen Key, Process B INCR auf denselben
Key, beide setzen EXPIRE" ist harmlos, weil EXPIRE idempotent dieselbe
TTL setzt. Ein Race-Window „INCR ohne EXPIRE" entsteht nur, wenn der
Process zwischen INCR und EXPIRE crasht — Folge: der Counter lebt ohne TTL,
bis er das nächste Mal incrementiert wird (und damit ein EXPIRE bekommt) oder
manuell entfernt wird. Für eine 15-min-Schutzperiode irrelevant.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from redis.asyncio import Redis

LOGIN_LIMIT: Final[int] = 5
LOGIN_WINDOW_SECONDS: Final[int] = 15 * 60  # 15 Minuten

_KEY_PREFIX: Final[str] = "auth:ratelimit:login"


@dataclass(frozen=True, slots=True)
class RateLimitResult:
    """Ergebnis eines Rate-Limit-Checks.

    ``allowed`` ist ``True``, solange der Counter den Schwellwert noch nicht
    überschritten hat. ``retry_after_seconds`` ist die TTL des Counters in
    Sekunden (für ``Retry-After``-Header); ``current`` ist der aktuelle
    Counter-Wert nach dem ``INCR``.
    """

    allowed: bool
    retry_after_seconds: int
    current: int


def login_ip_key(ip: str) -> str:
    return f"{_KEY_PREFIX}:ip:{ip}"


def login_user_key(username: str) -> str:
    return f"{_KEY_PREFIX}:user:{username}"


async def incr_and_check(
    client: Redis,
    key: str,
    *,
    limit: int,
    window_seconds: int,
) -> RateLimitResult:
    """Incrementiere ``key`` und prüfe gegen ``limit``.

    Setzt die TTL bei jedem ersten ``INCR`` auf ``window_seconds``. Folge-INCRs
    setzen die TTL nicht erneut — der Counter läuft ab, sobald der erste
    Versuch im Window ``window_seconds`` alt ist (Sliding-Window-artiges
    Verhalten an der Window-Grenze ist akzeptabel für die 15-min-Granularität).
    """
    current_raw = await client.incr(key)
    current = int(current_raw)
    if current == 1:
        await client.expire(key, window_seconds)
    ttl_raw = await client.ttl(key)
    ttl = int(ttl_raw)
    # ``ttl`` kann -1 (kein Ablauf gesetzt) oder -2 (Key existiert nicht)
    # zurückgeben; in beiden Fällen liefern wir den Window-Wert als
    # konservative Obergrenze.
    retry_after = window_seconds if ttl < 0 else ttl
    return RateLimitResult(
        allowed=current <= limit,
        retry_after_seconds=retry_after,
        current=current,
    )


async def reset(client: Redis, key: str) -> None:
    """Lösche ``key``, sodass der nächste ``INCR`` wieder bei 1 startet."""
    await client.delete(key)


async def check_login(
    client: Redis,
    *,
    ip: str,
    username: str,
) -> RateLimitResult:
    """Multi-Key-Login-Check (IP UND User).

    Beide Counter werden incrementiert. Der zurückgegebene ``RateLimitResult``
    spiegelt den restriktiveren der beiden — wenn einer der Counter über
    ``LOGIN_LIMIT`` ist, ist ``allowed=False``, und ``retry_after_seconds``
    ist die größere der beiden TTLs (Client wartet, bis das schärfere Limit
    verschwindet).

    Wir incrementieren **beide** Counter selbst dann, wenn einer schon über
    dem Limit liegt — das ist Absicht: ein Angreifer, der eine bekannt
    gesperrte IP nutzt, soll nicht durch Username-Variation den User-Counter
    schonen können.
    """
    ip_result = await incr_and_check(
        client,
        login_ip_key(ip),
        limit=LOGIN_LIMIT,
        window_seconds=LOGIN_WINDOW_SECONDS,
    )
    user_result = await incr_and_check(
        client,
        login_user_key(username),
        limit=LOGIN_LIMIT,
        window_seconds=LOGIN_WINDOW_SECONDS,
    )
    allowed = ip_result.allowed and user_result.allowed
    retry_after = max(ip_result.retry_after_seconds, user_result.retry_after_seconds)
    current = max(ip_result.current, user_result.current)
    return RateLimitResult(
        allowed=allowed,
        retry_after_seconds=retry_after,
        current=current,
    )


async def reset_user(client: Redis, username: str) -> None:
    """Setzt **nur** den User-Counter zurück.

    Aufgerufen nach erfolgreichem Login. IP-Counter bleibt absichtlich
    bestehen — siehe Modul-Docstring.
    """
    await reset(client, login_user_key(username))


__all__ = [
    "LOGIN_LIMIT",
    "LOGIN_WINDOW_SECONDS",
    "RateLimitResult",
    "check_login",
    "incr_and_check",
    "login_ip_key",
    "login_user_key",
    "reset",
    "reset_user",
]
