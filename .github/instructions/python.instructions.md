---
applyTo: "**/*.py"
description: "Python coding standards: PEP 8, async, type hints, AOS SDK patterns"
---

# Python Coding Standards

## Style & Formatting

- Follow **PEP 8** conventions (4-space indentation, 88-char line limit)
- Use **type hints** on all function signatures (`-> dict`, `List[str]`, etc.)
- Use `from __future__ import annotations` at the top of each module
- Write **Google-style docstrings** for public functions and classes
- Use double-quoted strings consistently

## Async Patterns

All workflows are `async` functions using `await`:

```python
@app.workflow("workflow-name")
async def my_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    agents = await request.client.list_agents()
    status = await request.client.start_orchestration(...)
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}
```

- **Always `await`** SDK calls — they are all coroutines
- Use `asyncio_mode = "auto"` (configured in `pyproject.toml`) for pytest-asyncio
- Avoid blocking I/O in async functions

## Type Hints

```python
from typing import Any, Dict, List, Callable

async def select_c_suite_agents(client: AOSClient) -> List[AgentDescriptor]: ...
async def my_workflow(request: WorkflowRequest) -> Dict[str, Any]: ...
```

- Use `Dict`, `List`, `Any` from `typing` for Python 3.10 compatibility
- Use `Callable[[ArgType], ReturnType]` for function parameters

## Imports

Order: stdlib → third-party → local, with blank lines between groups:

```python
from __future__ import annotations

import logging
from typing import Any, Dict, List

from aos_client import AOSApp, WorkflowRequest
```

## Logging

Use the module-level logger — never use `print()`:

```python
logger = logging.getLogger(__name__)
logger.info("Orchestration started: %s", orchestration_id)
```

## Error Handling

Raise `ValueError` with descriptive messages when required agents are unavailable:

```python
if not agent_ids:
    raise ValueError("No matching agents available in the catalog")
```

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v                              # Run all tests
pytest tests/ -v -k "test_name"              # Run specific test
pylint src/                                   # Lint
```

- Use `pytest` classes (not `unittest.TestCase`)
- Use descriptive test method names: `test_<what>_<condition>`
- Test constants, registration counts, and negative assertions (things that should NOT be registered)

## Tool Integration

```bash
pytest tests/ -v          # Validate correctness
pylint src/               # Enforce code quality
pip install -e ".[dev]"   # Install dependencies
```

## Related Documentation

→ **Repository spec**: `.github/specs/repository.md`  
→ **Azure Functions patterns**: `.github/instructions/azure-functions.instructions.md`  
→ **Conventional tools**: `.github/docs/conventional-tools.md`  
→ **Agent guidelines**: `/docs/specifications/github-copilot-agent-guidelines.md`  
→ **Architecture**: `/docs/specifications/architecture.md`  
→ **Build & deployment**: `/docs/specifications/build-deployment.md`
