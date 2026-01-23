# Pylint Quick Reference for AOS

## Installation

```bash
pip install -e ".[dev]"
```

## Basic Usage

### Check entire source code
```bash
pylint src/AgentOperatingSystem
```

### Check specific module
```bash
pylint src/AgentOperatingSystem/agents
```

### Check single file
```bash
pylint src/AgentOperatingSystem/agents/perpetual_agent.py
```

## Common Commands

### Get only the score
```bash
pylint src/AgentOperatingSystem --score-only
```

### Generate detailed report
```bash
pylint src/AgentOperatingSystem > pylint-report.txt
```

### Check for errors only
```bash
pylint src/AgentOperatingSystem --disable=all --enable=E
```

### Check with minimum score requirement
```bash
pylint src/AgentOperatingSystem --fail-under=5.0
```

## Issue Severity Levels

- **E (Error)**: Critical issues that will likely cause runtime errors
- **W (Warning)**: Important issues that should be fixed
- **C (Convention)**: Style and convention issues
- **R (Refactor)**: Code structure suggestions

## Common Issues and Quick Fixes

### Trailing Whitespace (C0303)
```bash
# Remove from all Python files
find src -name "*.py" -exec sed -i 's/[ \t]*$//' {} \;
```

### Unused Import (W0611)
Remove the import statement if truly unused.

### Reimport (W0404)
Remove duplicate import statements.

### Missing Type Hints
Add type annotations:
```python
def function(arg: str) -> int:
    return len(arg)
```

### Line Too Long
Break long lines (max 120 chars in AOS config):
```python
# Before
result = some_function(arg1, arg2, arg3, arg4, arg5)

# After
result = some_function(
    arg1, arg2, arg3,
    arg4, arg5
)
```

## Suppressing Warnings

### Single line
```python
result = risky_call()  # pylint: disable=broad-exception-caught
```

### Block of code
```python
# pylint: disable=too-many-arguments
def function(arg1, arg2, arg3, arg4, arg5, arg6):
    pass
# pylint: enable=too-many-arguments
```

### Entire file
```python
# At top of file
# pylint: disable=missing-module-docstring
```

## AOS-Specific Configuration

The repository has a comprehensive Pylint configuration in `pyproject.toml`:

- **Line length**: 120 characters
- **Minimum score**: 5.0/10 (CI/CD requirement)
- **Disabled**: Documentation requirements, some complexity metrics
- **Enabled**: Error detection, type checking, security issues

## Integration Points

### Pre-commit
Run before committing:
```bash
pylint src/AgentOperatingSystem
```

### CI/CD
GitHub Actions runs Pylint automatically on PRs and pushes.

### IDE Integration
Most IDEs support Pylint integration for real-time feedback.

## Helpful Resources

- **Full Documentation**: `.github/instructions/code-quality.instructions.md`
- **Skill Guide**: `.github/skills/code-quality-pylint/SKILL.md`
- **Expert Prompt**: `.github/prompts/code-quality-expert.md`
- **Pylint Docs**: https://pylint.readthedocs.io/

## Current Score

As of the latest run:
```
Your code has been rated at 8.52/10
```

This exceeds the minimum threshold of 5.0/10 required for CI/CD.

## Tips

1. **Fix errors first**: Focus on E-level issues before warnings
2. **Use suppressions sparingly**: Only when you have a good reason
3. **Run incrementally**: Check modules as you work on them
4. **Check before commit**: Avoid CI/CD failures
5. **Use Copilot**: Ask for help fixing Pylint issues
