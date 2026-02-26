# Contributing to aos-realm-of-agents

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
- Azure Functions Core Tools v4
- `git`

---

## Setup

```bash
# 1. Fork and clone
git clone https://github.com/<your-fork>/aos-realm-of-agents.git
cd aos-realm-of-agents

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Run locally
func start
```

---

## Project Structure

```
aos-realm-of-agents/
├── src/
│   ├── function_app.py
│   ├── function_app_original.py
│   ├── agent_config_schema.py
│   ├── example_agent_registry.json
│   ├── host.json
│   └── requirements.txt
├── tests/
│   ├── __init__.py
│   └── test_realm_of_agents.py
├── docs/
│   ├── architecture.md
│   ├── RealmOfAgents.md
│   ├── MIGRATION_TO_FOUNDRY.md
│   ├── api-reference.md
│   └── contributing.md       ← this file
├── .github/
│   ├── workflows/ci.yml
│   └── instructions/realm-of-agents.instructions.md
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## Testing

Tests use **pytest** with **pytest-asyncio**.

### Run all tests

```bash
pytest tests/ -v
```

### Run with coverage

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Linting

```bash
pylint src/ --fail-under=5.0
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
   pylint src/
   ```

6. **Commit** with a clear message (see [Commit Messages](#commit-messages)).

7. **Push** your branch and open a Pull Request against `main`.

---

## Code Style

- **Python 3.10+** type hints on all public functions and methods.
- `async def` for any I/O-bound operation.
- `snake_case` for functions, variables, and module names.
- `PascalCase` for class names.
- Maximum line length: **120 characters**.

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`

---

## Pull Request Checklist

Before submitting:

- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] New tests written for the changed/added code
- [ ] Pylint score ≥ 5.0 (`pylint src/ --fail-under=5.0`)
- [ ] Documentation updated if the public API changed
- [ ] CI is green

---

## Getting Help

- Open a [GitHub Issue](https://github.com/ASISaga/aos-realm-of-agents/issues)
- Join the discussion in
  [ASISaga/AgentOperatingSystem](https://github.com/ASISaga/AgentOperatingSystem/discussions)
