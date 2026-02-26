---
name: perpetual-agents
description: Expert knowledge for working with PurposeDrivenAgents in the Agent Operating System (AOS). Enables efficient development, debugging, and testing of perpetual agent implementations.
---

# Working with PurposeDrivenAgents in AOS

## Description
Expert knowledge for working with PurposeDrivenAgents in the Agent Operating System (AOS). This skill enables efficient development, debugging, and testing of perpetual agent implementations.

## When to Use This Skill
- Creating new purpose-driven perpetual agents
- Modifying existing agent behavior
- Debugging agent lifecycle issues
- Understanding agent state management
- Implementing purpose-driven decision making
- Working with ContextMCPServer for state preservation
- Deploying agents to Azure

## Key Concepts

### Perpetual vs Task-Based Agents
**Traditional (Task-Based)**:
```python
# Agent created, runs, then terminates
agent = create_agent()
result = agent.run(task)
# Agent and state are lost
```

**Perpetual (AOS)**:
```python
# Agent registered once, runs forever
agent = PurposeDrivenAgent(agent_id="assistant", purpose="...", adapter_name="general")
# Or use specialized agents
agent = LeadershipAgent(agent_id="ceo", adapter_name="ceo")
manager.register_agent(agent)
# Agent continuously responds to events, state persists
```

### Core Design Principles
- **Single purpose**: Exactly one purpose per agent, added to LLM context.
- **Layer stacking**: Each class in the inheritance chain calls `_add_layer()` once to contribute its LoRA adapter (vocabulary, persona, knowledge), domain context, and skills.
- **Deployable**: `agent.deploy()` pushes the agent to Azure via the Python deployment orchestrator.

### Agent Lifecycle
1. **Creation**: `PurposeDrivenAgent(...)` or a specialized subclass
2. **Initialization**: `await agent.initialize()` — sets up ContextMCPServer, stores purpose + layer contexts
3. **Registration**: `manager.register_agent(agent)` — makes agent available
4. **Event Loop**: Agent automatically responds to events while sleeping when idle
5. **Deregistration**: Only when explicitly removed

### State Persistence
- All agent state is preserved via **ContextMCPServer**
- State persists across all events and agent restarts
- Agents maintain full history and context
- No state is lost between operations

## Code Patterns

### Creating a Basic Perpetual Agent
```python
from AgentOperatingSystem.agents import PurposeDrivenAgent

# Create perpetual agent directly (no need for a separate subclass)
agent = PurposeDrivenAgent(
    agent_id="unique_agent_id",
    purpose="My agent's single, long-term purpose",
    adapter_name="adapter_name"   # LoRA adapter: vocabulary, persona, domain knowledge
)

# Initialize (creates ContextMCPServer, stores purpose in context)
await agent.initialize()

# Start perpetual operation
await agent.start()
```

### Creating a Purpose-Driven Agent (Specialized Subclass)
```python
from AgentOperatingSystem.agents import LeadershipAgent

# Create purpose-driven perpetual agent (specialized subclass)
agent = LeadershipAgent(
    agent_id="ceo",
    purpose="Strategic oversight and company growth",
    purpose_scope="Strategic planning, major decisions, resource allocation",
    success_criteria=["Revenue growth", "Team expansion", "Customer satisfaction"],
    adapter_name="ceo"
)

# Initialize
await agent.initialize()  # ContextMCPServer automatically created

# Start
await agent.start()

# Purpose-driven operations
alignment_score = await agent.evaluate_purpose_alignment(action)
decision = await agent.make_purpose_driven_decision(context)
goal_id = await agent.add_goal("Increase revenue by 50%")
```

### Extending PurposeDrivenAgent with a New Layer
```python
from AgentOperatingSystem.agents import PurposeDrivenAgent

class MyDomainAgent(PurposeDrivenAgent):
    def __init__(self, agent_id: str, purpose: str):
        super().__init__(agent_id=agent_id, purpose=purpose, adapter_name=None)
        self._add_layer(
            adapter_name="my-domain",
            context={
                "domain": "my-domain",
                "capabilities": ["capability_a", "capability_b"],
            },
            skills=["skill_a", "skill_b"],
        )
```

### Deploying an Agent to Azure
```python
# Deploy to dev (invokes deployment/deploy.py — the Python Bicep orchestrator)
return_code = agent.deploy(environment="dev", resource_group="my-agents-rg")

# Deploy to production with specific region
return_code = agent.deploy(
    environment="prod",
    resource_group="prod-agents-rg",
    location="eastus",
)
assert return_code == 0, "Deployment failed"
```

### Agent Event Handling
```python
async def handle_event(self, event):
    """Override to handle events."""
    try:
        result = await self.process_event_logic(event)
        await self._save_context_to_mcp()
        return result
    except Exception as e:
        self.logger.error(f"Error handling event: {e}")
        raise
```

### Agent Registration with Manager
```python
from AgentOperatingSystem.orchestration import AgentManager
from AgentOperatingSystem.agents import LeadershipAgent

manager = AgentManager()

ceo_agent = LeadershipAgent(agent_id="ceo", purpose="Strategic oversight", adapter_name="ceo")
await ceo_agent.initialize()
manager.register_agent(ceo_agent)

# Agent now runs perpetually
```

## Testing Patterns

### Testing Perpetual Agents
```python
import pytest
from AgentOperatingSystem.agents import PurposeDrivenAgent

@pytest.mark.asyncio
async def test_perpetual_agent_lifecycle():
    """Test agent creation and initialization."""
    agent = PurposeDrivenAgent(
        agent_id="test_agent",
        purpose="Testing",
        adapter_name="test"
    )
    
    # Initialize
    success = await agent.initialize()
    assert success
    assert agent.mcp_context_server is not None
    
    # Test purpose in context
    ctx = agent.get_layer_contexts()
    assert ctx["purpose"] == "Testing"
    
    # Cleanup
    await agent.stop()
```

### Mocking Azure Services
```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_agent_with_mocked_services():
    agent = PurposeDrivenAgent(agent_id="test", purpose="Testing", adapter_name="test")
    agent.mcp_context_server = AsyncMock()
    agent.mcp_context_server.initialize = AsyncMock()
    agent.mcp_context_server.set_context = AsyncMock()
    agent.mcp_context_server.get_context = AsyncMock(return_value=None)
    agent.mcp_context_server.get_all_context = AsyncMock(return_value={})
    await agent.initialize()
```

## Common Issues and Solutions

### Issue: Agent Not Receiving Events
**Solution**: Verify agent is initialized and registered; check event routing.

### Issue: State Not Persisting
**Solution**: Ensure ContextMCPServer is initialized; call `_save_context_to_mcp()` after updates.

### Issue: Deployment Fails
**Solution**: Check Azure credentials; verify `deployment/deploy.py` exists in the repository root.

## File Locations

### Core Agent Files
- `src/AgentOperatingSystem/agents/purpose_driven.py` — PurposeDrivenAgent (and GenericPurposeDrivenAgent alias)
- `src/AgentOperatingSystem/agents/leadership_agent.py` — LeadershipAgent
- `src/AgentOperatingSystem/agents/cmo_agent.py` — CMOAgent

### Related Components
- `src/AgentOperatingSystem/mcp/context_server.py` — ContextMCPServer for state
- `src/AgentOperatingSystem/orchestration/agent_manager.py` — Agent registration
- `deployment/deploy.py` — Python Azure deployment orchestrator

### Tests
- `tests/test_perpetual_agents.py` — Perpetual agent tests
- `tests/test_purpose_driven_integration.py` — Purpose-driven tests
- `tests/test_agent_personas.py` — Layer stacking tests
- `examples/perpetual_agents_example.py` — Usage examples

## Key Differences from Traditional Agents

| Aspect | Traditional Agent | Perpetual Agent |
|--------|------------------|-----------------|
| Lifecycle | Created per task | Created once, runs forever |
| State | Lost after task | Persists via ContextMCPServer |
| Activation | Manual start/stop | Event-driven awakening |
| Context | Current task only | Full history via ContextMCPServer |
| Resource Use | Constant while running | Sleep when idle |
| Purpose | Short-term task | Long-term assigned purpose |

## Related Skills
- `azure-functions` — Deploying agents to Azure Functions
- `async-python-testing` — Async/await patterns in Python testing
- `aos-architecture` — Agent Operating System architecture
- `leadership-agent` — LeadershipAgent-specific patterns
- `cmo-agent` — CMOAgent-specific patterns

