# AgentOperatingSystem (AOS) Migration Package

## Overview

This directory contains generic infrastructure code that should be moved from BusinessInfinity to AgentOperatingSystem (AOS). This refactoring establishes a clean separation between:

- **Infrastructure Layer (AOS)**: Generic, reusable agent infrastructure components
- **Application Layer (BusinessInfinity)**: Business-specific logic and workflows

## Files for Migration to AOS

### 1. `reliability.py`
**Purpose**: Generic reliability patterns for any agent-based system

**Contains**:
- `CircuitBreaker` - Circuit breaker pattern for fault tolerance
- `RetryPolicy` - Retry logic with exponential backoff
- `IdempotencyHandler` - Idempotency handling for safe retries
- Decorator utilities (`@with_circuit_breaker`, `@with_retry`, `@with_idempotency`)

**Target Location in AOS**: `AgentOperatingSystem/reliability.py`

**Why AOS?**: These are generic infrastructure patterns applicable to any distributed system, not specific to business logic.

### 2. `observability.py`
**Purpose**: Generic observability infrastructure

**Contains**:
- `CorrelationContext` - Distributed tracing with correlation IDs
- `StructuredLogger` - Structured logging with correlation support
- `MetricsCollector` - Metrics collection (counters, gauges, histograms)
- `HealthCheck` - Health check and readiness probe infrastructure
- Context managers for correlation scopes

**Target Location in AOS**: `AgentOperatingSystem/observability.py`

**Why AOS?**: Observability is infrastructure-level functionality that any application needs, regardless of domain.

### 3. `service_interfaces.py`
**Purpose**: Generic service interface definitions

**Contains**:
- `IStorageService` - Storage service interface
- `IMessagingService` - Messaging service interface
- `IWorkflowService` - Workflow service interface
- `IAuthService` - Authentication service interface

**Target Location in AOS**: `AgentOperatingSystem/service_interfaces.py`

**Why AOS?**: Service interfaces are infrastructure contracts that enable testability and flexibility, applicable to any system.

### 4. `audit_trail.py`
**Purpose**: Generic audit trail infrastructure

**Contains**:
- `AuditEvent` - Generic audit event with integrity protection
- `AuditSeverity` - Severity enumeration
- `AuditQuery` - Query parameters for audit searches
- `AuditTrailManager` - Audit trail management with compliance support

**Target Location in AOS**: `AgentOperatingSystem/audit_trail.py`

**Why AOS?**: Audit trails are a fundamental infrastructure concern for any compliance-aware system. Business-specific event types (e.g., boardroom decisions) should extend this base in BusinessInfinity.

## Integration Instructions

### Step 1: Add Files to AOS Repository

1. Clone the AgentOperatingSystem repository
2. Copy the files from this directory to their target locations in AOS
3. Add appropriate imports to `AgentOperatingSystem/__init__.py`:

```python
from .reliability import CircuitBreaker, RetryPolicy, IdempotencyHandler, with_retry, with_circuit_breaker
from .observability import StructuredLogger, correlation_scope, get_metrics_collector, get_health_check
from .service_interfaces import IStorageService, IMessagingService, IWorkflowService, IAuthService
from .audit_trail import AuditTrailManager, AuditEvent, AuditSeverity
```

4. Update AOS version in `pyproject.toml` (e.g., `1.1.0` or `2.0.0` for breaking changes)
5. Commit and push to AOS repository
6. Create a release/tag

### Step 2: Update BusinessInfinity

After the AOS changes are merged:

1. Update BusinessInfinity's `pyproject.toml` to use the new AOS version:
```toml
dependencies = [
    "AgentOperatingSystem[azure] @ git+https://github.com/ASISaga/AgentOperatingSystem.git@v1.1.0",
    # ... other dependencies
]
```

2. Update imports in BusinessInfinity files:

**Before:**
```python
from src.core.reliability import CircuitBreaker, with_retry
from src.core.observability import StructuredLogger, correlation_scope
from src.core.service_interfaces import IStorageService
from src.core.audit_trail import AuditTrailManager
```

**After:**
```python
from AgentOperatingSystem.reliability import CircuitBreaker, with_retry
from AgentOperatingSystem.observability import StructuredLogger, correlation_scope
from AgentOperatingSystem.service_interfaces import IStorageService
from AgentOperatingSystem.audit_trail import AuditTrailManager
```

3. Remove the old files from BusinessInfinity:
   - `src/core/reliability.py`
   - `src/core/observability.py`
   - `src/core/service_interfaces.py`
   - Keep `src/core/audit_trail.py` but refactor it to extend AOS base classes

4. Update `src/core/audit_trail.py` to extend AOS:

```python
"""
Business-specific audit trail extensions for BusinessInfinity
"""
from AgentOperatingSystem.audit_trail import AuditTrailManager as BaseAuditTrailManager, AuditEvent, AuditSeverity
from typing import Dict, Any, List
from enum import Enum

class BusinessEventType(Enum):
    """Business-specific event types"""
    BOARDROOM_DECISION = "boardroom_decision"
    AGENT_VOTE = "agent_vote"
    MCP_REQUEST = "mcp_request"
    # ... other business-specific types

class BusinessAuditTrailManager(BaseAuditTrailManager):
    """Business-specific audit trail manager extending AOS base"""
    
    def log_boardroom_decision(self, decision_id: str, decision_type: str, 
                               proposed_by: str, final_decision: str, 
                               rationale: str, votes: List[Dict[str, Any]],
                               confidence_score: float, consensus_score: float) -> str:
        """Log a boardroom decision with comprehensive details"""
        return self.log_event(
            event_type=BusinessEventType.BOARDROOM_DECISION.value,
            subject_id=decision_id,
            subject_type="boardroom",
            action=f"Made decision: {decision_type}",
            severity=AuditSeverity.HIGH,
            context={
                "decision_type": decision_type,
                "proposed_by": proposed_by,
                "final_decision": final_decision,
                "votes": votes,
                "vote_count": len(votes)
            },
            rationale=rationale,
            metrics={
                "confidence_score": confidence_score,
                "consensus_score": consensus_score
            },
            compliance_tags={"sox", "business_governance"}
        )
    
    # ... other business-specific methods
```

## Benefits of This Refactoring

### 1. Separation of Concerns
- **Infrastructure code in AOS**: Generic, reusable across any application
- **Business code in BusinessInfinity**: Domain-specific logic only

### 2. Reusability
- Other projects can use AOS infrastructure without importing business logic
- Reduces code duplication across ASISaga projects

### 3. Maintainability
- Single source of truth for infrastructure patterns
- Easier to test and update infrastructure independently

### 4. Testability
- Service interfaces enable dependency injection
- Infrastructure can be mocked for business logic tests

### 5. Scalability
- Applications build on a solid, tested infrastructure foundation
- Infrastructure improvements benefit all applications

## Testing Recommendations

### AOS Testing
After adding these files to AOS:
1. Add unit tests for reliability patterns
2. Add unit tests for observability components
3. Add integration tests for audit trail
4. Ensure service interfaces have example implementations
5. Document usage examples

### BusinessInfinity Testing
After refactoring BusinessInfinity:
1. Verify all imports resolve correctly
2. Run existing test suite to ensure no regressions
3. Test business-specific audit trail extensions
4. Verify observability features work with business workflows

## Migration Checklist

- [ ] Review and approve files for AOS migration
- [ ] Add files to AOS repository
- [ ] Add comprehensive tests to AOS
- [ ] Update AOS documentation
- [ ] Create AOS release/tag
- [ ] Update BusinessInfinity dependencies
- [ ] Update BusinessInfinity imports
- [ ] Remove old files from BusinessInfinity
- [ ] Refactor BusinessInfinity audit trail to extend AOS
- [ ] Test BusinessInfinity with new AOS version
- [ ] Update BusinessInfinity documentation
- [ ] Deploy and verify

## Questions or Issues?

If you have questions about this migration or encounter issues:
1. Check the AOS_UTILIZATION_ANALYSIS.md in BusinessInfinity for context
2. Review the REFACTORING_ARCHITECTURE.md for architectural decisions
3. Consult the team or create an issue in the respective repository

## Version History

- **v1.0** (2025-12-26): Initial migration package created
  - Generic reliability patterns
  - Generic observability infrastructure
  - Generic service interfaces
  - Generic audit trail base classes
