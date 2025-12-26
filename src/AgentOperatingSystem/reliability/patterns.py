"""
Generic Reliability Patterns for Agent Operating System

This module provides generic, reusable reliability patterns for any agent-based system:
- Circuit breaker pattern
- Retry logic with exponential backoff
- Idempotency handling
- Backpressure management

These patterns ensure robust fault tolerance and resilience in distributed systems.

Usage:
    from AgentOperatingSystem.reliability.patterns import CircuitBreaker, RetryPolicy, with_retry
    
    # Use as decorator
    @with_retry(max_retries=3)
    async def unreliable_operation():
        ...
    
    # Use directly
    policy = RetryPolicy(max_retries=5)
    result = await policy.execute(my_async_function, arg1, arg2)
"""

import asyncio
import logging
import time
from typing import Callable, Any, Optional, Dict
from enum import Enum
from functools import wraps
from datetime import datetime, timedelta
import random


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit Breaker Pattern Implementation
    
    Prevents cascading failures by stopping calls to failing services
    and allowing them time to recover.
    
    Example:
        breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        result = await breaker.call(external_api_call, param1, param2)
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.logger = logging.getLogger(__name__)
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit."""
        if self.state == CircuitState.OPEN and self.last_failure_time:
            time_since_failure = time.time() - self.last_failure_time
            return time_since_failure >= self.recovery_timeout
        return False
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        # Check if we should attempt reset
        if self._should_attempt_reset():
            self.state = CircuitState.HALF_OPEN
            self.logger.info("Circuit breaker entering HALF_OPEN state")
        
        # Reject if circuit is open
        if self.state == CircuitState.OPEN:
            raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            # Execute function
            result = await func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == CircuitState.HALF_OPEN:
                self.logger.info("Circuit breaker reset to CLOSED state")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            
            return result
            
        except self.expected_exception as e:
            # Record failure
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.logger.error(
                    f"Circuit breaker opened after {self.failure_count} failures"
                )
            
            raise


class RetryPolicy:
    """
    Retry Logic with Exponential Backoff
    
    Automatically retries failed operations with increasing delays
    between attempts to handle transient failures.
    
    Example:
        policy = RetryPolicy(max_retries=3, base_delay=1.0)
        result = await policy.execute(api_call, param1, param2)
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry policy.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Add randomness to delay to prevent thundering herd
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.logger = logging.getLogger(__name__)
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                
                if attempt > 0:
                    self.logger.info(f"Operation succeeded after {attempt} retries")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(
                        f"All {self.max_retries} retries exhausted. Giving up."
                    )
        
        raise last_exception


class IdempotencyHandler:
    """
    Idempotency Handling
    
    Ensures operations can be safely retried without side effects by
    caching results based on idempotency keys.
    
    Example:
        handler = IdempotencyHandler(cache_ttl=3600)
        result = await handler.execute("unique-key", operation, param1)
    """
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize idempotency handler.
        
        Args:
            cache_ttl: Time to live for cached results in seconds
        """
        self.cache: Dict[str, tuple] = {}  # key -> (result, timestamp)
        self.cache_ttl = cache_ttl
        self.logger = logging.getLogger(__name__)
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached result is still valid."""
        return time.time() - timestamp < self.cache_ttl
    
    async def execute(
        self,
        idempotency_key: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with idempotency guarantee.
        
        Args:
            idempotency_key: Unique key for this operation
            func: Async function to execute
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result (from cache or fresh execution)
        """
        # Check cache
        if idempotency_key in self.cache:
            result, timestamp = self.cache[idempotency_key]
            if self._is_cache_valid(timestamp):
                self.logger.info(f"Returning cached result for {idempotency_key}")
                return result
            else:
                # Expired cache entry
                del self.cache[idempotency_key]
        
        # Execute function
        result = await func(*args, **kwargs)
        
        # Cache result
        self.cache[idempotency_key] = (result, time.time())
        
        return result
    
    def clear_cache(self, idempotency_key: Optional[str] = None):
        """Clear cache for specific key or all keys."""
        if idempotency_key:
            self.cache.pop(idempotency_key, None)
        else:
            self.cache.clear()


# Decorator utilities

def with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60
):
    """
    Decorator to apply circuit breaker to async function.
    
    Example:
        @with_circuit_breaker(failure_threshold=3)
        async def my_function():
            ...
    """
    def decorator(func):
        breaker = CircuitBreaker(failure_threshold, recovery_timeout)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """
    Decorator to apply retry logic to async function.
    
    Example:
        @with_retry(max_retries=5, base_delay=2.0)
        async def my_function():
            ...
    """
    def decorator(func):
        policy = RetryPolicy(max_retries, base_delay, max_delay)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await policy.execute(func, *args, **kwargs)
        
        return wrapper
    return decorator


def with_idempotency(key_generator: Callable):
    """
    Decorator to apply idempotency to async function.
    
    Args:
        key_generator: Function to generate idempotency key from args
        
    Example:
        @with_idempotency(lambda *args, **kwargs: f"op-{args[0]}")
        async def my_function(id, data):
            ...
    """
    def decorator(func):
        handler = IdempotencyHandler()
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = key_generator(*args, **kwargs)
            return await handler.execute(key, func, *args, **kwargs)
        
        return wrapper
    return decorator
