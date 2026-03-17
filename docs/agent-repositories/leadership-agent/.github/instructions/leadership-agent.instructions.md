# Copilot Coding Instructions — leadership-agent

## Language & Version

- Python 3.10+
- All public functions and methods must have type hints
- `Optional[X]` not `X | None`

## Package conventions

```python
# Preferred import
from leadership_agent import LeadershipAgent

# Creating an agent — agent_id is the only required param
agent = LeadershipAgent(agent_id="my-leader")

# Always await lifecycle methods
await agent.initialize()
await agent.start()
decision = await agent.make_decision(context={...})
await agent.stop()
```

## Decision patterns

```python
# Autonomous decision
decision = await agent.make_decision(
    context={"proposal": "...", "budget": 100_000},
    mode="autonomous",
)

# Access outcome
print(decision["decision"])   # from _evaluate_decision()
print(decision["id"])         # UUID string
```

## Overriding `_evaluate_decision`

Always override for real decision logic:

```python
class MyAgent(LeadershipAgent):
    async def _evaluate_decision(self, context: Dict[str, Any]) -> Any:
        return {"approved": True, "reason": "Custom logic"}
```

## `consult_stakeholders` note

`consult_stakeholders()` raises `NotImplementedError`.  When generating code
that calls it, always wrap in `try/except NotImplementedError` or provide an
override with a message bus integration.

## Test patterns

```python
import pytest
from leadership_agent import LeadershipAgent

@pytest.mark.asyncio
async def test_decision() -> None:
    agent = LeadershipAgent(agent_id="t")
    await agent.initialize()
    d = await agent.make_decision(context={"x": 1})
    assert "id" in d
```

## Line length

Maximum 120 characters.

## Logging

Use `self.logger` with `%s` formatting, not f-strings.
