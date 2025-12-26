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

# Generic reliability patterns from migration
try:
    from .patterns import (
        CircuitBreaker as GenericCircuitBreaker,
        RetryPolicy as GenericRetryPolicy,
        IdempotencyHandler as GenericIdempotencyHandler,
        with_retry,
        with_circuit_breaker
    )
    HAS_PATTERNS = True
except ImportError:
    HAS_PATTERNS = False

# Advanced reliability features
try:
    from .state_machine_advanced import DistributedStateMachine, StateTransitionError
    from .chaos import ChaosOrchestrator, ChaosType
    
    base_exports = [
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
        'LoadShedder',
        # Advanced features
        'DistributedStateMachine',
        'StateTransitionError',
        'ChaosOrchestrator',
        'ChaosType'
    ]
    
    if HAS_PATTERNS:
        base_exports.extend([
            'GenericCircuitBreaker',
            'GenericRetryPolicy',
            'GenericIdempotencyHandler',
            'with_retry',
            'with_circuit_breaker'
        ])
    
    __all__ = base_exports
except ImportError:
    base_exports = [
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
    
    if HAS_PATTERNS:
        base_exports.extend([
            'GenericCircuitBreaker',
            'GenericRetryPolicy',
            'GenericIdempotencyHandler',
            'with_retry',
            'with_circuit_breaker'
        ])
    
    __all__ = base_exports
