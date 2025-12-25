# Technical Specification: Reliability and Resilience System

**Document Version:** 2025.1.2  
**Status:** Implemented  
**Date:** December 25, 2025  
**Module:** AgentOperatingSystem Reliability (`src/AgentOperatingSystem/reliability/`)

---

## 1. System Overview

The AOS Reliability System provides patterns and mechanisms for building resilient, fault-tolerant agent-based systems. It includes circuit breakers, retry logic, backpressure management, idempotency handling, and state machines.

**Key Components:**
- **Circuit Breaker** (`circuit_breaker.py`): Prevent cascading failures
- **Retry Logic** (`retry.py`): Automatic retry with backoff
- **Backpressure** (`backpressure.py`): Load management and throttling
- **Idempotency** (`idempotency.py`): Duplicate request handling
- **State Machine** (`state_machine.py`): Reliable state transitions

---

## 2. Circuit Breaker

### 2.1 Implementation

```python
from AgentOperatingSystem.reliability.circuit_breaker import CircuitBreaker, CircuitState

# Create circuit breaker
circuit = CircuitBreaker(
    name="external_api",
    failure_threshold=5,        # Open after 5 failures
    success_threshold=2,        # Close after 2 successes
    timeout_seconds=60,         # Try half-open after 60s
    failure_window_seconds=60   # Count failures in 60s window
)

# Protected operation
@circuit.protected
async def call_external_api():
    response = await http_client.get("https://api.example.com/data")
    return response.json()

# Use circuit breaker
try:
    result = await call_external_api()
except CircuitOpenError:
    # Circuit is open, use fallback
    result = get_cached_data()
```

### 2.2 Circuit States

```python
class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open" # Testing recovery
```

**State Transitions:**
- `CLOSED → OPEN`: When failure threshold exceeded
- `OPEN → HALF_OPEN`: After timeout period
- `HALF_OPEN → CLOSED`: After success threshold met
- `HALF_OPEN → OPEN`: On any failure

### 2.3 Fallback Strategies

```python
# Define fallback
def fallback_handler():
    return {"data": "cached", "source": "fallback"}

circuit = CircuitBreaker(
    name="service",
    fallback=fallback_handler
)

# Automatic fallback when circuit is open
result = await circuit.call(risky_operation)
```

### 2.4 Monitoring

```python
# Get circuit status
status = circuit.get_status()
# {
#   "state": "closed",
#   "failure_count": 2,
#   "success_count": 10,
#   "last_failure_time": "2025-12-25T00:00:00Z"
# }

# Reset circuit
circuit.reset()
```

---

## 3. Retry Logic

### 3.1 Retry Decorator

```python
from AgentOperatingSystem.reliability.retry import retry, RetryConfig

# Simple retry
@retry(max_attempts=3)
async def flaky_operation():
    result = await unreliable_service.call()
    return result

# Advanced retry with backoff
@retry(
    max_attempts=5,
    initial_delay=1.0,
    max_delay=60.0,
    exponential_base=2,
    jitter=True,
    retry_on=[TimeoutError, ConnectionError]
)
async def network_call():
    return await api.fetch_data()
```

### 3.2 Retry Configuration

```python
retry_config = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,        # Start with 1 second
    max_delay=30.0,           # Cap at 30 seconds
    exponential_base=2,       # Double each retry
    jitter=True,              # Add randomness
    retry_on=[TimeoutError],  # Only retry on specific errors
    on_retry=log_retry        # Callback on each retry
)

@retry(config=retry_config)
async def operation():
    pass
```

### 3.3 Retry Strategies

**Exponential Backoff:**
```python
# Delays: 1s, 2s, 4s, 8s, 16s
@retry(
    initial_delay=1,
    exponential_base=2,
    max_attempts=5
)
```

**Linear Backoff:**
```python
# Delays: 1s, 2s, 3s, 4s, 5s
@retry(
    initial_delay=1,
    linear_increment=1,
    max_attempts=5
)
```

**Fixed Delay:**
```python
# Delays: 5s, 5s, 5s
@retry(
    initial_delay=5,
    exponential_base=1,  # No exponential growth
    max_attempts=3
)
```

---

## 4. Backpressure Management

### 4.1 Rate Limiting

```python
from AgentOperatingSystem.reliability.backpressure import RateLimiter

# Create rate limiter
limiter = RateLimiter(
    max_requests=100,     # Max requests
    time_window=60        # Per 60 seconds
)

# Apply rate limiting
@limiter.limit
async def api_endpoint(request):
    return await process_request(request)

# Check if allowed
if limiter.is_allowed(user_id):
    await process_request()
else:
    raise TooManyRequestsError()
```

### 4.2 Throttling

```python
from AgentOperatingSystem.reliability.backpressure import Throttler

# Create throttler
throttler = Throttler(
    max_concurrent=10,        # Max concurrent operations
    queue_size=100,           # Queue size for waiting
    timeout_seconds=30        # Max wait time
)

# Throttle operation
async with throttler.acquire():
    await expensive_operation()
```

### 4.3 Load Shedding

```python
from AgentOperatingSystem.reliability.backpressure import LoadShedder

shedder = LoadShedder(
    max_load=0.8,            # Shed at 80% capacity
    priority_levels=3        # Support 3 priority levels
)

# Shed low priority requests under load
if shedder.should_shed(priority=1):  # Low priority
    raise ServiceUnavailableError("System overloaded")

await process_request(request)
```

---

## 5. Idempotency

### 5.1 Idempotent Operations

```python
from AgentOperatingSystem.reliability.idempotency import IdempotencyManager

idempotency = IdempotencyManager()

# Ensure operation runs only once per key
@idempotency.ensure_idempotent
async def process_payment(payment_id: str, amount: float):
    # This will only execute once for each payment_id
    result = await payment_service.charge(amount)
    return result

# Call with idempotency key
result = await process_payment(
    payment_id="pay_12345",
    amount=100.0,
    idempotency_key="pay_12345"
)

# Duplicate call returns cached result
result2 = await process_payment(
    payment_id="pay_12345",
    amount=100.0,
    idempotency_key="pay_12345"
)
# result2 == result, no duplicate charge
```

### 5.2 Idempotency Storage

```python
# Configure storage backend
idempotency = IdempotencyManager(
    storage=redis_client,
    ttl_seconds=86400  # 24 hours
)

# Manual idempotency check
key = f"operation_{operation_id}"
if await idempotency.exists(key):
    return await idempotency.get_result(key)

result = await perform_operation()
await idempotency.store(key, result)
```

---

## 6. State Machine

### 6.1 State Machine Definition

```python
from AgentOperatingSystem.reliability.state_machine import StateMachine, State, Transition

# Define states
class WorkflowState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Define state machine
workflow_sm = StateMachine(
    initial_state=WorkflowState.PENDING,
    states=[
        State(WorkflowState.PENDING, on_enter=log_pending),
        State(WorkflowState.RUNNING, on_enter=start_workflow),
        State(WorkflowState.COMPLETED, on_enter=cleanup),
        State(WorkflowState.FAILED, on_enter=handle_failure)
    ],
    transitions=[
        Transition(WorkflowState.PENDING, WorkflowState.RUNNING, "start"),
        Transition(WorkflowState.RUNNING, WorkflowState.COMPLETED, "complete"),
        Transition(WorkflowState.RUNNING, WorkflowState.FAILED, "fail"),
        Transition(WorkflowState.FAILED, WorkflowState.PENDING, "retry")
    ]
)
```

### 6.2 State Transitions

```python
# Get current state
current = workflow_sm.current_state

# Trigger transition
await workflow_sm.trigger("start")

# Check if transition is valid
if workflow_sm.can_transition("complete"):
    await workflow_sm.trigger("complete")

# Get valid transitions
valid_transitions = workflow_sm.get_valid_transitions()
```

### 6.3 State Persistence

```python
# Save state
state_data = workflow_sm.serialize()
await storage.save("workflow_state", state_data)

# Restore state
state_data = await storage.load("workflow_state")
workflow_sm.deserialize(state_data)
```

---

## 7. Resilience Patterns

### 7.1 Bulkhead Pattern

```python
from AgentOperatingSystem.reliability.bulkhead import Bulkhead

# Isolate resources
bulkhead = Bulkhead(
    compartments={
        "critical": {"max_concurrent": 10, "queue_size": 20},
        "normal": {"max_concurrent": 5, "queue_size": 10},
        "background": {"max_concurrent": 2, "queue_size": 5}
    }
)

# Execute in compartment
async with bulkhead.acquire("critical"):
    await critical_operation()
```

### 7.2 Timeout Pattern

```python
import asyncio

# Set timeout
async def with_timeout(coro, timeout_seconds):
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error("Operation timed out")
        raise

result = await with_timeout(slow_operation(), 30)
```

### 7.3 Fallback Pattern

```python
async def resilient_operation():
    try:
        return await primary_service.call()
    except Exception as e:
        logger.warning(f"Primary failed: {e}, using fallback")
        try:
            return await fallback_service.call()
        except Exception as e2:
            logger.error(f"Fallback failed: {e2}, using cache")
            return get_cached_result()
```

---

## 8. Monitoring and Metrics

### 8.1 Reliability Metrics

```python
from AgentOperatingSystem.observability.metrics import metrics

# Track circuit breaker
metrics.gauge("circuit_breaker.state", state_value, tags={"circuit": name})
metrics.increment("circuit_breaker.failures", tags={"circuit": name})

# Track retries
metrics.increment("retry.attempts", tags={"operation": op_name})
metrics.timing("retry.delay", delay_ms)

# Track backpressure
metrics.gauge("backpressure.queue_depth", depth)
metrics.increment("backpressure.shed_requests")
```

### 8.2 Health Checks

```python
# Circuit breaker health
def check_circuit_health():
    return {
        "circuit_breaker": {
            "state": circuit.state.value,
            "failure_rate": circuit.failure_rate(),
            "healthy": circuit.state == CircuitState.CLOSED
        }
    }

# Rate limiter health
def check_rate_limiter_health():
    return {
        "rate_limiter": {
            "current_rate": limiter.current_rate(),
            "limit": limiter.max_requests,
            "healthy": limiter.current_rate() < limiter.max_requests
        }
    }
```

---

## 9. Best Practices

### 9.1 Circuit Breaker
1. **Set appropriate thresholds** based on service characteristics
2. **Implement fallbacks** for critical operations
3. **Monitor circuit state** and alert on open circuits
4. **Test failure scenarios** regularly
5. **Use different circuits** for different dependencies

### 9.2 Retry Logic
1. **Use exponential backoff** to reduce load
2. **Add jitter** to prevent thundering herd
3. **Set maximum delays** to avoid indefinite waits
4. **Retry only on transient errors**
5. **Log retry attempts** for debugging

### 9.3 Backpressure
1. **Set appropriate limits** based on capacity
2. **Implement graceful degradation**
3. **Prioritize critical requests**
4. **Monitor queue depths**
5. **Alert on sustained high load**

---

**Document Approval:**
- **Status:** Implemented and Active
- **Last Updated:** December 25, 2025
- **Owner:** AOS Reliability Team
