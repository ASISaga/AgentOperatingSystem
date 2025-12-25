# Technical Specification: Storage Management System

**Document Version:** 2025.1.2  
**Status:** Implemented  
**Date:** December 25, 2025  
**Module:** AgentOperatingSystem Storage (`src/AgentOperatingSystem/storage/`)

---

## 1. System Overview

The AOS Storage Management system provides a unified, backend-agnostic storage abstraction layer for all data persistence needs across the Agent Operating System. It enables seamless switching between different storage backends (file-based, Azure, S3) while maintaining a consistent API for all consumers.

**Key Features:**
- Unified storage interface across multiple backends
- Support for Azure Blob Storage, Azure Tables, Azure Queues
- File-based storage for local development
- Backend abstraction for easy migration
- Type-safe storage operations
- Automatic serialization/deserialization

---

## 2. Architecture

### 2.1 Core Components

**StorageManager (`manager.py`)**
- High-level storage operations coordinator
- Backend selection and initialization
- Unified API for all storage operations
- Automatic backend configuration

**Storage Backends:**
1. **FileStorageBackend (`file_backend.py`)**: Local file-based storage
2. **AzureStorageBackend (`azure_backend.py`)**: Azure cloud storage services
3. **StorageBackend (`backend.py`)**: Abstract base class for backends

**StorageConfig (`config/storage.py`)**
- Storage backend configuration
- Connection parameters
- Storage paths and container names

### 2.2 Storage Backend Architecture

```
┌─────────────────────────────────────────────┐
│         Application Layer                   │
│  (Agents, Orchestrators, Business Logic)    │
└─────────────────┬───────────────────────────┘
                  │
                  │ Uses
                  ▼
┌─────────────────────────────────────────────┐
│         StorageManager                      │
│  (Unified Storage Interface)                │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴─────────┬─────────────┐
        │                   │             │
        ▼                   ▼             ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ File Backend │   │Azure Backend │   │  S3 Backend  │
│  (Local Dev) │   │ (Production) │   │  (Optional)  │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                  │
        ▼                   ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Local FS    │   │Azure Storage │   │   AWS S3     │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## 3. Implementation Details

### 3.1 StorageManager Class

**Initialization:**
```python
from AgentOperatingSystem.storage.manager import StorageManager
from AgentOperatingSystem.config.storage import StorageConfig

# Initialize with file backend (local development)
config = StorageConfig(
    storage_type="file",
    base_path="./data"
)
storage = StorageManager(config)

# Initialize with Azure backend (production)
config = StorageConfig(
    storage_type="azure",
    connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING")
)
storage = StorageManager(config)
```

**Core Operations:**

**1. Save Data:**
```python
# Save JSON data
await storage.save(
    key="agent_configs/ceo",
    data={"name": "CEO", "role": "executive", "status": "active"},
    content_type="application/json"
)

# Save binary data
with open("model.pkl", "rb") as f:
    await storage.save(
        key="models/ceo_adapter",
        data=f.read(),
        content_type="application/octet-stream"
    )
```

**2. Load Data:**
```python
# Load JSON data
config = await storage.load("agent_configs/ceo")

# Load binary data
model_data = await storage.load("models/ceo_adapter")
```

**3. List Keys:**
```python
# List all keys with prefix
agent_configs = await storage.list_keys(prefix="agent_configs/")
# Returns: ["agent_configs/ceo", "agent_configs/cfo", ...]
```

**4. Delete Data:**
```python
# Delete specific key
await storage.delete("agent_configs/old_config")
```

**5. Check Existence:**
```python
# Check if key exists
exists = await storage.exists("agent_configs/ceo")
```

### 3.2 File Storage Backend

**Implementation:**
- Uses local filesystem for storage
- Ideal for development and testing
- Hierarchical directory structure
- JSON and binary file support

**Features:**
```python
from AgentOperatingSystem.storage.file_backend import FileStorageBackend

backend = FileStorageBackend(base_path="./data")

# File operations
await backend.write("path/to/file.json", data)
data = await backend.read("path/to/file.json")
await backend.delete("path/to/file.json")
files = await backend.list_files(prefix="path/to/")
```

**Directory Structure:**
```
data/
├── agent_configs/
│   ├── ceo.json
│   ├── cfo.json
│   └── coo.json
├── models/
│   ├── ceo_adapter.pkl
│   └── cfo_adapter.pkl
├── conversations/
│   ├── conv_001.json
│   └── conv_002.json
└── knowledge/
    ├── documents/
    └── embeddings/
```

### 3.3 Azure Storage Backend

**Implementation:**
- Azure Blob Storage for objects and files
- Azure Table Storage for structured data
- Azure Queue Storage for message queues
- Seamless integration with Azure ecosystem

**Supported Services:**

**1. Azure Blob Storage:**
```python
from AgentOperatingSystem.storage.azure_backend import AzureStorageBackend

backend = AzureStorageBackend(connection_string)

# Blob operations
await backend.upload_blob(
    container="models",
    blob_name="ceo_adapter.pkl",
    data=model_data
)

data = await backend.download_blob(
    container="models",
    blob_name="ceo_adapter.pkl"
)

# List blobs
blobs = await backend.list_blobs(container="models", prefix="adapters/")
```

**2. Azure Table Storage:**
```python
# Table operations for structured data
await backend.insert_entity(
    table_name="conversations",
    entity={
        "PartitionKey": "agent_ceo",
        "RowKey": "conv_001",
        "timestamp": "2025-12-25T00:00:00Z",
        "messages": json.dumps(messages)
    }
)

entity = await backend.get_entity(
    table_name="conversations",
    partition_key="agent_ceo",
    row_key="conv_001"
)

# Query entities
entities = await backend.query_entities(
    table_name="conversations",
    filter="PartitionKey eq 'agent_ceo'"
)
```

**3. Azure Queue Storage:**
```python
# Queue operations for event processing
await backend.send_message(
    queue_name="agent_tasks",
    message=json.dumps({
        "task_id": "task_001",
        "agent_id": "ceo",
        "action": "analyze_report"
    })
)

message = await backend.receive_message(queue_name="agent_tasks")
await backend.delete_message(queue_name="agent_tasks", message)
```

**Connection Configuration:**
```python
# Using connection string
connection_string = (
    "DefaultEndpointsProtocol=https;"
    "AccountName=youraccount;"
    "AccountKey=yourkey;"
    "EndpointSuffix=core.windows.net"
)

# Or using Azure Identity (recommended for production)
from azure.identity import DefaultAzureCredential

backend = AzureStorageBackend(
    account_url="https://youraccount.blob.core.windows.net",
    credential=DefaultAzureCredential()
)
```

---

## 4. Data Models and Types

### 4.1 Storage Data Types

**Supported Data Types:**
1. **JSON Documents**: Configuration, metadata, structured data
2. **Binary Data**: Models, embeddings, files
3. **Text Data**: Logs, documents, content
4. **Structured Tables**: Relational data, indexes

**Serialization:**
```python
import json
import pickle

# JSON serialization (default for dicts/lists)
data = {"key": "value"}
serialized = json.dumps(data)

# Binary serialization (for complex objects)
model = SomeModel()
serialized = pickle.dumps(model)

# Storage manager handles serialization automatically
await storage.save("data_key", data)  # Auto-detects and serializes
```

### 4.2 Key Naming Conventions

**Recommended Key Structure:**
```
{domain}/{type}/{identifier}[/{version}]

Examples:
- agent_configs/ceo/current
- models/lora_adapters/ceo/v1.2
- conversations/boardroom/session_001
- knowledge/documents/policy_handbook
- training_data/ceo/dataset_001
- metrics/performance/2025-12
```

**Benefits:**
- Organized namespace
- Easy filtering and listing
- Version management
- Clear data ownership

---

## 5. Storage Patterns

### 5.1 Agent Configuration Storage

```python
# Save agent configuration
agent_config = {
    "agent_id": "ceo",
    "name": "Chief Executive Officer",
    "role": "executive",
    "capabilities": ["strategy", "decision_making"],
    "model_config": {
        "adapter_name": "ceo_adapter",
        "model_version": "v1.2"
    }
}

await storage.save(
    key=f"agent_configs/{agent_config['agent_id']}",
    data=agent_config
)

# Load agent configuration
config = await storage.load("agent_configs/ceo")
```

### 5.2 Model Storage

```python
# Save trained model
model_data = {
    "model_type": "lora_adapter",
    "base_model": "llama-3.1-8b",
    "adapter_weights": weights_binary,
    "hyperparameters": {"r": 16, "lora_alpha": 32},
    "training_metrics": {"accuracy": 0.95, "loss": 0.05},
    "created_at": "2025-12-25T00:00:00Z"
}

await storage.save(
    key="models/lora_adapters/ceo/v1.2",
    data=model_data
)
```

### 5.3 Conversation History Storage

```python
# Save conversation
conversation = {
    "conversation_id": "conv_001",
    "participants": ["ceo", "cfo"],
    "messages": [
        {"role": "ceo", "content": "What's the Q2 forecast?", "timestamp": "..."},
        {"role": "cfo", "content": "Revenue projection is $5M", "timestamp": "..."}
    ],
    "metadata": {
        "topic": "financial_planning",
        "created_at": "2025-12-25T00:00:00Z"
    }
}

await storage.save(
    key=f"conversations/{conversation['conversation_id']}",
    data=conversation
)

# Query conversations by participant
all_ceo_conversations = await storage.list_keys(prefix="conversations/")
# Filter in application logic or use Azure Tables for efficient queries
```

### 5.4 Knowledge Base Storage

```python
# Save document in knowledge base
document = {
    "document_id": "doc_001",
    "title": "Q2 Strategy Document",
    "content": "Full document text...",
    "embedding": embedding_vector,
    "metadata": {
        "category": "strategy",
        "author": "ceo",
        "tags": ["Q2", "strategy", "planning"]
    }
}

await storage.save(
    key=f"knowledge/documents/{document['document_id']}",
    data=document
)
```

---

## 6. Performance Optimization

### 6.1 Caching Strategies

**In-Memory Caching:**
```python
from functools import lru_cache

class CachedStorageManager:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.cache = {}
    
    async def load(self, key: str):
        if key in self.cache:
            return self.cache[key]
        
        data = await self.storage.load(key)
        self.cache[key] = data
        return data
    
    async def save(self, key: str, data):
        await self.storage.save(key, data)
        self.cache[key] = data  # Update cache
```

**TTL-Based Caching:**
```python
from datetime import datetime, timedelta

class TTLCache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return data
            del self.cache[key]
        return None
    
    def set(self, key, data):
        self.cache[key] = (data, datetime.now())
```

### 6.2 Batch Operations

```python
# Batch save
items = [
    ("key1", data1),
    ("key2", data2),
    ("key3", data3)
]

await asyncio.gather(*[
    storage.save(key, data) for key, data in items
])

# Batch load
keys = ["key1", "key2", "key3"]
results = await asyncio.gather(*[
    storage.load(key) for key in keys
])
```

### 6.3 Compression

```python
import gzip
import json

# Compress large data before storage
def compress_data(data):
    json_str = json.dumps(data)
    return gzip.compress(json_str.encode())

def decompress_data(compressed):
    json_str = gzip.decompress(compressed).decode()
    return json.loads(json_str)

# Use with storage
compressed = compress_data(large_dataset)
await storage.save("large_dataset", compressed)
```

---

## 7. Error Handling and Resilience

### 7.1 Exception Handling

**Storage Exceptions:**
```python
from AgentOperatingSystem.storage.backend import StorageError

try:
    data = await storage.load("some_key")
except KeyError:
    # Key not found
    logger.warning("Key not found, using default")
    data = default_data
except StorageError as e:
    # Storage backend error
    logger.error(f"Storage error: {e}")
    raise
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error: {e}")
    raise
```

### 7.2 Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class ResilientStorageManager:
    def __init__(self, storage_manager):
        self.storage = storage_manager
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def save(self, key, data):
        return await self.storage.save(key, data)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def load(self, key):
        return await self.storage.load(key)
```

### 7.3 Fallback Mechanisms

```python
# Primary storage with fallback
async def load_with_fallback(key):
    try:
        return await primary_storage.load(key)
    except Exception as e:
        logger.warning(f"Primary storage failed: {e}, trying fallback")
        return await fallback_storage.load(key)
```

---

## 8. Security and Compliance

### 8.1 Access Control

**Azure Storage Security:**
```python
# Use Azure RBAC for access control
from azure.identity import DefaultAzureCredential

backend = AzureStorageBackend(
    account_url="https://youraccount.blob.core.windows.net",
    credential=DefaultAzureCredential()
)

# Container-level access control
await backend.create_container(
    name="sensitive_data",
    access_level="private"  # No public access
)
```

**File Storage Security:**
```python
# File permissions for local storage
import os

# Restrict file permissions
os.chmod(file_path, 0o600)  # Owner read/write only
```

### 8.2 Data Encryption

**Encryption at Rest:**
- Azure Storage: Automatic encryption with Microsoft-managed keys
- File Storage: Use OS-level encryption (BitLocker, FileVault)

**Encryption in Transit:**
- Always use HTTPS for Azure Storage
- TLS 1.2+ for all connections

**Application-Level Encryption:**
```python
from cryptography.fernet import Fernet

class EncryptedStorage:
    def __init__(self, storage_manager, encryption_key):
        self.storage = storage_manager
        self.cipher = Fernet(encryption_key)
    
    async def save_encrypted(self, key, data):
        encrypted = self.cipher.encrypt(json.dumps(data).encode())
        await self.storage.save(key, encrypted)
    
    async def load_encrypted(self, key):
        encrypted = await self.storage.load(key)
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
```

### 8.3 Audit Logging

```python
from AgentOperatingSystem.governance.audit import audit_log

# Log storage operations
await audit_log(
    actor="system",
    action="storage_write",
    resource=f"storage/{key}",
    outcome="success",
    context={
        "storage_type": storage_type,
        "data_size": len(data),
        "timestamp": datetime.now().isoformat()
    }
)
```

---

## 9. Monitoring and Observability

### 9.1 Metrics

**Storage Metrics:**
```python
from AgentOperatingSystem.observability.metrics import MetricsCollector

metrics = MetricsCollector()

# Track storage operations
metrics.increment("storage.operations.total", tags={"operation": "write"})
metrics.timing("storage.latency", duration_ms, tags={"operation": "read"})
metrics.gauge("storage.size.bytes", total_bytes)
```

**Key Metrics to Track:**
- Operation count (read/write/delete)
- Operation latency (p50, p95, p99)
- Storage size and growth rate
- Error rates by operation type
- Cache hit rates
- Backend availability

### 9.2 Logging

```python
import logging

logger = logging.getLogger("AOS.Storage")

# Structured logging
logger.info(
    "Storage operation completed",
    extra={
        "operation": "write",
        "key": key,
        "size_bytes": len(data),
        "backend": backend_type,
        "duration_ms": duration
    }
)
```

---

## 10. Migration and Versioning

### 10.1 Backend Migration

**Migrate from File to Azure:**
```python
async def migrate_storage(source_storage, dest_storage):
    # List all keys from source
    keys = await source_storage.list_keys()
    
    for key in keys:
        # Load from source
        data = await source_storage.load(key)
        
        # Save to destination
        await dest_storage.save(key, data)
        
        logger.info(f"Migrated {key}")
```

### 10.2 Data Versioning

```python
# Version-aware storage
async def save_versioned(key, data, version=None):
    if version is None:
        # Auto-increment version
        versions = await storage.list_keys(prefix=f"{key}/v")
        version = len(versions) + 1
    
    versioned_key = f"{key}/v{version}"
    await storage.save(versioned_key, data)
    
    # Update current pointer
    await storage.save(f"{key}/current", {"version": version})
    
    return version
```

---

## 11. Best Practices

### 11.1 Key Design

1. **Use hierarchical keys** with slashes for organization
2. **Include type information** in key prefixes
3. **Version important data** for rollback capability
4. **Avoid special characters** in keys
5. **Keep keys concise** but descriptive

### 11.2 Performance

1. **Batch operations** when possible
2. **Use caching** for frequently accessed data
3. **Compress large payloads** before storage
4. **Implement connection pooling** for Azure
5. **Monitor and optimize** storage access patterns

### 11.3 Reliability

1. **Implement retry logic** for transient failures
2. **Use fallback storage** for critical data
3. **Validate data** before and after storage
4. **Implement health checks** for storage backends
5. **Monitor storage quotas** and limits

---

**Document Approval:**
- **Status:** Implemented and Active
- **Last Updated:** December 25, 2025
- **Next Review:** Quarterly
- **Owner:** AOS Infrastructure Team
