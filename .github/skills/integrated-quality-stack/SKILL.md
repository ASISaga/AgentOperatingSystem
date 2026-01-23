# Skill: Integrated Code Quality Stack

## Skill Overview

**Purpose**: Master the complete best-in-class code quality stack for AOS.

**When to use**: Before every commit, during code review, when investigating quality issues.

**Prerequisites**: Python 3.8+, repository dependencies installed.

For complete documentation, see: `docs/CODE_QUALITY_STACK.md`

## Quick Reference

### Setup
```bash
pip install -e ".[dev]"
pre-commit install
```

### Daily Use
```bash
# Format
black src/ tests/ function_app.py
isort src/ tests/ function_app.py

# Lint
pylint src/AgentOperatingSystem

# Full check
pre-commit run --all-files
```

### Tools Included
- Pylint (10.00/10) - Comprehensive linting
- Black - Code formatter
- isort - Import sorter
- mypy - Type checker
- Bandit - Security scanner
- Safety - Dependency scanner
- pytest - Testing

See full skill documentation in parent commit message.
