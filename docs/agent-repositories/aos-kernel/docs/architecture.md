# AOS Kernel Architecture

The AOS Kernel provides the core runtime infrastructure for the Agent Operating System.

## System Architecture

See [ARCHITECTURE.md](../../docs/architecture/ARCHITECTURE.md) in the monorepo for the full system architecture.
This file should be replaced with the contents of `docs/architecture/ARCHITECTURE.md` from the monorepo.

## Kernel Modules

| Module | Description | LOC |
|--------|-------------|-----|
| orchestration | Workflow orchestration, decision engines | 6,129 |
| messaging | Message bus, routing, Service Bus | 4,245 |
| reliability | Circuit breakers, retry policies | 2,442 |
| observability | Logging, metrics, tracing | 2,108 |
| testing | Test framework | 1,862 |
| extensibility | Plugin framework, registries | 1,619 |
| monitoring | System monitor, audit trail | 1,399 |
| governance | Audit, compliance, risk | 1,314 |
| mcp | Model Context Protocol | 1,049 |
| storage | Storage backends | 784 |
| platform | Platform contracts, events | 746 |
| environment | Environment manager | 413 |
| config | Configuration classes | 391 |
| auth | Authentication | 381 |
| services | Service interfaces | 312 |
| apps | App config | 178 |
| shared | Shared models | 80 |
| executor | Base executor | 28 |
