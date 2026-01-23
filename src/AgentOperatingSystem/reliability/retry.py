"""
Retry logic with exponential backoff for AgentOperatingSystem

Implements retry policies with:
- Exponential backoff with jitter
- Max attempts per failure class
- Poison message quarantine
"""

from typing import Callable, TypeVar, Optional, List
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import asyncio
import random
import logging


T = TypeVar('T')
logger = logging.getLogger(__name__)


class BackoffStrategy(str, Enum):
    """Backoff strategies for retries"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CONSTANT = "constant"


class FailureClass(str, Enum):
    """Classes of failures for retry policies"""
    TRANSIENT = "transient"  # Network issues, temporary unavailability
    RATE_LIMIT = "rate_limit"  # Rate limiting, backpressure
    VALIDATION = "validation"  # Invalid input, schema errors
    PERMANENT = "permanent"  # Cannot be retried
    UNKNOWN = "unknown"


class RetryPolicy(BaseModel):
    """
    Configuration for retry behavior.
    """
    max_attempts: int = 3
    base_delay_ms: int = 100
    max_delay_ms: int = 60000  # 1 minute
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    backoff_multiplier: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd

    # Failure class specific overrides
    failure_class_max_attempts: dict = Field(default_factory=dict)

    def get_max_attempts(self, failure_class: FailureClass) -> int:
        """Get max attempts for a specific failure class"""
        return self.failure_class_max_attempts.get(
            failure_class.value,
            self.max_attempts
        )

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay in seconds for the given attempt number.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        if self.backoff_strategy == BackoffStrategy.CONSTANT:
            delay_ms = self.base_delay_ms
        elif self.backoff_strategy == BackoffStrategy.LINEAR:
            delay_ms = self.base_delay_ms * (attempt + 1)
        else:  # EXPONENTIAL
            delay_ms = self.base_delay_ms * (self.backoff_multiplier ** attempt)

        # Cap at max delay
        delay_ms = min(delay_ms, self.max_delay_ms)

        # Add jitter if enabled
        if self.jitter:
            # Add random jitter between 0% and 25% of delay
            jitter_amount = delay_ms * random.uniform(0, 0.25)
            delay_ms += jitter_amount

        return delay_ms / 1000.0  # Convert to seconds


class PoisonMessage(BaseModel):
    """Record of a message that failed permanently"""
    message_id: str
    failure_class: FailureClass
    attempts: int
    last_error: str
    quarantined_at: datetime = Field(default_factory=datetime.utcnow)
    original_payload: dict = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RetryHandler:
    """
    Handler for retry logic with exponential backoff.
    """

    def __init__(self, policy: Optional[RetryPolicy] = None):
        """
        Initialize retry handler.

        Args:
            policy: Retry policy configuration
        """
        self.policy = policy or RetryPolicy()
        self.poison_messages: List[PoisonMessage] = []

    async def execute_with_retry(
        self,
        operation: Callable[[], T],
        failure_classifier: Optional[Callable[[Exception], FailureClass]] = None,
        message_id: Optional[str] = None
    ) -> T:
        """
        Execute operation with retry logic.

        Args:
            operation: Async function to execute
            failure_classifier: Function to classify exceptions
            message_id: Optional message ID for poison message tracking

        Returns:
            Result of successful operation

        Raises:
            Exception from the operation after all retries exhausted
        """
        classifier = failure_classifier or self._default_classifier
        attempt = 0
        last_exception = None

        while True:
            try:
                result = await operation()
                if attempt > 0:
                    logger.info(f"Operation succeeded on attempt {attempt + 1}")
                return result

            except Exception as e:
                failure_class = classifier(e)
                last_exception = e
                max_attempts = self.policy.get_max_attempts(failure_class)

                # Don't retry permanent failures
                if failure_class == FailureClass.PERMANENT:
                    logger.error(f"Permanent failure, not retrying: {e}")
                    raise

                attempt += 1

                if attempt >= max_attempts:
                    logger.error(
                        f"Max retry attempts ({max_attempts}) exceeded for "
                        f"failure class {failure_class.value}"
                    )

                    # Quarantine as poison message if we have message_id
                    if message_id:
                        self._quarantine_message(
                            message_id, failure_class, attempt, str(e)
                        )

                    raise

                delay = self.policy.calculate_delay(attempt - 1)
                logger.warning(
                    f"Attempt {attempt} failed with {failure_class.value}, "
                    f"retrying in {delay:.2f}s: {e}"
                )
                await asyncio.sleep(delay)

    def execute_sync_with_retry(
        self,
        operation: Callable[[], T],
        failure_classifier: Optional[Callable[[Exception], FailureClass]] = None,
        message_id: Optional[str] = None
    ) -> T:
        """
        Execute synchronous operation with retry logic.

        Args:
            operation: Function to execute
            failure_classifier: Function to classify exceptions
            message_id: Optional message ID for poison message tracking

        Returns:
            Result of successful operation

        Raises:
            Exception from the operation after all retries exhausted
        """
        import time

        classifier = failure_classifier or self._default_classifier
        attempt = 0
        last_exception = None

        while True:
            try:
                result = operation()
                if attempt > 0:
                    logger.info(f"Operation succeeded on attempt {attempt + 1}")
                return result

            except Exception as e:
                failure_class = classifier(e)
                last_exception = e
                max_attempts = self.policy.get_max_attempts(failure_class)

                # Don't retry permanent failures
                if failure_class == FailureClass.PERMANENT:
                    logger.error(f"Permanent failure, not retrying: {e}")
                    raise

                attempt += 1

                if attempt >= max_attempts:
                    logger.error(
                        f"Max retry attempts ({max_attempts}) exceeded for "
                        f"failure class {failure_class.value}"
                    )

                    # Quarantine as poison message if we have message_id
                    if message_id:
                        self._quarantine_message(
                            message_id, failure_class, attempt, str(e)
                        )

                    raise

                delay = self.policy.calculate_delay(attempt - 1)
                logger.warning(
                    f"Attempt {attempt} failed with {failure_class.value}, "
                    f"retrying in {delay:.2f}s: {e}"
                )
                time.sleep(delay)

    def _default_classifier(self, exception: Exception) -> FailureClass:
        """Default exception classifier"""
        exception_type = type(exception).__name__

        # Common transient errors
        if any(term in exception_type.lower() for term in ['timeout', 'connection', 'network']):
            return FailureClass.TRANSIENT

        # Validation errors
        if any(term in exception_type.lower() for term in ['validation', 'schema', 'parse']):
            return FailureClass.VALIDATION

        # Default to unknown
        return FailureClass.UNKNOWN

    def _quarantine_message(
        self,
        message_id: str,
        failure_class: FailureClass,
        attempts: int,
        error: str
    ):
        """Quarantine a poison message"""
        poison_msg = PoisonMessage(
            message_id=message_id,
            failure_class=failure_class,
            attempts=attempts,
            last_error=error
        )
        self.poison_messages.append(poison_msg)
        logger.warning(f"Message {message_id} quarantined as poison message")

    def get_poison_messages(self) -> List[PoisonMessage]:
        """Get all quarantined poison messages"""
        return self.poison_messages

    def clear_poison_messages(self):
        """Clear poison message queue"""
        self.poison_messages.clear()
