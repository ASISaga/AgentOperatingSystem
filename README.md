# Agent Operating System (AOS)

**Version:** 3.0.0  
**Status:** Production Ready  
**Platform:** Microsoft Azure + Microsoft Agent Framework

> *A complete, production-grade operating system for AI agents built on Microsoft Azure. Just as Linux, Windows, or macOS provide foundational infrastructure for applications, AOS provides the kernel, system services, runtime environment, and application framework for autonomous AI agents.*

---

## 🎯 What Makes AOS Different

**The fundamental difference is PERSISTENCE.**

### Traditional AI Frameworks
- ▶️ Agents created for specific tasks
- ⏹️ Agents terminate after completion
- 💾 State is lost between sessions
- 🔄 Manual restart required for each task

### Agent Operating System
- 🔄 Agents registered once, run perpetually
- 😴 Agents sleep when idle, awaken on events
- 💾 State persists forever via ContextMCPServer
- ⚡ Event-driven, reactive behavior
- 🎯 Purpose-driven operation (not just task-based)

| Aspect | Traditional | AOS |
|--------|------------|-----|
| **Lifecycle** | Temporary session | Permanent entity |
| **Activation** | Manual start/stop | Event-driven awakening |
| **State** | Lost after completion | Persists indefinitely |
| **Context** | Current task only | Full history preserved |
| **Paradigm** | Script execution | Operating system |

---

## 🚀 Quick Start

### Installation

```bash
# Install from GitHub
pip install git+https://github.com/ASISaga/AgentOperatingSystem.git

# Or install with all optional dependencies
pip install git+https://github.com/ASISaga/AgentOperatingSystem.git[all]
```

### Basic Usage

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent
from AgentOperatingSystem.mcp import ContextMCPServer

# Create a purpose-driven perpetual agent
agent = PurposeDrivenAgent(
    agent_id="ceo",
    purpose="Strategic oversight and company growth",
    purpose_scope="Strategic planning, major decisions",
    success_criteria=["Revenue growth", "Team expansion"],
    adapter_name="ceo"
)

# Initialize and start (runs perpetually)
await agent.initialize()
await agent.start()

# Purpose-driven operations
alignment = await agent.evaluate_purpose_alignment(action)
decision = await agent.make_purpose_driven_decision(context)
goal_id = await agent.add_goal("Increase revenue by 50%")
```

**[📖 Full Quick Start Guide →](docs/quickstart.md)**

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                           │
│         Business Applications, Domain-Specific Agents          │
├────────────────────────────────────────────────────────────────┤
│                  AGENT OPERATING SYSTEM (AOS)                  │
│                   System Services & Infrastructure             │
│  ┌──────────────── CORE KERNEL SERVICES ──────────────────┐   │
│  │  • Orchestration Engine    • Agent Lifecycle Manager   │   │
│  │  • Message Bus             • State Machine Manager     │   │
│  │  • Resource Scheduler      • Policy Enforcement        │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌────────────── SYSTEM SERVICE LAYER ─────────────────────┐   │
│  │  Storage  Auth  ML Pipeline  MCP Integration  Learning │   │
│  │  Messaging  Monitoring  Governance  Observability      │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌──────────────── HARDWARE ABSTRACTION ───────────────────┐   │
│  │  Azure Service Bus  Storage  ML  Functions  Monitor    │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
                              ↕
┌────────────────────────────────────────────────────────────────┐
│                      MICROSOFT AZURE PLATFORM                  │
└────────────────────────────────────────────────────────────────┘
```

**[📐 Detailed Architecture →](ARCHITECTURE.md)**

---

## ✨ Core Features

### 🤖 Purpose-Driven Perpetual Agents
- **PurposeDrivenAgent**: Fundamental building block of AOS
- Purpose alignment evaluation for all actions
- Persistent state via dedicated ContextMCPServers
- Event-driven awakening and lifecycle management

### 💾 Unified Infrastructure
- **Storage Layer**: Azure Tables, Blobs, Queues
- **Authentication**: Multi-provider with Azure B2C, OAuth, JWT
- **ML Pipeline**: LoRA fine-tuning, LoRAx multi-adapter serving
- **MCP Integration**: Model Context Protocol client/server support
- **Message Bus**: Azure Service Bus for A2A communication

### 🔧 System Services
- **Orchestration**: Multi-agent coordination and workflows
- **Governance**: Audit trails, policy enforcement, compliance
- **Observability**: Distributed tracing, metrics, logging
- **Learning**: Self-learning system with RAG and knowledge management
- **Reliability**: Circuit breakers, retry policies, graceful degradation

### 📊 Production-Ready
- **Enterprise Scale**: Horizontal scaling, distributed architecture
- **Security**: Encryption, RBAC, Key Vault integration
- **Cost Optimized**: LoRAx serving (90-95% reduction), inference caching
- **Observable**: OpenTelemetry integration, real-time monitoring

**[🎯 Complete Feature List →](features.md)**

---

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](docs/quickstart.md)** - Get up and running in minutes
- **[Installation](docs/quickstart.md#installation)** - Detailed installation instructions
- **[Configuration](docs/configuration.md)** - System configuration and setup

### Core Concepts
- **[Architecture Overview](ARCHITECTURE.md)** - System design and components
- **[Agent Development](docs/Implementation.md)** - Building agents on AOS
- **[Purpose-Driven Agents](PERPETUAL_AGENTS_SUMMARY.md)** - Understanding perpetual agents

### Features & Services
- **[ML Pipeline & LoRAx](docs/LORAX.md)** - Machine learning integration
- **[Azure Foundry Integration](docs/FOUNDRY_AGENT_SERVICE.md)** - Llama 3.3 70B support
- **[MCP Integration](docs/self_learning.md)** - Model Context Protocol
- **[Agent-to-Agent Communication](docs/a2a_communication.md)** - A2A messaging
- **[Self-Learning System](docs/self_learning.md)** - Automatic capability enhancement

### Advanced Topics
- **[Advanced Features](ADVANCED_FEATURES.md)** - Advanced capabilities
- **[Extensibility](docs/extensibility.md)** - Plugin framework and customization
- **[Performance & Scalability](ARCHITECTURE.md#scalability)** - Enterprise deployment
- **[Security & Compliance](ARCHITECTURE.md#security)** - Security best practices

### Reference
- **[API Reference](docs/rest_api.md)** - REST API documentation
- **[Code Organization](docs/CODE_ORGANIZATION.md)** - Repository structure
- **[Testing](docs/testing.md)** - Testing and validation
- **[Development Guide](docs/development.md)** - Contributing to AOS

### Migration & Changes
- **[Migration Guide](MIGRATION.md)** - Upgrading to v3.0.0
- **[Breaking Changes](BREAKING_CHANGES.md)** - v3.0.0 breaking changes
- **[Changelog](CHANGELOG.md)** - Version history
- **[Release Notes](RELEASE_NOTES.md)** - Latest releases

---

## 🚀 Production Deployment

### Azure Resources Required
- Azure Functions (serverless compute)
- Azure Service Bus (messaging)
- Azure Storage (blobs, tables, queues)
- Azure Key Vault (secrets management)
- Azure Monitor (observability)
- Azure ML (optional, for training)

### Infrastructure as Code

```bash
# Login to Azure
az login

# Deploy AOS infrastructure
az deployment group create \
  --resource-group aos-rg \
  --template-file infrastructure/azuredeploy.json \
  --parameters @infrastructure/parameters.json

# Configure environment
export AZURE_STORAGE_CONNECTION_STRING="..."
export AZURE_SERVICEBUS_CONNECTION_STRING="..."
```

**[📦 Complete Deployment Guide →](ARCHITECTURE.md#deployment-architecture)**

---

## 💡 Use Cases

- **Enterprise Automation**: Autonomous business process management
- **Multi-Agent Systems**: Coordinated teams of specialized agents
- **Continuous Learning**: Self-improving agent systems
- **Event-Driven Workflows**: Real-time responsive automation
- **Agent Marketplaces**: Plug-and-play agent ecosystems

**[📋 Detailed Use Cases →](features.md#use-cases)**

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Contribution Areas
- 🐛 Bug fixes and improvements
- 📚 Documentation enhancements
- ✨ New features and capabilities
- 🧪 Test coverage expansion
- 🔌 Plugins and extensions

**[📖 Contribution Guidelines →](CONTRIBUTING.md)**

---

## 🗺️ Roadmap

### Current Version: 3.0.0 (January 2026)
- ✅ Purpose-driven perpetual agents
- ✅ Unified MCP protocol/client
- ✅ LoRAx multi-adapter serving
- ✅ Azure Foundry integration
- ✅ Self-learning system
- ✅ Removed backward compatibility (v1.x, v2.x)

### Q1 2026: Intelligence Enhancement
- Advanced ML capabilities (federated learning, AutoML)
- Enhanced orchestration (dynamic workflows, predictive scheduling)
- Multi-modal AI integration

### Q2 2026: Resilience & Scale
- Adaptive resilience and self-healing
- Distributed storage mesh
- Enhanced multi-tier storage

### Q3-Q4 2026 & Beyond
- Next-gen observability with AI-powered anomaly detection
- Enterprise features (plugin marketplace, GraphQL API)
- Multi-cloud support (AWS, GCP)
- Zero-trust architecture
- Quantum computing preparation

**[🔮 Complete Roadmap →](README.md.backup#roadmap)**

---

## 📞 Support & Community

### Getting Help
- 📖 **[Documentation](docs/)** - Comprehensive guides and references
- 💬 **[Discussions](https://github.com/ASISaga/AgentOperatingSystem/discussions)** - Community Q&A
- 🐛 **[Issues](https://github.com/ASISaga/AgentOperatingSystem/issues)** - Bug reports and feature requests

### Stay Updated
- ⭐ **Star** this repository
- 👀 **Watch** for releases
- 🔔 **Subscribe** to notifications

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- **[Microsoft Agent Framework](https://github.com/microsoft/autogen)** - Core agent framework
- **[Microsoft Azure](https://azure.microsoft.com/)** - Cloud infrastructure
- **[OpenTelemetry](https://opentelemetry.io/)** - Observability standards
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Agent communication

Special thanks to all contributors and the open-source community.

---

<div align="center">

**[Documentation](docs/)** • **[Examples](examples/)** • **[Community](https://github.com/ASISaga/AgentOperatingSystem/discussions)**

Built with ❤️ by the ASISaga team

© 2026 ASISaga. All rights reserved.

</div>
