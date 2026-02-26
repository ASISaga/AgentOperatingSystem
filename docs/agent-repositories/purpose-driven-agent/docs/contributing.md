# Contributing to purpose-driven-agent

Thank you for your interest in contributing!  This guide covers everything you
need to set up the development environment, write tests, run linting, and
submit a pull request.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Project Structure](#project-structure)
4. [Testing](#testing)
5. [Linting](#linting)
6. [Contribution Workflow](#contribution-workflow)
7. [Code Style](#code-style)
8. [Commit Messages](#commit-messages)
9. [Pull Request Checklist](#pull-request-checklist)

---

## Prerequisites

- Python 3.10 or higher
- `git`
- Optionally: `make`

---

## Setup

```bash
# 1. Fork and clone
git clone https://github.com/<your-fork>/purpose-driven-agent.git
cd purpose-driven-agent

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate.bat    # Windows

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Verify the installation
python -c "from purpose_driven_agent import GenericPurposeDrivenAgent; print('OK')"
```

---

## Project Structure

```
purpose-driven-agent/
├── src/
│   └── purpose_driven_agent/
│       ├── __init__.py          # Public API exports
│       ├── agent.py             # PurposeDrivenAgent + GenericPurposeDrivenAgent
│       ├── context_server.py    # ContextMCPServer implementation
│       └── ml_interface.py      # IMLService abstract interface
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared pytest fixtures
│   └── test_purpose_driven_agent.py
├── examples/
│   └── basic_usage.py
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   └── contributing.md          ← this file
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
└── README.md
```

---

## Testing

Tests use **pytest** with **pytest-asyncio**.  All async tests must be
decorated with `@pytest.mark.asyncio`.

### Run all tests

```bash
pytest tests/ -v
```

### Run a single test file

```bash
pytest tests/test_purpose_driven_agent.py -v
```

### Run with coverage

```bash
pytest tests/ --cov=purpose_driven_agent --cov-report=term-missing
```

### Test naming conventions

- Test files: `test_<module>.py`
- Test classes: `Test<Feature>` (no docstring required)
- Test functions: `test_<what_is_being_tested>`

### Writing tests

```python
import pytest
from purpose_driven_agent import GenericPurposeDrivenAgent

@pytest.mark.asyncio
async def test_initialize_returns_true() -> None:
    agent = GenericPurposeDrivenAgent(
        agent_id="test", purpose="Testing"
    )
    result = await agent.initialize()
    assert result is True
```

For shared fixtures, add them to `tests/conftest.py`.

---

## Linting

This project uses **Pylint** for static analysis.

### Run Pylint

```bash
# Entire source package
pylint src/purpose_driven_agent

# Single file
pylint src/purpose_driven_agent/agent.py

# With minimum score enforcement
pylint src/purpose_driven_agent --fail-under=7.0
```

### Pylint configuration

Pylint is configured in `pyproject.toml` under `[tool.pylint.*]`:

- Max line length: 120
- Disabled: `missing-module-docstring`, `missing-class-docstring`,
  `missing-function-docstring`, `too-few-public-methods`

### Type checking

```bash
mypy src/purpose_driven_agent
```

### Formatting

```bash
# Format with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/
```

---

## Contribution Workflow

1. **Create a branch** from `main`:

   ```bash
   git checkout -b feat/my-new-feature
   ```

2. **Make your changes**, following the code style guidelines below.

3. **Write or update tests** for every code change.

4. **Run the full test suite** and ensure it passes:

   ```bash
   pytest tests/ -v
   ```

5. **Run Pylint** and address all warnings:

   ```bash
   pylint src/purpose_driven_agent
   ```

6. **Commit** with a clear message (see [Commit Messages](#commit-messages)).

7. **Push** your branch and open a Pull Request against `main`.

8. Ensure all CI checks pass before requesting review.

---

## Code Style

- **Python 3.10+** type hints on all public functions and methods.
- `async def` for any I/O-bound operation.
- `snake_case` for functions, variables, and module names.
- `PascalCase` for class names.
- `UPPER_SNAKE_CASE` for module-level constants.
- Maximum line length: **120 characters**.
- Use `Optional[X]` rather than `X | None` for compatibility.
- Prefer f-strings for logging and string formatting.
- Use descriptive variable names; avoid single-letter names outside comprehensions.

### Error handling

```python
# Good — specific exception types
try:
    await agent.initialize()
except ConnectionError as exc:
    logger.error("Connection failed: %s", exc)
    raise

# Acceptable with logging when catching broad exceptions at a boundary
try:
    result = await risky_operation()
except Exception as exc:  # pylint: disable=broad-exception-caught
    logger.error("Unexpected error: %s", exc)
    return {"status": "error", "error": str(exc)}
```

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`

**Examples:**

```
feat(agent): add purpose-driven decision making method
fix(context_server): handle empty context on initialize
docs(api-reference): document IMLService abstract methods
test(agent): add tests for update_goal_progress
```

---

## Pull Request Checklist

Before submitting:

- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] New tests written for the changed/added code
- [ ] Pylint score ≥ 7.0 (`pylint src/purpose_driven_agent --fail-under=7.0`)
- [ ] Type hints present on all public functions
- [ ] Docstrings updated or added
- [ ] `docs/api-reference.md` updated if the public API changed
- [ ] `CHANGELOG.md` entry added (if applicable)
- [ ] CI is green

---

## Getting Help

- Open a [GitHub Issue](https://github.com/ASISaga/purpose-driven-agent/issues)
- Join the discussion in
  [ASISaga/AgentOperatingSystem](https://github.com/ASISaga/AgentOperatingSystem/discussions)
