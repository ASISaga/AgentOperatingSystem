"""Reliability patterns for AOS client applications.

Provides circuit breaker, retry with exponential backoff, and idempotency
handling that can be applied to AOSClient calls automatically.

Usage::

    from aos_client.reliability import CircuitBreaker, RetryPolicy, IdempotencyHandler

    client = AOSClient(
        endpoint="https://my-aos.azurewebsites.net",
        retry_policy=RetryPolicy(max_retries=3),
        circuit_breaker=CircuitBreaker(failure_threshold=5),
    )
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures.

    Args:
        failure_threshold: Failures before the circuit opens.
        recovery_timeout: Seconds before attempting recovery.
        expected_exception: Exception type to intercept.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def _should_attempt_reset(self) -> bool:
        if self.state == CircuitState.OPEN and self.last_failure_time is not None:
            return (time.time() - self.last_failure_time) >= self.recovery_timeout
        return False

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute *func* with circuit breaker protection."""
        if self._should_attempt_reset():
            self.state = CircuitState.HALF_OPEN
            logger.info("Circuit breaker entering HALF_OPEN state")

        if self.state == CircuitState.OPEN:
            raise RuntimeError("Circuit breaker is OPEN — service unavailable")

        try:
            result = await func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                logger.info("Circuit breaker reset to CLOSED state")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            return result
        except self.expected_exception:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error(
                    "Circuit breaker opened after %d failures",
                    self.failure_count,
                )
            raise


class RetryPolicy:
    """Retry with exponential backoff and optional jitter.

    Args:
        max_retries: Maximum retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds.
        exponential_base: Multiplier for exponential backoff.
        jitter: Whether to add randomness to delays.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def _calculate_delay(self, attempt: int) -> float:
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay,
        )
        if self.jitter:
            delay *= 0.5 + random.random()
        return delay

    async def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute *func* with retry logic."""
        last_exception: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                if attempt > 0:
                    logger.info("Operation succeeded after %d retries", attempt)
                return result
            except Exception as exc:
                last_exception = exc
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        "Attempt %d failed: %s. Retrying in %.2fs…",
                        attempt + 1,
                        exc,
                        delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("All %d retries exhausted.", self.max_retries)
        raise last_exception  # type: ignore[misc]


class IdempotencyHandler:
    """Ensures operations can be safely retried without side effects.

    Args:
        cache_ttl: Time-to-live for cached results in seconds.
    """

    def __init__(self, cache_ttl: int = 3600) -> None:
        self.cache: Dict[str, tuple] = {}
        self.cache_ttl = cache_ttl

    def _is_valid(self, timestamp: float) -> bool:
        return (time.time() - timestamp) < self.cache_ttl

    async def execute(
        self,
        idempotency_key: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute *func* with idempotency guarantee."""
        if idempotency_key in self.cache:
            result, ts = self.cache[idempotency_key]
            if self._is_valid(ts):
                logger.info("Returning cached result for %s", idempotency_key)
                return result
            del self.cache[idempotency_key]

        result = await func(*args, **kwargs)
        self.cache[idempotency_key] = (result, time.time())
        return result

    def clear(self, idempotency_key: Optional[str] = None) -> None:
        """Clear cache for a specific key or all keys."""
        if idempotency_key:
            self.cache.pop(idempotency_key, None)
        else:
            self.cache.clear()


# ---------------------------------------------------------------------------
# Decorator utilities
# ---------------------------------------------------------------------------


def with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
) -> Callable:
    """Decorator to apply a circuit breaker to an async function."""

    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreaker(failure_threshold, recovery_timeout)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> Callable:
    """Decorator to apply retry logic to an async function."""

    def decorator(func: Callable) -> Callable:
        policy = RetryPolicy(max_retries, base_delay, max_delay)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await policy.execute(func, *args, **kwargs)

        return wrapper

    return decorator


def with_idempotency(key_generator: Callable) -> Callable:
    """Decorator to apply idempotency to an async function.

    Args:
        key_generator: Callable that produces an idempotency key from
            the function arguments.
    """

    def decorator(func: Callable) -> Callable:
        handler = IdempotencyHandler()

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = key_generator(*args, **kwargs)
            return await handler.execute(key, func, *args, **kwargs)

        return wrapper

    return decorator
