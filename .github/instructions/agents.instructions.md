# Agent Patterns and Architecture

## Purpose-Driven Agents

**PurposeDrivenAgent** is the fundamental building block of AOS, combining perpetual operation with purpose alignment. It is a **directly-instantiable** class that can be used on its own or extended by more specialised agents.

### Core Design Principles

- **Single purpose**: There is exactly one purpose per agent. It is added to the LLM context during initialization so that every decision is purpose-aligned.
- **LoRA Adapters**: Provide domain-specific vocabulary, persona, and knowledge. Each class in the inheritance chain contributes exactly one adapter via `_add_layer()`.
- **MCP (Model Context Protocol)**: Provides context management, domain-specific tools, and access to contemporary software systems.
- **Deployable**: `PurposeDrivenAgent.deploy()` invokes the Python Azure deployment orchestrator. Derived-agent GitHub workflows call this method.

### Agent Inheritance Hierarchy

```
PurposeDrivenAgent  (directly instantiable — the fundamental building block)
├── LeadershipAgent (adds Leadership LoRA adapter + context + skills)
│   └── CMOAgent    (adds Marketing LoRA adapter + context + skills)
└── PurposeDrivenAgentFoundry (extends with Microsoft Foundry runtime)
```

`GenericPurposeDrivenAgent`, `BaseAgent`, and `PerpetualAgent` are backward-compatibility aliases for `PurposeDrivenAgent`.

## Perpetual Agents

Agents in AOS run indefinitely, not as one-off tasks. All agents inherit from PurposeDrivenAgent:

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent

agent = PurposeDrivenAgent(agent_id="assistant", purpose="General assistance", adapter_name="general")
# Or use specialized agents like LeadershipAgent, CMOAgent, etc.
```

**Key characteristics:**
- Persistent: Remains registered and active indefinitely
- Event-driven: Awakens in response to events
- Stateful: Maintains context across all interactions via MCP
- Resource-efficient: Sleeps when idle, awakens on events

## PurposeDrivenAgent (Directly Instantiable)

The fundamental building block — directly instantiable with a single purpose:

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent

# Direct instantiation — one purpose, one LoRA adapter layer
agent = PurposeDrivenAgent(
    agent_id="assistant",
    purpose="General assistance and task execution",
    purpose_scope="General operations",
    adapter_name="general"   # LoRA adapter providing vocabulary, persona, knowledge
)

# The purpose is automatically added to the LLM context on initialize()
await agent.initialize()
await agent.start()

# Deploy to Azure via the Python deployment orchestrator
agent.deploy(environment="dev", resource_group="my-rg")
```

**Key characteristics:**
- **Directly instantiable**: Use it directly or extend it
- **Single purpose**: Exactly one purpose, added to LLM context
- **Perpetual**: Runs indefinitely
- **Context-aware**: Uses ContextMCPServer for state preservation
- **Event-responsive**: Awakens on events relevant to its purpose
- **Autonomous**: Makes decisions aligned with its purpose
- **Deployable**: `deploy()` pushes the agent to Azure via the orchestrator

## LeadershipAgent

Extends PurposeDrivenAgent with a leadership layer (adds adapter + context + skills):

```python
from AgentOperatingSystem.agents import LeadershipAgent

agent = LeadershipAgent(
    agent_id="leader",
    purpose="Leadership: Strategic decision-making and team coordination",
    adapter_name="leadership"  # Maps to "leadership" LoRA adapter
)
```

**What LeadershipAgent adds over PurposeDrivenAgent:**
- LoRA adapter: `"leadership"` (leadership vocabulary, persona, domain knowledge)
- Domain context: `{domain, purpose, capabilities}`
- Skills: `make_decision`, `consult_stakeholders`

## CMOAgent (Chief Marketing Officer)

Extends LeadershipAgent with a marketing layer:

```python
from AgentOperatingSystem.agents import CMOAgent

cmo = CMOAgent(
    agent_id="cmo",
    marketing_adapter_name="marketing",
    leadership_adapter_name="leadership"
)

# Layer stack (base → most specific):
print(cmo.get_adapters())   # ["leadership", "marketing"]
print(cmo.get_all_skills()) # make_decision, consult_stakeholders, analyze_market, …

# Execute tasks with a specific layer's adapter
await cmo.execute_with_purpose(task, purpose_type="marketing")
await cmo.execute_with_purpose(task, purpose_type="leadership")
```

## Layer Stacking Architecture

Each class in the inheritance chain calls `self._add_layer()` once in its `__init__` to contribute:
- **adapter_name**: LoRA adapter for this domain (vocabulary, persona, knowledge)
- **context**: domain-specific key-value pairs stored in MCP during `initialize()`
- **skills**: list of skill/capability names introduced at this level

```python
# Access accumulated layers
agent.get_adapters()        # ["leadership", "marketing"]   — ordered list
agent.get_all_skills()      # union of all skill names
agent.get_layer_contexts()  # merged context dict from all layers
agent.get_agent_type()      # alias for get_adapters()
```

## Deployment

Every `PurposeDrivenAgent` (and its subclasses) can deploy itself to Azure:

```python
# Deploy to dev environment
return_code = agent.deploy(environment="dev", resource_group="my-agents-rg")

# Deploy to production with a specific region
return_code = agent.deploy(
    environment="prod",
    resource_group="prod-agents-rg",
    location="eastus",
    extra_args=["--skip-health-checks"],
)
```

The `deploy()` method invokes `deployment/deploy.py` (the Python Bicep orchestrator).
Derived-agent GitHub workflows call `agent.deploy()` to push updates to Azure.

## Agent Lifecycle

### Initialization
```python
agent = PurposeDrivenAgent(agent_id="...", purpose="...", adapter_name="...")
# Or use a specialized agent
agent = LeadershipAgent(agent_id="...", purpose="...", adapter_name="...")

await agent.initialize()  # Sets up MCP context server, stores purpose + layer contexts
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
- Always provide a clear, specific purpose (exactly one per agent)
- Map purpose to appropriate LoRA adapter for domain expertise
- Define success criteria when possible
- Use descriptive agent_id values

### Extending PurposeDrivenAgent
```python
class MyAgent(PurposeDrivenAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id=agent_id, purpose="My domain purpose", adapter_name=None)
        self._add_layer(
            adapter_name="my-domain",
            context={"domain": "my-domain", "capabilities": ["skill_a"]},
            skills=["skill_a", "skill_b"],
        )
```

### State Management
- Agents maintain state via ContextMCPServer
- State persists across events (perpetual nature)
- Clean up state in tests to avoid cross-test contamination

### Purpose Alignment
- Regularly evaluate actions against purpose
- Use purpose-driven decision making methods
- Track purpose metrics for monitoring

