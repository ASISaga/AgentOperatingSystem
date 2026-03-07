# Conventional Tools Reference

**Last Updated**: 2026-03-07  
**Audience**: Developers, Copilot Coding Agents

## Introduction

This document catalogs all tools that GitHub Copilot coding agents leverage in this repository. These tools provide automated validation, testing, and build processes that agents orchestrate rather than duplicate.

## Philosophy: Tool Leverage

**AI agents SUPERCHARGE existing tools** through orchestration:

- **Never duplicate**: Reference existing commands, don't reimplement
- **Automate validation**: Use linters and validators already configured
- **Compose workflows**: Chain existing tools for complex tasks
- **Continuous feedback**: Run tools frequently during development

## Python Tools

All automation uses standard Python tooling:

### Primary Commands

```bash
pip install -e ".[dev]"               # Install all dev dependencies
pytest tests/ -v                      # Run all tests
pytest tests/ -v -k "test_name"       # Run specific tests
pylint src/         # Lint source code
```

### Recommended Workflow

**Before committing:**
```bash
pytest tests/ -v && pylint src/
```

**During development:**
```bash
pytest tests/ -v -k "relevant_test"   # Quick targeted check
```

**Full validation:**
```bash
pytest tests/ -v                      # All tests
pylint src/         # Full lint
```

## Tool Details

### 1. pytest

**Purpose**: Unit and integration testing

**Configuration**: `pyproject.toml` (`[tool.pytest.ini_options]`)

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Key features:**
- `asyncio_mode = "auto"` enables async test functions without explicit decorators
- Test discovery in `tests/` directory
- Parametrize, fixtures, and class-based test organization

**When agents should use:**
- After making any code changes
- Before committing Python files
- When debugging test failures
- To verify workflow registration

### 2. pylint

**Purpose**: Enforces code quality and style standards

**Configuration**: Defaults (no `.pylintrc` — uses project standard)

**Key rules:**
- PEP 8 compliance
- Unused imports / variables
- Missing docstrings
- Type checking

**When agents should use:**
- After making code changes
- Before committing Python files
- To enforce code quality standards

### 3. pip / pyproject.toml

**Purpose**: Dependency and build management

**Configuration**: `pyproject.toml`

```bash
pip install -e ".[dev]"    # Install with dev extras (pytest, pylint)
pip install -e "."         # Production install only
```

**Dependencies:**
- `aos-client-sdk[azure]>=7.0.0` — SDK + Azure Functions + Service Bus + Auth
- `pytest>=8.0.0` (dev)
- `pytest-asyncio>=0.24.0` (dev)
- `pylint>=3.0.0` (dev)

## Agent Validation Scripts

Custom validation scripts in `.github/skills/*/scripts/`:

```bash
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh     # Quality audit
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh      # Find duplicates
./.github/skills/agent-evolution-agent/scripts/sync-agents-with-specs.sh  # Check spec refs
./.github/skills/agent-evolution-agent/scripts/recommend-improvements.sh  # Get recommendations
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh           # Record metrics
```

**When agents should use:**
- When working on agent system files
- Before committing skill/agent changes
- During agent ecosystem validation

**See**: `.github/docs/dogfooding-guide.md` for complete dogfooding workflow.

## CI/CD Integration

**GitHub Actions workflow:** `.github/workflows/ci.yml`

**Triggers:**
- Push to `main`
- Pull requests to `main`

**Matrix:** Python 3.10, 3.11, 3.12

**Steps:**
1. `pip install -e ".[dev]"`
2. `pytest tests/ -v`

## Quick Reference for Agents

### When making workflow changes (`workflows.py`):
```bash
pytest tests/ -v                      # Verify registration + logic
pylint src/         # Lint
```

### When adding a new workflow:
```bash
pytest tests/ -v -k "test_workflow"   # Targeted test
pytest tests/ -v                      # Full suite
```

### When making documentation changes:
```bash
# No specific tools - manual review
```

### Before committing anything:
```bash
pytest tests/ -v && pylint src/
```

## Best Practices for Agents

1. **Run tests early and often** — Don't wait until the end
2. **Use targeted tests** — `pytest -k "name"` for fast feedback
3. **Read error messages** — pytest and pylint provide specific guidance
4. **Compose workflows** — Chain commands with `&&`
5. **Don't duplicate tools** — Reference existing test infrastructure

## Error Interpretation

### Common pytest Errors

**`AssertionError` in workflow count test**
```
AssertionError: assert 9 == 10
```
→ A new workflow was added but `test_workflow_count` wasn't updated

**`ImportError`**
```
ImportError: cannot import name 'NewClass'
```
→ Check `aos-client-sdk` version and import path

**`AttributeError: 'NoneType'...`**
→ SDK mock is missing; check test fixtures

### Common pylint Errors

**`E0401: Unable to import 'aos_client'`**
→ Run `pip install -e ".[dev]"` first

**`C0114: Missing module docstring`**
→ Add a module-level docstring at the top of the file

## Agent Validation Tools

### Agent Evolution Scripts

**Purpose**: Self-improving agent quality validation (Ouroboros pattern)

**Location**: `.github/skills/agent-evolution-agent/scripts/`

| Script | Purpose | How to Run |
|--------|---------|------------|
| `audit-agent-quality.sh` | Complete quality audit | Direct execution |
| `detect-duplication.sh` | Find duplicate content | Direct execution |
| `sync-agents-with-specs.sh` | Check spec references | Direct execution |
| `recommend-improvements.sh` | Generate action items | Direct execution |
| `track-metrics.sh` | Record quality trends | Direct execution |
| `find-related-agents.sh <spec>` | Find agents for a spec | Direct execution |
| `measure-context-efficiency.sh <file>` | Efficiency score | Direct execution |

**Configuration**: None required, scripts are self-contained

**Metrics Storage**: `.github/metrics/` directory

**Best Practices:**
1. Run before making agent system changes
2. Track improvements with `track-metrics.sh --history`
3. Follow recommendations from `recommend-improvements.sh`
4. Verify zero duplication before committing

## Related Documentation

- **Repository spec**: `.github/specs/repository.md`
- **Dogfooding guide**: `.github/docs/dogfooding-guide.md` - Complete workflow
- **Agent metrics**: `.github/docs/agent-metrics.md` - Metric definitions
- **Agent philosophy**: `.github/docs/agent-philosophy.md` - Ouroboros pattern
- **CI workflow**: `.github/workflows/ci.yml`

---

**Version**: 2.0.0 - Adapted for Python/Azure Functions repositories  
**Last Updated**: 2026-03-07  
**Mechanism**: Reference this file from `copilot-instructions.md` instead of duplicating tool lists
