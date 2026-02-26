# Contributing to cmo-agent

Thank you for contributing!  This guide covers development setup, testing,
linting, and the pull-request workflow for `cmo-agent`.

---

## Prerequisites

- Python 3.10+
- `git`
- `leadership-agent>=1.0.0` and `purpose-driven-agent>=1.0.0` (installed
  automatically)

---

## Setup

```bash
git clone https://github.com/<your-fork>/cmo-agent.git
cd cmo-agent

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

# Verify
python -c "from cmo_agent import CMOAgent; print('OK')"
```

---

## Project Structure

```
cmo-agent/
├── src/
│   └── cmo_agent/
│       ├── __init__.py   # exports CMOAgent
│       └── agent.py      # CMOAgent implementation
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_cmo_agent.py
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
pytest tests/ --cov=cmo_agent --cov-report=term-missing

# Single file
pytest tests/test_cmo_agent.py -v
```

### Test conventions

- File: `test_<module>.py`
- Class: `Test<Feature>`
- Function: `test_<what_is_being_tested>`
- All async tests use `@pytest.mark.asyncio`

### Example test

```python
import pytest
from cmo_agent import CMOAgent

@pytest.mark.asyncio
async def test_execute_with_purpose() -> None:
    cmo = CMOAgent(agent_id="test-cmo")
    await cmo.initialize()
    result = await cmo.execute_with_purpose(
        {"type": "brand_audit"}, purpose_type="marketing"
    )
    assert result["purpose_type"] == "marketing"
    assert result["adapter_used"] == "marketing"
```

---

## Linting

```bash
# Run Pylint
pylint src/cmo_agent

# Enforce minimum score
pylint src/cmo_agent --fail-under=7.0

# Type checking
mypy src/cmo_agent

# Formatting
black src/ tests/
isort src/ tests/
```

---

## Contribution Workflow

1. Fork and create a branch: `git checkout -b feat/my-change`
2. Make changes with type hints and docstrings
3. Write or update tests
4. `pytest tests/ -v` — all tests must pass
5. `pylint src/cmo_agent --fail-under=7.0`
6. Commit with [Conventional Commits](https://www.conventionalcommits.org/)
7. Open a PR against `main`

---

## Code Style

- Python 3.10+ type hints on all public APIs
- `async def` for I/O-bound methods
- Max line length: 120 characters
- `self.logger` with `%s` formatting (not f-strings) for log calls
- `Optional[X]` not `X | None`

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

- [GitHub Issues](https://github.com/ASISaga/cmo-agent/issues)
- [ASISaga/AgentOperatingSystem Discussions](https://github.com/ASISaga/AgentOperatingSystem/discussions)
