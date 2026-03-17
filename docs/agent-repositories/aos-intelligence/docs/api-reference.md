# API Reference — aos-intelligence

## Top-Level Package

```python
from aos_intelligence import MLConfig
from aos_intelligence.config import MLConfig
```

| Symbol | Description |
|---|---|
| `MLConfig` | Configuration dataclass for the ML pipeline |
| `MLConfig.from_env()` | Populate `MLConfig` from environment variables |

---

## `aos_intelligence.ml` — Machine Learning

```python
from aos_intelligence.ml import (
    MLPipelineManager,
    LoRAxServer, LoRAxConfig, LoRAxAdapterRegistry, AdapterInfo,
    DPOTrainer, DPOConfig, PreferenceData, PreferenceDataCollector,
    SelfLearningSystem, LearningEpisode, LearningPattern, AdaptationPlan,
    LearningPhase, LearningFocus, FeedbackType,
    FoundryAgentServiceClient, FoundryAgentServiceConfig, FoundryResponse, ThreadInfo,
)
```

### `MLPipelineManager`

Central manager for ML pipeline operations.

| Method | Signature | Description |
|---|---|---|
| `train_model` | `(config: Dict) → str` | Trigger training job; returns job ID |
| `get_training_status` | `(job_id: str) → Optional[Dict]` | Get status of a training job |
| `list_models` | `() → List[str]` | List all registered model names |
| `lorax_inference` | `(agent_role: str, prompt: str) → Dict` | Run inference via LoRAx with adapter |
| `register_lorax_adapter` | `(agent_role, adapter_path, ...) → None` | Register existing LoRA adapter |

**Constructor:** `MLPipelineManager(config: MLConfig)`

### `LoRAxServer`

Multi-adapter LoRAx server for concurrent serving.

| Method | Signature | Description |
|---|---|---|
| `start` | `() → None` | Start the server |
| `stop` | `() → None` | Stop the server |
| `inference` | `(adapter_id: str, prompt: str) → Dict` | Run inference with adapter |
| `get_status` | `() → Dict` | Get server status |

**Constructor:** `LoRAxServer(config: LoRAxConfig)`

### `LoRAxAdapterRegistry`

| Method | Signature | Description |
|---|---|---|
| `register_adapter` | `(adapter_id: str, agent_role: str, adapter_path: str) → AdapterInfo` | Register an adapter |
| `get_adapter` | `(adapter_id: str) → Optional[AdapterInfo]` | Get adapter by ID |
| `unregister_adapter` | `(adapter_id: str) → None` | Remove adapter |
| `list_adapters` | `() → List[AdapterInfo]` | List all adapters |

### `DPOTrainer`

Direct Preference Optimization trainer.

| Method | Signature | Description |
|---|---|---|
| `train` | `(preferences: List[PreferenceData]) → Dict` | Run DPO training |
| `evaluate` | `(preferences: List[PreferenceData]) → Dict` | Evaluate on preference data |

**Constructor:** `DPOTrainer(config: DPOConfig)`

### `PreferenceDataCollector`

| Method | Signature | Description |
|---|---|---|
| `add_human_preference` | `(prompt, response_a, response_b, preference, metadata=None) → None` | Add human-rated preference |
| `add_heuristic_preference` | `(prompt, good_response, bad_response) → None` | Add heuristic-based preference |
| `get_preferences` | `() → List[PreferenceData]` | Get all collected preferences |
| `get_training_data` | `() → List[Dict]` | Get data in DPO training format |

**Constructor:** `PreferenceDataCollector(storage_path: str)`

### `FoundryAgentServiceClient`

Azure AI Agents (Foundry Agent Service) integration.

**Constructor:** `FoundryAgentServiceClient(config: FoundryAgentServiceConfig)`

---

## `aos_intelligence.learning` — Self-Learning

```python
from aos_intelligence.learning import (
    KnowledgeManager, RAGEngine, InteractionLearner,
    SelfLearningMixin, DomainExpert, LearningPipeline,
    SelfLearningAgent, SelfLearningStatefulAgent,
)
```

### `KnowledgeManager`

Domain knowledge, contexts, and directives management.

| Method | Signature | Description |
|---|---|---|
| `initialize` | `() → None` | Load knowledge from storage |
| `get_domain_context` | `(domain: str) → Dict` | Get context for a domain |
| `get_domain_knowledge` | `(domain: str) → List[Dict]` | Get knowledge entries |
| `get_agent_directives` | `(domain: str) → str` | Get agent directives |
| `add_knowledge_entry` | `(domain: str, entry: Dict) → None` | Add knowledge entry |
| `update_interaction_pattern` | `(pattern_id: str, pattern: Dict) → None` | Update pattern |
| `get_knowledge_summary` | `() → Dict` | Get knowledge base summary |

**Constructor:** `KnowledgeManager(storage_manager: Any, config: Dict = None)`

The `storage_manager` parameter accepts any object implementing the `StorageManager` protocol
(`exists`, `read_json`, `write_json` async methods). Pass `None` for an in-memory fallback.

### `RAGEngine`

Retrieval-augmented generation using vector databases.

| Method | Signature | Description |
|---|---|---|
| `initialize` | `() → bool` | Initialize vector DB connection |
| `add_knowledge_entry` | `(domain, entry_id, content, metadata=None) → None` | Index document into domain |
| `query_knowledge` | `(domain, query, top_k=None) → List[Dict]` | Retrieve relevant docs from domain |

**Constructor:** `RAGEngine(config: Dict = None)`

Requires `chromadb` for vector storage: `pip install "aos-intelligence[rag]"`.

### `InteractionLearner`

Interaction pattern learning and feedback processing.

| Method | Signature | Description |
|---|---|---|
| `initialize` | `() → None` | Load history from storage |
| `log_interaction` | `(agent_id, user_input, response, domain, conversation_id, context=None) → None` | Log interaction |
| `add_feedback` | `(conversation_id, rating, feedback=None) → bool` | Add user feedback |
| `get_domain_insights` | `(domain: str) → Dict` | Get learning insights for domain |
| `get_learning_summary` | `() → Dict` | Get overall learning summary |
| `get_recent_interactions` | `(agent_id=None, domain=None, limit=50) → List[Dict]` | Get recent interactions |

**Constructor:** `InteractionLearner(storage_manager: Any, config: Dict = None)`

### `SelfLearningMixin`

Mixin class that adds self-learning capabilities to any agent class.

### `DomainExpert`

Domain-specialised query answering using knowledge and RAG.

### `LearningPipeline`

End-to-end orchestration of the full learning cycle.

### `SelfLearningAgent`

Ready-to-use agent class combining `PurposeDrivenAgent` with `SelfLearningMixin`.

---

## `aos_intelligence.knowledge` — Knowledge Services

```python
from aos_intelligence.knowledge import (
    EvidenceRetrieval, Evidence, EvidenceType,
    IndexingEngine, IndexedDocument, SearchQuery,
    PrecedentEngine, PrecedentQuery, PrecedentMatch,
)
```

### `EvidenceRetrieval`

| Method | Signature | Description |
|---|---|---|
| `add_evidence` | `(evidence: Evidence) → None` | Add evidence item |
| `retrieve` | `(query: str, limit: int = 10) → List[Evidence]` | Retrieve relevant evidence |

### `IndexingEngine`

| Method | Signature | Description |
|---|---|---|
| `ingest` | `(title, content, content_type, source, metadata=None, tags=None) → IndexedDocument` | Index a document; returns `IndexedDocument` |
| `search` | `(query: SearchQuery) → List[IndexedDocument]` | Search indexed documents |
| `get_document` | `(document_id: str) → Optional[IndexedDocument]` | Get document by ID |

### `PrecedentEngine`

| Method | Signature | Description |
|---|---|---|
| `register_decision` | `(decision_id, decision_type, title, description, outcome, tags=None, metadata=None) → None` | Register a precedent decision |
| `find_precedents` | `(query: PrecedentQuery) → List[PrecedentMatch]` | Find matching precedents by similarity |
| `link_decisions` | `(decision_id_1, decision_id_2) → None` | Link two related decisions |

---

## `MLConfig` Reference

| Field | Type | Default | Env Var |
|---|---|---|---|
| `enable_training` | `bool` | `True` | `AOS_ENABLE_ML_TRAINING` |
| `model_storage_path` | `str` | `"models"` | `AOS_MODEL_STORAGE_PATH` |
| `training_data_path` | `str` | `"training_data"` | `AOS_TRAINING_DATA_PATH` |
| `max_training_jobs` | `int` | `5` | `AOS_MAX_TRAINING_JOBS` |
| `enable_dpo` | `bool` | `True` | `AOS_ENABLE_DPO` |
| `dpo_beta` | `float` | `0.1` | `AOS_DPO_BETA` |
| `enable_lorax` | `bool` | `True` | `AOS_ENABLE_LORAX` |
| `lorax_base_model` | `str` | `"meta-llama/Llama-3.1-8B-Instruct"` | `AOS_LORAX_BASE_MODEL` |
| `lorax_port` | `int` | `8080` | `AOS_LORAX_PORT` |
| `lorax_adapter_cache_size` | `int` | `100` | `AOS_LORAX_ADAPTER_CACHE_SIZE` |
| `enable_foundry_agent_service` | `bool` | `True` | `AOS_ENABLE_FOUNDRY_AGENT_SERVICE` |
| `foundry_agent_service_endpoint` | `str` | `""` | `FOUNDRY_AGENT_SERVICE_ENDPOINT` |
| `foundry_model` | `str` | `"llama-3.3-70b"` | `FOUNDRY_MODEL` |
