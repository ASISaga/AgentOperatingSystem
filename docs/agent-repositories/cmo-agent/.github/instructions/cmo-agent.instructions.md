# Copilot Coding Instructions — cmo-agent

## Language & Version

- Python 3.10+
- All public functions and methods must have type hints
- `Optional[X]` not `X | None`

## Package conventions

```python
# Preferred import
from cmo_agent import CMOAgent

# Creating an agent — agent_id is the only required parameter
cmo = CMOAgent(agent_id="cmo-001")

# Always await lifecycle methods
await cmo.initialize()
await cmo.start()
```

## execute_with_purpose patterns

```python
# Marketing adapter
result = await cmo.execute_with_purpose(
    {"type": "brand_audit", "data": {"brand": "Acme"}},
    purpose_type="marketing",
)

# Leadership adapter
result = await cmo.execute_with_purpose(
    {"type": "budget_review"},
    purpose_type="leadership",
)

# Access results
print(result["purpose_type"])   # "marketing" | "leadership"
print(result["adapter_used"])   # adapter name
print(result["status"])         # "success" | "error"
```

## get_adapter_for_purpose

```python
# Lookup — case insensitive
adapter = cmo.get_adapter_for_purpose("marketing")   # "marketing"
adapter = cmo.get_adapter_for_purpose("Leadership")  # "leadership"

# Always wrap unknown inputs:
try:
    adapter = cmo.get_adapter_for_purpose(user_input)
except ValueError as exc:
    logger.error("Unknown purpose: %s", exc)
```

## get_status

```python
status = await cmo.get_status()
# Access dual-purpose info:
purposes = status["purposes"]        # {"marketing": {...}, "leadership": {...}}
mapping  = status["purpose_adapter_mapping"]  # {"marketing": "...", "leadership": "..."}
primary  = status["primary_adapter"] # always "marketing" by default
```

## Test patterns

```python
import pytest
from cmo_agent import CMOAgent

@pytest.mark.asyncio
async def test_execute_marketing() -> None:
    cmo = CMOAgent(agent_id="t")
    await cmo.initialize()
    result = await cmo.execute_with_purpose(
        {"type": "test"}, purpose_type="marketing"
    )
    assert result["adapter_used"] == "marketing"
```

## Adapter restoration

When generating code that calls `execute_with_purpose()`, **never** assume
`adapter_name` is changed permanently after the call — the method always
restores it via `try/finally`.

## Line length

Maximum 120 characters.

## Logging

Use `self.logger` with `%s` formatting.
