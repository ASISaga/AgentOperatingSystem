---
name: aos-intelligence
description: >
  Expert knowledge for developing, extending, testing, and deploying the
  aos-intelligence package — the ML/AI intelligence layer of the Agent Operating
  System. Covers ML pipelines, LoRAx multi-adapter serving, DPO training,
  self-learning systems, knowledge management, RAG engine, and integration with
  purpose-driven agents via the IMLService interface.
---

# AOS Intelligence Skill

## Overview

`aos-intelligence` provides the ML brain for AOS agents: LoRA adapter training,
LoRAx concurrent multi-adapter serving, DPO preference optimisation,
continuous self-learning, RAG-based knowledge retrieval, and evidence/precedent
management.

```python
from aos_intelligence.config import MLConfig
from aos_intelligence.ml import MLPipelineManager

config = MLConfig.from_env()
pipeline = MLPipelineManager(config)

job_id = await pipeline.train_model({"model_type": "lora", "adapter_name": "finance", ...})
result = await pipeline.infer("finance", "Summarise Q2 expenses")
```

## Module Map

| Import | Key Classes |
|---|---|
| `aos_intelligence.config` | `MLConfig` |
| `aos_intelligence.ml` | `MLPipelineManager`, `LoRAxServer`, `DPOTrainer`, `SelfLearningSystem`, `FoundryAgentServiceClient` |
| `aos_intelligence.learning` | `KnowledgeManager`, `RAGEngine`, `InteractionLearner`, `SelfLearningMixin`, `DomainExpert`, `LearningPipeline`, `SelfLearningAgent` |
| `aos_intelligence.knowledge` | `EvidenceRetrieval`, `IndexingEngine`, `PrecedentEngine` |

## Key Concepts

### LoRAx Multi-Adapter Serving

```python
from aos_intelligence.ml.lorax_server import LoRAxServer, LoRAxConfig

server = LoRAxServer(LoRAxConfig(base_model="meta-llama/Llama-3.3-70B-Instruct", port=8080))
server.adapter_registry.register_adapter("ceo", "CEO", "/models/leadership_v1")
server.adapter_registry.register_adapter("cfo", "CFO", "/models/finance_v1")
await server.start()

result = await server.inference("ceo", "What is our Q3 strategy?")
```

### DPO Training

```python
from aos_intelligence.ml.dpo_trainer import DPOTrainer, DPOConfig, PreferenceDataCollector

collector = PreferenceDataCollector("prefs.jsonl")
collector.add_human_preference(
    prompt="Strategic vision for Q2?",
    response_a="Expand to Europe with €5M investment.",
    response_b="Consider various factors.",
    preference="a",
)

trainer = DPOTrainer(DPOConfig(beta=0.1, num_epochs=3))
result = await trainer.train(collector.get_preferences())
```

### Self-Learning Loop

```python
from aos_intelligence.learning import InteractionLearner, KnowledgeManager

learner = InteractionLearner(storage_manager=storage)
await learner.initialize()
await learner.log_interaction("agent-001", "Top leads?", "Here are 5 leads...", "sales", "conv-001")
await learner.add_feedback("conv-001", rating=4.5)
insights = await learner.get_domain_insights("sales")
```

### RAG Engine

```python
from aos_intelligence.learning import RAGEngine

rag = RAGEngine({"vector_db_host": "localhost", "vector_db_port": 8000})
await rag.initialize()
await rag.add_document("sales_docs", "doc-001", "Value-based selling approach...")
results = await rag.retrieve("enterprise objection handling", "sales_docs")
```

## IMLService Integration

`aos-intelligence` implements the `IMLService` interface defined in `purpose-driven-agent`:

```python
from purpose_driven_agent.ml_interface import IMLService
from aos_intelligence.ml import MLPipelineManager

class AOSIntelligenceMLService(IMLService):
    def __init__(self):
        from aos_intelligence.config import MLConfig
        self.pipeline = MLPipelineManager(MLConfig.from_env())

    async def trigger_lora_training(self, training_params, adapters):
        return await self.pipeline.train_model({**training_params, "adapters": adapters})

    async def run_pipeline(self, subscription_id, resource_group, workspace_name):
        from aos_intelligence.ml.pipeline_ops import run_azure_ml_pipeline
        return await run_azure_ml_pipeline(subscription_id, resource_group, workspace_name)

    async def infer(self, agent_id, prompt):
        return await self.pipeline.infer(agent_id, prompt)
```

## Testing Patterns

```python
# Mock storage for unit tests
from unittest.mock import AsyncMock, MagicMock

def make_mock_storage():
    s = MagicMock()
    s.exists = AsyncMock(return_value=False)
    s.read_json = AsyncMock(return_value={})
    s.write_json = AsyncMock()
    return s

# Test KnowledgeManager
km = KnowledgeManager(make_mock_storage())
await km.initialize()
assert len(km.domain_contexts) > 0

# Test InteractionLearner
learner = InteractionLearner(make_mock_storage())
await learner.initialize()
await learner.log_interaction("a1", "input", "response", "sales", "conv-001")
assert len(learner.interaction_history) == 1
```

## Common Issues

### `ImportError: No module named 'chromadb'`
RAGEngine requires ChromaDB. Install with: `pip install "aos-intelligence[rag]"`

### `ImportError: No module named 'torch'`
ML training requires PyTorch. Install with: `pip install "aos-intelligence[ml]"`

### `ImportError: No module named 'azure.ai.agents'`
Foundry integration requires Azure SDK. Install with: `pip install "aos-intelligence[foundry]"`

### Storage backend not configured
`KnowledgeManager` and `InteractionLearner` accept `storage_manager=None` — state will be
held in memory only. For persistence, pass an `aos-kernel` `StorageManager` instance.
