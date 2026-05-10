"""Tests für ``backend/eb_digital/auth/rate_limit`` (ADR-013)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import fakeredis.aioredis
import pytest

from eb_digital.auth.rate_limit import (
    LOGIN_LIMIT,
    LOGIN_WINDOW_SECONDS,
    check_login,
    incr_and_check,
    login_ip_key,
    login_user_key,
    reset,
    reset_user,
)


@pytest.fixture
async def fake_valkey() -> AsyncIterator[fakeredis.aioredis.FakeRedis]:
    client = fakeredis.aioredis.FakeRedis()
    try:
        yield client
    finally:
        await client.flushall()
        await client.aclose()


class TestKeyHelpers:
    def test_login_ip_key_format(self) -> None:
        assert login_ip_key("198.51.100.7") == "auth:ratelimit:login:ip:198.51.100.7"

    def test_login_user_key_format(self) -> None:
        assert login_user_key("alice") == "auth:ratelimit:login:user:alice"


class TestIncrAndCheck:
    async def test_first_call_returns_allowed_with_full_window_ttl(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        result = await incr_and_check(fake_valkey, "k", limit=3, window_seconds=60)
        assert result.allowed is True
        assert result.current == 1
        # TTL should be ≤ 60 (window) and > 0.
        assert 0 < result.retry_after_seconds <= 60

    async def test_increments_count_on_each_call(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        await incr_and_check(fake_valkey, "k", limit=3, window_seconds=60)
        result2 = await incr_and_check(fake_valkey, "k", limit=3, window_seconds=60)
        assert result2.current == 2
        assert result2.allowed is True

    async def test_blocks_when_count_exceeds_limit(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        for _ in range(3):
            await incr_and_check(fake_valkey, "k", limit=3, window_seconds=60)
        # 4th call exceeds the limit (3).
        result = await incr_and_check(fake_valkey, "k", limit=3, window_seconds=60)
        assert result.allowed is False
        assert result.current == 4

    async def test_ttl_is_set_only_on_first_increment(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        await incr_and_check(fake_valkey, "k", limit=3, window_seconds=60)
        # Manuell auf 30 s reduzieren — Folge-INCR darf TTL nicht überschreiben.
        await fake_valkey.expire("k", 30)
        await incr_and_check(fake_valkey, "k", limit=3, window_seconds=60)
        ttl = int(await fake_valkey.ttl("k"))
        assert ttl <= 30, f"TTL={ttl} suggests Folge-INCR hat das EXPIRE überschrieben."


class TestReset:
    async def test_reset_removes_key(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        await incr_and_check(fake_valkey, "k", limit=3, window_seconds=60)
        await reset(fake_valkey, "k")
        # Nächster INCR startet bei 1.
        result = await incr_and_check(fake_valkey, "k", limit=3, window_seconds=60)
        assert result.current == 1


class TestCheckLogin:
    async def test_first_attempt_allowed_for_fresh_ip_and_user(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        result = await check_login(fake_valkey, ip="198.51.100.1", username="alice")
        assert result.allowed is True

    async def test_user_counter_blocks_after_5_attempts(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        for _ in range(LOGIN_LIMIT):
            await check_login(fake_valkey, ip="198.51.100.1", username="alice")
        result = await check_login(fake_valkey, ip="198.51.100.1", username="alice")
        assert result.allowed is False
        assert result.retry_after_seconds <= LOGIN_WINDOW_SECONDS

    async def test_ip_counter_blocks_brute_force_sweep_across_usernames(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        # 5 Versuche von derselben IP gegen 5 verschiedene Usernames.
        for n in range(LOGIN_LIMIT):
            await check_login(fake_valkey, ip="198.51.100.1", username=f"u{n}")
        # 6. Versuch gegen einen 6. Username muss am IP-Counter blocken.
        result = await check_login(fake_valkey, ip="198.51.100.1", username="u-fresh")
        assert result.allowed is False

    async def test_other_ips_are_unaffected(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        for n in range(LOGIN_LIMIT):
            await check_login(fake_valkey, ip="198.51.100.1", username=f"u{n}")
        # Andere IP startet mit frischem Counter.
        result = await check_login(fake_valkey, ip="198.51.100.2", username="alice")
        assert result.allowed is True


class TestResetUser:
    async def test_reset_user_clears_only_user_counter(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        # 5 Fehlversuche von derselben IP gegen denselben User.
        for _ in range(LOGIN_LIMIT):
            await check_login(fake_valkey, ip="198.51.100.1", username="alice")
        await reset_user(fake_valkey, "alice")
        # User-Counter ist 0, IP-Counter ist 5 → IP-Counter blockiert weiterhin.
        result = await check_login(fake_valkey, ip="198.51.100.1", username="alice")
        # User-Counter steht jetzt bei 1 (frisch nach Reset), aber IP bei 6 → blockiert.
        assert result.allowed is False

    async def test_reset_user_releases_user_counter_for_different_ip(
        self,
        fake_valkey: fakeredis.aioredis.FakeRedis,
    ) -> None:
        for _ in range(LOGIN_LIMIT):
            await check_login(fake_valkey, ip="198.51.100.1", username="alice")
        await reset_user(fake_valkey, "alice")
        # User-Counter weg → eine fremde IP kommt für „alice" wieder durch.
        result = await check_login(fake_valkey, ip="198.51.100.2", username="alice")
        assert result.allowed is True
