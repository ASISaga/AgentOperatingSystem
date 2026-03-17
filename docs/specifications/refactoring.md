# AgentOperatingSystem Refactoring Specification

## Overview

This specification describes the refactoring of AgentOperatingSystem (AOS) as a pure, generic infrastructure layer for agent-based systems. The refactoring removes business-specific code and provides clean, well-defined service interfaces.

## Objectives

1. **Generic Infrastructure**: Establish AOS as reusable infrastructure across domains
2. **Clean Separation**: Remove business logic from infrastructure layer
3. **Interface-Based Design**: Provide clean service contracts for dependency injection
4. **Backward Compatibility**: Maintain compatibility with existing code

## New Components

### 1. Enhanced Base Agent Classes

#### BaseAgent (`agents/base_agent.py`)
- Generic base agent providing lifecycle management
- Unique identity and metadata
- Lifecycle methods: `initialize()`, `start()`, `stop()`, `health_check()`
- Message handling via `handle_message()`
- State persistence support

#### LeadershipAgent (`agents/leadership_agent.py`)
- Extends BaseAgent with decision-making capabilities
- Decision-making with `make_decision()`
- Stakeholder coordination via `consult_stakeholders()`
- Consensus building patterns
- Decision provenance tracking

#### UnifiedAgentManager (`agents/manager.py`)
- Agent registration and deregistration
- Agent discovery and lookup
- Health monitoring across all agents
- Centralized agent lifecycle management

### 2. Service Interfaces (`services/interfaces.py`)

Clean service contracts for dependency injection:

- **IStorageService**: Storage operations (save, load, query, delete)
- **IMessagingService**: Messaging operations (publish, subscribe, send_to_agent)
- **IWorkflowService**: Workflow orchestration (execute_workflow, get_workflow_status)
- **IAuthService**: Authentication and authorization (authenticate, authorize)

### 3. Messaging Enhancements

#### MessageEnvelope (`messaging/envelope.py`)
- Standardized message format
- Correlation and causation IDs for distributed tracing
- Timestamp and actor information
- Schema validation support

#### Reliability Patterns (`messaging/reliability.py`)
- **RetryPolicy**: Exponential backoff with jitter
- **CircuitBreaker**: Fault tolerance pattern with configurable thresholds

### 4. Observability Foundation (`monitoring/observability.py`)

#### StructuredLogger
- Logging with context and correlation IDs
- Structured log format for better analysis
- Context propagation across operations

#### MetricsCollector
- Counter, gauge, and histogram metrics
- Tag-based categorization
- Simple in-memory collection

## Architecture Principles

### Single Responsibility
- **AOS**: Generic agent infrastructure, reusable across domains
- **Consumers**: Domain-specific logic built on AOS

### Dependency Direction
- Consumers depend on AOS interfaces
- AOS never depends on consumers
- One-way dependency for clean separation

### Interface-Based Design
- Clean service interfaces
- Enables testing with mocks
- Supports multiple implementations

## Breaking Changes and Compatibility

### Import Changes

**Old imports (still work)**:
```python
from AgentOperatingSystem.agents import LeadershipAgent
from AgentOperatingSystem.monitoring import MetricsCollector
```

**New imports (recommended)**:
```python
# New base classes with aliases
from AgentOperatingSystem.agents import BaseAgentNew, LeadershipAgentNew
from AgentOperatingSystem.agents import UnifiedAgentManager

# Direct imports from new modules
from AgentOperatingSystem.agents.base_agent import BaseAgent
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent

# Service interfaces
from AgentOperatingSystem.services.interfaces import IStorageService, IMessagingService

# Messaging components
from AgentOperatingSystem.messaging import MessageEnvelope, RetryPolicy, CircuitBreaker

# Observability with alias
from AgentOperatingSystem.monitoring import StructuredLogger, MetricsCollectorNew
```

### Backward Compatibility Strategy

The refactoring maintains backward compatibility by:
1. Keeping existing agent classes (`base.py`, `leadership.py`, etc.)
2. Adding new classes alongside existing ones
3. Using aliases (e.g., `BaseAgentNew`, `LeadershipAgentNew`) to avoid naming conflicts
4. Exporting both old and new classes from `__init__.py`

This allows:
- Existing code to continue working without changes
- New code to use clean interfaces
- Gradual migration path for consumers

## Usage Examples

### Creating a Custom Agent

```python
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
from typing import Dict, Any

class MyBusinessAgent(LeadershipAgent):
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            name="My Business Agent",
            role="business_analyst",
            config={}
        )
    
    async def initialize(self) -> bool:
        self.state = "initialized"
        return True
    
    async def start(self) -> bool:
        self.state = "running"
        return True
    
    async def stop(self) -> bool:
        self.state = "stopped"
        return True
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "processed", "agent": self.agent_id}
```

### Using the Agent Manager

```python
from AgentOperatingSystem.agents.manager import UnifiedAgentManager

# Create manager
manager = UnifiedAgentManager()

# Register agents
agent = MyBusinessAgent("agent_1")
await manager.register_agent(agent)

# Get agent
agent = manager.get_agent("agent_1")

# Health check all agents
health = await manager.health_check_all()
```

### Using Message Envelope

```python
from AgentOperatingSystem.messaging.envelope import MessageEnvelope

# Create message with correlation
envelope = MessageEnvelope(
    message_type="command",
    payload={"action": "process", "data": "value"},
    actor="user_123",
    correlation_id="trace_456"
)

# Convert to dict for transmission
message_dict = envelope.to_dict()

# Restore from dict
restored = MessageEnvelope.from_dict(message_dict)
```

### Using Retry Policy

```python
from AgentOperatingSystem.messaging.reliability import RetryPolicy

# Create retry policy
retry = RetryPolicy(max_attempts=3, initial_delay=1.0)

# Execute with retry
async def risky_operation():
    # Some operation that might fail
    pass

result = await retry.execute(risky_operation)
```

### Using Service Interfaces

```python
from AgentOperatingSystem.services.interfaces import IStorageService

class MyComponent:
    def __init__(self, storage: IStorageService):
        self.storage = storage  # Injected service
    
    async def save_data(self, key: str, data: Dict[str, Any]):
        await self.storage.save("my_collection", key, data)
```

## Migration Path for Consumers

1. **Update dependencies**: Use new AOS version in `pyproject.toml`
2. **Import new base classes**: Use `BaseAgentNew` and `LeadershipAgentNew` or direct imports
3. **Extend new classes**: Inherit from new base classes for business agents
4. **Use service interfaces**: Implement dependency injection with service interfaces
5. **Adopt reliability patterns**: Use `RetryPolicy` and `CircuitBreaker` for resilience
6. **Implement observability**: Use `StructuredLogger` and `MetricsCollectorNew` for monitoring

## Benefits

1. **Reusability**: Can be used by multiple domain applications
2. **Clarity**: Pure infrastructure with clear purpose
3. **Maintainability**: Single responsibility principle
4. **Testability**: Clean interfaces for mocking
5. **Flexibility**: Easy to change implementations
6. **Scalability**: Foundation for distributed agent systems

## Version Information

- **Version**: 2.0.0 (recommended for this refactoring)
- **Breaking Changes**: Yes, but backward compatible with aliases
- **Dependencies**: No new dependencies added

## Related Documentation

- `REFACTORING_README.md`: Implementation guide in repository root
- `MODULE_UPDATES.md`: Details on `__init__.py` updates (in temp directory)
- `INSTRUCTIONS.md`: Original PR creation instructions (in temp directory)

## Testing Recommendations

After implementing these changes:

1. Run existing AOS tests to ensure backward compatibility
2. Add new tests for new components:
   - Unit tests for `BaseAgent`, `LeadershipAgent`, `UnifiedAgentManager`
   - Tests for `RetryPolicy` and `CircuitBreaker`
   - Tests for `MessageEnvelope` serialization
   - Tests for `StructuredLogger` and `MetricsCollector`
3. Integration tests for agent manager
4. Verify imports work correctly

## Future Enhancements

Potential areas for future development:

1. **Event Sourcing**: Add event sourcing capabilities to agents
2. **Distributed Tracing**: Enhanced tracing with OpenTelemetry
3. **Service Mesh Integration**: Integration with service mesh for microservices
4. **Advanced Workflow**: More sophisticated workflow orchestration
5. **Multi-tenancy**: Support for multi-tenant agent systems

## Authors

- GitHub Copilot (refactoring implementation)
- ASISaga Team (specification and review)

## License

See LICENSE file for details.
