# Migration & Upgrade Guide

## Agent Framework Upgrade to 1.0.0rc1

**Version:** 1.0.0b251218 → 1.0.0rc1  
**New package:** agent-framework-orchestrations 1.0.0b260219  
**Date:** February 2026

### Quick Update

```bash
pip install agent-framework==1.0.0rc1 --pre --upgrade
pip install agent-framework-orchestrations==1.0.0b260219 --pre
```

### Breaking Changes

#### 1. ChatAgent → Agent

**Before:**
```python
from agent_framework import ChatAgent

agent = ChatAgent(
    chat_client=my_client,
    instructions="You are a helpful agent.",
    name="MyAgent",
)
```

**After:**
```python
from agent_framework import Agent

agent = Agent(
    client=my_client,
    instructions="You are a helpful agent.",
    name="MyAgent",
)
```

#### 2. Telemetry / Logging → Observability Instrumentation

**Before (1.0.0b251218):**
```python
from agent_framework import setup_logging
setup_logging(level=logging.INFO, enable_sensitive_data=True)
```

**After (1.0.0rc1):**
```python
from agent_framework.observability import enable_instrumentation
enable_instrumentation(enable_sensitive_data=True)
```

#### 3. WorkflowBuilder API

The WorkflowBuilder API has changed significantly. `register_agent()` and `register_executor()` no longer exist. Instead, use `add_chain()` and `add_edge()` with the executor/agent instances directly. The `start_executor` parameter is now required in the constructor.

**Before (1.0.0b251218):**
```python
builder = WorkflowBuilder()
builder.register_agent(agent1)
builder.register_agent(agent2)
workflow = builder.build()
```

**After (1.0.0rc1):**
```python
builder = WorkflowBuilder(start_executor=agent1)
builder.add_chain([agent1, agent2])
workflow = builder.build()
```

#### 4. Executor.__init__ Parameter

**Before:**
```python
class MyExecutor(Executor):
    def __init__(self):
        super().__init__(name="my_executor")
```

**After:**
```python
class MyExecutor(Executor):
    def __init__(self):
        super().__init__(id="my_executor")
```

#### 5. New: agent-framework-orchestrations Package

Multi-agent orchestration patterns are now in a separate package:

```python
from agent_framework_orchestrations import (
    SequentialBuilder,
    ConcurrentBuilder,
    GroupChatBuilder,
    HandoffBuilder,
    MagenticBuilder,
    TerminationCondition,
)

# Sequential workflow
workflow = SequentialBuilder(participants=[agent1, agent2]).build()

# Group chat with orchestrator
workflow = GroupChatBuilder(
    participants=[agent1, agent2, agent3],
    orchestrator_agent=manager_agent,
    max_rounds=10,
).build()

# Concurrent execution
workflow = ConcurrentBuilder(participants=[agent1, agent2]).build()

# Handoff pattern
workflow = HandoffBuilder(participants=[agent1, agent2]).build()
```

### Custom OTLP Configuration

**Option 1: Environment Variables**
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
```

**Option 2: OpenTelemetry SDK**
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
# Configure provider...
```

### Migration Checklist

- [x] `ChatAgent` → `Agent` (all imports and instantiations)
- [x] `chat_client=` → `client=` (Agent constructor parameter)
- [x] `setup_logging()` → `enable_instrumentation()` (from `agent_framework.observability`)
- [x] `WorkflowBuilder()` → `WorkflowBuilder(start_executor=...)` (required parameter)
- [x] `register_agent()`/`register_executor()` → `add_chain()`/`add_edge()`
- [x] `Executor(name=...)` → `Executor(id=...)`
- [x] Add `agent-framework-orchestrations` dependency
- [x] Tests updated and passing
- [x] Backward compatibility code removed

### New Features Available in 1.0.0rc1

```python
from agent_framework import (
    Agent,                    # Renamed from ChatAgent
    WorkflowBuilder,          # Updated API
    Runner,                   # Workflow runner
    FunctionTool,             # Function-based tools
    MCPStdioTool,             # MCP stdio tool integration
    MCPStreamableHTTPTool,    # MCP HTTP tool integration
    MCPWebsocketTool,         # MCP websocket tool integration
    InMemoryCheckpointStorage,# In-memory checkpointing
    FileCheckpointStorage,    # File-based checkpointing
)

from agent_framework.observability import (
    enable_instrumentation,   # Replaces setup_logging
    ObservabilitySettings,    # Observability configuration
)

from agent_framework_orchestrations import (
    SequentialBuilder,        # Sequential multi-agent workflows
    ConcurrentBuilder,        # Parallel multi-agent workflows
    GroupChatBuilder,         # Group chat orchestration
    HandoffBuilder,           # Agent handoff patterns
    MagenticBuilder,          # Magentic-One orchestration
    TerminationCondition,     # Custom termination conditions
)
```

## Previous Migration: 1.0.0b251001 → 1.0.0b251218

See [BREAKING_CHANGES.md](../releases/BREAKING_CHANGES.md) for the complete history of breaking changes.

## See Also

- [BREAKING_CHANGES.md](../releases/BREAKING_CHANGES.md) - Complete breaking changes log
- [RELEASE_NOTES.md](../releases/RELEASE_NOTES.md) - Official changelog
- [REFACTORING.md](REFACTORING.md) - AOS refactoring guide
