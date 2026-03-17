# Contributing to aos-intelligence

## Setup

```bash
git clone https://github.com/ASISaga/aos-intelligence.git
cd aos-intelligence
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=aos_intelligence --cov-report=term-missing

# Specific test file
pytest tests/test_ml_pipeline.py -v
pytest tests/test_lorax.py -v
pytest tests/test_learning.py -v
pytest tests/test_knowledge.py -v
```

Tests use `pytest-asyncio` with `asyncio_mode = "auto"` — no need for `@pytest.mark.asyncio`
decorators in most cases.

## Running Linter

```bash
pylint src/aos_intelligence
```

Target score: **≥ 7.0 / 10**.

## Optional Dependencies

Install extra dependency groups to test features requiring them:

```bash
pip install -e ".[ml]"       # ML training (torch, transformers, trl, peft, …)
pip install -e ".[rag]"      # RAG support (chromadb)
pip install -e ".[foundry]"  # Azure AI Agents integration
pip install -e ".[full]"     # all extras
```

## Project Structure

```
src/aos_intelligence/
├── __init__.py          ← public API
├── config.py            ← MLConfig (standalone, no external deps)
├── ml/                  ← ML pipeline, LoRAx, DPO, self-learning, Foundry
├── learning/            ← knowledge management, RAG, interaction learning
└── knowledge/           ← evidence, indexing, precedent
tests/
├── conftest.py
├── test_ml_pipeline.py
├── test_lorax.py
├── test_dpo_trainer.py
├── test_learning.py
└── test_knowledge.py
examples/
├── ml_pipeline_example.py
├── self_learning_example.py
└── rag_example.py
```

## Adding a New Feature

1. Add source code in the appropriate sub-package (`ml/`, `learning/`, or `knowledge/`)
2. Export from the sub-package `__init__.py`
3. Write tests in `tests/test_<module>.py`
4. Add an example in `examples/` if the feature has non-obvious usage
5. Update `docs/api-reference.md` with the new public API
6. Run `pytest tests/ -v` and `pylint src/aos_intelligence` before opening a PR

## Pull Request Guidelines

- Keep changes focused — one feature or bug fix per PR
- All tests must pass (`pytest tests/ -v`)
- Pylint score must remain ≥ 7.0
- Update `docs/api-reference.md` for any public API changes
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages

## Versioning

This package follows [Semantic Versioning](https://semver.org/):
- `MAJOR` — breaking API changes
- `MINOR` — new features, backward-compatible
- `PATCH` — bug fixes, backward-compatible

## Contact

Issues and PRs: [github.com/ASISaga/aos-intelligence](https://github.com/ASISaga/aos-intelligence)
