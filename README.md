# AgentOperatingSystem (AOS)
The AgentOperatingSystem (AOS) is the single source of truth for all core agent orchestration, resource management, agent lifecycle, inter-agent communication, storage, environment, ML pipeline, Model Context Protocol (MCP), and authentication features. All business and leadership agents (e.g., CEO, CFO, CMO, etc.) inherit from the generic `LeadershipAgent` defined in AOS. All applications (including BusinessInfinity) must import these features from AOS.

---

## Key Concepts
- **Unified Core Features:** All agent orchestration, storage, environment, ML pipeline, MCP, and authentication logic are implemented and maintained in AOS. No application-specific or local implementations exist outside AOS.
- **LeadershipAgent Base Class:** All business and leadership agents inherit from `LeadershipAgent` in AOS, ensuring a consistent interface and orchestration pattern.
- **Modular Agent Repositories:** Each C-Suite and leadership agent is implemented in its own repository under `RealmOfAgents/` (see below).
- **Separation of Concerns:** AOS provides all generic OS-like and infrastructure functionality. Applications (e.g., BusinessInfinity) only contain business-specific logic and orchestrate agents via AOS.

---

## Modular Agent Repository Structure (2025)

All C-Suite and leadership agents are implemented in their own dedicated repositories under `RealmOfAgents/`:

- CEO: `RealmOfAgents/CEO/ChiefExecutiveOfficer.py`
- CFO: `RealmOfAgents/CFO/ChiefFinancialOfficer.py`
- CMO: `RealmOfAgents/CMO/ChiefMarketingOfficer.py`
- COO: `RealmOfAgents/COO/ChiefOperatingOfficer.py`
- CTO: `RealmOfAgents/CTO/ChiefTechnologyOfficer.py`
- CHRO: `RealmOfAgents/CHRO/ChiefHumanResourcesOfficer.py`
- Founder: `RealmOfAgents/Founder/FounderAgent.py`
- Investor: `RealmOfAgents/Investor/InvestorAgent.py`

Each agent inherits from `LeadershipAgent` and implements domain-specific logic. This modular structure enables clean separation, easy extension, and reuse across multiple business domains.

---

## Unified Core Feature Imports

All applications must import core features from AOS. Example usage:
```python
from RealmOfAgents.AgentOperatingSystem.storage.manager import UnifiedStorageManager
from RealmOfAgents.AgentOperatingSystem.environment import UnifiedEnvManager
from RealmOfAgents.AgentOperatingSystem.ml_pipeline_ops import MLPipelineManager
from RealmOfAgents.AgentOperatingSystem.mcp_servicebus_client import MCPServiceBusClient
from RealmOfAgents.AgentOperatingSystem.aos_auth import UnifiedAuthHandler
```

See the docstrings and Implementation.md for full API details.

---

## Architecture Note: Unified, Domain-Agnostic Design

AOS is designed as a reusable, domain-agnostic orchestration and agent management layer. All core infrastructure is implemented here. Applications built on top of AOS (such as BusinessInfinity) only contain business logic, user interface, and orchestration of agents via AOS.

**Separation of Concerns:**
- AOS: All agent orchestration, resource management, storage, environment, ML pipeline, MCP, and authentication logic
- Application (e.g., BusinessInfinity): Business logic, user interface, and orchestration of agents via AOS

**Note:** All legacy code and local implementations of these features in applications have been removed. Update your imports and integrations accordingly.

---

## Migration Guidance

If migrating from a previous version, remove all local implementations of storage, environment, ML pipeline, MCP, and authentication logic from your application. Import and use the unified managers and handlers from AOS as shown above.

---

## Prerequisites
- Fine-tuned, domain-specific models exposed as API endpoints (see FineTunedLLM repo for details)
- Azure OpenAI Service subscription and access credentials
- Access to Copilot Studio

-----------------------------------------------------------
Configure Copilot Studio for Perpetually Running Agent Orchestration
Perpetually running agents configured in Copilot Studio that orchestrate queries to the appropriate endpoints
-----------------------------------------------------------

## Access and Setup in Copilot Studio
- Log in to Copilot Studio with your organizational credentials.
- Create a new project dedicated to multi-agent orchestration, naming it according to your domain or business function.
- Configure the project for “always-on” operation, ensuring agents remain active and responsive at all times.
- Set up project-level environment variables and secrets for secure integration with Azure OpenAI endpoints.

## Design Persistent Agent Workflows
- For each domain-specific task (e.g., answering FAQs, processing orders), design a custom agent using Copilot Studio’s visual workflow editor.
- Implement a continuous event loop within each agent so it can listen for and respond to incoming events or queries indefinitely.
- Enable persistent session support to maintain conversational context across multiple interactions.
- Integrate heartbeat or keep-alive mechanisms to monitor agent health and automatically recover from transient failures.

## Integrate with Azure OpenAI Endpoints
- For each agent, input the connection details (API endpoint, authentication keys) of the corresponding fine-tuned model.
- Define routing logic so the agent can:
  - Continuously poll for new events or remain responsive to triggers (e.g., webhooks, message queues).
  - Analyze the context of each query and select the appropriate Azure OpenAI endpoint for processing.
  - Format and store responses, maintaining state for multi-turn or context-rich interactions as needed.

## Enhance Resilience and Error Handling
- Implement robust error-handling routines to gracefully manage API failures, timeouts, or invalid responses.
- Set up logging within each agent to capture errors, operational metrics, and health signals for monitoring and troubleshooting.
- Integrate auto-recovery steps, such as self-reset or process restarts, to ensure agents can recover from unexpected issues.
- Optionally, connect agents to Azure messaging services (e.g., Service Bus, Event Grid) for asynchronous event processing and improved scalability.

## Continuous Validation and Iterative Refinement
- Use Copilot Studio’s built-in testing tools to simulate long-running sessions and validate agent behavior under various scenarios.
- Ensure agents reliably maintain context, correctly route queries, and handle high volumes of requests.
- Collect feedback from testing and real-world usage to iteratively refine agent workflows, state management, and error recovery strategies.
- Thoroughly document workflow configurations, state variables, and error-handling mechanisms to support ongoing maintenance and future enhancements.

---

## ML Pipeline Integration

The AgentOperatingSystem (AOS) now supports direct operation of the ML pipeline (LoRA training, Azure ML orchestration, and inference) via the `PerpetualAgent` interface. This is achieved by integrating the refactored ML pipeline from the FineTunedLLM project as agent-callable operations.

### How to Use

- The `PerpetualAgent` class exposes an `act` method that supports the following ML pipeline actions:
    - `trigger_lora_training`: Start LoRA adapter training with custom parameters
    - `run_azure_ml_pipeline`: Run the full Azure ML LoRA pipeline (provision, train, register)
    - `aml_infer`: Perform inference using UnifiedMLManager endpoints

#### Example Usage

```python
from PerpetualAgent import PerpetualAgent
import asyncio

agent = PerpetualAgent()

# Trigger LoRA training
asyncio.run(agent.act("trigger_lora_training", {
    "training_params": {"model_name": "meta-llama/Llama-3.1-8B-Instruct", "data_path": "./data/train.jsonl", "output_dir": "./outputs"},
    "adapters": [
        {"adapter_name": "lora_qv", "task_type": "causal_lm", "r": 16, "lora_alpha": 32, "target_modules": ["q_proj", "v_proj"]}
    ]
}))

# Run the full Azure ML pipeline
asyncio.run(agent.act("run_azure_ml_pipeline", {
    "subscription_id": "...",
    "resource_group": "...",
    "workspace_name": "..."
}))

# Perform inference
asyncio.run(agent.act("aml_infer", {
    "agent_id": "cmo",
    "prompt": "What is the Q2 marketing plan?"
}))
```

See `ml_pipeline_ops.py` for more details on available operations.

---

## Multi-Agent ML Pipeline Sharing

Multiple instances of `PerpetualAgent` (such as CEO, CFO, COO, etc.) can share the ML pipeline, each using a specific LoRA adapter. When you create a `PerpetualAgent`, pass its role or adapter name:

```python
from PerpetualAgent import PerpetualAgent

ceo_agent = PerpetualAgent(adapter_name="ceo")
cfo_agent = PerpetualAgent(adapter_name="cfo")
coo_agent = PerpetualAgent(adapter_name="coo")
```

When these agents call ML pipeline actions (training or inference), their `adapter_name` is automatically used for the correct LoRA adapter and endpoint.

- **Training:** The agent's adapter name is injected into the training config if not set.
- **Inference:** The agent's adapter name is used as the `agent_id` for endpoint selection.

This ensures each agent operates through its own LoRA adapter, while sharing the same ML pipeline infrastructure.

---

## Centralized ML Pipeline Management

AOS provides a centralized `MLPipelineManager` class for overall management of the ML pipeline. This manager can:
- Train adapters for any agent (CEO, CFO, COO, etc.)
- Run the full Azure ML pipeline
- Perform inference for any agent/adapter
- List and inspect all registered adapters

### Example Usage

```python
from MLPipelineManager import MLPipelineManager
import asyncio

ml_manager = MLPipelineManager()

# Train a new adapter for the CEO agent
asyncio.run(ml_manager.train_adapter(
    agent_role="ceo",
    training_params={"model_name": "meta-llama/Llama-3.1-8B-Instruct", "data_path": "./data/train.jsonl", "output_dir": "./outputs"},
    adapter_config={"task_type": "causal_lm", "r": 16, "lora_alpha": 32, "target_modules": ["q_proj", "v_proj"]}
))

# List all adapters
print(ml_manager.list_adapters())

# Run the full pipeline
asyncio.run(ml_manager.run_pipeline("...", "...", "..."))

# Inference for CFO
asyncio.run(ml_manager.infer("cfo", "What is the Q2 financial forecast?"))
```

This allows AOS to orchestrate, monitor, and control the ML pipeline for all agents in a unified way.

---

## Unified Storage Management (AOS)

AOS now provides a generic, reusable `UnifiedStorageManager` in `storage/manager.py` for agent-based systems. This manager supports:
- Azure Tables (conversations, messages)
- Azure Blob Storage (training data, profiles)
- Azure Queue (agent events, requests)

**How to use:**
- Applications (e.g., BusinessInfinity) should import and instantiate `UnifiedStorageManager` for their own needs.
- Boardroom-specific or domain-specific configuration should be provided by the application layer.

**Separation of Concerns:**
- AOS provides the storage manager as a generic utility.
- Applications configure and use it for their own data, keeping AOS domain-agnostic.

Example:
```python
from RealmOfAgents.AgentOperatingSystem.storage.manager import UnifiedStorageManager
storage = UnifiedStorageManager()
```

See the `storage/manager.py` docstring for full API details.

---

## MCP Protocol/Client Unification & Azure Service Bus Communication (2025)

The AgentOperatingSystem (AOS) is now the single source for all Model Context Protocol (MCP) protocol/client logic. All MCP communication between BusinessInfinity and external MCP services (ERPNext-MCP, linkedin-mcp-server, mcp-reddit, etc.) is handled via the AOS MCP client and Azure Service Bus.

- **MCP Client Location:** `mcp_servicebus_client.py` implements the unified client for sending/receiving MCP messages over Azure Service Bus.
- **Protocol Models:** All MCP protocol models (MCPRequest, MCPResponse) are defined in `mcp_protocol/` within AOS.
- **Migration:** All legacy MCP protocol/handler code has been removed from BusinessInfinity and other modules. Only the AOS MCP client should be used for MCP communication.
- **Service Bus Management:** Topic and subscription management utilities are provided in AOS.

For migration details, see the BusinessInfinity documentation (`MCP_CLIENT_MIGRATION.md`).

---

## Unified Authentication & Authorization (2025)

The AgentOperatingSystem (AOS) is now the single source for all authentication and authorization logic, including:
- Azure B2C authentication
- JWT validation and token management
- LinkedIn OAuth integration

All authentication endpoints and handlers in BusinessInfinity and other modules now import and use the unified handler from `aos_auth.py` in AOS. No authentication logic remains in BusinessInfinity; all logic is centralized here for maintainability and reuse.

See `aos_auth.py` for implementation details.
