# Contributing to AOS Kernel

## Development Setup

```bash
git clone https://github.com/ASISaga/aos-kernel.git
cd aos-kernel
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Quality

```bash
pylint src/AgentOperatingSystem
```

## Guidelines

- Follow PEP 8 style (120 char line length)
- Use type hints
- Write async functions for I/O operations
- Maintain Pylint score above 5.0/10
