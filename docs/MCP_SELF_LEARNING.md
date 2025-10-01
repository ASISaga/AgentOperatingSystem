# MCP Self-Learning Implementation

## Overview

Automatically detects missing functions in MCP servers, creates GitHub issues, and integrates completed functionality.

## Workflow

1. Business Process Trigger → Semantic Kernel Agent receives request
2. MCP Invocation → Agent calls domain-specific MCP Server
3. Capability Gap Detection → Function not available detected
4. Issue Creation → GitHub MCP Server creates implementation issue
5. Code Development → GitHub Coding Agent implements functionality
6. Deployment & Update → Updated MCP server supports new function

## Configuration Example

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

## Usage Example

```python
from src.Agents.SelfLearningOrchestrator import SelfLearningOrchestrator
# ... see docs/self_learning.md for details ...
```
