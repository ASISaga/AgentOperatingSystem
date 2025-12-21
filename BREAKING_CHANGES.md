# Breaking Changes - Microsoft Agent Framework Upgrade

## Version Upgrade: 1.0.0b251001 → 1.0.0b251218

This document details the breaking changes introduced when upgrading to the latest version of Microsoft's `agent-framework` package.

---

## Summary of Breaking Changes

The upgrade from `agent-framework>=1.0.0b251001` to `agent-framework>=1.0.0b251218` introduces several breaking changes that affect the AOS codebase and any applications built on top of it (e.g., BusinessInfinity).

### Critical Breaking Changes

1. **Telemetry/Logging API Changes**
2. **WorkflowBuilder API Changes**
3. **ChatAgent Constructor Requirements**
4. **Model Type Naming Updates**

---

## 1. Telemetry/Logging API Changes

### What Changed
The `setup_telemetry` function has been replaced with `setup_logging`.

### Migration Required

**Before (Old Code):**
```python
from agent_framework.telemetry import setup_telemetry

setup_telemetry(
    otlp_endpoint="http://localhost:4317",
    enable_sensitive_data=True
)
```

**After (New Code):**
```python
from agent_framework import setup_logging

setup_logging(
    level=logging.INFO,
    enable_sensitive_data=True
)
```

### Impact
- **Files Affected in AOS:**
  - `src/AgentOperatingSystem/agents/agent_framework_system.py`
- **Applications Impact:**
  - Any application code that uses `setup_telemetry` must be updated
  - **IMPORTANT**: The OTLP endpoint is no longer directly configurable via this function
  - Telemetry configuration is now managed through environment variables and OpenTelemetry SDK
  - Custom OTLP endpoints require alternative configuration

### Action Required for Downstream Applications
1. Replace all imports of `agent_framework.telemetry.setup_telemetry` with `agent_framework.setup_logging`
2. Update function calls to use the new signature
3. **Configure OpenTelemetry through environment variables or the OpenTelemetry SDK directly**

#### Alternative OTLP Configuration
If you need to configure a custom OTLP endpoint (previously done via `setup_telemetry(otlp_endpoint=...)`), use the OpenTelemetry SDK directly:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configure OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",  # Your custom OTLP endpoint
    insecure=True  # Use False in production with proper TLS
)

# Set up tracer provider
trace_provider = TracerProvider()
trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(trace_provider)

# Now call agent-framework setup_logging
from agent_framework import setup_logging
setup_logging(level=logging.INFO, enable_sensitive_data=True)
```

Or use environment variables:
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
```

---

## 2. WorkflowBuilder API Changes

### What Changed
The `add_executor()` method has been removed and replaced with `register_executor()` and `register_agent()`.

### Migration Required

**Before (Old Code):**
```python
from agent_framework import WorkflowBuilder, ChatAgent

builder = WorkflowBuilder()

# Adding an agent
agent = ChatAgent(...)
node_id = builder.add_executor(agent)

# Adding a custom executor
custom_executor = MyExecutor()
node_id = builder.add_executor(custom_executor)
```

**After (New Code):**
```python
from agent_framework import WorkflowBuilder, ChatAgent

builder = WorkflowBuilder()

# Adding an agent - use register_agent()
agent = ChatAgent(...)
node_id = builder.register_agent(agent)

# Adding a custom executor - use register_executor()
custom_executor = MyExecutor()
node_id = builder.register_executor(custom_executor)
```

### New Methods Available
The latest version also adds several new convenience methods:
- `add_agent()` - Alternative to `register_agent()` for adding agents
- `add_chain()` - Add a chain of executors sequentially
- `add_fan_in_edges()` - Connect multiple sources to one target
- `add_fan_out_edges()` - Connect one source to multiple targets
- `add_multi_selection_edge_group()` - Advanced edge grouping
- `add_switch_case_edge_group()` - Conditional routing
- `with_checkpointing()` - Enable workflow checkpointing

### Impact
- **Files Affected in AOS:**
  - `src/AgentOperatingSystem/orchestration/workflow_orchestrator.py`
- **Applications Impact:**
  - Any code using `WorkflowBuilder.add_executor()` will fail with `AttributeError`
  - Workflow construction code needs to be updated

### Action Required for Downstream Applications
1. Replace all calls to `builder.add_executor(agent)` with `builder.register_agent(agent)` for ChatAgent instances
2. Replace all calls to `builder.add_executor(executor)` with `builder.register_executor(executor)` for custom executors
3. Consider using the new convenience methods for simpler workflow patterns

---

## 3. ChatAgent Constructor Requirements

### What Changed
The `ChatAgent` constructor now requires `chat_client` as the first positional argument.

### Migration Required

**Before (Old Code):**
```python
from agent_framework import ChatAgent

# This may have worked in some scenarios
agent = ChatAgent(
    instructions="You are a helpful assistant",
    name="MyAgent"
)
```

**After (New Code):**
```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

# chat_client is now required
agent = ChatAgent(
    chat_client=OpenAIChatClient(),
    instructions="You are a helpful assistant",
    name="MyAgent"
)
```

### Impact
- **Files Affected in AOS:**
  - `src/AgentOperatingSystem/agents/agent_framework_system.py` (already uses mock client for testing)
- **Applications Impact:**
  - Any ChatAgent creation without explicit `chat_client` will fail
  - Need to import and instantiate appropriate chat client

### Supported Chat Clients
- `OpenAIChatClient` - For OpenAI API
- `AzureOpenAIChatClient` - For Azure OpenAI Service
- `AzureAIChatClient` - For Azure AI Foundry
- Custom implementations of `ChatClientProtocol`

### Action Required for Downstream Applications
1. Ensure all `ChatAgent` instantiations include a `chat_client` parameter
2. Import and configure the appropriate chat client for your use case
3. Set required environment variables (API keys, endpoints, etc.)

---

## 4. Model Type Naming Updates

### What Changed
References to "Semantic Kernel" have been updated to "Agent Framework" to reflect the evolution of the framework.

### Migration Required

**Before (Old Code):**
```python
from model_orchestration import ModelType

model_type = ModelType.SEMANTIC_KERNEL
```

**After (New Code):**
```python
from model_orchestration import ModelType

model_type = ModelType.AGENT_FRAMEWORK
```

### Impact
- **Files Affected in AOS:**
  - `src/AgentOperatingSystem/orchestration/model_orchestration.py`
- **Applications Impact:**
  - Any code referencing `ModelType.SEMANTIC_KERNEL` will need updates
  - Configuration files using "semantic_kernel" as a model type identifier

### Action Required for Downstream Applications
1. Update all references to `ModelType.SEMANTIC_KERNEL` to `ModelType.AGENT_FRAMEWORK`
2. Update configuration files that specify model types
3. Update any logging or monitoring code that references "semantic_kernel"

---

## 5. Additional API Enhancements (Non-Breaking)

While not breaking changes, the new version includes several enhancements:

### New Features
- **Improved orchestration patterns**: Sequential, GroupChat, Concurrent, Magentic, Handoff
- **Checkpointing support**: Save and restore workflow state
- **Enhanced middleware system**: More flexible agent/chat/function middleware
- **Better tool integration**: Improved function calling and tool support
- **MCP (Model Context Protocol) integration**: Built-in MCP server/tool support

### New Imports Available
```python
from agent_framework import (
    # Orchestration builders
    SequentialBuilder,
    ConcurrentBuilder,
    GroupChatBuilder,
    MagenticBuilder,
    HandoffBuilder,
    
    # Checkpointing
    CheckpointStorage,
    FileCheckpointStorage,
    InMemoryCheckpointStorage,
    
    # New tools
    MCPStdioTool,
    MCPWebsocketTool,
    HostedMCPTool,
    HostedWebSearchTool,
    HostedFileSearchTool,
    HostedCodeInterpreterTool,
    
    # And many more...
)
```

---

## Migration Checklist for Applications Using AOS

### For Application Developers (BusinessInfinity, etc.)

- [ ] **Update dependencies**
  - Update `agent-framework` to `>=1.0.0b251218` in your requirements/pyproject.toml
  - Run `pip install --upgrade agent-framework --pre`

- [ ] **Update telemetry/logging code**
  - Replace `setup_telemetry` imports with `setup_logging`
  - Update function calls to use new signature
  - Configure OpenTelemetry via environment variables if needed

- [ ] **Update WorkflowBuilder usage**
  - Replace `add_executor()` with `register_agent()` or `register_executor()`
  - Consider using new convenience methods for simpler patterns

- [ ] **Update ChatAgent instantiation**
  - Ensure all `ChatAgent` creations include `chat_client` parameter
  - Import and configure appropriate chat client
  - Set required environment variables

- [ ] **Update model type references**
  - Replace `ModelType.SEMANTIC_KERNEL` with `ModelType.AGENT_FRAMEWORK`
  - Update configuration files

- [ ] **Test your application**
  - Run unit tests
  - Run integration tests
  - Verify workflow orchestration works correctly
  - Check telemetry/logging output

- [ ] **Update documentation**
  - Update README and developer guides
  - Update API documentation
  - Update deployment guides with new environment variables

---

## Environment Variables

### New/Changed Environment Variables

For OpenAI:
```bash
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL_ID=gpt-4
```

For Azure OpenAI:
```bash
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=...
AZURE_OPENAI_API_VERSION=2024-10-21
```

For Azure AI Foundry:
```bash
AZURE_AI_PROJECT_ENDPOINT=...
AZURE_AI_MODEL_DEPLOYMENT_NAME=...
```

---

## Compatibility Notes

### Python Version Requirements
- **Minimum Python version**: 3.10+ (unchanged)
- Agent Framework now explicitly requires Python 3.10 or higher

### Platform Support
- Windows, macOS, Linux (unchanged)

### Dependencies
The new version includes several new dependencies:
- `openai-agents`
- `openai-chatkit`
- `mcp` (Model Context Protocol)
- Various Azure SDKs for enhanced integration

---

## Getting Help

### Resources
- [Agent Framework Repository](https://github.com/microsoft/agent-framework)
- [Python Package Documentation](https://github.com/microsoft/agent-framework/tree/main/python)
- [Release Notes](https://github.com/microsoft/agent-framework/releases?q=tag%3Apython-1&expanded=true)
- [Getting Started Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started)

### Support
For issues specific to AOS:
- File an issue in the AgentOperatingSystem repository
- Contact the AOS maintainers

For issues with agent-framework itself:
- File an issue in the [microsoft/agent-framework](https://github.com/microsoft/agent-framework/issues) repository

---

## Version History

- **1.0.0b251218** (Latest) - December 2024
  - Breaking changes to telemetry/logging API
  - Breaking changes to WorkflowBuilder API
  - Enhanced orchestration patterns
  - MCP integration
  
- **1.0.0b251001** (Previous) - October 2024
  - Initial integration in AOS

---

## Final Notes

This upgrade brings significant improvements to the Agent Framework, including better orchestration patterns, enhanced tooling support, and improved developer experience. While there are breaking changes, they are well-documented and the migration path is straightforward.

**Recommendation**: Test thoroughly in a development environment before deploying to production.

**Timeline**: Plan for 2-4 hours of development time for a typical application to complete the migration, plus additional time for testing.
