# Code Refactoring for Major Version Bumps

## Description
Expert knowledge for performing major version refactoring in the Agent Operating System, including removing backward compatibility code, consolidating duplicate implementations, and updating all references to use the latest patterns.

## When to Use This Skill
- Performing major version bumps (v1.x → v2.0.0, v2.x → v3.0.0)
- Removing deprecated code and backward compatibility layers
- Consolidating duplicate class implementations
- Updating imports across the entire codebase
- Cleaning up technical debt from gradual migrations

## Core Concepts

### Understanding Backward Compatibility Layers

AOS has maintained backward compatibility during refactoring by:
1. Keeping original classes (v1.x) alongside new ones (v2.0.0)
2. Exporting both versions with different names
3. Documenting the migration path

Example from `agents/__init__.py`:
```python
# Original v1.x classes
from .base import BaseAgent, Agent, StatefulAgent
from .leadership import LeadershipAgent

# New v2.0.0 classes (exported with "New" suffix)
from .base_agent import BaseAgent as BaseAgentNew
from .leadership_agent import LeadershipAgent as LeadershipAgentNew
```

### Major Version Refactoring Strategy

When removing backward compatibility:
1. **Identify duplicate implementations** (documented in CODE_ORGANIZATION.md)
2. **Choose the target version** (usually v2.0.0 classes)
3. **Update all imports** to use target version
4. **Remove deprecated classes**
5. **Update exports** to use canonical names
6. **Test thoroughly**

## Refactoring Steps

### Step 1: Identify Duplicates

Check `docs/CODE_ORGANIZATION.md` for documented duplicates:

**Agent Classes:**
- `agents/base.py` (v1.x) → Remove
- `agents/base_agent.py` (v2.0.0) → Keep
- `agents/leadership.py` (v1.x) → Remove
- `agents/leadership_agent.py` (v2.0.0) → Keep

**Service Interfaces:**
- `services/interfaces.py` (legacy) → Remove
- `services/service_interfaces.py` (primary) → Keep

**Monitoring:**
- `monitoring/audit_trail.py` (original) → Evaluate usage
- `monitoring/audit_trail_generic.py` (generic) → Evaluate usage

### Step 2: Find All Imports

Use grep to find all imports of deprecated classes:

```bash
# Find base.py imports
grep -r "from.*agents.base import\|from.*agents\.base import" src/ --include="*.py"

# Find leadership.py imports
grep -r "from.*agents.leadership import\|from.*agents\.leadership import" src/ --include="*.py"

# Find interfaces.py imports
grep -r "from.*services.interfaces import\|from.*services\.interfaces import" src/ --include="*.py"
```

### Step 3: Update Imports

Replace old imports with new ones:

**Before:**
```python
from AgentOperatingSystem.agents.base import BaseAgent
from AgentOperatingSystem.agents.leadership import LeadershipAgent
```

**After:**
```python
from AgentOperatingSystem.agents.base_agent import BaseAgent
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
```

### Step 4: Update __init__.py Exports

Simplify exports to use only v2.0.0 classes:

**Before (agents/__init__.py):**
```python
from .base import BaseAgent, Agent, StatefulAgent
from .leadership import LeadershipAgent
from .base_agent import BaseAgent as BaseAgentNew
from .leadership_agent import LeadershipAgent as LeadershipAgentNew
```

**After:**
```python
# v2.0.0 - Canonical implementations
from .base_agent import BaseAgent
from .leadership_agent import LeadershipAgent
from .perpetual import PerpetualAgent
from .purpose_driven import PurposeDrivenAgent
# ... other exports
```

### Step 5: Remove Deprecated Files

After all imports are updated:

```bash
git rm src/AgentOperatingSystem/agents/base.py
git rm src/AgentOperatingSystem/agents/leadership.py
git rm src/AgentOperatingSystem/services/interfaces.py
```

### Step 6: Update Documentation

Update all documentation references:
- REFACTORING.md
- CODE_ORGANIZATION.md
- MIGRATION.md
- README.md
- Any example code

### Step 7: Test

Run comprehensive tests:

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/ -m integration

# Specific component tests
pytest tests/test_agents.py
pytest tests/test_services.py
```

## File Locations

**Duplicate Classes (to be removed):**
- `src/AgentOperatingSystem/agents/base.py`
- `src/AgentOperatingSystem/agents/leadership.py`
- `src/AgentOperatingSystem/services/interfaces.py`

**Target Classes (to be kept):**
- `src/AgentOperatingSystem/agents/base_agent.py`
- `src/AgentOperatingSystem/agents/leadership_agent.py`
- `src/AgentOperatingSystem/services/service_interfaces.py`

**Files to Update:**
- `src/AgentOperatingSystem/agents/__init__.py`
- `src/AgentOperatingSystem/services/__init__.py`
- `src/AgentOperatingSystem/__init__.py`
- `docs/CODE_ORGANIZATION.md`
- `REFACTORING.md`
- `MIGRATION.md`

## Common Issues

### Issue 1: Missing Features in v2.0.0
**Problem**: v1.x class has methods not in v2.0.0
**Solution**: Port missing methods to v2.0.0 before removing v1.x

### Issue 2: Different Method Signatures
**Problem**: v2.0.0 has different method signatures
**Solution**: Create adapter methods or update callers

### Issue 3: Test Failures After Migration
**Problem**: Tests expect v1.x behavior
**Solution**: Update tests to match v2.0.0 behavior

### Issue 4: External Dependencies
**Problem**: Other repos depend on v1.x classes
**Solution**: Coordinate migration, update external repos first

### Issue 5: Import Circular Dependencies
**Problem**: Refactoring creates circular imports
**Solution**: Restructure imports, use TYPE_CHECKING

## Best Practices

1. **Create a Migration Branch**: Don't do this on main
2. **Update Incrementally**: One component at a time
3. **Test After Each Change**: Ensure nothing breaks
4. **Document Changes**: Update CHANGELOG.md
5. **Communicate**: Notify external consumers
6. **Backup**: Tag before major refactoring
7. **Review Thoroughly**: Code review all changes
8. **Monitor Production**: Watch for issues after deployment

## Validation Checklist

- [ ] All v1.x imports updated to v2.0.0
- [ ] Deprecated files removed
- [ ] __init__.py exports updated
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Examples updated
- [ ] CHANGELOG.md updated
- [ ] No grep matches for old imports
- [ ] External consumers notified
- [ ] Code review completed

## Related Skills
- `aos-architecture` - Understanding system architecture
- `async-python-testing` - Testing refactored code
- `perpetual-agents` - Understanding agent implementations

## Additional Resources
- `docs/CODE_ORGANIZATION.md` - Current duplication documentation
- `REFACTORING.md` - Refactoring history
- `MIGRATION.md` - Migration guides
- `CHANGELOG.md` - Version history
