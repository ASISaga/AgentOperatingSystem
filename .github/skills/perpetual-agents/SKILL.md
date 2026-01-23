# Working with Perpetual Agents in AOS

## Description
Expert knowledge for working with Perpetual Agents and PurposeDrivenAgents in the Agent Operating System (AOS). This skill enables efficient development, debugging, and testing of perpetual agent implementations.

## When to Use This Skill
- Creating new perpetual agents
- Modifying existing agent behavior
- Debugging agent lifecycle issues
- Understanding agent state management
- Implementing purpose-driven decision making
- Working with ContextMCPServer for state preservation

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
# Use concrete implementations
agent = GenericPurposeDrivenAgent(agent_id="assistant", purpose="...", adapter_name="general")
# Or use specialized agents
agent = LeadershipAgent(agent_id="ceo", adapter_name="ceo")
manager.register_agent(agent)
# Agent continuously responds to events, state persists
```

### Agent Lifecycle
1. **Creation**: Create concrete agent instance (LeadershipAgent, GenericPurposeDrivenAgent, etc.)
2. **Initialization**: `await agent.initialize()` - Sets up ContextMCPServer
3. **Registration**: `manager.register_agent(agent)` - Makes agent available
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
from AgentOperatingSystem.agents import PerpetualAgent

# Create perpetual agent
agent = PerpetualAgent(
    agent_id="unique_agent_id",
    adapter_name="adapter_name"
)

# Initialize (creates ContextMCPServer)
await agent.initialize()

# Start perpetual operation
await agent.start()
```

### Creating a Purpose-Driven Agent (Recommended)
```python
from AgentOperatingSystem.agents import LeadershipAgent

# Create purpose-driven perpetual agent (using concrete subclass)
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
goals = await agent.get_goals()
await agent.update_goal(goal_id, status="in_progress")
```

### Agent Event Handling
```python
async def handle_event(self, event):
    """Override to handle events."""
    try:
        # Process event
        result = await self.process_event_logic(event)
        
        # Update state (automatically persisted)
        self.state["last_event"] = event
        await self.save_state()
        
        return result
    except Exception as e:
        self.logger.error(f"Error handling event: {e}")
        raise
```

### State Management
```python
# State is automatically persisted via ContextMCPServer
class MyAgent(PurposeDrivenAgent):
    async def initialize(self):
        await super().initialize()
        # Load persisted state
        self.state = await self.load_state() or {}
    
    async def update_state(self, key, value):
        self.state[key] = value
        # State automatically saved via ContextMCPServer
        await self.save_state()
    
    async def get_state(self, key):
        return self.state.get(key)
```

### Agent Registration with Manager
```python
from AgentOperatingSystem.orchestration import AgentManager

# Create manager
manager = AgentManager()

# Create and register agents
ceo_agent = LeadershipAgent(
    agent_id="ceo",
    purpose="Strategic oversight",
    adapter_name="ceo"
)
await ceo_agent.initialize()
manager.register_agent(ceo_agent)

cfo_agent = LeadershipAgent(
    agent_id="cfo", 
    purpose="Financial management",
    adapter_name="cfo"
)
await cfo_agent.initialize()
manager.register_agent(cfo_agent)

# Agents now run perpetually
```

## Testing Patterns

### Testing Perpetual Agents
```python
import pytest
from AgentOperatingSystem.agents import GenericPurposeDrivenAgent

@pytest.mark.asyncio
async def test_perpetual_agent_lifecycle():
    """Test agent creation and initialization."""
    agent = GenericPurposeDrivenAgent(
        agent_id="test_agent",
        purpose="Testing",
        adapter_name="test"
    )
    
    # Initialize
    await agent.initialize()
    assert agent.context_server is not None  # ContextMCPServer created
    
    # Test state persistence
    await agent.update_state("test_key", "test_value")
    state = await agent.get_state("test_key")
    assert state == "test_value"
    
    # Cleanup
    await agent.cleanup()

@pytest.mark.asyncio
async def test_purpose_alignment():
    """Test purpose-driven decision making."""
    agent = GenericPurposeDrivenAgent(
        agent_id="ceo",
        purpose="Strategic growth",
        purpose_scope="Major decisions",
        adapter_name="ceo"
    )
    await agent.initialize()
    
    # Test purpose alignment
    action = {"type": "hire", "role": "engineer"}
    alignment = await agent.evaluate_purpose_alignment(action)
    assert isinstance(alignment, float)
    assert 0.0 <= alignment <= 1.0
    
    await agent.cleanup()

@pytest.mark.asyncio
async def test_event_handling():
    """Test agent event processing."""
    agent = GenericPurposeDrivenAgent(
        agent_id="test",
        purpose="Event processing",
        adapter_name="test"
    )
    await agent.initialize()
    
    event = {"type": "test_event", "data": "test"}
    result = await agent.handle_event(event)
    
    # Verify state was updated
    last_event = await agent.get_state("last_event")
    assert last_event is not None
    
    await agent.cleanup()
```

### Mocking Azure Services
```python
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_agent_with_mocked_services():
    """Test agent with mocked Azure services."""
    agent = GenericPurposeDrivenAgent(
        agent_id="test",
        purpose="Testing",
        adapter_name="test"
    )
    
    # Mock ContextMCPServer
    agent.context_server = AsyncMock()
    agent.context_server.save_state = AsyncMock(return_value=True)
    agent.context_server.load_state = AsyncMock(return_value={})
    
    await agent.initialize()
    await agent.update_state("key", "value")
    
    # Verify mock was called
    agent.context_server.save_state.assert_called()
```

## Common Issues and Solutions

### Issue: Agent Not Receiving Events
**Problem**: Agent is registered but not responding to events.

**Solution**: 
1. Verify agent is initialized: `await agent.initialize()`
2. Check agent is registered: `manager.register_agent(agent)`
3. Ensure event routing is configured correctly
4. Verify agent's event handler is implemented

### Issue: State Not Persisting
**Problem**: Agent state is lost between events.

**Solution**:
1. Ensure ContextMCPServer is initialized during `agent.initialize()`
2. Call `await agent.save_state()` after state updates
3. Verify Azure Storage connection is configured
4. Check for errors in state persistence logs

### Issue: Memory Leaks with Perpetual Agents
**Problem**: Agent memory usage grows over time.

**Solution**:
1. Clean up old events/state periodically
2. Implement state rotation/archival
3. Use weak references for cached data
4. Monitor memory usage with observability tools

### Issue: Agent Initialization Fails
**Problem**: `await agent.initialize()` throws error.

**Solution**:
1. Check Azure credentials in environment/config
2. Verify adapter_name is valid
3. Ensure all required dependencies are installed
4. Check logs for specific error messages

## File Locations

### Core Agent Files
- `src/AgentOperatingSystem/agents/` - Agent implementations
  - `perpetual_agent.py` - Base perpetual agent
  - `purpose_driven_agent.py` - Purpose-driven agent
  - `base_agent.py` - Core agent interface

### Related Components
- `src/AgentOperatingSystem/mcp/context_server.py` - ContextMCPServer for state
- `src/AgentOperatingSystem/orchestration/agent_manager.py` - Agent registration
- `src/AgentOperatingSystem/messaging/` - Inter-agent communication

### Tests
- `tests/test_perpetual_agents.py` - Perpetual agent tests
- `tests/test_purpose_driven_integration.py` - Purpose-driven tests
- `examples/perpetual_agents_example.py` - Usage examples

## Key Differences from Traditional Agents

| Aspect | Traditional Agent | Perpetual Agent |
|--------|------------------|-----------------|
| Lifecycle | Created per task | Created once, runs forever |
| State | Lost after task | Persists via ContextMCPServer |
| Activation | Manual start/stop | Event-driven awakening |
| Context | Current task only | Full history via ContextMCPServer |
| Resource Use | Constant while running | Sleep when idle |
| Purpose | Short-term task | Long-term assigned purpose |

## Best Practices

1. **Always initialize**: Call `await agent.initialize()` before use
2. **Purpose-driven design**: Use PurposeDrivenAgent for better alignment
3. **Save state regularly**: Call `await agent.save_state()` after updates
4. **Clean up in tests**: Call `await agent.cleanup()` to prevent resource leaks
5. **Use meaningful IDs**: Agent IDs should be unique and descriptive
6. **Handle errors**: Wrap event handling in try/except blocks
7. **Log extensively**: Use structured logging for debugging
8. **Monitor state size**: Prevent unbounded state growth
9. **Test perpetual behavior**: Test long-running scenarios, not just single operations
10. **Leverage ContextMCPServer**: Use it for all state persistence needs

## Related Skills
- `azure-functions` - Deploying agents to Azure Functions
- `async-python` - Async/await patterns in Python
- `testing-aos` - Testing AOS components
- `mcp-integration` - Model Context Protocol usage

## Additional Resources
- README.md - Core concepts and perpetual vs task-based comparison
- docs/architecture/ARCHITECTURE.md - System architecture and agent layer
- examples/perpetual_agents_example.py - Complete examples
- docs/summaries/PERPETUAL_AGENTS_SUMMARY.md - Detailed perpetual agent documentation
