---
applyTo: "src/aos_intelligence/**/*.py,tests/**/*.py,examples/**/*.py"
---

# aos-intelligence Development Instructions

## Package conventions

- All IO operations are `async`/`await`.
- `MLConfig` is the single source of truth for all configuration; always construct via `MLConfig(...)` or `MLConfig.from_env()`.
- Storage backends are dependency-injected: `KnowledgeManager(storage_manager=<any>)`. Never import storage classes directly.
- Optional ML training deps (`torch`, `transformers`, `trl`, `peft`) are always guarded with `try/except ImportError`.
- Use `logging.getLogger("AOS.<module>")` for all loggers.

## Code style

- Python 3.10+; use `from __future__ import annotations` only when needed for forward references.
- Type hints on all public methods.
- Line length ≤ 120 characters.
- Follow existing naming: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.

## Testing

- Use `pytest` with `asyncio_mode = "auto"` (configured in `pyproject.toml`).
- Mock storage: `MagicMock()` with `AsyncMock` for async methods (`exists`, `read_json`, `write_json`).
- Do not require real ChromaDB, Azure, or GPU resources in unit tests.

## Imports order

1. Standard library
2. Third-party (pydantic, torch, chromadb — always guarded with try/except)
3. Local (`from aos_intelligence.config import MLConfig`)
