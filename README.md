# AgentOperatingSystem
An operating system of agents
Top level agents generate natural language actions from purpose, domain knowledge, and environmental inputs.

---

## Architecture Note: Domain-Agnostic Design

The AgentOperatingSystem (AOS) is designed as a reusable, domain-agnostic orchestration and agent management layer. It provides the core infrastructure for agent coordination, resource management, and inter-agent communication, but does **not** include application-specific storage or environment managers.

**Why?**
- Keeping AOS generic allows it to be used as a foundation for many different domains and applications.
- Storage, environment configuration, and persistent data management are handled by applications built on top of AOS (such as BusinessInfinity), according to their specific needs.

**Separation of Concerns:**
- AOS: Agent orchestration, resource allocation, agent lifecycle, and communication.
- Application (e.g., BusinessInfinity): Business logic, user interface, storage, and environment management.

This separation ensures AOS remains flexible and reusable, while applications maintain control over their own operational context.

Down the line agents would take actions

Prerequisites:
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
