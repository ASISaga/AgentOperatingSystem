# Agent Patterns and Architecture

## Purpose-Driven Agents

**PurposeDrivenAgent** is the fundamental building block of AOS, combining perpetual operation with purpose alignment. It is an **abstract base class** that should be extended by concrete implementations.

### Architecture Components

- **LoRA Adapters**: Provide domain-specific knowledge (language, vocabulary, concepts, and importantly **agent persona**) to PurposeDrivenAgents
- **Core Purposes**: Added to the primary LLM context of PurposeDrivenAgents to guide agent behavior
- **MCP (Model Context Protocol)**: Provides context management, domain-specific tools, and access to contemporary software systems

### Agent Inheritance Hierarchy

```
PurposeDrivenAgent (abstract base class - fundamental building block)
├── GenericPurposeDrivenAgent (concrete implementation for general use)
├── LeadershipAgent (adds Leadership purpose)
│   └── CMOAgent (adds Marketing purpose + inherits Leadership)
└── PurposeDrivenAgentFoundry (extends with Microsoft Foundry runtime)
```

## Perpetual Agents

Agents in AOS run indefinitely, not as one-off tasks. All agents inherit from PurposeDrivenAgent (abstract base class):

```python
from AgentOperatingSystem.agents import GenericPurposeDrivenAgent

agent = GenericPurposeDrivenAgent(agent_id="assistant", purpose="General assistance", adapter_name="general")
# Or use specialized agents like LeadershipAgent, CMOAgent, etc.
```

**Key characteristics:**
- Persistent: Remains registered and active indefinitely
- Event-driven: Awakens in response to events
- Stateful: Maintains context across all interactions via MCP
- Resource-efficient: Sleeps when idle, awakens on events

## PurposeDrivenAgent (Abstract Base Class)

The fundamental building block - an abstract base class that defines the interface for all purpose-driven agents:

```python
# PurposeDrivenAgent is abstract - cannot be instantiated directly
# from AgentOperatingSystem.agents import PurposeDrivenAgent
# agent = PurposeDrivenAgent(...)  # ❌ This will raise TypeError

# Instead, use concrete implementations:
from AgentOperatingSystem.agents import GenericPurposeDrivenAgent, LeadershipAgent

# Option 1: Generic implementation for general-purpose agents
agent = GenericPurposeDrivenAgent(
    agent_id="assistant",
    purpose="General assistance and task execution",
    purpose_scope="General operations",
    adapter_name="general"
)

# Option 2: Specialized implementation (recommended)
agent = LeadershipAgent(
    agent_id="ceo",
    purpose="Strategic oversight and company growth",
    purpose_scope="Strategic planning, major decisions",
    adapter_name="ceo"  # Maps to LoRA adapter for domain knowledge & persona
)
```

**Key characteristics:**
- **Abstract**: Must be extended by concrete implementations
- **Perpetual**: Runs indefinitely
- **Purpose-driven**: Works toward a defined, long-term purpose
- **Context-aware**: Uses ContextMCPServer for state preservation
- **Event-responsive**: Awakens on events relevant to its purpose
- **Autonomous**: Makes decisions aligned with its purpose
- **Adapter-mapped**: Purpose mapped to LoRA adapter for domain expertise

## GenericPurposeDrivenAgent

Concrete implementation for general-purpose agents:

```python
from AgentOperatingSystem.agents import GenericPurposeDrivenAgent

agent = GenericPurposeDrivenAgent(
    agent_id="assistant",
    purpose="General assistance and task execution",
    adapter_name="general"
)
```

Use this when you need a basic purpose-driven agent. For specialized functionality, create custom subclasses.

## LeadershipAgent

Extends PurposeDrivenAgent with leadership and decision-making capabilities:

```python
from AgentOperatingSystem.agents import LeadershipAgent

agent = LeadershipAgent(
    agent_id="leader",
    purpose="Leadership: Strategic decision-making and team coordination",
    adapter_name="leadership"  # Maps to "leadership" LoRA adapter
)
```

**Capabilities:**
- Decision-making
- Stakeholder coordination
- Consensus building
- Delegation patterns
- Decision provenance

The Leadership purpose is mapped to the "leadership" LoRA adapter, which provides leadership-specific domain knowledge and agent persona. The core purpose is added to the primary LLM context to guide agent behavior.

## CMOAgent (Chief Marketing Officer)

Extends LeadershipAgent with dual purposes mapped to multiple LoRA adapters:

```python
from AgentOperatingSystem.agents import CMOAgent

# CMOAgent has TWO purposes mapped to TWO LoRA adapters:
# 1. Marketing purpose -> "marketing" LoRA adapter
# 2. Leadership purpose -> "leadership" LoRA adapter (inherited)

cmo = CMOAgent(
    agent_id="cmo",
    marketing_adapter_name="marketing",      # Marketing LoRA adapter
    leadership_adapter_name="leadership"     # Leadership LoRA adapter
)

# Check purpose-to-adapter mappings
status = await cmo.get_status()
print(status["purposes"])
# {
#   "marketing": {"adapter": "marketing", ...},
#   "leadership": {"adapter": "leadership", ...}
# }

# Execute tasks with specific purpose/adapter
await cmo.execute_with_purpose(task, purpose_type="marketing")  # Uses marketing adapter
await cmo.execute_with_purpose(task, purpose_type="leadership") # Uses leadership adapter
```

**Capabilities:**
- Marketing strategy and execution
- Brand management
- Customer acquisition and retention
- Market analysis
- Leadership and decision-making (inherited)

**Architecture:**
This agent maps two purposes to LoRA adapters:
1. Marketing purpose → "marketing" LoRA adapter (provides marketing domain knowledge & persona)
2. Leadership purpose → "leadership" LoRA adapter (provides leadership domain knowledge & persona)

The core purposes are added to the primary LLM context to guide behavior. MCP integration provides context management and domain-specific tools.

## Key Concept: Purpose-to-Adapter Mapping

PurposeDrivenAgent and its subclasses map purposes to LoRA adapters through configuration. This allows agents to leverage domain-specific fine-tuned models for different aspects of their responsibilities.

- **LoRA adapters** provide domain-specific knowledge including language, vocabulary, concepts, and agent persona
- **Core purposes** are incorporated into the primary LLM context to guide agent behavior
- **MCP integration** enables context management, domain tools, and access to external software systems

## Agent Lifecycle

### Initialization
```python
# Use concrete implementation
agent = GenericPurposeDrivenAgent(agent_id="...", purpose="...", adapter_name="...")
# Or use specialized agent
agent = LeadershipAgent(agent_id="...", purpose="...", adapter_name="...")

await agent.initialize()  # Sets up MCP context server, loads state
```

### Running
```python
await agent.start()  # Begins perpetual operation
# Agent runs indefinitely, responding to events
```

### Cleanup
```python
await agent.stop()  # Graceful shutdown, saves state
```

## Best Practices

### Agent Creation
- Always provide a clear, specific purpose
- Map purpose to appropriate LoRA adapter for domain expertise
- Define success criteria when possible
- Use descriptive agent_id values

### State Management
- Agents maintain state via ContextMCPServer
- State persists across events (perpetual nature)
- Clean up state in tests to avoid cross-test contamination

### Purpose Alignment
- Regularly evaluate actions against purpose
- Use purpose-driven decision making methods
- Track purpose metrics for monitoring

### Multi-Purpose Agents
- Use inheritance to add purposes (like CMOAgent)
- Each purpose should map to appropriate LoRA adapter
- Allow switching between adapters based on task type
