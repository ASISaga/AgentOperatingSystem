# Migration & Upgrade Guide

## Agent Framework Upgrade

**Version:** 1.0.0b251001 → 1.0.0b251218  
**Date:** December 22, 2024

### Quick Update

```bash
pip install agent-framework==1.0.0b251218 --pre --upgrade
```

### Breaking Changes

#### 1. Telemetry → Logging

**Before:**
```python
from agent_framework.telemetry import setup_telemetry
setup_telemetry(otlp_endpoint="http://localhost:4317")
```

**After:**
```python
from agent_framework import setup_logging
setup_logging(level=logging.INFO)
```

#### 2. WorkflowBuilder Methods

**Before:**
```python
builder.add_executor(agent)
```

**After:**
```python
builder.register_agent(agent)
builder.register_executor(executor)
```

#### 3. Model Type Names

**Before:**
```python
model = ModelType.SEMANTIC_KERNEL
```

**After:**
```python
model = ModelType.AGENT_FRAMEWORK
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

### Testing Checklist

- [ ] All imports updated
- [ ] WorkflowBuilder calls updated
- [ ] Model type references updated
- [ ] ChatAgent instantiations include chat_client
- [ ] Tests pass

### New Features Available

```python
from agent_framework import (
    SequentialBuilder,
    ConcurrentBuilder,
    GroupChatBuilder,
    CheckpointStorage,
    MCPStdioTool,
)
```

## See Also

- [BREAKING_CHANGES.md](BREAKING_CHANGES.md) - Complete breaking changes log
- [RELEASE_NOTES.md](RELEASE_NOTES.md) - Official changelog
- [REFACTORING.md](REFACTORING.md) - AOS refactoring guide
