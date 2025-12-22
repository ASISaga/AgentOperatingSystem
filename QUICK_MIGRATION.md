# Quick Migration Guide - Agent Framework v1.0.0b251218

**Quick reference for migrating from agent-framework 1.0.0b251001 to 1.0.0b251218**

---

## 📦 Update Package Version

```bash
pip install agent-framework==1.0.0b251218 --pre --upgrade
```

Or in `pyproject.toml` / `requirements.txt`:
```
agent-framework>=1.0.0b251218
```

---

## 🔄 Code Changes Required

### 1. Telemetry → Logging

**Before:**
```python
from agent_framework.telemetry import setup_telemetry

setup_telemetry(
    otlp_endpoint="http://localhost:4317",
    enable_sensitive_data=True
)
```

**After:**
```python
from agent_framework import setup_logging

setup_logging(
    level=logging.INFO,
    enable_sensitive_data=True
)
```

**Note:** For custom OTLP endpoints, configure via environment variables or OpenTelemetry SDK directly.

---

### 2. WorkflowBuilder Methods

**Before:**
```python
builder = WorkflowBuilder()

# Adding agents
node_id = builder.add_executor(agent)

# Adding executors  
node_id = builder.add_executor(executor)
```

**After:**
```python
builder = WorkflowBuilder()

# Adding agents - use register_agent()
node_id = builder.register_agent(agent)

# Adding executors - use register_executor()
node_id = builder.register_executor(executor)
```

---

### 3. Model Type Names

**Before:**
```python
from model_orchestration import ModelType

model = ModelType.SEMANTIC_KERNEL
```

**After:**
```python
from model_orchestration import ModelType

model = ModelType.AGENT_FRAMEWORK
```

---

### 4. ChatAgent Constructor (Reminder)

Always include `chat_client`:

```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

agent = ChatAgent(
    chat_client=OpenAIChatClient(),  # Required!
    instructions="You are a helpful assistant",
    name="MyAgent"
)
```

---

## 🔧 Custom OTLP Endpoint Configuration

If you need custom OTLP endpoints:

**Option 1: Environment Variables**
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
```

**Option 2: OpenTelemetry SDK**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configure OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True
)

# Set up tracer provider
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

# Then call setup_logging
from agent_framework import setup_logging
setup_logging(level=logging.INFO)
```

---

## ✅ Testing Checklist

After making changes:

- [ ] All imports updated
- [ ] WorkflowBuilder calls updated
- [ ] Model type references updated
- [ ] ChatAgent instantiations include chat_client
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Telemetry/logging is working
- [ ] Custom OTLP endpoints configured (if applicable)

---

## 🆕 New Features Available

Take advantage of new capabilities:

```python
from agent_framework import (
    SequentialBuilder,      # Sequential workflows
    ConcurrentBuilder,      # Parallel workflows
    GroupChatBuilder,       # Multi-agent chats
    MagenticBuilder,        # Advanced orchestration
    HandoffBuilder,         # Agent handoffs
    CheckpointStorage,      # State persistence
    MCPStdioTool,          # MCP integration
    HostedWebSearchTool,   # Web search
)
```

---

## 📚 Full Documentation

For detailed information:
- **BREAKING_CHANGES.md** - Complete breaking changes documentation
- **UPGRADE_SUMMARY.md** - Upgrade summary and metrics
- [Agent Framework Repo](https://github.com/microsoft/agent-framework)
- [Python Docs](https://github.com/microsoft/agent-framework/tree/main/python)

---

## 🐛 Common Issues

### Issue: "setup_telemetry not found"
**Solution:** Replace with `setup_logging` from `agent_framework`

### Issue: "add_executor not found"  
**Solution:** Use `register_agent()` or `register_executor()`

### Issue: "ChatAgent missing required argument"
**Solution:** Add `chat_client` as first parameter

### Issue: "Telemetry not working"
**Solution:** Configure OTLP via environment variables or SDK

---

## ⏱️ Estimated Migration Time

- Small project: **1-2 hours**
- Medium project: **2-4 hours**
- Large project: **4-8 hours**

---

**Need help?** See BREAKING_CHANGES.md or file an issue in the repository.
