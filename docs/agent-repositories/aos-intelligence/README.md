# aos-intelligence

[![PyPI version](https://img.shields.io/pypi/v/aos-intelligence.svg)](https://pypi.org/project/aos-intelligence/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/aos-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/aos-intelligence/actions/workflows/ci.yml)

**ML pipelines, LoRA/LoRAx, DPO training, self-learning, knowledge management, and RAG for the Agent Operating System.**

`aos-intelligence` is the machine-learning and knowledge layer of the **Agent Operating System (AOS)**.
It equips `PurposeDrivenAgent` subclasses with domain-adaptive ML capabilities — fine-tuning, multi-adapter
serving, self-improvement, and retrieval-augmented generation — without coupling these heavy ML concerns
to the lightweight OS kernel.

---

## Table of Contents

1. [What is aos-intelligence?](#what-is-aos-intelligence)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Architecture Overview](#architecture-overview)
5. [Modules](#modules)
   - [ML Module](#ml-module)
   - [Learning Module](#learning-module)
   - [Knowledge Module](#knowledge-module)
6. [Usage Examples](#usage-examples)
   - [ML Pipeline](#ml-pipeline)
   - [LoRAx Multi-Adapter Serving](#lorax-multi-adapter-serving)
   - [DPO Training](#dpo-training)
   - [Self-Learning Agent](#self-learning-agent)
   - [RAG Engine](#rag-engine)
   - [Knowledge Management](#knowledge-management)
7. [Configuration](#configuration)
8. [Testing](#testing)
9. [API Reference](#api-reference)
10. [Contributing](#contributing)
11. [Related Packages](#related-packages)
12. [License](#license)

---

## What is aos-intelligence?

`aos-intelligence` provides the AI/ML brain for AOS agents:

| Capability | Module | Description |
|---|---|---|
| ML Pipeline | `aos_intelligence.ml` | Training, inference, model management |
| LoRAx Server | `aos_intelligence.ml` | Multi-adapter concurrent serving on single GPU |
| DPO Training | `aos_intelligence.ml` | Direct Preference Optimization (30–50% cheaper than PPO) |
| Self-Learning | `aos_intelligence.ml` | Continuous agent improvement loop |
| Foundry Integration | `aos_intelligence.ml` | Azure AI Agents / Foundry Agent Service |
| Knowledge Manager | `aos_intelligence.learning` | Domain knowledge, contexts, directives |
| RAG Engine | `aos_intelligence.learning` | Vector-based retrieval-augmented generation |
| Interaction Learner | `aos_intelligence.learning` | Pattern learning from agent interactions |
| Domain Expert | `aos_intelligence.learning` | Domain-specialised query answering |
| Learning Pipeline | `aos_intelligence.learning` | End-to-end learning orchestration |
| Evidence Retrieval | `aos_intelligence.knowledge` | Structured evidence retrieval |
| Indexing Engine | `aos_intelligence.knowledge` | Document indexing and search |
| Precedent Engine | `aos_intelligence.knowledge` | Precedent-based decision support |

All ML operations use **Llama 3.3 70B** as the base model.

---

## Installation

```bash
# Core (no ML deps — safe for environments without GPU)
pip install aos-intelligence

# With ML training dependencies (transformers, torch, trl, peft, …)
pip install "aos-intelligence[ml]"

# With RAG support (chromadb)
pip install "aos-intelligence[rag]"

# With Azure Foundry Agent Service
pip install "aos-intelligence[foundry]"

# Everything
pip install "aos-intelligence[full]"

# Development
pip install "aos-intelligence[dev]"
```

**Requirements:** Python 3.10 or higher.

---

## Quick Start

```python
import asyncio
from aos_intelligence.ml import MLPipelineManager
from aos_intelligence.config import MLConfig

async def main():
    config = MLConfig.from_env()
    pipeline = MLPipelineManager(config)

    # Trigger LoRA adapter training
    job_id = await pipeline.train_model({
        "model_type": "lora",
        "adapter_name": "finance",
        "training_data_path": "data/finance_training.jsonl",
        "output_dir": "models/finance_v1",
    })
    print(f"Training job started: {job_id}")

    # Run inference
    result = await pipeline.infer("finance", "Summarise Q2 expenses")
    print(result["response"])

asyncio.run(main())
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      aos-intelligence                        │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    ML Module                          │  │
│  │  MLPipelineManager · LoRAxServer · DPOTrainer         │  │
│  │  SelfLearningSystem · FoundryAgentServiceClient       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  Learning Module                      │  │
│  │  KnowledgeManager · RAGEngine · InteractionLearner   │  │
│  │  SelfLearningMixin · DomainExpert · LearningPipeline  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 Knowledge Module                      │  │
│  │  EvidenceRetrieval · IndexingEngine · PrecedentEngine │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                  depends on (optional)
                            │
               ┌────────────▼────────────┐
               │    purpose-driven-agent  │
               │   aos-kernel (storage)   │
               └─────────────────────────┘
```

---

## Modules

### ML Module

```python
from aos_intelligence.ml import (
    MLPipelineManager,       # Central pipeline manager
    LoRAxServer,             # Multi-adapter LoRAx server
    LoRAxConfig,             # LoRAx configuration
    LoRAxAdapterRegistry,    # Adapter registry
    DPOTrainer,              # Direct Preference Optimization trainer
    DPOConfig,               # DPO configuration
    PreferenceData,          # Preference data model
    PreferenceDataCollector, # Preference collection helper
    SelfLearningSystem,      # Self-learning loop
    FoundryAgentServiceClient,  # Azure AI Agents integration
)
```

### Learning Module

```python
from aos_intelligence.learning import (
    KnowledgeManager,        # Domain knowledge management
    RAGEngine,               # Retrieval-augmented generation
    InteractionLearner,      # Interaction pattern learning
    SelfLearningMixin,       # Mixin for self-learning agents
    DomainExpert,            # Domain-specific query answering
    LearningPipeline,        # End-to-end learning orchestration
    SelfLearningAgent,       # Self-learning agent implementation
)
```

### Knowledge Module

```python
from aos_intelligence.knowledge import (
    EvidenceRetrieval,   # Structured evidence retrieval
    Evidence,            # Evidence model
    EvidenceType,        # Evidence type enum
    IndexingEngine,      # Document indexing
    IndexedDocument,     # Indexed document model
    SearchQuery,         # Search query model
    PrecedentEngine,     # Precedent-based decision support
    PrecedentQuery,      # Precedent query model
    PrecedentMatch,      # Precedent match result
)
```

---

## Usage Examples

### ML Pipeline

```python
from aos_intelligence.ml import MLPipelineManager
from aos_intelligence.config import MLConfig

config = MLConfig(
    enable_training=True,
    enable_lorax=True,
    lorax_base_model="meta-llama/Llama-3.3-70B-Instruct",
)
pipeline = MLPipelineManager(config)

# Train a LoRA adapter
job_id = await pipeline.train_model({
    "model_type": "lora",
    "adapter_name": "legal",
    "training_data_path": "data/legal.jsonl",
    "output_dir": "models/legal_v1",
})

# Check training status
status = await pipeline.get_job_status(job_id)
print(status["status"])  # "running", "completed", "failed"

# Run inference
result = await pipeline.infer("legal", "Summarise the NDA risk clauses")
print(result["response"])
```

### LoRAx Multi-Adapter Serving

```python
from aos_intelligence.ml import LoRAxServer, LoRAxConfig

config = LoRAxConfig(
    base_model="meta-llama/Llama-3.3-70B-Instruct",
    port=8080,
    adapter_cache_size=100,
)
server = LoRAxServer(config)

# Register adapters
server.adapter_registry.register_adapter("ceo", "CEO", "/models/leadership_v1")
server.adapter_registry.register_adapter("cmo", "CMO", "/models/marketing_v1")

# Start server
await server.start()

# Inference with a specific adapter
result = await server.inference("ceo", "What is our Q3 growth strategy?")
print(result["response"])
```

### DPO Training

```python
from aos_intelligence.ml import DPOTrainer, DPOConfig, PreferenceData

config = DPOConfig(
    base_model="meta-llama/Llama-3.3-70B-Instruct",
    beta=0.1,
    learning_rate=5e-5,
    num_epochs=3,
)
trainer = DPOTrainer(config)

# Add preference data
preference = PreferenceData(
    prompt="What is our strategic vision for Q2?",
    chosen_response="We should focus on market expansion in Europe and Asia.",
    rejected_response="I think we need to consider various factors.",
)

# Run training
result = await trainer.train([preference])
print(f"Training complete: {result['status']}")
```

### Self-Learning Agent

```python
from aos_intelligence.learning import SelfLearningAgent

agent = SelfLearningAgent(
    agent_id="sales-001",
    name="Sales Assistant",
    domains=["sales", "crm"],
)

await agent.start()

# Process a query with learning
response = await agent.process_query(
    user_input="What are our top leads this quarter?",
    domain="sales",
    conversation_id="conv-001",
)
print(response["response"])

# Add feedback for continuous learning
await agent.rate_interaction("conv-001", rating=4.5, feedback="Very helpful")
```

### RAG Engine

```python
from aos_intelligence.learning import RAGEngine

rag = RAGEngine(config={
    "vector_db_host": "localhost",
    "vector_db_port": 8000,
    "top_k_snippets": 5,
})

await rag.initialize()

# Add documents to knowledge base
await rag.add_document(
    collection="sales_playbook",
    document_id="doc-001",
    content="Our sales methodology focuses on value-based selling...",
    metadata={"domain": "sales", "version": "2025"},
)

# Retrieve relevant context
results = await rag.retrieve(
    query="How should we handle enterprise objections?",
    collection="sales_playbook",
)
for result in results:
    print(f"[{result['score']:.2f}] {result['content'][:100]}")
```

### Knowledge Management

```python
from aos_intelligence.learning import KnowledgeManager

# KnowledgeManager accepts an optional storage backend
km = KnowledgeManager(storage_manager=None, config={
    "knowledge_base_path": "knowledge",
})
await km.initialize()

# Get domain context
context = await km.get_domain_context("sales")
print(context["purpose"])

# Add a knowledge entry
await km.add_knowledge_entry("sales", {
    "title": "Enterprise objection handling",
    "content": "When facing budget objections, focus on ROI...",
    "tags": ["objections", "enterprise"],
})

# Get domain directives
directives = await km.get_agent_directives("sales")
print(directives)
```

---

## Configuration

`MLConfig` can be constructed directly or populated from environment variables:

```python
from aos_intelligence.config import MLConfig

# From environment variables
config = MLConfig.from_env()

# Direct construction
config = MLConfig(
    enable_training=True,
    enable_dpo=True,
    enable_lorax=True,
    lorax_base_model="meta-llama/Llama-3.3-70B-Instruct",
    lorax_port=8080,
    enable_foundry_agent_service=False,
)
```

| Environment Variable | Default | Description |
|---|---|---|
| `AOS_ENABLE_ML_TRAINING` | `true` | Enable model training |
| `AOS_LORAX_BASE_MODEL` | `meta-llama/Llama-3.1-8B-Instruct` | LoRAx base model |
| `AOS_LORAX_PORT` | `8080` | LoRAx server port |
| `AOS_ENABLE_DPO` | `true` | Enable DPO training |
| `AOS_ENABLE_LORAX` | `true` | Enable LoRAx multi-adapter serving |
| `FOUNDRY_AGENT_SERVICE_ENDPOINT` | `""` | Azure AI Agents endpoint |
| `FOUNDRY_MODEL` | `llama-3.3-70b` | Foundry model name |

---

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=aos_intelligence --cov-report=term-missing

# Single module
pytest tests/test_ml_pipeline.py -v
pytest tests/test_lorax.py -v
pytest tests/test_learning.py -v
pytest tests/test_knowledge.py -v
```

---

## API Reference

Full API documentation: [`docs/api-reference.md`](docs/api-reference.md)

---

## Contributing

See [`docs/contributing.md`](docs/contributing.md) for setup, testing, linting, and pull-request guidelines.

```bash
git clone https://github.com/ASISaga/aos-intelligence.git
cd aos-intelligence
pip install -e ".[dev]"
pytest tests/ -v
pylint src/aos_intelligence
```

---

## Related Packages

| Package | Description |
|---|---|
| [`purpose-driven-agent`](https://github.com/ASISaga/purpose-driven-agent) | PurposeDrivenAgent — the fundamental building block |
| [`leadership-agent`](https://github.com/ASISaga/leadership-agent) | LeadershipAgent — decision-making and coordination |
| [`cmo-agent`](https://github.com/ASISaga/cmo-agent) | CMOAgent — marketing + leadership dual-purpose |
| [`AgentOperatingSystem`](https://github.com/ASISaga/AgentOperatingSystem) | Full AOS monorepo |

---

## License

[Apache License 2.0](LICENSE) — © 2024 ASISaga
