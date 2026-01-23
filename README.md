# Agent Operating System (AOS)
## A Complete Operating System for AI Agents

**Version:** 2025.1.2  
**Status:** Production Ready  
**Platform:** Microsoft Azure + Microsoft Agent Framework

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Azure](https://img.shields.io/badge/platform-Azure-blue.svg)](https://azure.microsoft.com/)

---

## 🎯 Overview

The **Agent Operating System (AOS)** is a complete, production-grade operating system designed from the ground up for AI agents. Just as Linux, Windows, or macOS provide foundational infrastructure for applications, AOS provides the **kernel, system services, runtime environment, and application framework** for autonomous AI agents.

### Key Differentiator: Perpetual Agents

**The key difference between AOS and traditional AI orchestration frameworks is PERSISTENCE.**

| Traditional (Task-Based) | AOS (Perpetual + Purpose-Driven) |
|-------------------------|----------------------------------|
| Temporary session | Permanent entity |
| Manual start/stop | Event-driven awakening |
| Lost after completion | Persists via ContextMCPServer indefinitely |
| Current task only | Full history via ContextMCPServer |
| Short-term tasks | Long-term assigned purpose |

📖 **[Learn more about Perpetual Agents](docs/overview/perpetual-agents.md)**

---

## 🚀 Quick Start

### Installation

```bash
pip install git+https://github.com/ASISaga/AgentOperatingSystem.git
```

### Basic Example - Code-Based Configuration

```python
from AgentOperatingSystem import AgentOperatingSystem
from AgentOperatingSystem.agents import PurposeDrivenAgent

# Create a purpose-driven perpetual agent
agent = PurposeDrivenAgent(
    agent_id="ceo",
    purpose="Strategic oversight and company growth",
    purpose_scope="Strategic planning, major decisions",
    adapter_name="ceo"
)

await agent.initialize()  # ContextMCPServer automatically created
await agent.start()       # Runs perpetually

# Purpose-driven operations
alignment = await agent.evaluate_purpose_alignment(action)
decision = await agent.make_purpose_driven_decision(context)
```

### YAML-Based Configuration (Recommended)

Agents can be configured using YAML files that define purposes, LoRA adapters, MCP tools, and capabilities:

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent, CMOAgent

# Load agent from YAML configuration
ceo_agent = PurposeDrivenAgent.from_yaml("config/agents/ceo_agent.yaml")
await ceo_agent.initialize()
await ceo_agent.start()

# Load multi-purpose agent (e.g., CMO with marketing + leadership)
cmo_agent = CMOAgent.from_yaml("config/agents/cmo_agent.yaml")
await cmo_agent.initialize()

# Execute tasks with specific purpose/adapter
await cmo_agent.execute_with_purpose(task, purpose_type="marketing")
await cmo_agent.execute_with_purpose(task, purpose_type="leadership")
```

#### Example agent.yaml Structure

```yaml
agent_id: cmo
agent_type: cmo

# Multiple purposes, each mapped to a LoRA adapter
purposes:
  - name: marketing
    description: "Marketing: Brand strategy and customer acquisition"
    adapter_name: marketing  # Maps to "marketing" LoRA adapter
    
  - name: leadership
    description: "Leadership: Strategic decision-making"
    adapter_name: leadership  # Maps to "leadership" LoRA adapter

# MCP tools required
mcp_tools:
  - server_name: "analytics"
    tool_name: "get_marketing_metrics"

# Agent capabilities
capabilities:
  - "Marketing strategy development"
  - "Brand management"
  - "Team leadership"
```

See [Agent Configuration Schema](docs/agent-configuration-schema.md) for complete details.

📖 **[Full Quick Start Guide](docs/getting-started/quickstart.md)**

---

## 🏗️ Architecture

AOS provides a complete operating system architecture:

```
┌────────────────────────────────────────────────────────────┐
│              APPLICATION LAYER (USER SPACE)                │
│        Business Applications, Domain-Specific Agents       │
└────────────────────────────────────────────────────────────┘
                    ↕ System Calls & APIs
┌────────────────────────────────────────────────────────────┐
│        AGENT OPERATING SYSTEM (AOS) - KERNEL               │
├────────────────────────────────────────────────────────────┤
│  Core Services: Orchestration • Lifecycle • Messaging     │
│  System Services: Storage • Auth • ML • MCP • Governance  │
│  Hardware Abstraction: Azure Services Integration         │
└────────────────────────────────────────────────────────────┘
                    ↕ Cloud APIs
┌────────────────────────────────────────────────────────────┐
│              MICROSOFT AZURE PLATFORM                      │
└────────────────────────────────────────────────────────────┘
```

📖 **[Architecture Documentation](docs/architecture/ARCHITECTURE.md)**  
📖 **[Vision & Principles](docs/overview/vision.md)**  
📖 **[Core Services](docs/overview/services.md)**

---

## ✨ Core Features

### 🔧 Operating System Services
- **Orchestration Engine** - Agent lifecycle management and workflow execution
- **Agent Lifecycle Manager** - Process management for agents
- **Message Bus** - Inter-agent communication (IPC for agents)
- **State Machine Manager** - Deterministic state transitions

### 💾 System Service Layer
- **Storage Service** - Unified storage abstraction (Blob, Table, Queue, Cosmos DB)
- **Authentication & Authorization** - Multi-provider auth and RBAC
- **ML Pipeline Service** - Azure ML integration with LoRA adapters
- **MCP Integration** - Model Context Protocol for tool access
- **Governance** - Compliance, audit logging, and policy enforcement
- **Observability** - Monitoring, tracing, and alerting
- **Knowledge Service** - RAG and information retrieval
- **Extensibility Framework** - Plugin system for extending AOS

📖 **[Complete Features List](docs/features/features-overview.md)**  
📖 **[Advanced Features](docs/features/advanced-features.md)**

---

## 🎯 Agent Configuration System

### YAML-Based Agent Definition

AOS introduces a **declarative agent configuration system** using `agent.yaml` files. Each agent defines:

- **Purposes** - Long-term objectives that guide agent behavior
- **LoRA Adapters** - Domain-specific knowledge mapped to each purpose  
- **MCP Tools** - Model Context Protocol tools for domain-specific capabilities
- **Capabilities** - List of agent capabilities and responsibilities

#### Purpose-to-Adapter Mapping

The key architectural concept is **mapping purposes to LoRA adapters**:

1. **LoRA Adapters** provide domain-specific knowledge (language, vocabulary, concepts, agent persona)
2. **Core Purposes** are added to the primary LLM context to guide behavior
3. **MCP Integration** provides context management and domain-specific tools

#### Single-Purpose Agent Example

```yaml
agent_id: ceo
purposes:
  - name: strategic_oversight
    description: "Strategic oversight and decision-making"
    adapter_name: ceo  # Maps to "ceo" LoRA adapter
    success_criteria:
      - "Achieve quarterly revenue targets"
      - "Maintain strategic alignment"
```

#### Multi-Purpose Agent Example

```yaml
agent_id: cmo
purposes:
  - name: marketing
    adapter_name: marketing  # Marketing domain knowledge
  - name: leadership  
    adapter_name: leadership  # Leadership domain knowledge
```

### Lean Agent Architecture

**PurposeDrivenAgent is the fundamental agent class** containing all core functionality:
- Multi-purpose support and adapter switching
- YAML configuration loading
- Purpose-to-adapter mapping
- Goal tracking, metrics, decision-making

**Derived agents** (LeadershipAgent, CMOAgent) are lean wrappers (~60-150 lines) that:
- Provide domain-specific defaults
- Add domain-specific methods only when needed
- Are primarily YAML-configured
- Inherit all core functionality

This architecture ensures derived agents are minimal and maintainable, with all repetitive logic in PurposeDrivenAgent.

📖 **[Agent Configuration Schema](docs/agent-configuration-schema.md)** - Complete YAML schema reference  
📖 **[Example Configurations](config/agents/)** - CEO, CMO, Leadership agent examples

---

## 🔌 Plug-and-Play Infrastructure

### RealmOfAgents - Configuration-Driven Agent Deployment

Deploy agents with **zero code** - just configuration:

```json
{
  "agent_id": "cfo",
  "purpose": "Financial oversight and strategic planning",
  "mcp_tools": [{"server_name": "erpnext", "tool_name": "get_financial_reports"}],
  "enabled": true
}
```

### MCPServers - Configuration-Driven MCP Server Deployment

Add MCP servers with **zero code** - just configuration:

```json
{
  "server_id": "github",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "enabled": true
}
```

📖 **[Azure Functions Infrastructure](docs/getting-started/azure-functions.md)**

---

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](docs/getting-started/quickstart.md)** - Get up and running quickly
- **[Installation Guide](docs/getting-started/installation.md)** - Detailed installation instructions
- **[Configuration Guide](docs/configuration.md)** - System configuration
- **[Deployment Guide](docs/getting-started/deployment.md)** - Production deployment

### Core Concepts
- **[Architecture Overview](docs/architecture/ARCHITECTURE.md)** - System architecture and design
- **[Vision & Why "Operating System"](docs/overview/vision.md)** - The OS for AI agents
- **[Core Principles](docs/overview/principles.md)** - Design principles and philosophy
- **[Perpetual vs Task-Based Agents](docs/overview/perpetual-agents.md)** - Key architectural difference
- **[Agent Configuration Schema](docs/agent-configuration-schema.md)** - YAML-based agent configuration
- **[Operating System Services](docs/overview/services.md)** - Core OS services

### Development & Integration
- **[System APIs Reference](docs/reference/system-apis.md)** - API documentation
- **[Development Guide](docs/development.md)** - Developer documentation
- **[Contributing Guidelines](docs/development/CONTRIBUTING.md)** - How to contribute
- **[Testing Guide](docs/testing.md)** - Testing infrastructure

### Technical Specifications
- **[LLM Architecture](docs/llm_architecture.md)** - Language model integration
- **[Agent-to-Agent Communication](docs/a2a_communication.md)** - A2A messaging
- **[Extensibility](docs/extensibility.md)** - Extending the system
- **[REST API](docs/rest_api.md)** - REST API documentation

### Release Information
- **[Changelog](docs/releases/CHANGELOG.md)** - Version history
- **[Release Notes](docs/releases/RELEASE_NOTES.md)** - Release announcements
- **[Breaking Changes](docs/releases/BREAKING_CHANGES.md)** - Breaking changes by version
- **[Migration Guide](docs/development/MIGRATION.md)** - Migration from older versions

📖 **[Complete Documentation Index](docs/README.md)**

---

## 🛠️ Development

### Building a Custom Agent

```python
from AgentOperatingSystem.agents import LeadershipAgent

class CFOAgent(LeadershipAgent):
    def __init__(self):
        super().__init__(agent_id="cfo", name="CFO", role="CFO")
    
    async def make_decision(self, context):
        # Use AOS system services
        precedents = await self.knowledge.find_similar(context)
        risks = await self.governance.assess_risks(context)
        
        # Make decision
        decision = await self.analyze(context, precedents, risks)
        
        # Audit and broadcast
        await self.governance.audit(decision)
        await self.messaging.broadcast("decision_made", decision)
        
        return decision
```

📖 **[Development Guide](docs/development.md)**  
📖 **[Contributing Guidelines](docs/development/CONTRIBUTING.md)**

---

## 🔐 Security & Compliance

- Multi-provider authentication (Azure B2C, OAuth, JWT)
- Role-based access control (RBAC)
- Encrypted storage and secure communication
- Tamper-evident audit logging
- Policy enforcement and compliance tracking

📖 **[Security Documentation](docs/overview/services.md#authentication--authorization)**

---

## 📊 Production Ready

### Performance & Scale
- Built for enterprise scale
- Optimized for cost efficiency
- Auto-scaling and redundancy
- Circuit breakers and retry logic

### Monitoring & Observability
- Distributed tracing
- Real-time metrics and alerting
- Structured logging
- Azure Application Insights integration

📖 **[Deployment Guide](docs/getting-started/deployment.md)**

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guidelines](docs/development/CONTRIBUTING.md) for details.

### Contribution Areas
- Core infrastructure improvements
- New service implementations
- Documentation enhancements
- Test coverage expansion
- Bug fixes and performance optimization

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Acknowledgments

Built with ❤️ using Microsoft Azure, Microsoft Agent Framework, and the Model Context Protocol (MCP).

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/ASISaga/AgentOperatingSystem/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ASISaga/AgentOperatingSystem/discussions)

---

**Ready to build the next generation of AI agents?** [Get Started](docs/getting-started/quickstart.md) →
