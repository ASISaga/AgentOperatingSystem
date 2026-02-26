# aos-mcp-servers API Reference

## MCP Server Registry Schema

### Server Entry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `server_id` | string | Yes | Unique server identifier |
| `server_type` | string | Yes | Server class name |
| `tools` | array | No | List of tool names to expose |
| `resources` | array | No | List of resource names to expose |
| `config` | object | No | Additional runtime configuration |

### Example Registry

```json
{
    "mcp_servers": [
        {
            "server_id": "context-server",
            "server_type": "ContextMCPServer",
            "tools": ["get_context", "set_context", "list_contexts"],
            "resources": ["agent_state", "session_data"],
            "config": {
                "max_context_size": 10000
            }
        }
    ]
}
```

## MCP Protocol Endpoints

### Tool Invocation

MCP servers expose tools that agents can invoke:

```json
{
    "method": "tools/call",
    "params": {
        "name": "get_context",
        "arguments": {
            "key": "agent_state"
        }
    }
}
```

### Resource Access

MCP servers expose resources that agents can read:

```json
{
    "method": "resources/read",
    "params": {
        "uri": "mcp://context-server/agent_state"
    }
}
```

## HTTP Endpoints

### Server Status

```
GET /api/mcp/servers
```

Returns the list of registered MCP servers and their current status.

### Server Configuration

```
GET /api/mcp/config
```

Returns the current MCP server registry configuration.
