"""
Reliability patterns for AgentOperatingSystem

Implements core reliability patterns as specified in features.md:
- Idempotency framework
- Retry logic with exponential backoff
- Circuit breakers
- State machines
- Backpressure controls
"""

from .idempotency import IdempotencyHandler, IdempotencyKey
from .retry import RetryPolicy, RetryHandler, BackoffStrategy
from .circuit_breaker import CircuitBreaker, CircuitState
from .state_machine import StateMachine, State, Transition
from .backpressure import BackpressureController, LoadShedder

__all__ = [
    'IdempotencyHandler',
    'IdempotencyKey',
    'RetryPolicy',
    'RetryHandler',
    'BackoffStrategy',
    'CircuitBreaker',
    'CircuitState',
    'StateMachine',
    'State',
    'Transition',
    'BackpressureController',
    'LoadShedder'
]
