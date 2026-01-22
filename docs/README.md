# Agent Operating System (AOS) - Documentation

Welcome to the comprehensive documentation for the Agent Operating System. This directory contains all the guides, references, and resources you need to work with AOS.

---

## 📖 Documentation Index

### Getting Started
- **[Quick Start Guide](quickstart.md)** - Get up and running in minutes
- **[Installation](quickstart.md#installation)** - Detailed installation instructions
- **[Configuration](configuration.md)** - System configuration and setup

### Core Concepts
- **[Architecture Overview](../ARCHITECTURE.md)** - System design and components
- **[Agent Implementation](Implementation.md)** - Building agents on AOS
- **[Purpose-Driven Agents](../PERPETUAL_AGENTS_SUMMARY.md)** - Understanding perpetual agents
- **[Code Organization](CODE_ORGANIZATION.md)** - Repository structure (v3.0.0)

### Platform Features

#### Infrastructure & Services
- **[Deployment Guide](deployment.md)** - Deploy AOS to production on Azure
- **[Performance & Scalability](performance.md)** - Optimize for enterprise scale
- **[App Configuration](APP_CONFIGURATION.md)** - Plug-and-play app registry system

#### AI & Machine Learning
- **[ML Pipeline & LoRAx](LORAX.md)** - Machine learning integration and multi-adapter serving
- **[Azure Foundry Integration](FOUNDRY_AGENT_SERVICE.md)** - Llama 3.3 70B support
- **[DPO Training](DPO_README.md)** - Direct Preference Optimization for cost-effective RL
- **[LLM Architecture](llm_architecture.md)** - LLM, LoRA, and agent design

#### Communication & Integration
- **[MCP Integration](self_learning.md#mcp-integration)** - Model Context Protocol
- **[Agent-to-Agent Communication](a2a_communication.md)** - A2A messaging patterns
- **[REST API](rest_api.md)** - REST API for web clients

#### Intelligence & Learning
- **[Self-Learning System](self_learning.md)** - Automatic capability enhancement
- **[RealmOfAgents](RealmOfAgents.md)** - Interactive showcase platform

#### Advanced Features
- **[Enhanced Orchestration](ENHANCED_ORCHESTRATION_INTEGRATION.md)** - Advanced coordination
- **[Extensibility Framework](extensibility.md)** - Plugin system and customization

### Development & Testing
- **[Development Guide](development.md)** - Contributing to AOS
- **[Testing & Validation](testing.md)** - Testing strategies
- **[Testing Infrastructure](testing_infrastructure.md)** - Test framework setup

### Reference Documentation
- **[API Reference](rest_api.md)** - REST API documentation
- **[Feature Specifications](specifications/)** - Detailed feature specs

### Migration & Changes
- **[Migration Guide](../MIGRATION.md)** - Upgrading to v3.0.0
- **[Breaking Changes](../BREAKING_CHANGES.md)** - v3.0.0 breaking changes
- **[Changelog](../CHANGELOG.md)** - Version history
- **[Release Notes](../RELEASE_NOTES.md)** - Latest releases
- **[Refactoring Guide](../REFACTORING.md)** - Refactoring documentation
- **[Migration Status](MIGRATION_STATUS.md)** - SelfLearningAgent migration

### Implementation Summaries
- **[Implementation Summary](../IMPLEMENTATION_SUMMARY.md)** - Implementation details
- **[Integration Complete](INTEGRATION_COMPLETE.md)** - SelfLearningAgent integration
- **[Foundry Integration Summary](../FOUNDRY_INTEGRATION_SUMMARY.md)** - Foundry integration details
- **[Cleanup Summary](../CLEANUP_SUMMARY.md)** - v3.0.0 cleanup audit

---

## 🗂️ Documentation by Topic

### For New Users
Start here if you're new to AOS:
1. [Quick Start Guide](quickstart.md)
2. [Architecture Overview](../ARCHITECTURE.md)
3. [Basic Examples](quickstart.md#quick-start-examples)

### For Developers
Building agents and applications on AOS:
1. [Agent Implementation](Implementation.md)
2. [Development Guide](development.md)
3. [Extensibility Framework](extensibility.md)
4. [Testing Guide](testing.md)

### For DevOps Engineers
Deploying and operating AOS:
1. [Deployment Guide](deployment.md)
2. [Performance & Scalability](performance.md)
3. [Configuration](configuration.md)
4. [App Configuration](APP_CONFIGURATION.md)

### For AI/ML Engineers
Working with ML features:
1. [ML Pipeline & LoRAx](LORAX.md)
2. [Azure Foundry Integration](FOUNDRY_AGENT_SERVICE.md)
3. [DPO Training](DPO_README.md)
4. [LLM Architecture](llm_architecture.md)

### For System Architects
Understanding system design:
1. [Architecture Overview](../ARCHITECTURE.md)
2. [Enhanced Orchestration](ENHANCED_ORCHESTRATION_INTEGRATION.md)
3. [Code Organization](CODE_ORGANIZATION.md)
4. [Feature Specifications](specifications/)

---

## 📋 Quick Reference

### Key Concepts
- **Purpose-Driven Agents**: Fundamental building block, works against assigned purpose perpetually
- **Perpetual Agents**: Agents that run indefinitely, sleep when idle, awaken on events
- **ContextMCPServer**: Dedicated context preservation for each agent
- **LoRAx**: Multi-adapter serving for cost-efficient ML (90-95% savings)
- **Self-Learning**: Automatic capability gap detection and resolution

### Architecture Layers
1. **Application Layer**: Business applications and domain-specific agents
2. **System Services**: Storage, Auth, ML Pipeline, MCP, Learning, etc.
3. **Core Kernel**: Orchestration, Lifecycle, Message Bus, State Machine
4. **Hardware Abstraction**: Azure Service Bus, Storage, ML, Functions

### Core Services
- **Orchestration Engine**: Multi-agent coordination and workflows
- **Agent Lifecycle Manager**: Registration, initialization, perpetual operation
- **Message Bus**: Azure Service Bus for A2A communication
- **Storage Service**: Unified access to Azure Tables, Blobs, Queues
- **ML Pipeline Service**: LoRA training, LoRAx serving, inference caching
- **MCP Integration**: Model Context Protocol client/server
- **Governance Service**: Audit trails, policy enforcement, compliance
- **Observability Service**: Tracing, metrics, logging with OpenTelemetry
- **Learning Service**: Self-learning with RAG and knowledge management

---

## 🔍 Finding What You Need

### By Use Case

**"I want to build my first agent"**
→ [Quick Start Guide](quickstart.md) → [Agent Implementation](Implementation.md)

**"I need to deploy AOS to production"**
→ [Deployment Guide](deployment.md) → [Performance Guide](performance.md)

**"I want to integrate ML models"**
→ [ML Pipeline & LoRAx](LORAX.md) → [Azure Foundry](FOUNDRY_AGENT_SERVICE.md)

**"I need to scale to enterprise workloads"**
→ [Performance & Scalability](performance.md) → [Architecture](../ARCHITECTURE.md)

**"I want to enable self-learning capabilities"**
→ [Self-Learning System](self_learning.md) → [MCP Integration](self_learning.md#mcp-integration)

**"I'm upgrading from v2.x to v3.0"**
→ [Migration Guide](../MIGRATION.md) → [Breaking Changes](../BREAKING_CHANGES.md)

---

## 📚 Additional Resources

### Community & Support
- **[GitHub Discussions](https://github.com/ASISaga/AgentOperatingSystem/discussions)** - Ask questions, share ideas
- **[GitHub Issues](https://github.com/ASISaga/AgentOperatingSystem/issues)** - Report bugs, request features
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute
- **[Code of Conduct](../CODE_OF_CONDUCT.md)** - Community guidelines

### External Resources
- **[Microsoft Agent Framework](https://github.com/microsoft/autogen)** - Core agent framework
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - MCP documentation
- **[Azure Documentation](https://docs.microsoft.com/azure/)** - Azure platform docs
- **[OpenTelemetry](https://opentelemetry.io/)** - Observability standards

---

## 🚀 Quick Links

| Topic | Link |
|-------|------|
| Quick Start | [quickstart.md](quickstart.md) |
| Architecture | [../ARCHITECTURE.md](../ARCHITECTURE.md) |
| Deployment | [deployment.md](deployment.md) |
| Performance | [performance.md](performance.md) |
| ML Pipeline | [LORAX.md](LORAX.md) |
| Self-Learning | [self_learning.md](self_learning.md) |
| Testing | [testing.md](testing.md) |
| API Reference | [rest_api.md](rest_api.md) |
| Migration | [../MIGRATION.md](../MIGRATION.md) |
| Contributing | [../CONTRIBUTING.md](../CONTRIBUTING.md) |

---

## 📝 Documentation Standards

All documentation in this directory follows these standards:
- Clear, concise language
- Code examples with explanations
- Cross-references to related topics
- Version-specific information clearly marked
- Maintained alongside code changes

**Found an issue?** Please [open an issue](https://github.com/ASISaga/AgentOperatingSystem/issues) or submit a pull request.

---

<div align="center">

**[Back to Main README](../README.md)** • **[Examples](../examples/)** • **[Community](https://github.com/ASISaga/AgentOperatingSystem/discussions)**

</div>
