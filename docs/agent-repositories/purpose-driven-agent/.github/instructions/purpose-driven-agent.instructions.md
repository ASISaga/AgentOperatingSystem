# Copilot Coding Instructions — purpose-driven-agent

## Language & Version

- Python 3.10+
- All public functions and methods must have type hints
- Use `Optional[X]` (not `X | None`) for optional parameters

## Package conventions

- Import from `purpose_driven_agent` (the package root), not from sub-modules
  unless necessary:
  ```python
  # Preferred
  from purpose_driven_agent import GenericPurposeDrivenAgent

  # When needed
  from purpose_driven_agent.context_server import ContextMCPServer
  ```

- `PurposeDrivenAgent` is abstract; never generate code that instantiates it
  directly.

- Always use `await` on async methods:
  ```python
  await agent.initialize()
  await agent.handle_event(event)
  ```

## Async patterns

- Agent methods that do I/O (`initialize`, `start`, `stop`, `handle_event`,
  `add_goal`, `get_state`, etc.) are all `async def`.
- Wrap non-async entry points with `asyncio.run(main())`.

## Test patterns

```python
import pytest
from purpose_driven_agent import GenericPurposeDrivenAgent

@pytest.mark.asyncio
async def test_example() -> None:
    agent = GenericPurposeDrivenAgent(agent_id="x", purpose="Testing")
    result = await agent.initialize()
    assert result is True
```

- Use `pytest-asyncio` with `asyncio_mode = "auto"` (set in `pyproject.toml`).
- Place shared fixtures in `tests/conftest.py`.

## Subclassing

When generating a custom agent subclass:

```python
from typing import List
from purpose_driven_agent import PurposeDrivenAgent

class MyAgent(PurposeDrivenAgent):
    def get_agent_type(self) -> List[str]:
        available = self.get_available_personas()
        return ["my_persona"] if "my_persona" in available else ["my_persona"]
```

## Error handling

- Use specific exception types where possible.
- Catch broad exceptions at public API boundaries only; include logging:
  ```python
  except Exception as exc:  # pylint: disable=broad-exception-caught
      self.logger.error("Descriptive message: %s", exc)
  ```

## Logging

- Use `self.logger` (a `logging.Logger` bound to the agent ID).
- Prefer `%s` formatting over f-strings in log calls.

## Line length

Maximum 120 characters per line.
