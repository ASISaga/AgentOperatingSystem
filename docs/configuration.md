# Configuration

## Consolidated Configuration Example (`config/consolidated_config.json`)

```json
{
    "orchestrator": {"type": "consolidated", "version": "1.0.0"},
    "azure_function": {"ml_endpoint_url": "${MLENDPOINTURL}", "storage_connection": "${AzureWebJobsStorage}"},
    "self_learning": {
        "github_mcp": {"uri": "${GITHUB_MCP_URI}", "api_key": "${GITHUB_MCP_APIKEY}"},
        "domain_mcp_servers": {
            "erp": {"uri": "${ERP_MCP_URI}", "api_key": "${ERP_MCP_APIKEY}"},
            "crm": {"uri": "${CRM_MCP_URI}", "api_key": "${CRM_MCP_APIKEY}"}
        }
    },
    "a2a_communication": {"enabled": true, "message_queue_size": 1000, "message_timeout": 60}
}
```

## Environment Variables

```bash
AzureWebJobsStorage="..."
MLENDPOINTURL="..."
MLENDPOINTKEY="..."
GITHUB_MCP_URI="..."
GITHUB_MCP_APIKEY="..."
ERP_MCP_URI="..."
CRM_MCP_URI="..."
VLLM_SERVER_URL="..."
```
