# SelfLearningAgent - Consolidated Architecture

## Overview

This repository contains a **consolidated multi-agent orchestration system** that combines multiple agent frameworks with **Agent-to-Agent (A2A) communication** capabilities. The system supports various orchestrator types while maintaining a unified foundation for collaboration and self-learning.

## 🧠 SelfLearningAgent Modular Architecture

The `SelfLearningAgent` is now fully modular, split into the following core components:

- `KnowledgeBaseManager`: Loads and manages domain knowledge, contexts, and directives.
- `VectorDBManager`: Handles vector database (RAG) initialization and queries.
- `MCPClientManager`: Manages MCP client connections for each domain.
- `SemanticKernelManager`: Integrates with Semantic Kernel for advanced AI responses.
- The main `SelfLearningAgent` class orchestrates all managers and provides:
  - User request handling
  - Context retrieval and RAG
  - A2A (agent-to-agent) messaging
  - Conversation tracking and rating
  - Status and cleanup

### Example Usage

```python
from src.self_learning_agent.self_learning_agent import SelfLearningAgent

agent = SelfLearningAgent()
await agent.handle_user_request("How do I improve sales?", domain="sales")
```

### Project Structure

- `src/self_learning_agent/knowledge_base_manager.py`
- `src/self_learning_agent/vector_db_manager.py`
- `src/self_learning_agent/mcp_client_manager.py`
- `src/self_learning_agent/semantic_kernel_manager.py`
- `src/self_learning_agent/self_learning_agent.py`

All features from the original monolithic agent are preserved and now organized for clarity, extensibility, and maintainability.

## 🏗️ Architecture

### Core Components

1. **BaseOrchestrator** (`src/core/base_orchestrator.py`)
   - Unified foundation for all orchestrator implementations
   - Built-in A2A communication framework
   - Consistent configuration and logging management
   - Azure blob storage integration

2. **Orchestrator Implementations**
   - **Azure Function Orchestrator** - Serverless execution with Werner Erhard-style context
   - **Enhanced MCP Orchestrator** - Self-learning with GitHub issue creation  
   - **Multi-Agent Orchestrator** - Concurrent agent coordination with A2A
   - **Generic Orchestrator** - FastAPI-based with LoRA adapters and mentor mode
   - **Self-Learning Orchestrator** - MCP server integration with capability gap handling

3. **Agent-to-Agent Communication**
   - Message queuing and routing system
   - Agent registration and discovery
   - Asynchronous message processing
   - Health monitoring and status reporting

## 🚀 Quick Start

### Basic Usage

```python

from src.orchestrator import orchestrator

# Initialize orchestrator (modular, all features)
await orchestrator.initialize()

# Handle a request
request = {
    "domain": "leadership",
    "message": "How to motivate teams during challenging times?",
    "conversationId": "session-123"
}

response = await orchestrator.handle_request(request)
print(f"Response: {response}")
```

### A2A Communication Example

```python

# Register agents for collaboration
sales_agent = SalesAgent()
leadership_agent = LeadershipAgent()

await orchestrator.register_domain_agent("sales", sales_agent)
await orchestrator.register_domain_agent("leadership", leadership_agent)

# Send message between agents
message = {
    "type": "collaboration_request",
    "content": "Need leadership strategy for Q4 sales targets",
    "priority": "high"
}

result = await orchestrator.send_agent_message(
    "sales_agent", "leadership_agent", message
)

# Process pending messages
await orchestrator.process_agent_messages()
```

### Self-Learning with GitHub Integration

```python
# Configure self-learning orchestrator
domain_config = {
    "erp": {"uri": "wss://erp-mcp.example.com", "api_key": "key123"},
    "crm": {"uri": "wss://crm-mcp.example.com", "api_key": "key456"}
}

github_config = {
    "uri": "wss://github-mcp-server.example.com",
    "api_key": "github_token"
}

self_learning = SelfLearningOrchestrator(domain_config, github_config)
await self_learning.initialize()

# Execute business process - creates GitHub issue if capability missing
result = await self_learning.execute_business_process(
    domain="erp",
    function_name="create_sales_order", 
    parameters={"customer": "ACME Corp", "amount": 10000}
)
```

## ⚙️ Configuration

### Consolidated Configuration (`config/consolidated_config.json`)

```json
{
    "orchestrator": {
        "type": "consolidated",
        "version": "1.0.0"
    },
    "azure_function": {
        "ml_endpoint_url": "${MLENDPOINTURL}",
        "storage_connection": "${AzureWebJobsStorage}"
    },
    "self_learning": {
        "github_mcp": {
            "uri": "${GITHUB_MCP_URI}",
            "api_key": "${GITHUB_MCP_APIKEY}"
        },
        "domain_mcp_servers": {
            "erp": {"uri": "${ERP_MCP_URI}", "api_key": "${ERP_MCP_APIKEY}"},
            "crm": {"uri": "${CRM_MCP_URI}", "api_key": "${CRM_MCP_APIKEY}"}
        }
    },
    "a2a_communication": {
        "enabled": true,
        "message_queue_size": 1000,
        "message_timeout": 60
    }
}
```

### Environment Variables

```bash
# Azure Configuration
AzureWebJobsStorage="DefaultEndpointsProtocol=https;AccountName=..."
MLENDPOINTURL="https://your-ml-endpoint.azureml.net/score"
MLENDPOINTKEY="your-ml-endpoint-key"

# MCP Server Configuration  
GITHUB_MCP_URI="wss://github-mcp-server.example.com"
GITHUB_MCP_APIKEY="your-github-token"
ERP_MCP_URI="wss://erp-mcp.example.com"
CRM_MCP_URI="wss://crm-mcp.example.com"

# Generic Orchestrator

# SelfLearningAgent

Welcome to the SelfLearningAgent project! This repository provides a unified, multi-agent orchestration system with self-learning, agent-to-agent (A2A) communication, and Azure integration.

## Contents

- [docs/architecture.md](docs/architecture.md): System architecture and design
- [docs/quickstart.md](docs/quickstart.md): Quick start and usage examples
- [docs/configuration.md](docs/configuration.md): Configuration and environment setup
- [docs/a2a_communication.md](docs/a2a_communication.md): Agent-to-agent communication
- [docs/self_learning.md](docs/self_learning.md): Self-learning workflow and GitHub integration
- [docs/testing.md](docs/testing.md): Testing and validation
- [docs/development.md](docs/development.md): Development, contributing, and extending
- [docs/llm_architecture.md](docs/llm_architecture.md): LLM, LoRA, and ontological agent design
- [docs/rest_api.md](docs/rest_api.md): REST API for agent conversation (Web client integration)
- [docs/mcp_self_learning.md](docs/mcp_self_learning.md): MCP self-learning implementation

## Project Structure

See [docs/architecture.md](docs/architecture.md) for a detailed breakdown of the codebase and components.

## License

MIT License - see [LICENSE](LICENSE) for details.