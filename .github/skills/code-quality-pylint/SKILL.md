---
name: code-quality-pylint
description: Master Pylint usage for maintaining high code quality in the Agent Operating System (AOS) repository. Includes static code analysis, error detection, PEP 8 enforcement, and code quality metrics.
---

# Skill: Code Quality with Pylint

## Skill Overview

**Purpose**: Master Pylint usage for maintaining high code quality in the Agent Operating System (AOS) repository.

**When to use**: 
- Before committing code changes
- During code review
- When debugging quality issues
- When refactoring code
- As part of CI/CD pipeline

**Prerequisites**:
- Python 3.10+ installed
- Repository dependencies installed (`pip install -e ".[dev]"`)
- Basic understanding of Python syntax and PEP 8

## Core Knowledge

### What is Pylint?

Pylint is a static code analysis tool that:
- **Detects errors**: Syntax errors, logic errors, and potential bugs
- **Enforces standards**: PEP 8 style guide and best practices
- **Finds code smells**: Duplicated code, unused variables, complex functions
- **Provides metrics**: Code quality scores and detailed reports

### AOS Pylint Configuration

The repository uses a comprehensive Pylint configuration in `pyproject.toml` optimized for:

1. **Async Python**: Handles async/await patterns correctly
2. **Azure Services**: Understands Azure SDK patterns
3. **Agent Architecture**: Tailored for perpetual agents and event-driven code
4. **Type Safety**: Encourages type hints and modern Python

## Step-by-Step Procedures

### Procedure 1: Run Pylint Locally

**Goal**: Check code quality before committing

**Steps**:

1. **Install Pylint** (if not already installed):
   ```bash
   cd /home/runner/work/AgentOperatingSystem/AgentOperatingSystem
   pip install -e ".[dev]"
   ```

2. **Run on entire source**:
   ```bash
   pylint src/AgentOperatingSystem
   ```

3. **Run on specific module**:
   ```bash
   # Check agents module
   pylint src/AgentOperatingSystem/agents
   
   # Check orchestration module
   pylint src/AgentOperatingSystem/orchestration
   ```

4. **Run on single file**:
   ```bash
   pylint src/AgentOperatingSystem/agents/perpetual_agent.py
   ```

5. **Review results**:
   - Look for **E (Error)**: Critical issues that must be fixed
   - Look for **W (Warning)**: Important issues that should be fixed
   - Look for **C (Convention)**: Style issues (informational)
   - Look for **R (Refactor)**: Code structure suggestions

**Expected outcome**: Pylint report showing issues and overall score.

### Procedure 2: Fix Common Pylint Issues

**Goal**: Resolve typical Pylint warnings in AOS code

**Common Issues and Fixes**:

#### Issue 1: Missing Type Hints

**Pylint message**: `missing-type-arg`, `no-type-hint`

```python
# Before (Pylint warning)
async def process_event(self, event):
    return await self.handle(event)

# After (Fixed)
from typing import Any

async def process_event(self, event: dict) -> Any:
    return await self.handle(event)
```

#### Issue 2: Unused Imports

**Pylint message**: `unused-import`

```python
# Before (Pylint warning)
import asyncio
import logging
from typing import Dict  # Not used

async def task():
    await asyncio.sleep(1)

# After (Fixed)
import asyncio
import logging

async def task():
    await asyncio.sleep(1)
```

#### Issue 3: Undefined Variables

**Pylint message**: `undefined-variable`

```python
# Before (Pylint warning)
async def get_status():
    return agent_status  # Where does this come from?

# After (Fixed)
async def get_status(agent_id: str) -> dict:
    agent_status = await fetch_status(agent_id)
    return agent_status
```

#### Issue 4: Broad Exception Catching

**Pylint message**: `broad-exception-caught`

```python
# Before (Not ideal, but sometimes necessary)
try:
    await azure_operation()
except Exception as e:  # Too broad
    logger.error(f"Error: {e}")

# After (Better - specific exceptions)
try:
    await azure_operation()
except (ConnectionError, TimeoutError) as e:
    logger.error(f"Azure connection error: {e}")
except Exception as e:
    # Only if you really need to catch everything
    logger.error(f"Unexpected error: {e}")
    raise
```

#### Issue 5: Too Many Arguments

**Pylint message**: `too-many-arguments`

```python
# Before (Pylint warning)
async def create_agent(
    self, id, name, purpose, scope, criteria, adapter, config, metadata
):
    pass

# After (Fixed - use config object)
from dataclasses import dataclass

@dataclass
class AgentConfig:
    id: str
    name: str
    purpose: str
    scope: str
    criteria: list
    adapter: str
    metadata: dict

async def create_agent(self, config: AgentConfig) -> Agent:
    pass
```

### Procedure 3: Generate and Review Pylint Reports

**Goal**: Create detailed quality reports for analysis

**Steps**:

1. **Generate text report**:
   ```bash
   pylint src/AgentOperatingSystem --output-format=text > pylint-report.txt
   ```

2. **Generate JSON report** (for programmatic analysis):
   ```bash
   pylint src/AgentOperatingSystem --output-format=json > pylint-report.json
   ```

3. **Generate colorized console output**:
   ```bash
   pylint src/AgentOperatingSystem --output-format=colorized
   ```

4. **Get only the score**:
   ```bash
   pylint src/AgentOperatingSystem --score-only
   ```

5. **Review report sections**:
   - **Messages by category**: Groups issues by type
   - **Statistics by type**: Counts of each issue
   - **Raw metrics**: Lines of code, comments, etc.
   - **Global evaluation**: Overall score and rating

### Procedure 4: Fix Critical Issues in AOS Codebase

**Goal**: Address high-priority Pylint findings

**Priority Levels**:

1. **Critical (Must Fix)**:
   - Syntax errors
   - Undefined variables
   - Import errors
   - Logic errors

2. **High Priority (Should Fix)**:
   - Unused variables
   - Redefined names
   - Dangerous default values
   - Missing awaits on async functions

3. **Medium Priority (Consider Fixing)**:
   - Complex functions (too many branches)
   - Long functions
   - Unused imports

4. **Low Priority (Optional)**:
   - Line length (if < 150 chars)
   - Missing docstrings (handled by code review)
   - Naming convention variations

**Fixing workflow**:

1. **Run Pylint and save output**:
   ```bash
   pylint src/AgentOperatingSystem > issues.txt
   ```

2. **Filter for critical issues**:
   ```bash
   grep "E:" issues.txt  # Errors only
   ```

3. **Fix issues one by one**:
   - Open the file mentioned
   - Locate the line number
   - Apply the fix
   - Re-run Pylint on that file

4. **Verify fix**:
   ```bash
   pylint src/AgentOperatingSystem/path/to/fixed_file.py
   ```

### Procedure 5: Integrate with GitHub Copilot

**Goal**: Use Copilot to assist with Pylint compliance

**Copilot Prompts for Quality**:

```python
# Prompt: "Fix all Pylint warnings in this function"
async def my_function():
    # Copilot will suggest fixes
    pass

# Prompt: "Add type hints to this method"
async def process(self, data):
    # Copilot will add proper type hints
    pass

# Prompt: "Refactor this to reduce complexity"
async def complex_function():
    # Copilot will suggest simpler structure
    pass

# Prompt: "Organize these imports according to PEP 8"
import sys
from azure.identity import DefaultAzureCredential
import asyncio
from typing import Dict
```

**Using Copilot Chat**:

1. Select problematic code
2. Open Copilot Chat
3. Ask: "What Pylint issues does this have and how can I fix them?"
4. Review suggestions
5. Apply fixes

### Procedure 6: Suppress Pylint Warnings (When Necessary)

**Goal**: Temporarily disable warnings when you have a good reason

**When to suppress**:
- False positives
- Third-party code patterns
- Temporary workarounds
- Intentional design decisions

**How to suppress**:

```python
# Suppress for a single line
result = risky_call()  # pylint: disable=broad-exception-caught

# Suppress for a block
# pylint: disable=too-many-arguments
async def complex_function(arg1, arg2, arg3, arg4, arg5, arg6):
    # Implementation
    pass
# pylint: enable=too-many-arguments

# Suppress for entire file (use sparingly)
# At top of file:
# pylint: disable=missing-module-docstring

# Suppress specific check in entire file
# pylint: disable=fixme
# TODO: This is okay here
```

**Best practice**: Always add a comment explaining why you're suppressing.

## Common Patterns in AOS

### Pattern 1: Async Agent Methods

```python
from typing import Dict, Any, Optional

class MyAgent(PurposeDrivenAgent):
    async def initialize(self) -> None:
        """Initialize agent resources."""
        await super().initialize()
        self.state: Dict[str, Any] = {}
    
    async def process_event(
        self, 
        event: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Process event with optional timeout."""
        # Implementation
        result: Dict[str, Any] = {}
        return result
```

### Pattern 2: Azure Service Integration

```python
from typing import Optional
from azure.identity import DefaultAzureCredential

class AzureServiceManager:
    def __init__(
        self,
        credential: Optional[DefaultAzureCredential] = None
    ) -> None:
        self.credential = credential or DefaultAzureCredential()
    
    async def connect(self) -> bool:
        """Connect to Azure service."""
        try:
            # Connection logic
            return True
        except ConnectionError as exc:
            logger.error("Connection failed: %s", exc)
            return False
```

### Pattern 3: Error Handling with Logging

```python
import logging
from typing import Any

logger = logging.getLogger(__name__)

async def safe_operation(data: Any) -> bool:
    """Perform operation with comprehensive error handling."""
    try:
        await risky_operation(data)
        return True
    except ValueError as exc:
        logger.warning("Invalid data: %s", exc)
        return False
    except ConnectionError as exc:
        logger.error("Connection lost: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        return False
```

## Troubleshooting

### Issue: "Import error" for git-based dependencies

**Symptom**: Pylint complains about imports from LeadershipAgent or PurposeDrivenAgent

**Solution**: These are disabled in config. If needed:
```python
# pylint: disable=import-error
from LeadershipAgent import LeadershipAgent
# pylint: enable=import-error
```

### Issue: "No member" errors for Azure SDK

**Symptom**: Pylint doesn't recognize Azure SDK attributes

**Solution**: Already configured in `pyproject.toml` with `ignore-on-opaque-inference`. If still occurs:
```python
# pylint: disable=no-member
azure_client.dynamic_property
# pylint: enable=no-member
```

### Issue: Score too low

**Symptom**: Pylint score below 5.0, failing CI/CD

**Solution**:
1. Focus on errors (E) first
2. Then warnings (W)
3. Document remaining issues
4. Consider if score threshold needs adjustment

### Issue: Too many warnings to fix at once

**Symptom**: Hundreds of warnings, overwhelming

**Solution**:
1. Run on specific modules: `pylint src/AgentOperatingSystem/agents`
2. Filter by severity: `pylint src | grep "E:"`
3. Fix incrementally, one module at a time
4. Track progress in issues/PRs

## Integration with Development Workflow

### Daily Development

1. **Before coding**: Review Pylint configuration
2. **During coding**: Use Copilot for quality suggestions
3. **After coding**: Run Pylint on changed files
4. **Before commit**: Run Pylint on affected modules
5. **In PR**: Review CI/CD Pylint results

### Code Review Checklist

- [ ] Pylint score maintained or improved
- [ ] No new errors (E) introduced
- [ ] Critical warnings (W) addressed
- [ ] Suppressions documented with reasons
- [ ] Type hints added for public APIs
- [ ] Imports organized properly

## Resources

- **Pylint Documentation**: https://pylint.readthedocs.io/
- **AOS Code Quality Instructions**: `.github/instructions/code-quality.instructions.md`
- **Pylint Configuration**: `pyproject.toml` (`[tool.pylint.*]` sections)
- **GitHub Workflow**: `.github/workflows/pylint.yml`

## Quick Command Reference

```bash
# Basic checks
pylint src/AgentOperatingSystem
pylint tests
pylint function_app.py

# Specific modules
pylint src/AgentOperatingSystem/agents
pylint src/AgentOperatingSystem/orchestration
pylint src/AgentOperatingSystem/mcp

# With options
pylint src --fail-under=5.0
pylint src --score-only
pylint src --output-format=json > report.json

# Install/update
pip install -e ".[dev]"
pip install --upgrade pylint
```

## Success Criteria

You've mastered this skill when you can:

- [ ] Run Pylint effectively on any part of the codebase
- [ ] Interpret Pylint messages and understand their severity
- [ ] Fix common Pylint issues without breaking functionality
- [ ] Generate and analyze Pylint reports
- [ ] Integrate Pylint checks into your development workflow
- [ ] Use Copilot to assist with Pylint compliance
- [ ] Know when to suppress warnings appropriately
- [ ] Maintain or improve code quality scores

---

**Next Steps**: 
1. Practice running Pylint on small code sections
2. Fix one category of issues at a time
3. Review CI/CD Pylint results regularly
4. Share learnings with the team
