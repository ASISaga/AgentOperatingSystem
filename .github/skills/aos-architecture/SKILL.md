# Agent Operating System Architecture

## Description
Expert knowledge of the Agent Operating System (AOS) architecture, components, and design patterns. This skill provides deep understanding of how AOS works as a complete operating system for AI agents.

## When to Use This Skill
- Understanding AOS architecture and design
- Working across multiple AOS components
- Making architectural decisions
- Integrating new components
- Understanding component interactions
- Debugging cross-component issues

## Core Architectural Concept

### Operating System Paradigm
AOS is an **operating system** for AI agents, not a framework or library. This means:

- **Kernel**: Core orchestration engine
- **System Services**: Storage, messaging, auth, etc.
- **Applications**: Business agents (CEO, CFO, etc.)
- **System Calls**: Python APIs to access services
- **Processes**: Perpetual agents (like daemons)
- **IPC**: Inter-agent messaging

### Perpetual vs Task-Based (The Fundamental Difference)

**Task-Based Frameworks** (Traditional):
```
Create Agent → Execute Task → Terminate → State Lost
```

**Perpetual Architecture** (AOS):
```
Register Agent → Runs Forever → Event-Driven → State Persists
```

This is the **defining characteristic** of AOS architecture.

## Architectural Layers

### 1. Application Layer
Business applications and agents that use AOS services.

**Components**:
- PurposeDrivenAgent (fundamental building block)
- Custom business agents (CEO, CFO, CTO)
- Business applications using AOS

**Location**: External applications, `examples/`

**Key Pattern**: Applications extend base classes and use system APIs

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent

class CEOAgent(PurposeDrivenAgent):
    """Business-specific agent using AOS."""
    def __init__(self):
        super().__init__(
            agent_id="ceo",
            purpose="Strategic oversight",
            adapter_name="ceo"
        )
```

### 2. System Service Layer
Services that agents use (like OS system calls).

**Core Services**:
- **Authentication & Authorization** (`auth/`)
- **Storage Management** (`storage/`)
- **Message Bus** (`messaging/`)
- **Environment & Config** (`environment/`, `config/`)
- **State Persistence** (via ContextMCPServer)

**Advanced Services**:
- **ML Pipeline** (`ml/`)
- **MCP Integration** (`mcp/`)
- **Knowledge & Learning** (`knowledge/`, `learning/`)
- **Governance & Audit** (`governance/`)

**Cross-Cutting Services**:
- **Reliability** (`reliability/`)
- **Observability** (`observability/`)
- **Extensibility** (`extensibility/`)
- **Platform Services** (`platform/`)

**Location**: `src/AgentOperatingSystem/`

**Key Pattern**: Services provide clean APIs for agents

### 3. Kernel Layer
Core orchestration and agent lifecycle management.

**Components**:
- **Orchestration Engine** (`orchestration/`)
- **Agent Lifecycle Manager** (`agents/`)
- **State Machine Manager** (`reliability/state_machine.py`)

**Location**: `src/AgentOperatingSystem/orchestration/`, `src/AgentOperatingSystem/agents/`

**Key Pattern**: Event-driven, asynchronous operation

## Key Components Deep Dive

### Orchestration Engine
**Purpose**: Kernel that manages agent lifecycles and workflows.

**Responsibilities**:
- Agent registration and discovery
- Workflow state management
- Dependency resolution
- Resource scheduling
- Event routing

**Key Files**:
- `src/AgentOperatingSystem/orchestration/`
- `src/AgentOperatingSystem/agent_operating_system.py`

**Usage**:
```python
from AgentOperatingSystem import AgentOperatingSystem, AOSConfig

aos = AgentOperatingSystem(config)
await aos.initialize()

# Register agent
await aos.register_agent(agent)

# Process events
await aos.process_event(event)
```

### Agent Lifecycle Manager
**Purpose**: Process management for agents (like init system in Linux).

**Responsibilities**:
- Agent provisioning and initialization
- Health monitoring and auto-recovery
- Capability tracking
- State preservation via ContextMCPServer

**Key Files**:
- `src/AgentOperatingSystem/agents/base_agent.py`
- `src/AgentOperatingSystem/agents/perpetual_agent.py`
- `src/AgentOperatingSystem/agents/purpose_driven_agent.py`

**Agent States**:
1. Created
2. Initialized (ContextMCPServer created)
3. Running (event loop active)
4. Sleeping (idle, waiting for events)
5. Terminated (deregistered)

### Message Bus
**Purpose**: Inter-Process Communication (IPC) for agents.

**Responsibilities**:
- Topic-based routing
- Message delivery guarantees
- Conversation management
- Azure Service Bus integration

**Key Files**:
- `src/AgentOperatingSystem/messaging/`
- `src/AgentOperatingSystem/messaging/servicebus_manager.py`

**Patterns**:
```python
# Publish message
await message_bus.publish(topic="agent.events", message=data)

# Subscribe to topic
await message_bus.subscribe(topic="agent.events", handler=my_handler)

# Agent-to-agent communication
await send_agent_message(from_agent, to_agent, message)
```

### Storage Service
**Purpose**: Unified file system abstraction.

**Responsibilities**:
- Azure Blob Storage (objects)
- Azure Table Storage (structured data)
- Azure Queue Storage (message queues)
- Cosmos DB (documents)
- Backend-agnostic interface

**Key Files**:
- `src/AgentOperatingSystem/storage/`

**Usage**:
```python
from AgentOperatingSystem.storage import AzureBlobStorage

storage = AzureBlobStorage(connection_string)
await storage.upload("container", "blob", data)
data = await storage.download("container", "blob")
```

### MCP Integration
**Purpose**: Model Context Protocol for tool/resource access.

**Responsibilities**:
- MCP client/server implementation
- Tool discovery and execution
- Resource access management
- ContextMCPServer for state preservation

**Key Files**:
- `src/AgentOperatingSystem/mcp/`
- `src/AgentOperatingSystem/mcp/context_server.py`

**Pattern**:
```python
# ContextMCPServer for agent state
agent.context_server = ContextMCPServer(agent_id)
await agent.context_server.initialize()
await agent.context_server.save_state(state)
```

### ML Pipeline
**Purpose**: Machine learning infrastructure.

**Responsibilities**:
- Azure ML integration
- LoRA adapter management
- Model versioning and deployment
- Inference with caching
- DPO (Direct Preference Optimization) training

**Key Files**:
- `src/AgentOperatingSystem/ml/`
- `examples/dpo_training_example.py`

### Governance Service
**Purpose**: Enterprise compliance and audit.

**Responsibilities**:
- Tamper-evident audit logging
- Policy enforcement
- Risk registry
- Decision rationale tracking

**Key Files**:
- `src/AgentOperatingSystem/governance/`

### Observability Service
**Purpose**: System monitoring and tracing.

**Responsibilities**:
- Metrics collection (counters, gauges, histograms)
- Distributed tracing (OpenTelemetry)
- Structured logging
- Alert management

**Key Files**:
- `src/AgentOperatingSystem/observability/`
- `src/AgentOperatingSystem/monitoring/`

**Usage**:
```python
from AgentOperatingSystem.observability import metrics, tracing

# Metrics
metrics.increment("agent.events.processed")
metrics.histogram("agent.processing.duration", duration)

# Tracing
with tracing.span("process_event"):
    await process_event(event)
```

## Data Flow

### Event Processing Flow
```
1. Event arrives (HTTP, Service Bus, Timer)
   ↓
2. Azure Functions receives event
   ↓
3. AOS initialized/retrieved
   ↓
4. Event routed to appropriate agent(s)
   ↓
5. Agent(s) process event (async)
   ↓
6. State persisted (ContextMCPServer)
   ↓
7. Result returned/published
   ↓
8. Agent returns to sleep state
```

### Agent Initialization Flow
```
1. Agent created (PurposeDrivenAgent)
   ↓
2. await agent.initialize()
   ├─ ContextMCPServer created
   ├─ State loaded from storage
   └─ Resources allocated
   ↓
3. Agent registered with orchestrator
   ↓
4. Agent enters event loop (perpetual)
```

### Inter-Agent Communication Flow
```
Agent A → Message Bus → Agent B
   ↓           ↓           ↓
Save State  Route    Load State
(Context)  Message   (Context)
   ↓           ↓           ↓
Response ← Message ← Process
   ↓       Bus        ↓
Update              Update
State               State
```

## Design Patterns

### 1. Perpetual Process Pattern
Agents are long-running processes, not transient tasks.

```python
# Register once, runs forever
agent = PurposeDrivenAgent(...)
await agent.initialize()  # ContextMCPServer created
manager.register_agent(agent)
# Agent now perpetual, responds to events
```

### 2. Event-Driven Architecture
Agents wake on events, sleep when idle.

```python
async def handle_event(self, event):
    """Wake up, process, go back to sleep."""
    result = await self.process(event)
    await self.save_state()  # Persist via ContextMCPServer
    return result
```

### 3. State Machine Pattern
Deterministic state transitions.

```python
from AgentOperatingSystem.reliability import StateMachine

states = ["created", "initialized", "running", "sleeping"]
transitions = [
    ("created", "initialize", "initialized"),
    ("initialized", "start", "running"),
    ("running", "idle", "sleeping"),
]
sm = StateMachine(states, transitions)
```

### 4. Circuit Breaker Pattern
Fault tolerance and resilience.

```python
from AgentOperatingSystem.reliability import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60,
    expected_exception=ServiceError
)

async with breaker:
    result = await external_service.call()
```

### 5. Repository Pattern
Backend-agnostic storage access.

```python
# Same interface, different backends
storage = AzureBlobStorage(...)  # or
storage = AzureTableStorage(...)  # or
storage = CosmosDBStorage(...)

await storage.save(key, value)
```

## Component Interactions

### Agent → Storage
```python
agent = PurposeDrivenAgent(...)
await agent.initialize()  # ContextMCPServer created
await agent.save_state()  # State → ContextMCPServer → Azure Storage
```

### Agent → Message Bus → Agent
```python
# Agent A
await message_bus.publish("task.created", task_data)

# Agent B (subscribed to "task.created")
async def handle_task(message):
    await self.process_task(message)
```

### Application → AOS → Azure
```python
# Application layer
aos = AgentOperatingSystem(config)
await aos.initialize()

# AOS uses services
# Services use Azure SDK
# Azure SDK calls Azure cloud services
```

## Configuration Architecture

### Hierarchical Configuration
1. **Default Configuration**: Built-in defaults
2. **File Configuration**: `config/*.json`
3. **Environment Variables**: Override files
4. **Runtime Configuration**: Override all

**Example**:
```python
config = AOSConfig(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    servicebus_connection_string=os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING"),
    environment=os.getenv("APP_ENVIRONMENT", "production"),
)
```

### Configuration Files
- `config/consolidated_config.json` - Main configuration
- `config/example_app_registry.json` - App registry example
- `config/self_learning_config.json` - Self-learning configuration
- `local.settings.json` - Local development (not in git)

## Deployment Architecture

### Azure Functions Deployment
```
Internet → Azure Load Balancer
             ↓
         Azure Functions (AOS)
             ↓
    ┌────────┴────────┐
    ↓                 ↓
Service Bus      Storage Account
    ↓                 ↓
Agents ←────────→ State (ContextMCPServer)
```

### Production Components
- **Azure Functions**: Serverless compute for AOS
- **Azure Service Bus**: Message queuing and routing
- **Azure Storage**: Blob, Table, Queue for persistence
- **Azure Key Vault**: Secrets management
- **Application Insights**: Monitoring and telemetry
- **Cosmos DB**: Optional document storage

## File Organization

```
src/AgentOperatingSystem/
├── __init__.py                    # Package exports
├── agent_operating_system.py      # Main AOS class
├── agents/                        # Agent implementations
│   ├── base_agent.py
│   ├── perpetual_agent.py
│   └── purpose_driven_agent.py
├── orchestration/                 # Orchestration engine
├── messaging/                     # Message bus
├── storage/                       # Storage services
├── auth/                          # Authentication
├── mcp/                          # MCP integration
│   └── context_server.py         # ContextMCPServer
├── ml/                           # ML pipeline
├── governance/                   # Compliance
├── reliability/                  # Fault tolerance
├── observability/                # Monitoring
├── knowledge/                    # Knowledge base
├── learning/                     # Self-learning
└── ...
```

## Best Practices

1. **Understand the Paradigm**: AOS is an OS, not a framework
2. **Think Perpetual**: Agents run forever, not per-task
3. **Use ContextMCPServer**: All state should persist via ContextMCPServer
4. **Event-Driven Design**: Design for event-driven architecture
5. **Async All The Way**: Use async/await throughout
6. **Leverage Services**: Use existing services, don't reinvent
7. **Follow Patterns**: Use established patterns (circuit breaker, state machine)
8. **Monitor Everything**: Use observability services
9. **Secure by Design**: Use auth service, never hardcode secrets
10. **Test Thoroughly**: Test async, concurrent, and failure scenarios

## Common Architectural Decisions

### When to Create a New Service?
Create a new service when:
- Functionality is cross-cutting (used by multiple agents)
- Clear separation of concerns
- Reusable across applications
- Complex enough to warrant isolation

Add to existing service when:
- Closely related to existing functionality
- Small, focused feature
- No clear reason for separation

### When to Use Message Bus vs Direct Calls?
**Use Message Bus**:
- Async, fire-and-forget communication
- Multiple subscribers
- Decoupled components
- Event broadcasting

**Use Direct Calls**:
- Synchronous responses needed
- Single recipient
- Tightly coupled components
- Simple request-response

### When to Create a New Agent Type?
Create new agent type when:
- Distinct business purpose
- Different capabilities/tools
- Separate domain of responsibility
- Different lifecycle requirements

Extend existing agent when:
- Minor variation
- Same core purpose
- Shared capabilities

## Related Skills
- `perpetual-agents` - Working with agents
- `azure-functions` - Deployment architecture
- `async-python-testing` - Testing patterns
- `mcp-integration` - MCP and ContextMCPServer usage

## Additional Resources
- ARCHITECTURE.md - Detailed architecture documentation
- README.md - Core concepts overview
- CONTRIBUTING.md - Development guidelines
- docs/ - Additional technical documentation
- examples/ - Architecture examples in practice
