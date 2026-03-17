# Design: Merge Parent Directories into Submodules

## Architecture Overview

```
BEFORE:                                  AFTER:
agent-operating-system/                  agent-operating-system/
├── src/AgentOperatingSystem/  ───┐      ├── aos-kernel/src/AgentOperatingSystem/
│   ├── agents/                   │      │   ├── agents/ (merged)
│   ├── messaging/                │      │   ├── messaging/ (merged)
│   ├── orchestration/            ├──►   │   ├── orchestration/ (merged)
│   ├── knowledge/                │      │   └── ... (all kernel modules)
│   ├── learning/                 │      ├── aos-intelligence/src/aos_intelligence/
│   └── ml/                       │      │   ├── knowledge/ (already)
├── deployment/               ────┤      │   ├── learning/ (already)
├── config/                   ────┤      │   └── ml/ (merged)
├── data/                     ────┤      ├── aos-infrastructure/deployment/ (merged)
├── docs/                     ────┤      ├── aos-client-sdk/config/ (merged)
└── tests/                    ────┘      └── (parent dirs REMOVED)
```

## File Mapping

### 1. src/ → aos-kernel (kernel modules)

Parent files NOT in kernel (parent-only files to copy):

| Module | Files to Copy |
|--------|--------------|
| agents/ | cmo_agent.py, leadership_agent.py, purpose_driven.py |
| apps/ | app_config_schema.py |
| auth/ | manager.py |
| config/ | aos.py, auth.py, decision.py, learning.py, messagebus.py, ml.py, monitoring.py, orchestration.py, storage.py |
| environment/ | manager.py |
| executor/ | base_executor.py |
| extensibility/ | enhanced_agent_registry.py, plugin_framework.py, schema_registry.py |
| governance/ | audit.py, compliance.py, decision_rationale.py, risk.py |
| mcp/ | client_manager.py, client.py, context_server.py |
| messaging/ | bus.py, contracts.py, conversation_system.py, envelope.py, network_protocol.py, priority.py, reliability.py, router.py, routing.py, saga.py, servicebus_handlers.py, servicebus_manager.py, streaming.py, types.py |
| monitoring/ | audit_trail_generic.py, audit_trail.py, monitor.py, observability.py |
| observability/ | alerting.py, dashboard.py, logging.py, metrics.py, predictive.py, structured.py, tracing.py |
| orchestration/ | agent_framework_system.py, agent_manager.py, agent_registry.py, decision.py, dynamic.py, engine.py, events.py, mcp_integration.py, member.py, model_orchestration.py, multi_agent_coordinator.py, multi_agent.py, optimization.py, orchestration.py, orchestrator.py, role.py, scheduler.py, state.py, unified_orchestrator.py, workflow_orchestrator.py, workflow_step.py, workflow.py |
| platform/ | contracts.py, events.py |
| reliability/ | backpressure.py, chaos.py, circuit_breaker.py, idempotency.py, patterns.py, retry.py, state_machine_advanced.py, state_machine.py |
| services/ | service_interfaces.py |
| storage/ | azure_backend.py, backend.py, file_backend.py, manager.py |
| testing/ | audit_tests.py, chaos_tests.py, contract_tests.py, integration_tests.py |

Also copy: `__init__.py`, `agent_operating_system.py` (top-level)

MCP protocol subdirectory: `mcp/protocol/__init__.py`, `mcp/protocol/request.py`, `mcp/protocol/response.py`

### 2. src/ → aos-intelligence (intelligence modules)

knowledge/, learning/ are IDENTICAL between parent and intelligence — no copy needed.
ml/ — intelligence has 3 EXTRA files (lora_adapter_registry.py, lora_inference_client.py, lora_orchestration_router.py) that parent doesn't. Parent files already in intelligence. No copy needed.

### 3. deployment/ → aos-infrastructure

Infrastructure already has 59 files vs parent's 52. Copy any unique parent-only files.

### 4. config/ distribution
- `consolidated_config.json` → `aos-kernel/config/`
- `self_learning_config.json` → `aos-intelligence/config/`
- `example_app_registry.json` → `aos-client-sdk/config/`

### 5. data/ → aos-intelligence/data/
All 7 JSON files → `aos-intelligence/data/`

### 6. docs/ distribution

| Doc File/Dir | Target Submodule | Rationale |
|-------------|-----------------|-----------|
| architecture/ | aos-kernel/docs/ | System architecture |
| overview/ | aos-kernel/docs/ | System vision/principles |
| getting-started/ | aos-kernel/docs/ | Installation/quickstart |
| features/ | aos-kernel/docs/ | Feature overview |
| reference/ | aos-kernel/docs/ | System API reference |
| development/ | aos-kernel/docs/ | Contributing/dev guides |
| releases/ | aos-kernel/docs/ | Changelog/release notes |
| specifications/ | aos-kernel/docs/ | System specifications |
| agent-repositories/ | aos-kernel/docs/ | Repository structures |
| specs-sync/ | aos-kernel/docs/ | Spec sync plans |
| a2a_communication.md | aos-kernel/docs/ | Agent-to-agent comms |
| AOS_ENHANCEMENT_REQUESTS.md | aos-kernel/docs/ | Enhancement tracking |
| AOS_FURTHER_ENHANCEMENTS.md | aos-kernel/docs/ | Enhancement tracking |
| APP_CONFIGURATION.md | aos-client-sdk/docs/ | App configuration |
| CODE_ORGANIZATION.md | aos-kernel/docs/ | Code organization |
| configuration.md | aos-kernel/docs/ | System configuration |
| development.md | aos-kernel/docs/ | Development guide |
| DPO_README.md | aos-intelligence/docs/ | DPO training |
| ENHANCED_ORCHESTRATION_INTEGRATION.md | aos-kernel/docs/ | Orchestration |
| extensibility.md | aos-kernel/docs/ | Plugin framework |
| FOUNDRY_AGENT_SERVICE.md | aos-intelligence/docs/ | Foundry integration |
| Implementation.md | aos-kernel/docs/ | Implementation guide |
| INTEGRATION_COMPLETE.md | aos-kernel/docs/ | Integration status |
| llm_architecture.md | aos-intelligence/docs/ | LLM architecture |
| LORAX.md | aos-intelligence/docs/ | LoRA serving |
| README.md | aos-kernel/docs/ | Overview |
| RealmOfAgents.md | aos-kernel/docs/ | Realm of agents |
| REPOSITORY_SPLIT_PLAN.md | aos-kernel/docs/ | Repo split plan |
| rest_api.md | aos-dispatcher/docs/ | REST API docs |
| self_learning.md | aos-intelligence/docs/ | Self-learning |
| testing_infrastructure.md | aos-kernel/docs/ | Testing infra |
| testing.md | aos-kernel/docs/ | Testing guide |

### 7. tests/ distribution

| Test File | Target | Rationale |
|-----------|--------|-----------|
| conftest.py | aos-kernel/tests/ | Shared fixtures (kernel-centric) |
| simple_test.py | aos-kernel/tests/ | Basic tests |
| test_abstract_purpose_driven.py | aos-kernel/tests/ | Agent tests |
| test_advanced_features.py | aos-kernel/tests/ | Feature tests |
| test_agent_framework_components.py | aos-kernel/tests/ | Agent framework |
| test_agent_personas.py | aos-kernel/tests/ | Agent personas |
| test_azure_functions_infrastructure.py | aos-dispatcher/tests/ | Azure Functions |
| test_extensibility.py | aos-kernel/tests/ | Extensibility |
| test_foundry_agent_service.py | aos-intelligence/tests/ | Foundry ML |
| test_integration.py | aos-kernel/tests/ | Integration |
| test_lorax.py | aos-intelligence/tests/ | LoRA tests |
| test_new_features.py | aos-kernel/tests/ | Feature tests |
| test_perpetual_agents.py | aos-kernel/tests/ | Agent tests |
| test_persona_registry.py | aos-kernel/tests/ | Registry tests |
| test_purpose_driven_integration.py | aos-kernel/tests/ | Agent integration |
| test_testing_framework.py | aos-kernel/tests/ | Test framework |
| test_testing_standalone.py | aos-kernel/tests/ | Standalone tests |
| validate_cmo_agent.py | aos-kernel/tests/ | CMO agent validation |
| validate_foundry_integration.py | aos-intelligence/tests/ | Foundry validation |
| validate_implementation.py | aos-kernel/tests/ | Implementation validation |

## Error Handling

- Files already existing in target: SKIP (preserve submodule version)
- Empty parent directories after move: DELETE
- `__pycache__/` directories: SKIP (not tracked in git)
- `.egg-info/` directory: SKIP
