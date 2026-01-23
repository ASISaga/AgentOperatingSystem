# Agent Operating System - Copilot Agent Onboarding Guide

Welcome to the Agent Operating System (AOS) repository! This guide will help you quickly understand and work effectively with this codebase.

## 🎯 What is This Repository?

**Agent Operating System (AOS)** is a production-ready operating system for AI agents, built on Microsoft Azure and the Microsoft Agent Framework. The key architectural difference from traditional AI orchestration frameworks is **PERSISTENCE** - agents are perpetual entities that run indefinitely, not temporary task-based sessions.

### Core Concept: Perpetual vs Task-Based

- Traditional frameworks: Temporary sessions that start, execute, and terminate
- AOS: Perpetual agents that register once and run indefinitely, awakening on events
- State persists across the agent's entire lifetime via ContextMCPServer

## 📚 Instruction Files

This repository includes specialized instruction files to help you navigate different aspects of the codebase:

- **[agents.instructions.md](agents.instructions.md)** - Agent patterns, inheritance hierarchy, PurposeDrivenAgent, LeadershipAgent, CMOAgent
- **[architecture.instructions.md](architecture.instructions.md)** - Repository structure, technology stack, Azure integration, MCP
- **[development.instructions.md](development.instructions.md)** - Development workflow, testing, best practices, FAQ
- **[python.instructions.md](python.instructions.md)** - Python-specific coding guidelines (to be completed)
- **[documents.instructions.md](documents.instructions.md)** - Documentation standards (to be completed)

## �� Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[full]"  # Install with all optional dependencies
```

### Basic Usage

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent

# Create a purpose-driven agent
agent = PurposeDrivenAgent(
    agent_id="ceo",
    purpose="Strategic oversight and company growth",
    purpose_scope="Strategic planning, major decisions",
    success_criteria=["Revenue growth", "Team expansion"],
    adapter_name="ceo"  # Maps to LoRA adapter for domain knowledge
)

# Initialize and start
await agent.initialize()
await agent.start()
# Agent now runs perpetually, working toward its purpose
```

### Running Tests

```bash
pytest tests/  # Run all tests
pytest tests/test_perpetual_agents.py  # Run specific test file
```

## 🔑 Key Concepts

### 1. Perpetual Agents

Agents in AOS run indefinitely, not as one-off tasks. They register once and run forever, awakening on events.

### 2. Purpose-Driven Agents

The fundamental building block, combining perpetual operation with purpose alignment. PurposeDrivenAgent maps purposes to LoRA adapters for domain expertise.

### 3. Agent Hierarchy

```
BaseAgent
└── PerpetualAgent (runs indefinitely)
    └── PurposeDrivenAgent (maps purposes to LoRA adapters)
        └── LeadershipAgent (adds Leadership purpose)
            └── CMOAgent (adds Marketing + Leadership purposes)
```

### 4. Architecture Components

- **LoRA Adapters**: Provide domain-specific knowledge (language, vocabulary, concepts, and agent persona)
- **Core Purposes**: Added to the primary LLM context to guide agent behavior
- **MCP**: Provides context management, domain-specific tools, and access to external software

## 📖 Documentation

- **Main README**: [README.md](../../README.md) - Project overview
- **Architecture**: [docs/architecture/ARCHITECTURE.md](../../docs/architecture/ARCHITECTURE.md)
- **Contributing**: [docs/development/CONTRIBUTING.md](../../docs/development/CONTRIBUTING.md)
- **Examples**: [examples/](../../examples/)

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **Platform**: Microsoft Azure (Functions, Service Bus, Storage)
- **Framework**: Microsoft Agent Framework
- **Async**: Asyncio for concurrent operations
- **Testing**: pytest with pytest-asyncio

## 💡 Important Notes

- **Async/Await Everywhere**: Most AOS code is asynchronous
- **State is Persistent**: Agents maintain state across their lifetime
- **Azure Integration**: Many features require Azure credentials
- **Perpetual Architecture**: Think in terms of persistent processes, not request-response

## ❓ Need Help?

1. Check the specialized instruction files above
2. Review examples in `examples/`
3. Read tests in `tests/` for usage patterns
4. Consult the main documentation in `docs/`

---

**Remember**: This is an operating system for AI agents, not a traditional application. Think in terms of persistent processes, event-driven architecture, and long-running state.
