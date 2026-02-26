# aos-kernel

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/aos-kernel/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/aos-kernel/actions/workflows/ci.yml)

**The OS kernel for the Agent Operating System (AOS).**

`aos-kernel` provides the core runtime services: orchestration engine, messaging bus,
storage layer, authentication, configuration, monitoring, observability, reliability,
governance, extensibility, and the MCP (Model Context Protocol) server.

## Installation

```bash
pip install aos-kernel
pip install "aos-kernel[azure]"   # With Azure backends
pip install "aos-kernel[full]"    # Everything
```

## Architecture

```
aos-kernel
├── orchestration/    # Orchestration engine (agent_framework integration)
├── messaging/        # Inter-agent messaging bus
├── storage/          # Pluggable storage layer (Azure Blob/Table/Queue)
├── auth/             # Authentication & authorization
├── config/           # Configuration management
├── monitoring/       # Health monitoring & metrics
├── observability/    # OpenTelemetry tracing & logging
├── reliability/      # Circuit breakers, retries, fault tolerance
├── governance/       # Compliance, audit, policy enforcement
├── extensibility/    # Plugin system & extension points
├── mcp/              # Model Context Protocol server
├── testing/          # Test utilities & framework
├── environment/      # Environment detection & management
├── services/         # Shared service interfaces
├── shared/           # Shared utilities
├── apps/             # Application entry points
└── executor/         # Task executor
```

## Related Packages

| Package | Description |
|---|---|
| [`purpose-driven-agent`](https://github.com/ASISaga/purpose-driven-agent) | The fundamental agent building block |
| [`aos-intelligence`](https://github.com/ASISaga/aos-intelligence) | ML pipelines, LoRA, DPO, self-learning |
| [`aos-deployment`](https://github.com/ASISaga/aos-deployment) | Infrastructure deployment (Bicep + orchestrator) |
| [`aos-function-app`](https://github.com/ASISaga/aos-function-app) | Main Azure Functions host |

## Documentation

- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Contributing](docs/development/CONTRIBUTING.md)
- [API Reference](docs/reference/system-apis.md)

## License

[MIT License](LICENSE)
