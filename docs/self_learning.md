# Self-Learning System

## Overview

The Agent Operating System implements automatic capability gap detection and resolution through its self-learning system. When an agent needs functionality that doesn't exist, the system automatically creates the capability.

## Workflow

1. **Business Process Execution**: Agent attempts to invoke MCP server function
2. **Capability Gap Detection**: Function not available in domain MCP server
3. **GitHub Issue Creation**: Automated issue creation for missing functionality
4. **Code Implementation**: GitHub Coding Agent implements missing capability
5. **Capability Update**: MCP server gains new function, gap resolved
6. **Persistent Improvement**: Future requests use newly implemented capability

## MCP Integration

The self-learning system integrates with Model Context Protocol (MCP) servers:

### Configuration

```json
{
  "domain_mcp_servers": {
    "erp": {
      "uri": "wss://your-erp-mcp-server.com",
      "api_key_env": "ERP_MCP_APIKEY",
      "repository": {
        "owner": "YourOrg",
        "name": "ERP-MCP",
        "coding_agent": "github-coding-agent"
      }
    }
  },
  "github_mcp_server": {
    "uri": "wss://github-mcp-server.com",
    "api_key_env": "GITHUB_MCP_APIKEY"
  }
}
```

### Usage Example

```python
from src.orchestrator import SelfLearningOrchestrator

# Initialize
orchestrator = SelfLearningOrchestrator(domain_config, github_config)
await orchestrator.initialize()

# Execute business process
result = await orchestrator.execute_business_process(
    domain="erp",
    function_name="generate_invoice_pdf",
    parameters={"invoice_id": "INV-001"}
)
```

## Agent Architecture

The `SelfLearningAgent` is fully modular with these components:

- **KnowledgeBaseManager**: Manages domain knowledge, contexts, and directives
- **VectorDBManager**: Handles vector database (RAG) initialization and queries
- **MCPClientManager**: Manages MCP client connections for each domain
- **SemanticKernelManager**: Integrates with Semantic Kernel for AI responses

### Example

```python
from src.self_learning_agent.self_learning_agent import SelfLearningAgent

agent = SelfLearningAgent()
await agent.handle_user_request("How do I improve sales?", domain="sales")
```

## Implementation Details

- Automated GitHub issue creation for missing functions
- Tracks pending implementations and updates capabilities
- Robust error handling and monitoring
- Agent-to-Agent (A2A) communication support

## Related Documentation

- [A2A Communication](a2a_communication.md)
- [MCP Documentation](specifications/mcp.md)
- [Architecture Overview](architecture.md)
