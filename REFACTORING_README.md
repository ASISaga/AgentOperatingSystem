# AgentOperatingSystem Refactoring - Implementation Guide

## Overview

This refactoring establishes AgentOperatingSystem as a pure, generic infrastructure layer for agent-based systems, removing any business-specific code and providing clean, well-defined service interfaces.

## What Changed

### New Components Added

#### 1. Enhanced Base Agent Classes
- **`agents/base_agent.py`**: Generic `BaseAgent` class with lifecycle management
  - Unique identity and metadata
  - Lifecycle methods (initialize, start, stop, health_check)
  - Message handling
  - State persistence
  
- **`agents/leadership_agent.py`**: `LeadershipAgent` extending BaseAgent
  - Decision-making capabilities
  - Stakeholder coordination
  - Consensus building patterns
  - Decision provenance

- **`agents/manager.py`**: `UnifiedAgentManager` for agent lifecycle
  - Agent registration and deregistration
  - Agent discovery and lookup
  - Health monitoring across all agents

#### 2. Service Interfaces
- **`services/interfaces.py`**: Clean service contracts
  - `IStorageService`: Storage operations interface
  - `IMessagingService`: Messaging operations interface
  - `IWorkflowService`: Workflow orchestration interface
  - `IAuthService`: Authentication and authorization interface

#### 3. Messaging Enhancements
- **`messaging/envelope.py`**: `MessageEnvelope` with correlation
  - Standardized message format
  - Correlation and causation IDs for tracing
  - Timestamp and actor information
  
- **`messaging/reliability.py`**: Reliability patterns
  - `RetryPolicy`: Exponential backoff with jitter
  - `CircuitBreaker`: Fault tolerance pattern

#### 4. Observability Foundation
- **`monitoring/observability.py`**: Structured logging and metrics
  - `StructuredLogger`: Logging with context and correlation
  - `MetricsCollector`: Metrics collection (counter, gauge, histogram)

## Breaking Changes

### Import Changes

**Before**:
```python
from AgentOperatingSystem.agents import LeadershipAgent
```

**After (with new classes)**:
```python
# New clean base classes
from AgentOperatingSystem.agents import BaseAgentNew, LeadershipAgentNew
from AgentOperatingSystem.agents import UnifiedAgentManager

# Or direct import from new modules
from AgentOperatingSystem.agents.base_agent import BaseAgent
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent

# Service interfaces
from AgentOperatingSystem.services.interfaces import IStorageService, IMessagingService

# Messaging components
from AgentOperatingSystem.messaging import MessageEnvelope, RetryPolicy, CircuitBreaker

# Observability
from AgentOperatingSystem.monitoring import StructuredLogger, MetricsCollector
```

### Agent Class Changes

**Before**: Various agent patterns

**After**: Must extend `BaseAgent` or `LeadershipAgent` (new classes)

Example:
```python
from AgentOperatingSystem.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
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
        return {"status": "processed"}
```

### Service Access Changes

**After**: Use service interfaces for dependency injection

```python
from AgentOperatingSystem.services.interfaces import IStorageService

class MyComponent:
    def __init__(self, storage: IStorageService):
        self.storage = storage  # Injected service
    
    async def save_data(self, key: str, data: Dict[str, Any]):
        await self.storage.save("my_collection", key, data)
```

## Compatibility

The refactoring maintains backward compatibility with existing code by:
- Keeping existing agent classes (`base.py`, `leadership.py`, etc.)
- Adding new classes alongside existing ones
- Exporting both old and new classes from `__init__.py`

Existing code continues to work, and new code can use the clean interfaces.

## Migration Path for Consumers

### For BusinessInfinity

1. **Update dependencies** to use new AOS version
2. **Import new base classes**:
   ```python
   from AgentOperatingSystem.agents.base_agent import BaseAgent
   from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
   ```
3. **Extend new classes** for business agents
4. **Use service interfaces** for dependency injection

See BusinessInfinity's `MIGRATION_GUIDE.md` for detailed steps.

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

## Testing

The refactoring includes:
- Unit tests for base agent classes
- Tests for reliability patterns
- Integration tests for agent manager

Run tests:
```bash
pytest tests/
```

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
        # Custom initialization
        self.state = "initialized"
        return True
    
    async def start(self) -> bool:
        self.state = "running"
        return True
    
    async def stop(self) -> bool:
        self.state = "stopped"
        return True
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # Custom message handling
        return {"status": "processed", "agent": self.agent_id}
```

### Using the Agent Manager

```python
from AgentOperatingSystem.agents.manager import UnifiedAgentManager

# Create manager
manager = UnifiedAgentManager()

# Register agents
agent1 = MyBusinessAgent("agent_1")
await manager.register_agent(agent1)

# Get agent
agent = manager.get_agent("agent_1")

# Health check all agents
health = await manager.health_check_all()
```

### Using Message Envelope

```python
from AgentOperatingSystem.messaging.envelope import MessageEnvelope

# Create message
envelope = MessageEnvelope(
    message_type="command",
    payload={"action": "process", "data": "value"},
    actor="user_123",
    correlation_id="trace_456"
)

# Convert to dict
message_dict = envelope.to_dict()

# Create from dict
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

## Benefits

1. **Reusability**: Can be used by multiple domain applications
2. **Clarity**: Pure infrastructure with clear purpose
3. **Maintainability**: Single responsibility principle
4. **Testability**: Clean interfaces for mocking
5. **Flexibility**: Easy to change implementations

## Version

This refactoring is part of AOS v2.0.0, which introduces breaking changes.

## Support

For questions or issues, refer to:
- **AOS_REFACTORING_SPEC.md** (BusinessInfinity repo): Complete specification
- **MIGRATION_GUIDE.md** (BusinessInfinity repo): Consumer migration guide
- **REFACTORING_SUMMARY.md** (BusinessInfinity repo): Overall vision

## Authors

- GitHub Copilot (refactoring implementation)
- ASISaga Team (specification and review)

## License

See LICENSE file for details.
