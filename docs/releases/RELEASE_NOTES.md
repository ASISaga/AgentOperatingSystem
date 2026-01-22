# Microsoft Agent Framework Release Notes

## Upgrade Details

**From Version:** 1.0.0b251001 (October 1, 2024)  
**To Version:** 1.0.0b251218 (December 18, 2024)

This document provides detailed release notes for the Microsoft agent-framework versions between our upgrade path, based on official GitHub releases.

---

## Version 1.0.0b251218 (December 18, 2024) - Current Version

**Published:** December 19, 2024  
**Official Tag:** python-1.0.0b251218

### Added Features

- **Azure AI Agent with Bing Grounding Citations** - New sample demonstrating Bing grounding citations integration ([#2892](https://github.com/microsoft/agent-framework/pull/2892))
- **Workflow Visualization** - Option to visualize internal executors in workflows ([#2917](https://github.com/microsoft/agent-framework/pull/2917))
- **Workflow Cancellation** - Sample demonstrating workflow cancellation patterns ([#2732](https://github.com/microsoft/agent-framework/pull/2732))
- **Azure Managed Redis Support** - Support with credential provider for enhanced caching ([#2887](https://github.com/microsoft/agent-framework/pull/2887))
- **Additional Azure AI Configuration** - More arguments for Azure AI agent configuration ([#2922](https://github.com/microsoft/agent-framework/pull/2922))

### Changed

- **Ollama Package Update** - Updated Ollama package version ([#2920](https://github.com/microsoft/agent-framework/pull/2920))
- **Ollama Samples Reorganization** - Moved Ollama samples to getting started directory ([#2921](https://github.com/microsoft/agent-framework/pull/2921))
- **Chat Clients Refactoring** - Cleanup and refactoring of chat clients ([#2937](https://github.com/microsoft/agent-framework/pull/2937))
- **ID Casing Alignment** - Aligned Run ID and Thread ID casing with AG-UI TypeScript SDK ([#2948](https://github.com/microsoft/agent-framework/pull/2948))

### Fixed

- **Pydantic Literal Types** - Fixed Pydantic error when using Literal types for tool parameters ([#2893](https://github.com/microsoft/agent-framework/pull/2893))
- **MCP Image Type Conversion** - Corrected MCP image type conversion in `_mcp.py` ([#2901](https://github.com/microsoft/agent-framework/pull/2901))
- **Response Format Pydantic Models** - Fixed BadRequestError when using Pydantic models in response formatting ([#1843](https://github.com/microsoft/agent-framework/pull/1843))
- **Sub-workflow Kwargs** - Propagate workflow kwargs to sub-workflows via WorkflowExecutor ([#2923](https://github.com/microsoft/agent-framework/pull/2923))
- **WorkflowAgent Event Handling** - Fixed WorkflowAgent event handling and kwargs forwarding ([#2946](https://github.com/microsoft/agent-framework/pull/2946))

### New Contributors

- @egeozanozyedek ([#2901](https://github.com/microsoft/agent-framework/pull/2901))
- @samueljohnsiby ([#1843](https://github.com/microsoft/agent-framework/pull/1843))

**Full Changelog:** [python-1.0.0b251216...python-1.0.0b251218](https://github.com/microsoft/agent-framework/compare/python-1.0.0b251216...python-1.0.0b251218)

---

## Version 1.0.0b251216 (December 16, 2024)

**Published:** December 17, 2024  
**Official Tag:** python-1.0.0b251216

### Added Features

- **Ollama Connector** - New Ollama connector for Agent Framework ([#1104](https://github.com/microsoft/agent-framework/pull/1104))
- **AI Function Custom Args** - Added custom args and thread object to `ai_function` kwargs ([#2769](https://github.com/microsoft/agent-framework/pull/2769))
- **WorkflowAgent Checkpointing** - Enable checkpointing for `WorkflowAgent` ([#2774](https://github.com/microsoft/agent-framework/pull/2774))

### Changed

- **⚠️ BREAKING: Observability Updates** - Major observability updates ([#2782](https://github.com/microsoft/agent-framework/pull/2782))
- **HandoffBuilder Descriptions** - Use agent description in `HandoffBuilder` auto-generated tools ([#2714](https://github.com/microsoft/agent-framework/pull/2714))
- **Magentic Ledger Management** - Improve Magentic ledger management and context access ([#2753](https://github.com/microsoft/agent-framework/pull/2753))

### Fixed

- **Sequential Builder Deduplication** - Fix dedupe logic in sequential builder ([#2780](https://github.com/microsoft/agent-framework/pull/2780))
- **Response Handler Type Hints** - Fixed response handler type hints ([#2755](https://github.com/microsoft/agent-framework/pull/2755))

---

## Version 1.0.0b251211 (December 11, 2024)

**Published:** December 11, 2024  
**Official Tag:** python-1.0.0b251211

### Added Features

- **HITL Support Extension** - Extend Human-in-the-Loop support for all orchestration patterns ([#2620](https://github.com/microsoft/agent-framework/pull/2620))
- **Concurrent Factory Pattern** - Add factory pattern to concurrent orchestration builder ([#2738](https://github.com/microsoft/agent-framework/pull/2738))
- **Sequential Factory Pattern** - Add factory pattern to sequential orchestration builder ([#2710](https://github.com/microsoft/agent-framework/pull/2710))
- **Azure AI File IDs Capture** - Capture file IDs from code interpreter in streaming responses ([#2741](https://github.com/microsoft/agent-framework/pull/2741))

### Changed

- **DurableAIAgent Return Type** - Changed DurableAIAgent return type ([#2746](https://github.com/microsoft/agent-framework/pull/2746))
- **Azure AI Client Improvements** - Improved Azure AI client handling ([#2721](https://github.com/microsoft/agent-framework/pull/2721))

---

## Version 1.0.0b251209 (December 9, 2024)

**Published:** December 9, 2024  
**Official Tag:** python-1.0.0b251209

### Added Features

- **Autonomous Handoff Flow** - Support an autonomous handoff flow ([#2497](https://github.com/microsoft/agent-framework/pull/2497))
- **WorkflowBuilder Registry** - New workflow builder registry ([#2486](https://github.com/microsoft/agent-framework/pull/2486))
- **A2A Timeout Configuration** - Add configurable timeout support to A2AAgent ([#2432](https://github.com/microsoft/agent-framework/pull/2432))
- **Azure OpenAI File Search Sample** - Added Azure OpenAI Responses File Search sample ([#2645](https://github.com/microsoft/agent-framework/pull/2645))
- **Fan In/Out Concurrency** - Update fan in fan out sample to show concurrency ([#2705](https://github.com/microsoft/agent-framework/pull/2705))

### Changed

- **⚠️ BREAKING: Azure AI Renaming** - Renamed specific Azure AI components ([details needed](https://github.com/microsoft/agent-framework/pull/XXXX))
- **Structured Output Improvements** - Various structured output improvements
- **Magentic State Management** - Enhanced Magentic state management

---

## Version 1.0.0b251001 (October 1, 2024) - Previous Version

**Published:** October 1, 2024  
**Official Tag:** python-1.0.0b251001

### Initial Release Features

This was the first official release of Agent Framework for Python, comprising:

#### Core Packages
- **agent-framework-core** - Main abstractions, types, and implementations for OpenAI and Azure OpenAI
- **agent-framework-azure-ai** - Integration with Azure AI Foundry Agents
- **agent-framework-copilotstudio** - Integration with Microsoft Copilot Studio agents
- **agent-framework-a2a** - Create A2A (Agent-to-Agent) agents
- **agent-framework-devui** - Browser-based UI to chat with agents and workflows with tracing visualization
- **agent-framework-mem0** - Mem0 integration for Context Provider (agent memory)
- **agent-framework-redis** - Redis integration for Context Provider and Chat Memory Store
- **agent-framework** - Complete "kitchen-sink" install with all packages

**Official Announcement:** [Introducing Microsoft Agent Framework](https://devblogs.microsoft.com/foundry/introducing-microsoft-agent-framework-the-open-source-engine-for-agentic)

---

## Summary of Changes Between Versions

### Major Additions (Since 1.0.0b251001)

1. **Ollama Integration** - Full connector support for Ollama models
2. **Enhanced Orchestration** 
   - Autonomous handoff flows
   - Factory patterns for Sequential and Concurrent builders
   - Extended HITL (Human-in-the-Loop) support across all patterns
3. **Workflow Enhancements**
   - Checkpointing for WorkflowAgent
   - Workflow cancellation support
   - Internal executor visualization
   - WorkflowBuilder registry
4. **Azure Integration Improvements**
   - Managed Redis support with credential provider
   - Bing grounding citations
   - Enhanced file handling in streaming responses
5. **Developer Experience**
   - Improved observability and tracing
   - Better error handling for Pydantic models
   - Enhanced MCP integration

### Breaking Changes (Since 1.0.0b251001)

1. **Observability API Changes** (v1.0.0b251216)
   - Major refactoring of observability components
   - May affect custom telemetry implementations

2. **Azure AI Component Renaming** (v1.0.0b251209)
   - Specific component names changed
   - Affects Azure AI Foundry integrations

3. **Telemetry to Logging Migration** (Our upgrade addresses this)
   - `setup_telemetry` replaced with `setup_logging`
   - OTLP endpoint configuration moved to OpenTelemetry SDK

4. **WorkflowBuilder API Changes** (Our upgrade addresses this)
   - `add_executor()` replaced with `register_agent()` / `register_executor()`

---

## Impact on AOS

### Direct Impacts (Already Addressed)
✅ Telemetry/Logging API migration completed  
✅ WorkflowBuilder API updates completed  
✅ Model type naming updates completed  
✅ All tests passing with new version  

### Potential Benefits for Future Development

1. **Ollama Support** - Can now integrate Ollama models if needed
2. **Enhanced Orchestration** - Access to improved handoff and factory patterns
3. **Checkpointing** - Can implement workflow state persistence
4. **Better Debugging** - Improved visualization and error handling
5. **Azure Enhancements** - Better Azure AI and Redis integration

### Recommended Next Steps

1. ✅ Complete current upgrade (this PR)
2. Consider leveraging new orchestration patterns in future features
3. Evaluate Ollama integration for local development/testing
4. Explore workflow checkpointing for long-running processes
5. Consider workflow visualization for debugging complex orchestrations

---

## References

- [Agent Framework GitHub Repository](https://github.com/microsoft/agent-framework)
- [Python Package Releases](https://github.com/microsoft/agent-framework/releases?q=python-)
- [Official Documentation](https://github.com/microsoft/agent-framework/tree/main/python)
- [Getting Started Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started)

---

**Last Updated:** December 22, 2024  
**Document Version:** 1.0  
**Prepared For:** AOS agent-framework upgrade PR
