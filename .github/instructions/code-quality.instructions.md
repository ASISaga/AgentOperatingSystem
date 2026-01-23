# Code Quality Instructions for AOS

## Overview

This document provides comprehensive code quality guidelines for the Agent Operating System (AOS) repository, integrated with Pylint for automated code quality assurance.

## Pylint Integration

### Running Pylint

```bash
# Run on entire source code
pylint src/AgentOperatingSystem

# Run on specific module
pylint src/AgentOperatingSystem/agents

# Run on tests
pylint tests

# Generate detailed report
pylint src/AgentOperatingSystem --output-format=text > pylint-report.txt

# Check specific file
pylint src/AgentOperatingSystem/agents/perpetual_agent.py
```

### Pylint Configuration

The repository uses a comprehensive `.pylintrc` configuration in `pyproject.toml` that is tailored for:

- **Python 3.8+** compatibility
- **Async/await** patterns
- **Azure services** integration
- **Agent-based architecture** patterns
- **Type hints** and modern Python practices

### Key Pylint Settings

- **Line length**: 120 characters (extended from PEP 8's 79 for modern development)
- **Minimum score**: 5.0/10 (enforced in CI/CD)
- **Disabled warnings**: Documentation requirements, complexity metrics (handled by code review)
- **Enabled checks**: Syntax errors, logic errors, potential bugs, security issues

## Code Quality Standards

### 1. Async/Await Patterns

✅ **Good**:
```python
async def process_event(self, event: Event) -> Result:
    """Process an event asynchronously."""
    result = await self.handler.handle(event)
    await self.save_state(result)
    return result
```

❌ **Bad**:
```python
def process_event(self, event):  # Missing async
    result = self.handler.handle(event)  # Missing await
    return result
```

### 2. Type Hints

✅ **Good**:
```python
from typing import Optional, List, Dict, Any

async def get_agent_status(
    self,
    agent_id: str,
    include_metrics: bool = False
) -> Dict[str, Any]:
    """Get agent status with optional metrics."""
    status: Dict[str, Any] = {}
    # Implementation
    return status
```

❌ **Bad**:
```python
async def get_agent_status(self, agent_id, include_metrics=False):
    status = {}
    return status
```

### 3. Error Handling

✅ **Good**:
```python
async def connect_to_service(self) -> bool:
    """Connect to Azure service with proper error handling."""
    try:
        await self.client.connect()
        return True
    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
```

❌ **Bad**:
```python
async def connect_to_service(self):
    try:
        await self.client.connect()
        return True
    except:  # Too broad
        return False  # Silently fails
```

### 4. Naming Conventions

- **Classes**: `PascalCase` (e.g., `PurposeDrivenAgent`, `ContextMCPServer`)
- **Functions/Methods**: `snake_case` (e.g., `process_event`, `get_status`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private methods**: `_leading_underscore` (e.g., `_internal_method`)
- **Variables**: `snake_case`, descriptive names (e.g., `agent_id`, `event_queue`)

### 5. Import Organization

```python
# Standard library imports
import asyncio
import logging
from typing import Optional, Dict, Any

# Third-party imports
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel

# Local imports
from AgentOperatingSystem.agents import BaseAgent
from AgentOperatingSystem.mcp import ContextMCPServer
```

### 6. Documentation

While Pylint doesn't enforce docstrings in our config, we encourage:

```python
async def critical_operation(
    self,
    data: Dict[str, Any],
    timeout: Optional[int] = None
) -> bool:
    """
    Perform critical operation with timeout.
    
    Args:
        data: Operation data dictionary
        timeout: Optional timeout in seconds
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        TimeoutError: If operation exceeds timeout
        ValueError: If data is invalid
    """
    # Implementation
```

## Common Pylint Warnings and How to Fix Them

### 1. `unused-import`

```python
# Bad
import asyncio  # Imported but never used

# Good - Remove it
# Only import what you use
```

### 2. `undefined-variable`

```python
# Bad
result = undefined_var  # pylint: disable=undefined-variable

# Good
result = defined_var  # Variable is defined
```

### 3. `redefined-outer-name`

```python
# Bad
async def test_agent():
    agent = Agent()  # Shadows outer 'agent'
    
# Good
async def test_agent():
    test_agent_instance = Agent()
```

### 4. `unused-variable`

```python
# Bad
async def process():
    result = await compute()  # Never used
    return True

# Good
async def process():
    await compute()  # Don't assign if not using
    return True
```

## CI/CD Integration

### GitHub Actions Workflow

The repository includes a GitHub Actions workflow (`.github/workflows/pylint.yml`) that:

1. Runs on every push and pull request to `main` and `develop` branches
2. Tests against Python 3.8, 3.9, 3.10, and 3.11
3. Generates detailed reports for source code, tests, and function app
4. Uploads results as artifacts for review
5. Enforces minimum quality score of 5.0/10

### Pre-commit Checks

Before committing:

```bash
# Run Pylint locally
pylint src/AgentOperatingSystem

# If score is too low, fix issues or:
pylint src/AgentOperatingSystem --fail-under=5.0
```

## Integration with GitHub Copilot

### Using Copilot for Code Quality

1. **Real-time suggestions**: Copilot will suggest fixes for common Pylint warnings
2. **Refactoring assistance**: Ask Copilot to refactor code to meet Pylint standards
3. **Pattern learning**: Copilot learns from the Pylint configuration to suggest better code

### Example Copilot Prompts

```
# Refactor this function to pass Pylint checks
# Add type hints to this method according to Pylint standards
# Fix all Pylint warnings in this file
# Organize imports according to Pylint rules
```

## Best Practices for AOS

### 1. Perpetual Agents

```python
class MyPerpetualAgent(PurposeDrivenAgent):
    """Agent that runs indefinitely."""
    
    async def initialize(self) -> None:
        """Initialize agent resources."""
        await super().initialize()
        # Setup resources that persist
        
    async def cleanup(self) -> None:
        """Clean up agent resources."""
        # Clean up persistent resources
        await super().cleanup()
```

### 2. Azure Integration

```python
async def connect_azure_service(
    self,
    credential: Optional[DefaultAzureCredential] = None
) -> bool:
    """Connect to Azure service with proper credential handling."""
    try:
        cred = credential or DefaultAzureCredential()
        self.client = AzureClient(credential=cred)
        await self.client.initialize()
        return True
    except Exception as e:
        logger.error(f"Azure connection failed: {e}")
        return False
```

### 3. MCP Context Management

```python
async def update_context(self, key: str, value: Any) -> None:
    """Update MCP context with type safety."""
    if not isinstance(key, str):
        raise TypeError("Key must be string")
    await self.context_server.update(key, value)
```

## Suppressing Pylint Warnings

Only suppress when absolutely necessary:

```python
# Suppress specific warning with justification
# pylint: disable=broad-exception-caught
try:
    await risky_operation()
except Exception as e:  # Need to catch all exceptions here
    logger.error(f"Operation failed: {e}")
# pylint: enable=broad-exception-caught
```

## Resources

- **Pylint Documentation**: https://pylint.readthedocs.io/
- **PEP 8 Style Guide**: https://pep8.org/
- **Type Hints (PEP 484)**: https://peps.python.org/pep-0484/
- **Async Best Practices**: https://docs.python.org/3/library/asyncio-dev.html

## Quick Reference

| Check | Command | Purpose |
|-------|---------|---------|
| Full scan | `pylint src/AgentOperatingSystem` | Check entire codebase |
| Module scan | `pylint src/AgentOperatingSystem/agents` | Check specific module |
| File scan | `pylint path/to/file.py` | Check single file |
| Score only | `pylint src --score-only` | Get quality score |
| Detailed report | `pylint src --output-format=text > report.txt` | Generate report |

## Integration Checklist

- [ ] Pylint installed via `pip install -e ".[dev]"`
- [ ] Configuration in `pyproject.toml` reviewed
- [ ] GitHub Actions workflow enabled
- [ ] Pre-commit hooks configured (optional)
- [ ] Team trained on Pylint usage
- [ ] Code quality standards documented
- [ ] CI/CD pipeline includes Pylint checks
- [ ] Minimum quality score enforced

---

**Remember**: Code quality is not about perfection, but about maintainability, readability, and reducing bugs. Use Pylint as a tool to improve code, not as a rigid rulebook.
