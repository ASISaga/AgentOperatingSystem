# AOS Kernel API Reference

## Core Classes

### AgentOperatingSystem
Main kernel class. Entry point for the OS.

### Orchestration
- `DecisionEngine` — Decision-making engine
- `Workflow` — Workflow definition
- `WorkflowOrchestrator` — Orchestration engine

### Messaging
- `Message` — Message model
- `MessageBus` — In-process message bus
- `MessageRouter` — Message routing
- `ServiceBusManager` — Azure Service Bus integration

### Storage
- `StorageManager` — Storage backend manager

### Authentication
- `AuthManager` — Authentication and authorization

### MCP
- `MCPClient` — Model Context Protocol client

### Reliability
- `CircuitBreaker` — Circuit breaker pattern
- `RetryPolicy` — Retry with backoff

### Observability
- `MetricsCollector` — Metrics collection
- `DistributedTracer` — Distributed tracing
