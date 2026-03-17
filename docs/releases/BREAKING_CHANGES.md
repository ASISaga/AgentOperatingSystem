# Breaking Changes - Microsoft Agent Framework Upgrade

## Version Upgrade: 1.0.0b251218 → 1.0.0rc1 (AOS 3.0.0)

This document details the breaking changes introduced when upgrading to agent-framework 1.0.0rc1 and adding agent-framework-orchestrations 1.0.0b260219.

**Release Date:** February 2026  
**AOS Version:** 3.0.0  
**Backward Compatibility:** Not maintained — clean break

---

## Summary of Breaking Changes (1.0.0rc1)

### 1. ChatAgent Renamed to Agent

The `ChatAgent` class has been renamed to `Agent`. The constructor parameter `chat_client` has been renamed to `client`.

```python
# Before (1.0.0b251218)
from agent_framework import ChatAgent
agent = ChatAgent(chat_client=my_client, instructions="...", name="MyAgent")

# After (1.0.0rc1)
from agent_framework import Agent
agent = Agent(client=my_client, instructions="...", name="MyAgent")
```

### 2. setup_logging Replaced by enable_instrumentation

The `setup_logging()` function has been removed from the top-level module. Use `enable_instrumentation()` from `agent_framework.observability` instead.

```python
# Before (1.0.0b251218)
from agent_framework import setup_logging
setup_logging(level=logging.INFO, enable_sensitive_data=True)

# After (1.0.0rc1)
from agent_framework.observability import enable_instrumentation
enable_instrumentation(enable_sensitive_data=True)
```

### 3. WorkflowBuilder API Overhaul

The `WorkflowBuilder` API has changed significantly:
- `start_executor` is now a required constructor parameter
- `register_agent()` and `register_executor()` methods have been removed
- Use `add_chain()` and `add_edge()` to compose workflows

```python
# Before (1.0.0b251218)
builder = WorkflowBuilder()
builder.register_agent(agent1)
builder.register_agent(agent2)
workflow = builder.build()

# After (1.0.0rc1)
builder = WorkflowBuilder(start_executor=agent1)
builder.add_chain([agent1, agent2])
workflow = builder.build()
```

### 4. Executor Constructor Parameter

The `Executor` base class constructor parameter changed from `name` to `id`.

```python
# Before
class MyExecutor(Executor):
    def __init__(self):
        super().__init__(name="my_executor")

# After
class MyExecutor(Executor):
    def __init__(self):
        super().__init__(id="my_executor")
```

### 5. New Separate Orchestrations Package

Multi-agent orchestration builders have been moved to the new `agent-framework-orchestrations` package:

```python
from agent_framework_orchestrations import (
    SequentialBuilder,      # Sequential multi-agent workflows
    ConcurrentBuilder,      # Parallel multi-agent workflows
    GroupChatBuilder,       # Group chat with orchestrator agent
    HandoffBuilder,         # Agent handoff patterns
    MagenticBuilder,        # Magentic-One orchestration
)
```

---

## AOS Files Changed for 1.0.0rc1

| File | Changes |
|------|---------|
| `pyproject.toml` | Added agent-framework>=1.0.0rc1, agent-framework-orchestrations>=1.0.0b260219 |
| `azure_functions/RealmOfAgents/requirements.txt` | Updated agent-framework version |
| `src/.../orchestration/agent_framework_system.py` | ChatAgent→Agent, setup_logging→enable_instrumentation, SequentialBuilder |
| `src/.../orchestration/model_orchestration.py` | ChatAgent→Agent, client parameter |
| `src/.../orchestration/workflow_orchestrator.py` | New WorkflowBuilder API, SequentialBuilder |
| `src/.../orchestration/multi_agent.py` | ChatAgent→Agent |
| `src/.../executor/base_executor.py` | Executor(name=) → Executor(id=) |
| `tests/test_agent_framework_components.py` | Updated all mocks and assertions |

---

## Previous: Version Upgrade 1.0.0b251001 → 1.0.0b251218

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

## 5. Upstream Breaking Changes (May Affect Advanced Use Cases)

These breaking changes were introduced in intermediate releases and may affect applications with custom implementations:

### 5.1. Observability Updates (v1.0.0b251216)

**What Changed:**  
Major refactoring of observability components in agent-framework-core.

**Potential Impact:**
- Custom telemetry implementations may need updates
- Tracing and monitoring integrations may require adjustments
- Observability middleware may need modifications

**Who This Affects:**
- Applications with custom observability solutions
- Applications directly using observability APIs
- Custom monitoring/tracing implementations

**Action Required:**
- Review your custom observability code if you have any
- Test telemetry and tracing after upgrade
- Consult [agent-framework PR #2782](https://github.com/microsoft/agent-framework/pull/2782) for details

### 5.2. Azure AI Component Renaming (v1.0.0b251209)

**What Changed:**  
Specific Azure AI Foundry components were renamed.

**Potential Impact:**
- Direct imports of Azure AI components may break
- Azure AI Foundry integrations may need updates

**Who This Affects:**
- Applications using Azure AI Foundry Agents directly
- Code importing specific Azure AI components

**Action Required:**
- Check for any direct Azure AI component imports
- Update component names as needed
- Refer to v1.0.0b251209 release notes for specific renamings

**Note:** AOS does not directly use these components in the current implementation, so this is primarily a concern for applications building on AOS.

---

## 6. New Features Available (Non-Breaking)

While not breaking changes, the new version includes several enhancements worth noting:

### New Orchestration Patterns
- **Autonomous Handoff Flow** - Support for automatic agent-to-agent handoffs
- **Factory Patterns** - Sequential and Concurrent builders with factory support
- **Extended HITL** - Human-in-the-loop support across all orchestration patterns

### Enhanced Integrations
- **Ollama Connector** - Full support for Ollama models (new in v1.0.0b251216)
- **Azure Managed Redis** - Support with credential provider
- **Bing Grounding Citations** - Integration for grounded responses

### Developer Experience Improvements
- **Workflow Visualization** - Visualize internal executors
- **Workflow Cancellation** - Proper cancellation support
- **Checkpointing** - State persistence for WorkflowAgent
- **Better Error Handling** - Fixed Pydantic model issues

See [RELEASE_NOTES.md](./RELEASE_NOTES.md) for complete details on all new features.

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

### Release Timeline

- **1.0.0b251218** (December 18, 2024) - Current Version
  - Breaking: Telemetry/logging API changes (addressed in this upgrade)
  - Breaking: WorkflowBuilder API changes (addressed in this upgrade)
  - Added: Azure Managed Redis, Bing citations, workflow visualization
  - Fixed: Pydantic errors, MCP image conversion, workflow event handling
  
- **1.0.0b251216** (December 16, 2024)
  - Breaking: Major observability updates ([#2782](https://github.com/microsoft/agent-framework/pull/2782))
  - Added: Ollama connector, WorkflowAgent checkpointing
  - Added: Custom args for ai_function
  
- **1.0.0b251211** (December 11, 2024)
  - Added: Extended HITL support, factory patterns for orchestration builders
  - Changed: DurableAIAgent return type
  
- **1.0.0b251209** (December 9, 2024)
  - Breaking: Azure AI component renaming
  - Added: Autonomous handoff flow, WorkflowBuilder registry, A2A timeout config
  
- **1.0.0b251001** (October 1, 2024) - Previous Version
  - Initial release of Agent Framework for Python
  - Core packages: core, azure-ai, copilotstudio, a2a, devui, mem0, redis

For complete changelog details, see [RELEASE_NOTES.md](./RELEASE_NOTES.md)

---

## Final Notes

This upgrade brings significant improvements to the Agent Framework, including better orchestration patterns, enhanced tooling support, and improved developer experience. While there are breaking changes, they are well-documented and the migration path is straightforward.

**Recommendation**: Test thoroughly in a development environment before deploying to production.

**Timeline**: Plan for 2-4 hours of development time for a typical application to complete the migration, plus additional time for testing.
