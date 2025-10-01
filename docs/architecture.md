# Architecture

This document describes the architecture of the SelfLearningAgent system.

## Core Components

- **BaseOrchestrator**: Unified foundation for all orchestrator implementations, with built-in A2A communication, configuration, logging, and Azure blob storage integration.
- **Orchestrator Implementations**: Includes Azure Function Orchestrator, Enhanced MCP Orchestrator (self-learning, GitHub issue creation), Multi-Agent Orchestrator (A2A), Generic Orchestrator (FastAPI, LoRA, mentor mode), and Self-Learning Orchestrator (MCP server integration).
- **Agent-to-Agent Communication**: Message queuing/routing, agent registration/discovery, async message processing, health/status reporting.
- **MCP Client**: Unified client for domain-specific and GitHub MCP servers.
- **Pipeline**: ML training pipeline for Azure ML and local execution.
- **Azure Integration**: Python-based resource management, deployment, and storage.

## Directory Structure

```
SelfLearningAgent/
├── src/
│   ├── core/
│   ├── Orchestrator/
│   ├── Agents/
│   ├── Pipeline/
├── config/
├── validation_test.py
└── README.md
```

See other docs for details on each component.