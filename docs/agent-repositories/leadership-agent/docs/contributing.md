# Contributing to leadership-agent

Thank you for contributing!  This guide covers development setup, testing,
linting, and the pull-request workflow.

---

## Prerequisites

- Python 3.10+
- `git`
- `purpose-driven-agent>=1.0.0` (installed automatically by `pip install -e ".[dev]"`)

---

## Setup

```bash
git clone https://github.com/<your-fork>/leadership-agent.git
cd leadership-agent

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

# Verify
python -c "from leadership_agent import LeadershipAgent; print('OK')"
```

---

## Project Structure

```
leadership-agent/
├── src/
│   └── leadership_agent/
│       ├── __init__.py      # exports LeadershipAgent
│       └── agent.py         # LeadershipAgent implementation
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_leadership_agent.py
├── examples/
│   └── basic_usage.py
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   └── contributing.md
├── .github/workflows/ci.yml
├── pyproject.toml
└── README.md
```

---

## Testing

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=leadership_agent --cov-report=term-missing

# Single file
pytest tests/test_leadership_agent.py -v
```

### Test conventions

- File: `test_<module>.py`
- Class: `Test<Feature>`
- Function: `test_<what_is_being_tested>`
- All async tests use `@pytest.mark.asyncio`

### Writing tests

```python
import pytest
from leadership_agent import LeadershipAgent

@pytest.mark.asyncio
async def test_make_decision_returns_id() -> None:
    agent = LeadershipAgent(agent_id="test-leader")
    await agent.initialize()
    decision = await agent.make_decision(context={"topic": "test"})
    assert "id" in decision
```

---

## Linting

```bash
# Run Pylint
pylint src/leadership_agent

# Enforce minimum score
pylint src/leadership_agent --fail-under=7.0

# Type checking
mypy src/leadership_agent

# Formatting
black src/ tests/
isort src/ tests/
```

---

## Contribution Workflow

1. Fork and create a branch: `git checkout -b feat/my-change`
2. Make changes with type hints and docstrings
3. Write tests covering the changes
4. Run `pytest tests/ -v` — all must pass
5. Run `pylint src/leadership_agent` — score ≥ 7.0
6. Commit with [Conventional Commits](https://www.conventionalcommits.org/)
7. Open a PR against `main`

---

## Code Style

- Python 3.10+ type hints on all public APIs
- `async def` for I/O-bound methods
- `snake_case` functions and variables
- `PascalCase` class names
- Max line length: 120 characters
- Use `self.logger` (not `print`) for runtime messages

---

## Pull Request Checklist

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] New tests added for changed code
- [ ] Pylint score ≥ 7.0
- [ ] Type hints on all public methods
- [ ] Docstrings updated
- [ ] `docs/api-reference.md` updated if public API changed
- [ ] CI green

---

## Getting Help

- [GitHub Issues](https://github.com/ASISaga/leadership-agent/issues)
- [ASISaga/AgentOperatingSystem Discussions](https://github.com/ASISaga/AgentOperatingSystem/discussions)
