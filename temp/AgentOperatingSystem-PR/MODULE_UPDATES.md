# Module Updates Required

These are the changes needed to existing `__init__.py` files in the AgentOperatingSystem repository.

## 1. `src/AgentOperatingSystem/agents/__init__.py`

Add these imports and exports:

```python
# Add to imports section
from .base_agent import BaseAgent as BaseAgentNew
from .leadership_agent import LeadershipAgent as LeadershipAgentNew
from .manager import UnifiedAgentManager

# Add to __all__ list
__all__ = [
    # ... existing exports ...
    "BaseAgentNew",
    "LeadershipAgentNew",
    "UnifiedAgentManager"
]
```

**Note**: We use aliases (`BaseAgentNew`, `LeadershipAgentNew`) to avoid conflicts with existing classes and maintain backward compatibility.

## 2. `src/AgentOperatingSystem/messaging/__init__.py`

Add these imports and exports:

```python
# Add to imports section
from .envelope import MessageEnvelope
from .reliability import RetryPolicy, CircuitBreaker

# Add to __all__ list
__all__ = [
    # ... existing exports ...
    "MessageEnvelope",
    "RetryPolicy",
    "CircuitBreaker"
]
```

## 3. `src/AgentOperatingSystem/monitoring/__init__.py`

Add these imports and exports:

```python
# Add to imports section  
from .observability import StructuredLogger, MetricsCollector as MetricsCollectorNew

# Add to __all__ list
__all__ = [
    # ... existing exports ...
    "StructuredLogger",
    "MetricsCollectorNew"  # Aliased to avoid conflict with existing MetricsCollector
]
```

**Note**: We use alias for `MetricsCollector` to avoid conflicts with existing implementation.

## Complete Example for agents/__init__.py

Here's what the complete file might look like (adjust based on current content):

```python
"""
AOS Agent Module

Base agent classes and agent-related functionality.
"""

from .base import BaseAgent, Agent, StatefulAgent
from .base_agent import BaseAgent as BaseAgentNew
from .leadership import LeadershipAgent
from .leadership_agent import LeadershipAgent as LeadershipAgentNew
from .manager import UnifiedAgentManager
from .perpetual import PerpetualAgent
from .multi_agent import (
    MultiAgentSystem, 
    BusinessAnalystAgent, 
    SoftwareEngineerAgent, 
    ProductOwnerAgent,
    ApprovalTerminationStrategy
)

__all__ = [
    # Existing classes
    "BaseAgent",
    "Agent",
    "StatefulAgent", 
    "LeadershipAgent",
    "PerpetualAgent",
    "MultiAgentSystem",
    "BusinessAnalystAgent",
    "SoftwareEngineerAgent", 
    "ProductOwnerAgent",
    "ApprovalTerminationStrategy",
    # New refactored classes
    "BaseAgentNew",
    "LeadershipAgentNew",
    "UnifiedAgentManager"
]
```

## Backward Compatibility

By using aliases, we ensure:
- ✅ Existing code continues to work
- ✅ New code can use the refactored classes
- ✅ No breaking changes for current consumers
- ✅ Clear migration path to new classes

## Migration Path

Consumers can gradually migrate:

**Old way** (still works):
```python
from AgentOperatingSystem.agents import LeadershipAgent
```

**New way** (recommended):
```python
from AgentOperatingSystem.agents import LeadershipAgentNew as LeadershipAgent
```

Or for new code:
```python
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
```
