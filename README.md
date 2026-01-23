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

### LLM-First YAML Configuration

**PurposeDrivenAgents are LLM-first agents** configured via YAML with verbose purpose descriptions. The agent's behavior emerges from LLM reasoning over these purposes, not hard-coded logic.

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent, CMOAgent

# Load LLM-first agent from YAML with verbose purposes
ceo_agent = PurposeDrivenAgent.from_yaml("config/agents/ceo_agent.yaml")
await ceo_agent.initialize()  # Verbose purposes converted to LLM context
await ceo_agent.start()       # Agent operates via LLM reasoning

# Multi-purpose agent (CMO with marketing + leadership purposes)
cmo_agent = CMOAgent.from_yaml("config/agents/cmo_agent.yaml")
await cmo_agent.initialize()

# Execute with specific purpose/adapter - LLM reasons over purpose context
await cmo_agent.execute_with_purpose(task, purpose_type="marketing")
await cmo_agent.execute_with_purpose(task, purpose_type="leadership")
```

#### Verbose Purpose Example in YAML

Purposes should be comprehensive, multi-line descriptions that provide rich context for the LLM:

```yaml
agent_id: ceo
agent_type: purpose_driven

purposes:
  - name: strategic_oversight
    description: |
      You are the Chief Executive Officer (CEO), responsible for overall 
      strategic direction and operational success.
      
      Your Purpose:
      Provide visionary leadership and strategic oversight to drive sustainable 
      company growth while balancing stakeholder interests...
      
      Core Responsibilities:
      - Set and communicate company vision and strategic objectives
      - Make high-impact decisions on direction and investments
      - Ensure alignment across all departments
      - Manage board, investor, and stakeholder relationships
      ...
      
      Decision-Making Framework:
      - Balance short-term performance with long-term sustainability
      - Consider impact on all stakeholders
      - Base decisions on data and strategic foresight
      ...
    adapter_name: ceo  # LoRA adapter receives verbose purpose as LLM context


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

### LLM-First Agent Architecture

**PurposeDrivenAgents are LLM-first agents**, not conventional logic-based agents. They operate through LLM reasoning over verbose purpose descriptions, not hard-coded decision logic.

#### Key Principles:

1. **Verbose Purposes as LLM Context**
   - Purpose descriptions are comprehensive, multi-line narratives
   - Converted to LLM context and passed to LoRA adapters
   - LLM reasons over this context to guide all behavior

2. **LoRA Adapters** 
   - Receive verbose purpose descriptions as LLM context
   - Provide domain-specific knowledge, language, and persona
   - Enable LLM to reason within domain expertise

3. **Configuration-Driven**
   - Agents created from YAML (not code)
   - No backward compatibility with code-based initialization
   - Purpose descriptions are the primary configuration

#### Verbose Purpose Example

```yaml
agent_id: ceo
purposes:
  - name: strategic_oversight
    description: |
      You are the Chief Executive Officer (CEO), responsible for...
      
      Your Purpose:
      Provide visionary leadership and strategic oversight to drive 
      sustainable company growth while balancing stakeholder interests...
      
      Core Responsibilities:
      - Set and communicate company vision
      - Make high-impact strategic decisions
      - Ensure cross-departmental alignment
      - Manage board and investor relationships
      
      Decision-Making Framework:
      - Balance short-term vs long-term impact
      - Consider all stakeholder perspectives
      - Base decisions on data and foresight
      
      Success Metrics:
      - Revenue and profitability growth
      - Market share and competitive position
      - Employee and customer satisfaction
      ...
    adapter_name: ceo  # Receives verbose purpose as LLM context
```

### Lean Agent Architecture

**PurposeDrivenAgent is the fundamental LLM-first agent class** containing all core functionality:
- Converts verbose purposes to LLM context
- Multi-purpose support and adapter switching
- YAML configuration loading
- Purpose-to-adapter mapping
- Goal tracking, metrics, decision infrastructure

**Derived agents** (LeadershipAgent, CMOAgent) are lean wrappers (~60-150 lines) that:
- Provide domain-specific defaults only
- Add domain-specific methods when needed (minimal)
- Are YAML-configured with verbose purposes
- Inherit all LLM-first core functionality

This architecture ensures agents are LLM-first, configuration-driven, and maintainable.

📖 **[Agent Configuration Schema](docs/agent-configuration-schema.md)** - Complete YAML schema reference  
📖 **[Example Configurations](config/agents/)** - CEO, CMO, Leadership with verbose purposes

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
