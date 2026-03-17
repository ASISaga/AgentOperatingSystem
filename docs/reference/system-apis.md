# System APIs Reference

## Core Base Classes

AOS provides foundational classes that business applications extend:

- **`LeadershipAgent`**: Base class for executive/leadership agents
- **`BaseAgent`**: Core agent with AOS integration
- **`BaseOrchestrator`**: Base orchestration patterns
- **`PurposeDrivenAgent`**: Purpose-focused agent implementation

## System Call Interface (Python API)

Business applications interact with AOS through clean, well-defined APIs:

### System Initialization

```python
# System Initialization (Booting AOS)
from AgentOperatingSystem import AgentOperatingSystem
aos = AgentOperatingSystem(config)
```

### Storage System Calls

```python
from AgentOperatingSystem.storage import UnifiedStorageManager
storage = UnifiedStorageManager()
storage.save(key="data", value=data, storage_type="blob")
data = storage.load(key="data", storage_type="blob")
```

### Environment System Calls

```python
from AgentOperatingSystem.environment import UnifiedEnvManager
env = UnifiedEnvManager()
secret = env.get_secret("API_KEY")
```

### Authentication System Calls

```python
from AgentOperatingSystem.auth import UnifiedAuthHandler
auth = UnifiedAuthHandler()
session = auth.authenticate(provider="azure_b2c", credentials=creds)
```

### ML Pipeline System Calls

```python
from AgentOperatingSystem.ml import MLPipelineManager
ml = MLPipelineManager()
await ml.train_adapter(agent_role="ceo", training_params=params)
result = await ml.infer(agent_id="ceo", prompt="Analyze Q2 results")
```

### Messaging System Calls

```python
from AgentOperatingSystem.messaging import MessageBus
bus = MessageBus()
bus.publish(topic="decisions", message=decision_msg)
bus.subscribe(topic="decisions", handler=decision_handler)
```

### MCP System Calls

```python
from AgentOperatingSystem.mcp import MCPServiceBusClient
mcp = MCPServiceBusClient()
tools = await mcp.list_tools("github")
result = await mcp.call_tool("github", "create_issue", params)
```

### Governance System Calls

```python
from AgentOperatingSystem.governance import AuditLogger
audit = AuditLogger()
audit.log_decision(decision_id, context, rationale)
```

### Observability System Calls

```python
from AgentOperatingSystem.observability import MetricsCollector, Tracer
metrics = MetricsCollector()
metrics.increment("agent.decisions.count", tags={"agent": "ceo"})

tracer = Tracer()
with tracer.span("process_decision") as span:
    span.set_attribute("decision_type", "strategic")
    # Process decision
```

## See Also

- [Services Overview](../overview/services.md) - Operating system services
- [Architecture](../architecture/ARCHITECTURE.md) - System architecture
- [Development Guide](../development.md) - Developer documentation
