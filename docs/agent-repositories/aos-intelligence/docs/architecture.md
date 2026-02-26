# Architecture — aos-intelligence

## Overview

`aos-intelligence` provides the ML/AI intelligence layer for the Agent Operating System (AOS).
It is designed to be deployed independently of the OS kernel and agent packages, following
the repository split plan for the AOS monorepo.

## Repository Position

```
ASISaga/
├── purpose-driven-agent    ← fundamental building block
├── leadership-agent        ← extends purpose-driven-agent
├── cmo-agent               ← extends leadership-agent
├── aos-kernel              ← OS kernel (orchestration, messaging, storage)
├── aos-intelligence        ← this package (ML, learning, knowledge)
├── aos-deployment          ← infrastructure (Bicep, orchestrator)
├── aos-docs                ← all documentation
├── aos-azure-functions     ← Azure Functions hosting
└── aos-copilot-extensions  ← GitHub Copilot skills and workflows
```

## Module Architecture

```
aos-intelligence/
├── config.py               ← standalone MLConfig (no external dependencies)
├── ml/
│   ├── pipeline.py         ← MLPipelineManager (central orchestrator)
│   ├── pipeline_ops.py     ← Azure ML pipeline operations
│   ├── lorax_server.py     ← LoRAx multi-adapter serving
│   ├── dpo_trainer.py      ← Direct Preference Optimization
│   ├── self_learning_system.py  ← Continuous self-improvement loop
│   └── foundry_agent_service.py ← Azure AI Agents integration
├── learning/
│   ├── knowledge_manager.py    ← Domain knowledge and directives
│   ├── rag_engine.py           ← ChromaDB-backed RAG
│   ├── interaction_learner.py  ← Interaction pattern learning
│   ├── self_learning_mixin.py  ← Reusable mixin for any agent
│   ├── domain_expert.py        ← Domain-specialised query answering
│   ├── learning_pipeline.py    ← End-to-end learning orchestration
│   └── self_learning_agents.py ← SelfLearningAgent implementation
└── knowledge/
    ├── evidence.py         ← Structured evidence retrieval
    ├── indexing.py         ← Document indexing and search
    └── precedent.py        ← Precedent-based decision support
```

## Design Principles

### 1. Separation from OS Kernel

`aos-intelligence` does **not** import from `aos-kernel`. All ML operations are decoupled from
the core orchestration, messaging, and storage layers. When storage persistence is needed
(e.g., in `KnowledgeManager` and `InteractionLearner`), the storage manager is passed as a
dependency-injected parameter using duck typing, not a hard import.

### 2. Optional Heavy Dependencies

ML training libraries (`transformers`, `torch`, `trl`, `peft`) are optional extras:

```bash
pip install aos-intelligence          # core only (no ML deps)
pip install "aos-intelligence[ml]"    # adds ML training deps
pip install "aos-intelligence[rag]"   # adds ChromaDB for RAG
pip install "aos-intelligence[full]"  # everything
```

This means `aos-intelligence` can be installed in lightweight environments (e.g., Azure Functions)
without pulling in GPU-optimised libraries.

### 3. Graceful Degradation

All optional components use `try/except ImportError` guards:

```python
try:
    from .self_learning_system import SelfLearningSystem, ...
    SELF_LEARNING_AVAILABLE = True
except ImportError:
    SELF_LEARNING_AVAILABLE = False
```

### 4. Llama 3.3 70B as Base Model

All ML operations use **Llama 3.3 70B** (`meta-llama/Llama-3.3-70B-Instruct`) as the
base model, with LoRA adapters providing domain-specific fine-tuning.

## LoRAx Architecture

```
┌────────────────────────────────────────────────────────────┐
│                       LoRAx Server                         │
│                                                            │
│  Base Model: Llama 3.3 70B (shared, loaded once)           │
│                          │                                 │
│    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐         │
│    │ CEO    │  │ CMO    │  │ CFO    │  │ Legal  │  ...    │
│    │ adapter│  │ adapter│  │ adapter│  │ adapter│         │
│    └────────┘  └────────┘  └────────┘  └────────┘         │
│         ↑           ↑           ↑           ↑             │
│         │           │           │           │             │
│    100+ LoRA adapters served concurrently per GPU          │
└────────────────────────────────────────────────────────────┘
```

**Cost benefit:** Serving 100+ agents with different LoRA adapters on a single GPU
reduces inference costs 10–50× vs separate model deployments.

## DPO Training Pipeline

```
1. Preference Collection
   ├── Human feedback (explicit ratings)
   ├── Teacher model (synthetic preferences)
   └── Heuristic signals (response quality metrics)
         ↓
2. PreferenceDataCollector.get_training_data()
         ↓
3. DPOTrainer.train(preferences)
   ├── Load base model (Llama 3.3 70B)
   ├── Apply existing LoRA adapter (optional)
   ├── Run DPO optimisation (β = 0.1 default)
   └── Save new adapter checkpoint
         ↓
4. Register adapter in LoRAxServer
         ↓
5. Serve via MLPipelineManager.infer()
```

**Cost benefit:** DPO eliminates the need for a separate Reward Model, reducing
training compute by 30–50% compared to PPO-based RLHF.

## Self-Learning Loop

```
Agent processes event
        │
        ▼
InteractionLearner.log_interaction()
        │
User provides feedback (optional)
        │
        ▼
InteractionLearner.add_feedback()
        │
        ▼
InteractionLearner.get_domain_insights()
        │
SelfLearningSystem.record_episode()  ←  periodic batch analysis
        │
        ▼
SelfLearningSystem.identify_patterns()
        │
        ▼
SelfLearningSystem.create_adaptation_plan()
        │
        ▼
DPOTrainer.train()  ←  new adapter trained from feedback
        │
        ▼
LoRAxServer.register_adapter()  ←  updated adapter deployed
```

## Interface with aos-kernel

`purpose-driven-agent` defines `IMLService` as the abstract interface for ML operations.
`aos-intelligence` implements this interface via `MLPipelineManager`:

```python
# purpose-driven-agent defines:
class IMLService(ABC):
    async def trigger_lora_training(self, ...) -> str: ...
    async def run_pipeline(self, ...) -> str: ...
    async def infer(self, agent_id: str, prompt: str) -> Dict: ...

# aos-intelligence implements:
class MLPipelineManager(IMLService):
    ...
```

Register at application startup:

```python
from aos_intelligence.ml import MLPipelineManager
from aos_intelligence.config import MLConfig

ml_service = MLPipelineManager(MLConfig.from_env())
agent = GenericPurposeDrivenAgent(
    agent_id="assistant",
    purpose="...",
    ml_service=ml_service,
)
```

## Storage Protocol

`KnowledgeManager` and `InteractionLearner` accept any object implementing:

```python
class StorageManagerProtocol(Protocol):
    async def exists(self, path: str) -> bool: ...
    async def read_json(self, path: str) -> Any: ...
    async def write_json(self, path: str, data: Any) -> None: ...
```

Pass `None` to use a no-op in-memory implementation (state not persisted between restarts).
In production, provide an `aos-kernel` `StorageManager` instance.
