---
name: deployment-error-fixer
description: Expert knowledge for autonomously detecting and fixing logic errors in Python and Bicep deployment code. Handles syntax errors, validation failures, and common deployment issues to enable fully autonomous deployment workflows.
---

# Deployment Error Fixer Skill

## Description
Expert skill for autonomously analyzing and fixing logic errors in deployment code (Python and Bicep). This skill enables the deployment agent to handle not just environmental failures, but also code-level issues without requiring manual developer intervention.

## When to Use This Skill
- When Python linting errors are detected in deployment/orchestrator/ code
- When Python syntax errors occur during deployment execution
- When Bicep validation errors are found (BCP error codes)
- When Bicep template errors prevent successful deployment
- When parameter validation fails
- After initial deployment attempt fails with logic errors

## Core Capabilities

### 1. Python Error Detection and Fixing

#### Common Python Issues
**Syntax Errors**:
- Missing colons, parentheses, brackets
- Indentation errors (mix of tabs/spaces)
- Invalid identifiers or keywords
- String quote mismatches

**Import Errors**:
- Missing imports
- Circular import dependencies
- Incorrect module paths

**Type Errors**:
- Type hint mismatches
- None type errors
- Attribute access on None

**Common Fixes**:
```python
# BEFORE: Missing colon
def deploy_resource(name)
    return name

# AFTER: Fixed
def deploy_resource(name):
    return name

# BEFORE: Indentation error
def process():
  if True:
      return "A"
    return "B"  # Mixed indentation

# AFTER: Fixed
def process():
    if True:
        return "A"
    return "B"

# BEFORE: Missing import
def main():
    result = subprocess.run(["ls"])  # NameError

# AFTER: Fixed
import subprocess

def main():
    result = subprocess.run(["ls"])
```

### 2. Bicep Error Detection and Fixing

#### Common Bicep Error Codes (BCP)

**BCP029**: Invalid resource type format
```bicep
// BEFORE: Invalid format
resource storage 'Microsoft.Storage/storageAccounts' = {
  ...
}

// AFTER: Fixed with API version
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  ...
}
```

**BCP033**: Expected value of type X but got Y
```bicep
// BEFORE: Type mismatch
param instanceCount int = '3'  // String instead of int

// AFTER: Fixed
param instanceCount int = 3
```

**BCP037**: Property X is not allowed
```bicep
// BEFORE: Invalid property
resource vm 'Microsoft.Compute/virtualMachines@2023-03-01' = {
  name: 'myvm'
  location: 'eastus'
  invalidProperty: 'value'  // Not allowed
}

// AFTER: Fixed (removed invalid property)
resource vm 'Microsoft.Compute/virtualMachines@2023-03-01' = {
  name: 'myvm'
  location: 'eastus'
}
```

### 3. Parameter Validation Errors

**Missing Required Parameters**:
```bicep
// main-modular.bicep requires: environment, location, projectName

// BEFORE: Missing parameters
az deployment group create \
  --resource-group my-rg \
  --template-file main-modular.bicep

// AFTER: Fixed with all required parameters
az deployment group create \
  --resource-group my-rg \
  --template-file main-modular.bicep \
  --parameters environment=dev location=eastus projectName=aos
```

## Autonomous Fix Decision Tree

```
Error Detected
    ↓
Is it a known pattern?
    ↓ YES                                    ↓ NO
Apply fix automatically                  Extract error details
    ↓                                         ↓
Verify fix doesn't break other code      Is it critical (prod)?
    ↓                                         ↓ YES        ↓ NO
Re-run validation                         Ask human    Try fix
    ↓                                         ↓            ↓
Success?                                  Wait         Re-validate
    ↓ YES        ↓ NO                                      ↓
Continue    Report & halt                              Success?
                                                           ↓ YES    ↓ NO
                                                        Continue  Report
```

## Error Analysis Process

### Step 1: Detect Error Type
```bash
# Parse error output
ERROR_TYPE=""

if echo "$ERROR" | grep -q "error BCP"; then
  ERROR_TYPE="bicep_validation"
  BCP_CODE=$(echo "$ERROR" | grep -oE "BCP[0-9]+")
elif echo "$ERROR" | grep -q "SyntaxError\|IndentationError"; then
  ERROR_TYPE="python_syntax"
elif echo "$ERROR" | grep -q "ImportError\|ModuleNotFoundError"; then
  ERROR_TYPE="python_import"
elif echo "$ERROR" | grep -q "invalid.*parameter\|missing.*parameter"; then
  ERROR_TYPE="parameter_validation"
fi
```

### Step 2: Extract Context
```bash
# Get file and line number
FILE=$(echo "$ERROR" | grep -oP '(?<=File ")[^"]+')
LINE=$(echo "$ERROR" | grep -oP '(?<=line )[0-9]+')

# Get surrounding code context
if [[ -f "$FILE" ]]; then
  START=$((LINE - 3))
  END=$((LINE + 3))
  CONTEXT=$(sed -n "${START},${END}p" "$FILE")
fi
```

### Step 3: Apply Fix

For **Bicep errors**:
```bash
# Example: Fix BCP029 (missing API version)
if [[ "$BCP_CODE" == "BCP029" ]]; then
  # Extract resource type
  RESOURCE_TYPE=$(echo "$ERROR_DETAILS" | grep -oP "Microsoft\.[^']+")
  
  # Find latest API version
  LATEST_VERSION=$(az provider show \
    --namespace ${RESOURCE_TYPE%%/*} \
    --query "resourceTypes[?resourceType=='${RESOURCE_TYPE##*/}'].apiVersions[0]" \
    -o tsv)
  
  # Apply fix
  sed -i "s|'${RESOURCE_TYPE}'|'${RESOURCE_TYPE}@${LATEST_VERSION}'|" "$FILE"
fi
```

For **Python errors**:
```bash
# Example: Fix missing import
if [[ "$ERROR_TYPE" == "python_import" ]]; then
  MODULE=$(echo "$ERROR" | grep -oP "(?<=No module named ')[^']+")
  
  # Add import at top of file
  echo "import ${MODULE}" | cat - "$FILE" > temp && mv temp "$FILE"
fi
```

## Safety Constraints

### Never Auto-Fix
- Changes to production parameter files
- Modifications to security-related resources (Key Vault, RBAC)
- Deletion or renaming of resources
- Changes to networking (VNET, NSG, firewall rules)
- Database connection strings or credentials

### Always Ask Before Fixing
- Changes affecting > 5 files
- Modifications to main-modular.bicep architecture
- API version upgrades (may introduce breaking changes)
- Parameter value changes in production

### Auto-Fix Allowed
- Syntax errors (missing colons, parentheses)
- Indentation fixes
- Missing imports (from same repo)
- BCP error codes for invalid syntax
- Type mismatches in parameters
- Missing required parameters (use defaults)
- Typos in function names
- Read-only property removal

## Example Scenarios

### Scenario 1: Bicep BCP029 Error

**Input**:
```
Error: BCP029: The resource type is not valid. 
File: deployment/modules/storage.bicep, Line: 5
```

**Fix Applied**:
```bicep
// Before
resource storage 'Microsoft.Storage/storageAccounts' = {

// After
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
```

**Outcome**: ✅ Auto-fixed, deployment retried

### Scenario 2: Python Import Error

**Input**:
```
ImportError: No module named 'pathlib'
File: deployment/orchestrator/cli/deploy.py, line 5
```

**Outcome**: ✅ Classified correctly, appropriate action taken

### Scenario 3: Missing Parameter

**Input**:
```
Error: Missing required parameter: projectName
File: deployment/parameters/dev.bicepparam
```

**Fix Applied**:
```bicep
// Before
using './main-modular.bicep'
param environment = 'dev'
param location = 'eastus'

// After
using './main-modular.bicep'
param environment = 'dev'
param location = 'eastus'
param projectName = 'aos'  // Added with sensible default
```

**Outcome**: ✅ Auto-fixed, deployment retried

## Best Practices

1. **Always validate before fixing**: Understand the error completely
2. **Use minimal changes**: Fix only what's broken
3. **Preserve formatting**: Match existing code style
4. **Test after fixing**: Re-run validation immediately
5. **Log all fixes**: Document what was changed and why
6. **Ask when uncertain**: Better to ask than break production

## Error Patterns Database

### Python Common Patterns

| Pattern | Fix | Auto? |
|---------|-----|-------|
| Missing `:` in function def | Add `:` | ✅ Yes |
| Indentation mix (tabs/spaces) | Convert to spaces | ✅ Yes |
| Missing import | Add import line | ✅ Yes |
| Undefined variable | Check scope, add declaration | ⚠️ Ask |
| Type hint error | Fix or remove hint | ✅ Yes |

### Bicep Common Patterns

| BCP Code | Issue | Fix | Auto? |
|----------|-------|-----|-------|
| BCP029 | Missing API version | Add @apiVersion | ✅ Yes |
| BCP033 | Type mismatch | Cast or change type | ✅ Yes |
| BCP037 | Invalid property | Remove property | ✅ Yes |
| BCP051 | Missing keyword | Add resource/param/var | ✅ Yes |
| BCP062 | Invalid function | Correct function name | ✅ Yes |
| BCP073 | Read-only property | Remove property | ✅ Yes |

## Summary

This skill enables the deployment agent to:
1. ✅ Detect Python and Bicep logic errors
2. ✅ Analyze error context and patterns
3. ✅ Apply automatic fixes for common issues
4. ✅ Validate fixes before re-attempting deployment
5. ✅ Ask for help when uncertain
6. ✅ Maintain safety constraints for critical changes
