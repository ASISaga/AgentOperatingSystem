"""
Backpressure control for AgentOperatingSystem

Queue monitoring, rate limiting, and load shedding for non-critical tasks
to prevent system overload.
"""

import logging
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Callable, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BackpressureConfig(BaseModel):
    """Configuration for backpressure control"""
    max_queue_length: int = 1000
    warning_threshold: float = 0.8  # Warn at 80% capacity
    critical_threshold: float = 0.95  # Critical at 95% capacity

    # Rate limiting
    max_requests_per_second: Optional[int] = None
    rate_limit_window_seconds: int = 1


class LoadSheddingPolicy(BaseModel):
    """Policy for load shedding"""
    enabled: bool = True
    shed_non_critical: bool = True  # Shed non-critical tasks first
    shed_threshold: float = 0.95  # Start shedding at 95% capacity


class BackpressureController:
    """
    Controller for backpressure management.

    Monitors queue length, applies rate limiting, and performs load shedding
    when system is overloaded.
    """

    def __init__(
        self,
        name: str,
        config: Optional[BackpressureConfig] = None,
        load_shedding: Optional[LoadSheddingPolicy] = None
    ):
        """
        Initialize backpressure controller.

        Args:
            name: Name of this controller
            config: Backpressure configuration
            load_shedding: Load shedding policy
        """
        self.name = name
        self.config = config or BackpressureConfig()
        self.load_shedding = load_shedding or LoadSheddingPolicy()

        self._queue_length = 0
        self._total_processed = 0
        self._total_shed = 0
        self._request_times: deque = deque()

    def check_capacity(self) -> tuple[bool, float]:
        """
        Check if system has capacity for new requests.

        Returns:
            Tuple of (has_capacity, utilization_ratio)
        """
        utilization = self._queue_length / self.config.max_queue_length

        if utilization >= self.config.critical_threshold:
            logger.error(
                f"Backpressure controller {self.name} at CRITICAL capacity: "
                f"{utilization:.1%}"
            )
            return False, utilization

        if utilization >= self.config.warning_threshold:
            logger.warning(
                f"Backpressure controller {self.name} at WARNING capacity: "
                f"{utilization:.1%}"
            )

        return True, utilization

    def should_shed_load(self, is_critical: bool = False) -> bool:
        """
        Determine if request should be shed based on load.

        Args:
            is_critical: Whether this is a critical request

        Returns:
            True if request should be shed
        """
        if not self.load_shedding.enabled:
            return False

        has_capacity, utilization = self.check_capacity()

        # Never shed critical requests unless absolutely necessary
        if is_critical:
            return utilization >= 1.0

        # Shed non-critical requests when over threshold
        if self.load_shedding.shed_non_critical:
            return utilization >= self.load_shedding.shed_threshold

        return False

    def check_rate_limit(self) -> bool:
        """
        Check if request should be rate limited.

        Returns:
            True if request is allowed, False if rate limited
        """
        if self.config.max_requests_per_second is None:
            return True

        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.config.rate_limit_window_seconds)

        # Remove old timestamps outside the window
        while self._request_times and self._request_times[0] < window_start:
            self._request_times.popleft()

        # Check if we're under the rate limit
        current_rate = len(self._request_times)
        if current_rate >= self.config.max_requests_per_second:
            logger.warning(
                f"Rate limit exceeded for {self.name}: "
                f"{current_rate}/{self.config.max_requests_per_second} req/s"
            )
            return False

        # Record this request
        self._request_times.append(now)
        return True

    async def execute_with_backpressure(
        self,
        operation: Callable[[], Any],
        is_critical: bool = False
    ) -> Any:
        """
        Execute operation with backpressure control.

        Args:
            operation: Async function to execute
            is_critical: Whether this is a critical request

        Returns:
            Result of operation

        Raises:
            BackpressureError if request is shed or rate limited
        """
        # Check load shedding
        if self.should_shed_load(is_critical):
            self._total_shed += 1
            logger.warning("Shedding load for %s (total shed: %s)", self.name, self._total_shed)
            raise LoadSheddingError(f"Load shed by {self.name}")

        # Check rate limit
        if not self.check_rate_limit():
            raise RateLimitError(f"Rate limited by {self.name}")

        # Check capacity
        has_capacity, utilization = self.check_capacity()
        if not has_capacity and not is_critical:
            raise BackpressureError(
                f"No capacity in {self.name} (utilization: {utilization:.1%})"
            )

        # Execute operation
        self._queue_length += 1
        try:
            result = await operation()
            self._total_processed += 1
            return result
        finally:
            self._queue_length -= 1

    def execute_sync_with_backpressure(
        self,
        operation: Callable[[], Any],
        is_critical: bool = False
    ) -> Any:
        """
        Execute synchronous operation with backpressure control.

        Args:
            operation: Function to execute
            is_critical: Whether this is a critical request

        Returns:
            Result of operation

        Raises:
            BackpressureError if request is shed or rate limited
        """
        # Check load shedding
        if self.should_shed_load(is_critical):
            self._total_shed += 1
            logger.warning("Shedding load for %s (total shed: %s)", self.name, self._total_shed)
            raise LoadSheddingError(f"Load shed by {self.name}")

        # Check rate limit
        if not self.check_rate_limit():
            raise RateLimitError(f"Rate limited by {self.name}")

        # Check capacity
        has_capacity, utilization = self.check_capacity()
        if not has_capacity and not is_critical:
            raise BackpressureError(
                f"No capacity in {self.name} (utilization: {utilization:.1%})"
            )

        # Execute operation
        self._queue_length += 1
        try:
            result = operation()
            self._total_processed += 1
            return result
        finally:
            self._queue_length -= 1

    def get_stats(self) -> dict:
        """Get current backpressure statistics"""
        utilization = self._queue_length / self.config.max_queue_length
        return {
            "name": self.name,
            "queue_length": self._queue_length,
            "max_queue_length": self.config.max_queue_length,
            "utilization": utilization,
            "total_processed": self._total_processed,
            "total_shed": self._total_shed,
            "current_rate": len(self._request_times)
        }


class LoadShedder:
    """
    Simple load shedder for prioritized request handling.

    Sheds low-priority requests when system is overloaded.
    """

    def __init__(self, max_load: int = 100):
        """
        Initialize load shedder.

        Args:
            max_load: Maximum concurrent load
        """
        self.max_load = max_load
        self._current_load = 0

    def should_accept(self, priority: int = 0) -> bool:
        """
        Check if request should be accepted.

        Args:
            priority: Request priority (higher = more important)

        Returns:
            True if request should be accepted
        """
        # Always accept if under max load
        if self._current_load < self.max_load:
            return True

        # For high priority requests, accept if not severely overloaded
        if priority >= 5 and self._current_load < self.max_load * 1.2:
            return True

        return False

    async def execute(
        self,
        operation: Callable[[], Any],
        priority: int = 0
    ) -> Any:
        """
        Execute operation with load shedding.

        Args:
            operation: Async function to execute
            priority: Request priority

        Returns:
            Result of operation

        Raises:
            LoadSheddingError if request is shed
        """
        if not self.should_accept(priority):
            raise LoadSheddingError("Request shed due to high load")

        self._current_load += 1
        try:
            return await operation()
        finally:
            self._current_load -= 1


class BackpressureError(Exception):
    """Base exception for backpressure-related errors"""


class LoadSheddingError(BackpressureError):
    """Exception raised when load is shed"""


class RateLimitError(BackpressureError):
    """Exception raised when rate limit is exceeded"""
