"""
Circuit breaker pattern for AgentOperatingSystem

Short-circuits failing dependencies with fallback mechanisms to prevent
cascading failures and enable graceful degradation.
"""

from typing import Callable, TypeVar, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import asyncio
import logging


T = TypeVar('T')
logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """States of a circuit breaker"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, requests rejected
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Number of failures before opening
    success_threshold: int = 2  # Number of successes to close from half-open
    timeout_seconds: int = 60  # Time to wait before trying half-open
    
    # Time window for failure counting
    failure_window_seconds: int = 60


class CircuitBreaker:
    """
    Circuit breaker implementation for dependency protection.
    
    Tracks failures and automatically opens circuit to prevent further
    calls when failure threshold is exceeded. Automatically attempts
    recovery after timeout period.
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        fallback: Optional[Callable[[], Any]] = None
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Name of this circuit breaker (for logging)
            config: Circuit breaker configuration
            fallback: Optional fallback function when circuit is open
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.fallback = fallback
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._opened_at: Optional[datetime] = None
        self._failures_in_window: list = []
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state"""
        # Check if we should transition from OPEN to HALF_OPEN
        if self._state == CircuitState.OPEN and self._opened_at:
            elapsed = (datetime.utcnow() - self._opened_at).total_seconds()
            if elapsed >= self.config.timeout_seconds:
                self._transition_to_half_open()
        
        return self._state
    
    async def execute(self, operation: Callable[[], T]) -> T:
        """
        Execute operation through circuit breaker.
        
        Args:
            operation: Async function to execute
            
        Returns:
            Result of operation or fallback
            
        Raises:
            Exception if circuit is open and no fallback provided
        """
        current_state = self.state
        
        if current_state == CircuitState.OPEN:
            logger.warning(f"Circuit breaker {self.name} is OPEN")
            if self.fallback:
                logger.info(f"Using fallback for {self.name}")
                return await self._execute_fallback()
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker {self.name} is open"
                )
        
        try:
            result = await operation()
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    def execute_sync(self, operation: Callable[[], T]) -> T:
        """
        Execute synchronous operation through circuit breaker.
        
        Args:
            operation: Function to execute
            
        Returns:
            Result of operation or fallback
            
        Raises:
            Exception if circuit is open and no fallback provided
        """
        current_state = self.state
        
        if current_state == CircuitState.OPEN:
            logger.warning(f"Circuit breaker {self.name} is OPEN")
            if self.fallback:
                logger.info(f"Using fallback for {self.name}")
                return self.fallback()
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker {self.name} is open"
                )
        
        try:
            result = operation()
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful execution"""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            logger.info(
                f"Circuit breaker {self.name} success count: "
                f"{self._success_count}/{self.config.success_threshold}"
            )
            
            if self._success_count >= self.config.success_threshold:
                self._transition_to_closed()
        
        elif self._state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0
            self._failures_in_window.clear()
    
    def _on_failure(self):
        """Handle failed execution"""
        now = datetime.utcnow()
        self._last_failure_time = now
        self._failures_in_window.append(now)
        
        # Clean up old failures outside the window
        window_start = now - timedelta(seconds=self.config.failure_window_seconds)
        self._failures_in_window = [
            f for f in self._failures_in_window if f > window_start
        ]
        
        failure_count = len(self._failures_in_window)
        
        if self._state == CircuitState.HALF_OPEN:
            # Any failure in half-open transitions back to open
            self._transition_to_open()
        
        elif self._state == CircuitState.CLOSED:
            if failure_count >= self.config.failure_threshold:
                self._transition_to_open()
    
    def _transition_to_open(self):
        """Transition to OPEN state"""
        self._state = CircuitState.OPEN
        self._opened_at = datetime.utcnow()
        self._success_count = 0
        logger.warning(f"Circuit breaker {self.name} transitioned to OPEN")
    
    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        self._state = CircuitState.HALF_OPEN
        self._success_count = 0
        logger.info(f"Circuit breaker {self.name} transitioned to HALF_OPEN")
    
    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._opened_at = None
        self._failures_in_window.clear()
        logger.info(f"Circuit breaker {self.name} transitioned to CLOSED")
    
    async def _execute_fallback(self) -> Any:
        """Execute fallback if it's async"""
        if asyncio.iscoroutinefunction(self.fallback):
            return await self.fallback()
        else:
            return self.fallback()
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED state"""
        logger.info(f"Manually resetting circuit breaker {self.name}")
        self._transition_to_closed()
    
    def get_stats(self) -> dict:
        """Get current circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": len(self._failures_in_window),
            "success_count": self._success_count,
            "last_failure_time": self._last_failure_time.isoformat() if self._last_failure_time else None,
            "opened_at": self._opened_at.isoformat() if self._opened_at else None
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass
