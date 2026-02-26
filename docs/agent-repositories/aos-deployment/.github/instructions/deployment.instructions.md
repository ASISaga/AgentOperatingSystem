# Deployment Instructions

## Azure Deployment

- Use the Python orchestrator (`deployment/deploy.py`) for all deployments
- Always run Bicep linting before deployment
- Use what-if analysis for production deployments
- Follow the regional validation workflow for new regions

## Deployment Patterns

- Environment-specific parameters in `deployment/parameters/`
- Modular Bicep templates in `deployment/modules/`
- Health checks run automatically post-deployment

## Error Handling

- Logic errors (BCP codes, syntax) → Auto-fix via deployment-error-fixer
- Environmental errors (timeout, throttling) → Auto-retry with backoff

## Code Style

- Python 3.10+ with full type hints
- Line length: 120 characters maximum
- Use `async def` for I/O-bound operations
- Follow PEP 8 naming conventions
- Imports: stdlib → third-party → local

## Bicep Style

- Use modules for reusable components
- Parameterize environment-specific values
- Include descriptions on all parameters
- Use `@secure()` decorator for secrets

## Testing

- Run `pytest deployment/tests/` before committing
- Test Bicep with `az bicep build --file deployment/main-modular.bicep --stdout`
- Validate parameters with the orchestrator's `--plan-only` flag
