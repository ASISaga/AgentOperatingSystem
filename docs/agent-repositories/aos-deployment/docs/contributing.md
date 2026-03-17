# Contributing to aos-deployment

## Prerequisites

- Python 3.10+
- Azure CLI (`az`) with Bicep extension
- Git

## Setup

```bash
git clone https://github.com/ASISaga/aos-deployment.git
cd aos-deployment
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Project Structure

```
deployment/
├── main-modular.bicep      # Primary Bicep template
├── deploy.py               # CLI entry point
├── modules/                # Bicep modules
├── parameters/             # Environment parameters
├── orchestrator/           # Python orchestrator
├── tests/                  # Tests
├── examples/               # Usage examples
└── docs/                   # Internal documentation
docs/                       # Public documentation
.github/                    # Workflows, skills, prompts
```

## Development Workflow

1. Create a feature branch from `main`
2. Make changes
3. Run tests: `pytest deployment/tests/ -v`
4. Validate Bicep: `az bicep build --file deployment/main-modular.bicep --stdout`
5. Run linting: `pylint deployment/`
6. Commit with conventional commit messages
7. Open a pull request

## Testing

```bash
# Run all tests
pytest deployment/tests/ -v

# Run with coverage
pytest deployment/tests/ --cov=deployment
```

## Linting

```bash
# Python linting
pylint deployment/ --fail-under=7.0

# Bicep linting
az bicep build --file deployment/main-modular.bicep --stdout
```

## Code Style

- Python 3.10+ with type hints on all public functions
- Line length: 120 characters maximum
- Use `async def` for I/O-bound operations
- Follow PEP 8 naming conventions
- Imports: stdlib → third-party → local

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add regional validation for swedencentral
fix: correct health check timeout calculation
docs: update deployment architecture diagram
chore: upgrade pydantic to 2.12
```

## Pull Request Checklist

- [ ] Tests pass (`pytest deployment/tests/`)
- [ ] Bicep validates (`az bicep build`)
- [ ] Pylint passes (`pylint deployment/ --fail-under=7.0`)
- [ ] Documentation updated if needed
- [ ] Conventional commit message used
