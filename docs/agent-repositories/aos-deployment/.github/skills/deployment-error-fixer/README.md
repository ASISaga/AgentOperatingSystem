# Deployment Error Fixer Skill

## Overview

The **Deployment Error Fixer** skill enables autonomous detection and fixing of logic errors in Python and Bicep deployment code. It allows the deployment agent to handle not just environmental failures (with retry), but also code-level issues without requiring manual developer intervention.

## Files

- **`SKILL.md`** - Comprehensive skill documentation with error patterns and fix examples
- **`scripts/fix_error.py`** - Autonomous error analysis and fixing script
- **`tests/test_error_fixer.py`** - Test suite for error detection and fixing logic

## Quick Start

### Analyze an Error

```bash
python3 scripts/fix_error.py \
  --error-file path/to/error.log \
  --deployment-dir deployment/ \
  --dry-run
```

### Auto-Fix an Error

```bash
python3 scripts/fix_error.py \
  --error-file path/to/error.log \
  --deployment-dir deployment/ \
  --auto-fix
```

## Supported Error Types

### Bicep Errors

| BCP Code | Description | Auto-Fix |
|----------|-------------|----------|
| BCP029 | Missing API version | ✅ Yes |
| BCP033 | Type mismatch | ✅ Yes |
| BCP037 | Invalid property | ✅ Yes |
| BCP051 | Missing keyword | ✅ Yes |
| BCP062 | Invalid function | ✅ Yes |
| BCP068 | Invalid resource reference | ✅ Yes |
| BCP073 | Read-only property | ✅ Yes |

### Python Errors

| Error Type | Description | Auto-Fix |
|------------|-------------|----------|
| Syntax | Missing colons, parentheses | ✅ Yes |
| Indentation | Tabs vs spaces | ✅ Yes |
| Import | Missing imports | ✅ Yes |

### Parameter Errors

| Error Type | Description | Auto-Fix |
|------------|-------------|----------|
| Missing parameter | Required parameter not provided | ✅ Yes (with defaults) |
| Invalid value | Wrong parameter type/value | ✅ Yes |

## Integration with Workflow

The skill is integrated into `.github/workflows/infrastructure-deploy.yml` as the "Autonomous logic error fixing" step. When a deployment fails with a logic error:

1. **Detect**: Classify the error type
2. **Analyze**: Determine if error is auto-fixable
3. **Fix**: Apply appropriate fix if safe
4. **Validate**: Re-run linting/compilation
5. **Retry**: Re-execute deployment

## Safety Constraints

### Never Auto-Fix
- Production security configurations
- Resource deletions or renames
- Network security rules
- Database credentials
- Breaking architectural changes

### Always Ask First
- Changes affecting > 5 files
- API version upgrades (potential breaking changes)
- Parameter value changes in production

### Auto-Fix Allowed
- Syntax errors
- Indentation fixes
- Missing imports (from same repo)
- Known BCP error codes
- Type mismatches
- Missing parameters (with sensible defaults)

## Testing

Run the test suite:

```bash
python3 tests/test_error_fixer.py
```

All 11 tests should pass:
- 6 error detection tests
- 3 fix application tests
- 2 error classification tests

## Examples

### Example 1: BCP029 Error

**Before:**
```bicep
resource storage 'Microsoft.Storage/storageAccounts' = {
  name: 'mysto rage'
  location: 'eastus'
}
```

**Error:**
```
Error BCP029: The resource type is not valid.
```

**After (Auto-Fixed):**
```bicep
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'mystorage'
  location: 'eastus'
}
```

### Example 2: Python Syntax Error

**Before:**
```python
def deploy_resource(name)
    return name
```

**Error:**
```
SyntaxError: invalid syntax
```

**After (Auto-Fixed):**
```python
def deploy_resource(name):
    return name
```

### Example 3: Indentation Error

**Before:**
```python
def main():
	return True  # Tab instead of spaces
```

**Error:**
```
IndentationError: inconsistent use of tabs and spaces
```

**After (Auto-Fixed):**
```python
def main():
    return True  # Converted to 4 spaces
```

## Architecture

```
Error Occurs in Deployment
        ↓
Workflow Detects Logic Failure
        ↓
Invoke fix_error.py
        ↓
Analyze Error
  - Extract error type
  - Get file & line number
  - Classify fix-ability
        ↓
Auto-Fixable?
  ↓ Yes              ↓ No
Apply Fix        Report Error
  ↓                    ↓
Validate Fix     Ask for Help
  ↓                    
Retry Deployment      
  ↓
Success!
```

## Extending

To add support for new error types:

1. **Add pattern to analyzer** in `fix_error.py`:
   ```python
   elif 'NewErrorPattern' in error_text:
       result['error_type'] = ErrorType.NEW_TYPE
       result['can_auto_fix'] = True
   ```

2. **Implement fix logic**:
   ```python
   def fix_new_error(self, file_path: str, line_number: int) -> bool:
       # Fix logic here
       pass
   ```

3. **Add to apply_fix method**:
   ```python
   elif error_type == ErrorType.NEW_TYPE:
       return self.fix_new_error(file_path, line_number)
   ```

4. **Add tests** in `tests/test_error_fixer.py`

5. **Update SKILL.md** with the new error pattern

## Contributing

When adding new error patterns:
1. Add comprehensive tests
2. Document the pattern in SKILL.md
3. Update this README
4. Test thoroughly before deploying

## Related Documentation

- [Infrastructure Deploy Agent](../../agents/infrastructure-deploy.agent.md)
- [Deployment Expert Prompt](../../prompts/deployment-expert.md)
- [Python Orchestrator](../../../deployment/ORCHESTRATOR_USER_GUIDE.md)
- [Bicep Templates](../../../deployment/modules/README.md)

## Summary

The Deployment Error Fixer skill provides:
- ✅ Autonomous error detection for Python and Bicep
- ✅ Automatic fixing of common errors
- ✅ Validation before retry
- ✅ Safety constraints for production
- ✅ Comprehensive test coverage
- ✅ Integration with deployment workflow

This enables fully autonomous deployment workflows that handle both environmental AND logic failures, dramatically reducing manual intervention time.
