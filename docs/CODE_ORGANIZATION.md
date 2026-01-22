# Code Organization Notes

## Duplicate Classes - Intentional Design

During the v2.0.0 refactoring, new base classes were added while maintaining backward compatibility. This creates intentional duplication:

### Agent Base Classes

#### Original Classes (v1.x - Still Supported)
- **`agents/base.py`**: Contains `BaseAgent`, `Agent`, `StatefulAgent`
  - Used by: Main AOS system, existing consumer code
  - Purpose: Original agent lifecycle and messaging

- **`agents/leadership.py`**: Contains `LeadershipAgent`
  - Used by: Orchestration system
  - Purpose: Decision-making and stakeholder coordination

#### Refactored Classes (v2.0.0 - New Style)
- **`agents/base_agent.py`**: Contains `BaseAgent` (exported as `BaseAgentNew`)
  - Used by: New implementations, example code
  - Purpose: Enhanced lifecycle with better state management
  - **Differences**: More detailed lifecycle, health checks, metadata

- **`agents/leadership_agent.py`**: Contains `LeadershipAgent` (exported as `LeadershipAgentNew`)
  - Used by: Example code, documentation
  - Purpose: Simplified leadership patterns
  - **Differences**: Cleaner interface, less complexity

#### Migration Strategy

**Current State**: Both versions coexist
```python
# agents/__init__.py exports both:
from .base import BaseAgent                    # Original
from .base_agent import BaseAgent as BaseAgentNew  # New style
```

**Recommended Approach**:
- New projects: Use `BaseAgentNew` / `LeadershipAgentNew`
- Existing projects: Continue using original classes
- No forced migration required

### Service Interfaces

#### service_interfaces.py (Primary)
- **Used by**: Main AOS exports, documented APIs
- Contains: `IStorageService`, `IMessagingService`, `IWorkflowService`, `IAuthService`
- Purpose: Clean service contracts for dependency injection

#### interfaces.py (Legacy)
- **Used by**: Internal code, compatibility
- Contains: Similar interfaces with different implementation
- Purpose: Backward compatibility during refactoring

### Monitoring Classes

#### audit_trail.py (Original)
- **Used by**: Orchestration, messaging, ML systems
- Contains: `AuditTrailManager`, `AuditEventType`, `AuditSeverity`
- Import pattern: `from ..monitoring.audit_trail import audit_log`

#### audit_trail_generic.py (Generic Version)
- **Used by**: Self-reference in exports
- Contains: `AuditTrailManager`, `AuditEvent`, `AuditSeverity`
- Purpose: Generic implementation variant

## Why Keep Both?

### 1. Backward Compatibility
External consumers (e.g., BusinessInfinity) depend on original classes. Breaking these would require coordinated upgrades across multiple repositories.

### 2. Gradual Migration
Teams can migrate at their own pace without being forced to update all code at once.

### 3. Documentation & Examples
Both styles are documented, allowing developers to choose based on their needs.

## Future Cleanup Considerations

When safe to remove duplicates (major version bump):
1. Deprecate old classes with warnings
2. Update all examples to use new style
3. Provide automated migration tools
4. Remove old classes in next major version

## Related Documentation

- [REFACTORING.md](../REFACTORING.md) - Complete refactoring guide
- [MIGRATION.md](../MIGRATION.md) - Migration instructions
- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture
- [CODE_ORGANIZATION.md](CODE_ORGANIZATION.md) - This document
