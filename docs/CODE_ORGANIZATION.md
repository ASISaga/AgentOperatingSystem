# Code Organization Notes

## v3.0.0 Major Version - Backward Compatibility Removed

As of v3.0.0, all backward compatibility code has been removed. The repository now uses only the v2.0.0 refactored classes.

### Removed Files
- `agents/base.py` (v1.x) - Replaced by `agents/base_agent.py`
- `agents/leadership.py` (v1.x) - Replaced by `agents/leadership_agent.py`
- `services/interfaces.py` (legacy) - Replaced by `services/service_interfaces.py`

### Current Agent Classes (v3.0.0)

**Base Agent** - `agents/base_agent.py`
- `BaseAgent` - Enhanced lifecycle management with health checks and metadata
- Used throughout the codebase
- Full async/await support

**Leadership Agent** - `agents/leadership_agent.py`
- `LeadershipAgent` - Decision-making and stakeholder coordination
- Used by orchestration components
- Simplified, cleaner interface

**Service Interfaces** - `services/service_interfaces.py`
- `IStorageService` - Storage operations
- `IMessagingService` - Messaging operations
- `IWorkflowService` - Workflow orchestration
- `IAuthService` - Authentication/authorization

### Migration Guide

All external consumers must update their imports:

**Before (v1.x):**
```python
from AgentOperatingSystem.agents.base import BaseAgent
from AgentOperatingSystem.agents.leadership import LeadershipAgent
```

**After (v3.0.0):**
```python
from AgentOperatingSystem.agents import BaseAgent, LeadershipAgent
# or
from AgentOperatingSystem.agents.base_agent import BaseAgent
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
```

### Monitoring Classes

**Note:** Both audit trail implementations are still present as they serve different purposes:
- `monitoring/audit_trail.py` - Original implementation used by core systems
- `monitoring/audit_trail_generic.py` - Generic implementation for extensibility

## Related Documentation

- [REFACTORING.md](development/REFACTORING.md) - Complete refactoring guide
- [MIGRATION.md](development/MIGRATION.md) - Migration instructions
- [ARCHITECTURE.md](architecture/ARCHITECTURE.md) - System architecture
- [CODE_ORGANIZATION.md](CODE_ORGANIZATION.md) - This document
