# Operating System Services

AOS provides a comprehensive suite of services that form the infrastructure for AI agents.

## 🔧 Core Kernel Services

### **Orchestration Engine** (`orchestration/`)
The AOS kernel that manages agent lifecycles, workflow execution, and multi-agent coordination.
- Agent registration and discovery
- Workflow state management
- Dependency resolution
- Resource scheduling

### **Agent Lifecycle Manager** (`agents/`)
Process management for agents - creation, execution, monitoring, and termination.
- Agent provisioning and initialization
- Health monitoring and auto-recovery
- Capability tracking
- Upgrade orchestration

### **Message Bus** (`messaging/`)
Inter-agent communication (IPC for agents) with pub/sub and request-response patterns.
- Topic-based routing
- Message delivery guarantees
- Conversation management
- Azure Service Bus integration

### **State Machine Manager** (`reliability/state_machine.py`)
Deterministic state transitions for workflows and decisions.
- Explicit lifecycle states
- Timeout and escalation rules
- State persistence and recovery

---

## 💾 System Service Layer

### **Storage Service** (`storage/`)
Unified file system abstraction across multiple backends.
- Azure Blob Storage (objects)
- Azure Table Storage (structured data)
- Azure Queue Storage (message queues)
- Cosmos DB (document database)
- Backend-agnostic interface

### **Authentication & Authorization** (`auth/`)
Security layer for agent identity and access control.
- Multi-provider authentication
- Session management
- Role-based access control (RBAC)
- Token lifecycle management

### **ML Pipeline Service** (`ml/`)
Machine learning infrastructure for training and inference.
- Azure ML integration
- LoRA adapter management
- Model versioning and deployment
- Inference with caching

### **MCP Integration Service** (`mcp/`)
Model Context Protocol for external tool and resource access.
- MCP client/server implementation
- Tool discovery and execution
- Resource access management
- Protocol standardization

### **Governance Service** (`governance/`)
Enterprise compliance and audit infrastructure.
- Tamper-evident audit logging
- Policy enforcement
- Risk registry
- Decision rationale tracking

### **Reliability Service** (`reliability/`)
Fault tolerance and resilience patterns.
- Circuit breakers
- Retry with exponential backoff
- Idempotency handling
- Backpressure management

### **Observability Service** (`observability/`)
System monitoring, tracing, and alerting.
- Metrics collection (counters, gauges, histograms)
- Distributed tracing
- Structured logging
- Alert management

### **Learning Service** (`learning/`)
Continuous improvement and adaptation.
- Learning pipeline orchestration
- Performance tracking
- Self-improvement loops
- Domain expertise development

### **Knowledge Service** (`knowledge/`)
Information retrieval and precedent tracking.
- Knowledge base management
- RAG (Retrieval-Augmented Generation)
- Document indexing
- Evidence retrieval

### **Extensibility Framework** (`extensibility/`)
Plugin system for extending AOS capabilities.
- Plugin lifecycle management
- Schema registry
- Hot-swappable adapters
- Plugin marketplace support

## See Also

- [System APIs](../reference/system-apis.md) - API reference for services
- [Architecture](../architecture/ARCHITECTURE.md) - Detailed architecture
- [Vision](vision.md) - Operating system vision
