"""
Reliability patterns for AgentOperatingSystem

Implements core reliability patterns as specified in features.md:
- Idempotency framework
- Retry logic with exponential backoff
- Circuit breakers
- State machines
- Backpressure controls
"""


# Generic reliability patterns from migration
try:
    HAS_PATTERNS = True
except ImportError:
    HAS_PATTERNS = False

# Advanced reliability features
try:
    pass

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
