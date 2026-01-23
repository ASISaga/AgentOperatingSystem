# Architecture and Technology Stack

## Core Concept: Perpetual vs Task-Based

**Agent Operating System (AOS)** is a production-ready operating system for AI agents, built on Microsoft Azure and the Microsoft Agent Framework. The key architectural difference from traditional AI orchestration frameworks is **PERSISTENCE** - agents are perpetual entities that run indefinitely, not temporary task-based sessions.

- **Traditional frameworks**: Temporary sessions that start, execute, and terminate
- **AOS**: Perpetual agents that register once and run indefinitely, awakening on events
- **State persists** across the agent's entire lifetime via ContextMCPServer

## Repository Structure

```
AgentOperatingSystem/
├── src/AgentOperatingSystem/     # Main source code
│   ├── agents/                   # Agent implementations (PerpetualAgent, PurposeDrivenAgent)
│   ├── orchestration/            # Orchestration engine (kernel)
│   ├── messaging/                # Inter-agent communication (message bus)
│   ├── storage/                  # Storage services (Azure Blob, Table, Queue)
│   ├── auth/                     # Authentication & authorization
│   ├── mcp/                      # Model Context Protocol integration
│   ├── ml/                       # Machine learning pipeline
│   ├── governance/               # Compliance and audit
│   ├── reliability/              # Fault tolerance patterns
│   ├── observability/            # Monitoring and tracing
│   └── ...                       # Other system services
├── tests/                        # Test files
├── azure_functions/              # Azure Functions specific code
├── function_app.py               # Main Azure Functions entry point
├── examples/                     # Usage examples
├── docs/                         # Detailed documentation
└── pyproject.toml               # Project configuration and dependencies
```

## Technology Stack

- **Language**: Python 3.8+
- **Platform**: Microsoft Azure (Functions, Service Bus, Storage, etc.)
- **Framework**: Microsoft Agent Framework
- **Async**: Asyncio for concurrent operations
- **Testing**: pytest with pytest-asyncio
- **Dependencies**: See pyproject.toml

## Azure Integration

AOS heavily uses Azure services:

- **Azure Functions** for deployment
- **Azure Service Bus** for messaging
- **Azure Storage** (Blob, Table, Queue) for persistence
- **Azure Key Vault** for secrets

## MCP (Model Context Protocol)

AOS implements MCP for tool and resource access:

- `src/AgentOperatingSystem/mcp/` - MCP implementation
- **ContextMCPServer** for state preservation
- Domain-specific tools and access to contemporary software systems

## Important Files to Know

### Core Entry Points

- `function_app.py` - Azure Functions application entry point
- `src/AgentOperatingSystem/agent_operating_system.py` - Main AOS class
- `src/AgentOperatingSystem/__init__.py` - Package exports

### Key Documentation

- `README.md` - Main project README with overview
- `docs/architecture/ARCHITECTURE.md` - Detailed architecture documentation
- `docs/development/CONTRIBUTING.md` - Contribution guidelines
- `docs/` - Additional technical documentation

### Configuration

- `pyproject.toml` - Python project configuration and dependencies
- `host.json` - Azure Functions host configuration
- `local.settings.json` - Local development settings (not in git)
- `config/` - Configuration files

### Examples

- `examples/perpetual_agents_example.py` - Perpetual agents usage
- `examples/foundry_agent_service_example.py` - Foundry integration
- `examples/platform_integration_example.py` - Platform examples

## Key Resources

- **Repository**: https://github.com/ASISaga/AgentOperatingSystem
- **Issues**: https://github.com/ASISaga/AgentOperatingSystem/issues
- **Microsoft Agent Framework**: https://github.com/microsoft/agent-framework
- **Azure Functions**: https://learn.microsoft.com/azure/azure-functions/
- **MCP Protocol**: https://modelcontextprotocol.io/
