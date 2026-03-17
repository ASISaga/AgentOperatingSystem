# Perpetual vs Task-Based Agents

**The key difference between Agent Operating System and traditional AI Orchestration frameworks is PERSISTENCE.**

## Traditional AI Orchestration Frameworks

Traditional Orchestration frameworks run **Temporary Task-Based Sessions**:
- ▶️ Start an Agent Orchestration for a specific task
- ⚙️ Agent Orchestration processes the task sequentially or hierarchically  
- ⏹️ Agent Orchestration completes and terminates
- 💾 State is lost (unless explicitly saved)
- 🔄 Must restart Agent Orchestration for next task

**Memory is session-focused** - Agents remember only the current mission.

## Agent Operating System (Perpetual Orchestration)

AOS agents are **Purpose-Driven Perpetual entities that never stop**:
- 🔄 Register agent once - it runs indefinitely
- 😴 Agent sleeps when idle (resource efficient)
- ⚡ Agent awakens automatically when events occur
- 💾 State persists forever via dedicated ContextMCPServer
- 🎯 Event-driven, Perpetual Orchestration, with reactive behavior
- 🏃 Never terminates unless explicitly deregistered
- 🎭 **PurposeDrivenAgent** works against Perpetual, Assigned purpose (not short-term tasks)

**Memory is persistent** - agents build knowledge continuously over their lifetime through MCP context preservation.

## The Foundation: PurposeDrivenAgent

**PurposeDrivenAgent** (implemented in AOS, will be moved to dedicated repository) inherits from **PerpetualAgent** and is the fundamental building block of AgentOperatingSystem. It makes AOS an operating system of Purpose-Driven, Perpetual Agents.

**Key Features:**
- Uses **ContextMCPServer** (common infrastructure) for state preservation
- Works against perpetual, assigned purpose (not short-term tasks)
- Purpose alignment evaluation for all actions
- Purpose-driven decision making
- Goal management aligned with purpose

### Example Usage

```python
from AgentOperatingSystem.agents import LeadershipAgent
from AgentOperatingSystem.mcp import ContextMCPServer

# Native AOS agent - purpose-driven and perpetual
agent = LeadershipAgent(
    agent_id="ceo",
    purpose="Strategic oversight and company growth",
    purpose_scope="Strategic planning, major decisions",
    success_criteria=["Revenue growth", "Team expansion"],
    adapter_name="ceo"
)

await agent.initialize()  # ContextMCPServer automatically created
await agent.start()       # Runs perpetually

# Purpose-driven operations
alignment = await agent.evaluate_purpose_alignment(action)
decision = await agent.make_purpose_driven_decision(context)
goal_id = await agent.add_goal("Increase revenue by 50%")
```

## Why This Matters

| Aspect | Traditional (Task-Based) | AOS (Perpetual + Purpose-Driven) |
|--------|-------------------------|----------------------------------|
| **Lifecycle** | Temporary session | Permanent entity |
| **Activation** | Manual start/stop | Event-driven awakening |
| **State** | Lost after completion | Persists via ContextMCPServer indefinitely |
| **Context** | Current task only | Full history via ContextMCPServer |
| **Purpose** | Short-term tasks | Long-term assigned purpose |
| **Operations** | Sequential tasks | Continuous operations |
| **Paradigm** | Script execution | Operating system |

## Code Comparison

### Traditional Framework
```python
# Traditional Framework
for task in tasks:
    agent = create_agent()      # Create new agent
    result = agent.run(task)    # Process task
    # Agent terminates, state lost
```

### Agent Operating System - Perpetual Operation
```python
# Agent Operating System - Perpetual Operation
from AgentOperatingSystem.agents import PerpetualAgent
agent = PerpetualAgent(agent_id="ceo", adapter_name="ceo")
manager.register_agent(agent)  # Register once, runs perpetually by default
# Agent now runs FOREVER, responding to events automatically
# State persists via dedicated ContextMCPServer across all events
```

### Purpose-Driven Perpetual Agent
```python
# Purpose-Driven Perpetual Agent (Fundamental Building Block)
from AgentOperatingSystem.agents import LeadershipAgent
purpose_agent = LeadershipAgent(
    agent_id="ceo",
    purpose="Strategic oversight and decision-making",
    purpose_scope="Strategic planning, major decisions",
    adapter_name="ceo"
)
# Works against assigned purpose perpetually, not short-term tasks
```

## See Also

- [Vision](vision.md) - The operating system for the AI era
- [Architecture](../architecture/ARCHITECTURE.md) - Detailed architecture
- [Services](services.md) - Operating system services
