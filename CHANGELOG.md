# Changelog

All notable changes to the Agent Operating System (AOS) will be documented in this file.

## [Unreleased]

### Documentation
- Consolidated duplicate documentation files
- Created unified self-learning documentation
- Merged LORAX documentation into single comprehensive guide
- Unified refactoring and migration guides
- Added code organization documentation

## [2.0.0] - 2025-10-02

### Added

#### Refactored Agent Classes
- New `BaseAgentNew` class with enhanced lifecycle management
- New `LeadershipAgentNew` class with improved decision-making patterns
- `UnifiedAgentManager` for centralized agent lifecycle management
- Comprehensive service interfaces for storage, messaging, workflow, and auth

#### Azure Foundry Integration
- Native support for Microsoft Azure Foundry Agent Service
- Llama 3.3 70B integration as core reasoning engine
- Stateful thread management
- Entra Agent ID integration
- Foundry Tools support

#### Perpetual Agents Feature
- `PerpetualAgent` class for event-driven, always-on agents
- Automatic sleep/wake cycles for resource efficiency
- Persistent state across all interactions
- Event subscription system

#### Testing Infrastructure (P2)
- Contract tests with schema validation
- Integration test framework with scenario management
- Chaos testing for resilience verification
- End-to-end test runner

#### LoRAx Integration
- Multi-adapter serving with shared base model
- Cost reduction: 90-95% for multi-agent ML workloads
- Dynamic adapter loading and caching
- Batch inference optimization
- Integration with orchestration layer

### Changed
- Migrated all code from `old/` directory to proper `src/` structure
- Enhanced ML pipeline with LoRA support
- Improved MCP client management
- Refactored orchestration engine
- Updated messaging with reliability patterns

### Maintained for Backward Compatibility
- Original `BaseAgent`, `Agent`, `StatefulAgent` classes
- Original `LeadershipAgent` implementation
- Existing service interfaces
- Legacy audit trail implementation

## [1.0.0] - Earlier

### Core Features
- Multi-agent orchestration system
- Agent-to-Agent (A2A) communication
- Self-learning with GitHub integration
- MCP (Model Context Protocol) client support
- Azure Function orchestration
- ML pipeline with Azure ML integration
- Autonomous boardroom pattern
- Purpose-driven agents

## Feature Implementation Summaries

### Foundry Integration (October 2025)
Comprehensive integration with Azure Foundry Agent Service providing enterprise-grade AI capabilities:
- Llama 3.3 70B as default reasoning engine
- Stateful conversation threads
- Advanced metrics and health monitoring
- Model orchestration integration

See [FOUNDRY_INTEGRATION_SUMMARY.md](FOUNDRY_INTEGRATION_SUMMARY.md) for details.

### Perpetual Agents (October 2025)
Implementation of AOS's core USP - perpetual persistence:
- Event-driven awakening mechanism
- Resource-efficient sleep/wake cycles
- Continuous state building over agent lifetime
- Distinction from traditional task-based frameworks

See [PERPETUAL_AGENTS_SUMMARY.md](PERPETUAL_AGENTS_SUMMARY.md) for details.

### Testing Infrastructure (October 2025)
Comprehensive P2 and P3 feature implementations:
- Contract, integration, and chaos testing
- Audit logging and security testing
- Multi-agent coordination testing
- Performance monitoring

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for details.

---

## Migration Guides

- [MIGRATION.md](MIGRATION.md) - Agent Framework upgrade guide
- [REFACTORING.md](REFACTORING.md) - AOS v2.0.0 refactoring guide
- [BREAKING_CHANGES.md](BREAKING_CHANGES.md) - Breaking changes log

## Documentation

- [README.md](README.md) - Main documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
