# Technical Specification: MCP (Model Context Protocol) System

**Document Version:** 2025.1.2  
**Status:** Implemented  
**Date:** December 25, 2025  
**Module:** AgentOperatingSystem MCP (`src/AgentOperatingSystem/mcp/`)

---

## 1. System Overview

The AOS MCP (Model Context Protocol) System provides integration with external MCP servers, enabling agents to access tools, resources, and capabilities from various external services. This is the single source of truth for all MCP protocol communication in AOS.

**Key Features:**
- MCP client for connecting to external servers
- Client lifecycle management
- Protocol request/response handling
- Tool and resource discovery
- Azure Service Bus integration for MCP messaging

---

## 2. Architecture

### 2.1 Core Components

**MCPClient (`client.py`)**
- Connection management to MCP servers
- Request/response handling
- Capability negotiation
- Tool execution

**MCPClientManager (`client_manager.py`)**
- Multi-client coordination
- Client pooling and reuse
- Health monitoring
- Configuration management

**Protocol Models (`protocol/`)**
- Request structures (`request.py`)
- Response structures (`response.py`)
- Protocol definitions

---

## 3. Implementation Details

### 3.1 MCP Client

**Initialization:**
```python
from AgentOperatingSystem.mcp.client import MCPClient

# Initialize MCP client
client = MCPClient(
    server_name="github_mcp",
    config={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")
        }
    }
)

# Connect to server
await client.connect()
```

**Connection Status:**
```python
from AgentOperatingSystem.mcp.client import MCPConnectionStatus

# Check connection status
if client.status == MCPConnectionStatus.CONNECTED:
    print("Connected to MCP server")

# Connection states:
# - DISCONNECTED
# - CONNECTING
# - CONNECTED
# - ERROR
```

**Tool Discovery:**
```python
# List available tools
tools = await client.list_tools()

for tool in tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Parameters: {tool.parameters}")
```

**Tool Execution:**
```python
# Execute MCP tool
result = await client.call_tool(
    tool_name="create_issue",
    arguments={
        "owner": "ASISaga",
        "repo": "AgentOperatingSystem",
        "title": "New feature request",
        "body": "Description of the feature..."
    }
)

print(f"Result: {result}")
```

**Resource Access:**
```python
# List available resources
resources = await client.list_resources()

# Read resource
resource_data = await client.read_resource(
    uri="github://ASISaga/AgentOperatingSystem/README.md"
)
```

### 3.2 MCP Client Manager

**Managing Multiple Clients:**
```python
from AgentOperatingSystem.mcp.client_manager import MCPClientManager

# Initialize manager
manager = MCPClientManager()

# Register MCP servers
await manager.register_server(
    server_name="github_mcp",
    config={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")}
    }
)

await manager.register_server(
    server_name="linkedin_mcp",
    config={
        "command": "node",
        "args": ["linkedin-mcp-server"],
        "env": {"LINKEDIN_TOKEN": os.getenv("LINKEDIN_TOKEN")}
    }
)

# Get client for specific server
github_client = await manager.get_client("github_mcp")
```

**Client Pooling:**
```python
# Configure client pooling
manager.configure_pool(
    max_clients_per_server=5,
    idle_timeout_seconds=300,
    reuse_connections=True
)

# Get client from pool (creates or reuses)
async with manager.acquire_client("github_mcp") as client:
    await client.call_tool("create_issue", arguments)
```

**Health Monitoring:**
```python
# Check health of all clients
health_status = await manager.check_health()

for server_name, status in health_status.items():
    print(f"{server_name}: {status['status']}")
    if status['status'] == 'unhealthy':
        print(f"  Error: {status['error']}")

# Cleanup unhealthy clients
await manager.cleanup_unhealthy_clients()
```

### 3.3 Protocol Structures

**MCP Request:**
```python
from AgentOperatingSystem.mcp.protocol.request import MCPRequest

request = MCPRequest(
    request_id="req_001",
    method="tools/call",
    params={
        "name": "create_issue",
        "arguments": {
            "title": "Bug report",
            "body": "Description..."
        }
    }
)
```

**MCP Response:**
```python
from AgentOperatingSystem.mcp.protocol.response import MCPResponse

response = MCPResponse(
    request_id="req_001",
    result={
        "issue_number": 123,
        "url": "https://github.com/..."
    },
    error=None
)
```

---

## 4. Integration with Azure Service Bus

### 4.1 MCP over Service Bus

```python
from AgentOperatingSystem.messaging.servicebus_manager import ServiceBusManager

# Initialize Service Bus for MCP communication
service_bus = ServiceBusManager(
    connection_string=os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")
)

# Send MCP request via Service Bus
await service_bus.send_to_topic(
    topic_name="mcp_requests",
    message={
        "server": "github_mcp",
        "tool": "create_issue",
        "arguments": arguments,
        "correlation_id": correlation_id
    }
)

# Receive MCP responses
async for message in service_bus.receive_from_subscription(
    topic_name="mcp_responses",
    subscription_name="orchestrator_responses"
):
    response = message.body
    await process_mcp_response(response)
    await service_bus.complete_message(message)
```

### 4.2 Distributed MCP Architecture

```
┌──────────────┐
│ Orchestrator │
└──────┬───────┘
       │
       │ Send MCP Request
       ▼
┌──────────────────┐
│ Service Bus      │
│  (mcp_requests)  │
└──────┬───────────┘
       │
       │ Route to MCP Worker
       ▼
┌──────────────────┐
│ MCP Worker       │
│  - MCPClient     │
│  - Tool Executor │
└──────┬───────────┘
       │
       │ Send Result
       ▼
┌──────────────────┐
│ Service Bus      │
│ (mcp_responses)  │
└──────┬───────────┘
       │
       │ Deliver Response
       ▼
┌──────────────┐
│ Orchestrator │
└──────────────┘
```

---

## 5. Common MCP Servers

### 5.1 GitHub MCP Server

**Configuration:**
```python
github_config = {
    "server_name": "github_mcp",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")
    }
}
```

**Available Tools:**
- `create_issue`: Create GitHub issue
- `create_pull_request`: Create pull request
- `search_repositories`: Search repositories
- `get_file_contents`: Read file contents
- `create_or_update_file`: Modify files

**Example Usage:**
```python
# Create GitHub issue
await github_client.call_tool(
    tool_name="create_issue",
    arguments={
        "owner": "ASISaga",
        "repo": "AgentOperatingSystem",
        "title": "Feature: Add new agent capability",
        "body": "Description of the feature request...",
        "labels": ["enhancement", "agent"]
    }
)
```

### 5.2 LinkedIn MCP Server

**Configuration:**
```python
linkedin_config = {
    "server_name": "linkedin_mcp",
    "command": "node",
    "args": ["linkedin-mcp-server"],
    "env": {
        "LINKEDIN_CLIENT_ID": os.getenv("LINKEDIN_CLIENT_ID"),
        "LINKEDIN_CLIENT_SECRET": os.getenv("LINKEDIN_CLIENT_SECRET")
    }
}
```

**Available Tools:**
- `get_profile`: Get LinkedIn profile
- `post_update`: Post status update
- `search_people`: Search for people
- `get_connections`: Get connections

### 5.3 Custom MCP Servers

**Creating Custom Server:**
```python
# Custom server configuration
custom_server_config = {
    "server_name": "custom_api",
    "command": "python",
    "args": ["custom_mcp_server.py"],
    "env": {
        "API_KEY": os.getenv("CUSTOM_API_KEY"),
        "API_URL": "https://api.example.com"
    }
}

await manager.register_server("custom_api", custom_server_config)
```

---

## 6. Error Handling

### 6.1 Connection Errors

```python
from AgentOperatingSystem.mcp.client import MCPConnectionError

try:
    await client.connect()
except MCPConnectionError as e:
    logger.error(f"Failed to connect to MCP server: {e}")
    # Implement retry or fallback
```

### 6.2 Tool Execution Errors

```python
from AgentOperatingSystem.mcp.client import MCPToolError

try:
    result = await client.call_tool("create_issue", arguments)
except MCPToolError as e:
    logger.error(f"Tool execution failed: {e}")
    # Handle error appropriately
```

### 6.3 Retry Logic

```python
from AgentOperatingSystem.reliability.retry import retry

@retry(max_attempts=3, backoff_multiplier=2)
async def call_mcp_tool_with_retry(client, tool_name, arguments):
    return await client.call_tool(tool_name, arguments)
```

---

## 7. Security

### 7.1 Credential Management

```python
# Use environment variables for credentials
config = {
    "env": {
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "API_KEY": os.getenv("API_KEY")
    }
}

# Never hardcode credentials in config
```

### 7.2 Request Validation

```python
# Validate MCP requests
def validate_mcp_request(request):
    if not request.get("tool_name"):
        raise ValueError("Tool name is required")
    
    if not request.get("arguments"):
        raise ValueError("Arguments are required")
    
    # Additional validation...
```

---

## 8. Monitoring

### 8.1 Metrics

```python
from AgentOperatingSystem.observability.metrics import metrics

# Track MCP operations
metrics.increment("mcp.tool_calls.total", tags={
    "server": server_name,
    "tool": tool_name
})

metrics.timing("mcp.tool_call.duration_ms", duration, tags={
    "server": server_name,
    "tool": tool_name
})

metrics.increment("mcp.errors", tags={
    "server": server_name,
    "error_type": error_type
})
```

### 8.2 Health Checks

```python
# MCP server health check
async def check_mcp_health(server_name):
    try:
        client = await manager.get_client(server_name)
        tools = await client.list_tools()
        return {
            "status": "healthy",
            "tool_count": len(tools)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

---

## 9. Best Practices

### 9.1 Client Management
1. **Reuse clients** when possible via client pooling
2. **Monitor connection health** and reconnect as needed
3. **Implement timeouts** for tool calls
4. **Handle errors gracefully** with retry logic
5. **Clean up** idle connections

### 9.2 Tool Execution
1. **Validate inputs** before calling tools
2. **Set appropriate timeouts** for long-running tools
3. **Log all tool calls** for audit trail
4. **Handle rate limits** from external services
5. **Cache results** when appropriate

### 9.3 Security
1. **Use environment variables** for credentials
2. **Rotate credentials** regularly
3. **Implement access control** for tool execution
4. **Validate tool parameters** to prevent injection
5. **Audit all MCP operations**

---

**Document Approval:**
- **Status:** Implemented and Active
- **Last Updated:** December 25, 2025
- **Owner:** AOS Integration Team
