"""Tests for AOS Client SDK reliability patterns."""

import pytest
from aos_client.reliability import (
    CircuitBreaker, CircuitState, RetryPolicy, IdempotencyHandler,
    with_circuit_breaker, with_retry, with_idempotency,
)


class TestCircuitBreaker:
    def test_initial_state(self):
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.state == CircuitState.CLOSED

    async def test_success_stays_closed(self):
        cb = CircuitBreaker(failure_threshold=3)
        async def ok():
            return "ok"
        result = await cb.call(ok)
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED

    async def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2)
        async def fail():
            raise ValueError("boom")
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(fail)
        assert cb.state == CircuitState.OPEN

    async def test_open_circuit_rejects(self):
        cb = CircuitBreaker(failure_threshold=1)
        async def fail():
            raise ValueError("boom")
        with pytest.raises(ValueError):
            await cb.call(fail)
        with pytest.raises(RuntimeError, match="OPEN"):
            await cb.call(fail)


class TestRetryPolicy:
    async def test_success_no_retry(self):
        policy = RetryPolicy(max_retries=3, base_delay=0.01)
        async def ok():
            return 42
        result = await policy.execute(ok)
        assert result == 42

    async def test_eventual_success(self):
        attempts = {"count": 0}
        policy = RetryPolicy(max_retries=3, base_delay=0.01, jitter=False)
        async def flaky():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("not yet")
            return "done"
        result = await policy.execute(flaky)
        assert result == "done"
        assert attempts["count"] == 3

    async def test_exhausted_retries(self):
        policy = RetryPolicy(max_retries=2, base_delay=0.01, jitter=False)
        async def always_fail():
            raise ValueError("fail")
        with pytest.raises(ValueError, match="fail"):
            await policy.execute(always_fail)


class TestIdempotencyHandler:
    async def test_caches_result(self):
        handler = IdempotencyHandler(cache_ttl=60)
        call_count = {"n": 0}
        async def expensive():
            call_count["n"] += 1
            return "result"
        r1 = await handler.execute("key1", expensive)
        r2 = await handler.execute("key1", expensive)
        assert r1 == r2 == "result"
        assert call_count["n"] == 1

    async def test_different_keys(self):
        handler = IdempotencyHandler()
        async def fn():
            return "val"
        await handler.execute("a", fn)
        await handler.execute("b", fn)
        assert len(handler.cache) == 2

    def test_clear_specific(self):
        handler = IdempotencyHandler()
        handler.cache["a"] = ("val", 0)
        handler.cache["b"] = ("val", 0)
        handler.clear("a")
        assert "a" not in handler.cache
        assert "b" in handler.cache

    def test_clear_all(self):
        handler = IdempotencyHandler()
        handler.cache["a"] = ("val", 0)
        handler.clear()
        assert len(handler.cache) == 0


class TestDecorators:
    async def test_with_retry_decorator(self):
        @with_retry(max_retries=1, base_delay=0.01)
        async def ok():
            return "ok"
        assert await ok() == "ok"

    async def test_with_circuit_breaker_decorator(self):
        @with_circuit_breaker(failure_threshold=5)
        async def ok():
            return "ok"
        assert await ok() == "ok"
