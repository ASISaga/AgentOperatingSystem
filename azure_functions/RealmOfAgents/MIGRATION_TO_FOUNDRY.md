# Migration Guide: Azure Functions Custom Runtime → Azure AI Agents (Foundry) Runtime

## Overview

RealmOfAgents has been migrated from using **Azure Functions as a custom runtime** for Microsoft Agent Framework agents to using the **Azure AI Agents runtime (Foundry Agent Service)**. This provides a more robust, scalable, and officially supported platform for running AI agents.

## What Changed

### Before (Custom Runtime)
```
Azure Functions (RealmOfAgents)
├── Manually instantiate PurposeDrivenAgent
├── Manually manage agent lifecycle
├── Custom event processing
└── Custom thread/state management
```

### After (Foundry Runtime)
```
Azure Functions (RealmOfAgents) → Orchestration Layer
├── Uses AgentsClient from azure-ai-agents
├── Agents run on Azure AI Agents runtime
├── Foundry handles agent lifecycle
└── Built-in thread/state management
```

## Architecture Changes

### Old Architecture
- **Custom Agent Instantiation**: `PurposeDrivenAgent`, `PerpetualAgent`, `LeadershipAgent` were manually created in Python
- **Custom State Management**: State was managed through custom ContextMCPServer
- **Manual Lifecycle**: Start/stop/restart was handled manually
- **Custom Threading**: Thread management implemented from scratch

### New Architecture
- **Foundry Agent Service**: Agents are created using `AgentsClient.create_agent()`
- **Built-in State**: Azure AI Agents provides built-in thread and state management
- **Managed Lifecycle**: Foundry handles agent lifecycle automatically
- **Stateful Threads**: Native support for stateful conversations via `AgentThread`

## Breaking Changes

### 1. Agent Creation

**Before:**
```python
from AgentOperatingSystem.agents import PurposeDrivenAgent

agent = PurposeDrivenAgent(
    agent_id="ceo",
    purpose="Strategic leadership",
    tools=tools,
    adapter_name="ceo"
)
await agent.initialize()
await agent.start()
```

**After:**
```python
from azure.ai.agents import AgentsClient
from azure.identity.aio import DefaultAzureCredential

client = AgentsClient(
    endpoint=os.getenv('AZURE_AI_PROJECT_ENDPOINT'),
    credential=DefaultAzureCredential()
)

agent = await client.create_agent(
    model="gpt-4",
    name="ceo",
    description="Strategic leadership",
    instructions="You are the CEO...",
    toolset=toolset
)
```

### 2. Agent Interaction

**Before:**
```python
# Direct method call
result = await agent.process_event(event_type, payload)
```

**After:**
```python
# Create thread and run
thread = await client.create_thread()
run = await client.create_thread_and_process_run(
    agent_id=agent.id,
    thread=thread,
    additional_messages=[{"role": "user", "content": message}]
)
```

### 3. Required Environment Variables

**New Required Variables:**
```bash
# Azure AI Project endpoint
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>

# Model deployment name
AZURE_AI_MODEL_DEPLOYMENT=gpt-4

# Existing variables (unchanged)
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_SERVICE_BUS_CONNECTION_STRING=...
```

## Migration Steps

### Step 1: Update Dependencies

Update `requirements.txt`:
```txt
# Add
azure-ai-agents>=1.1.0
azure-ai-projects>=1.0.0

# Keep (for compatibility)
agent-framework>=1.0.0b251218
git+https://github.com/ASISaga/AgentOperatingSystem.git
```

### Step 2: Deploy Azure AI Project

```bash
# Create Azure AI Hub (if not exists)
az ml workspace create \
  --kind project \
  --name aos-ai-project \
  --resource-group aos-genesis \
  --location eastus

# Get project endpoint
az ml workspace show \
  --name aos-ai-project \
  --resource-group aos-genesis \
  --query "discovery_url" -o tsv
```

### Step 3: Update Configuration

Update `local.settings.json` (or Azure Function App Settings):
```json
{
  "Values": {
    "AZURE_AI_PROJECT_ENDPOINT": "https://<your-project>.services.ai.azure.com/api/projects/<project-name>",
    "AZURE_AI_MODEL_DEPLOYMENT": "gpt-4",
    "AZURE_SERVICE_BUS_CONNECTION_STRING": "<unchanged>",
    "AZURE_STORAGE_CONNECTION_STRING": "<unchanged>",
    "AGENT_CONFIG_BLOB_CONTAINER": "agent-configs"
  }
}
```

### Step 4: Update Agent Configurations (Optional)

Agent configurations in `agent_registry.json` remain largely the same. The system will automatically convert them to Foundry format.

### Step 5: Deploy Function App

```bash
cd azure_functions/RealmOfAgents
func azure functionapp publish <your-function-app-name>
```

### Step 6: Verify Deployment

```bash
# Check health
curl https://<your-app>.azurewebsites.net/api/health

# Expected response:
{
  "status": "healthy",
  "runtime": "Azure AI Agents (Foundry Agent Service)",
  "active_agents": 4,
  "agent_ids": ["ceo", "cfo", "cmo", "coo"]
}
```

## Key Benefits

### 1. **Official Microsoft Support**
- Azure AI Agents is an officially supported service
- Regular updates and improvements from Microsoft
- Enterprise SLA and support

### 2. **Better Scalability**
- Foundry handles scaling automatically
- No need to manage agent instances manually
- Built-in load balancing

### 3. **Built-in Features**
- Stateful threads out of the box
- Vector stores for knowledge
- File handling capabilities
- Code interpreter
- Function calling

### 4. **Improved Reliability**
- Managed service with high availability
- Built-in retry logic
- Better error handling

### 5. **Cost Optimization**
- Pay only for what you use
- No idle agent instances consuming resources
- Better resource utilization

## Tool Integration

### MCP Tools

MCP tools continue to work through the MCPServers function app. The integration has been updated to bridge between MCP and Foundry:

**Old Flow:**
```
Agent → Direct MCP Call → Tool Execution
```

**New Flow:**
```
Foundry Agent → FunctionTool → Service Bus → MCPServers → Tool Execution → Service Bus → Foundry
```

The conversion happens automatically in `convert_mcp_tools_to_function_tools()`.

## Rollback Procedure

If you need to rollback to the custom runtime:

```bash
# Restore original function_app.py
cd azure_functions/RealmOfAgents
cp function_app_original.py function_app.py

# Redeploy
func azure functionapp publish <your-function-app-name>
```

## Troubleshooting

### Issue: "AZURE_AI_PROJECT_ENDPOINT not configured"

**Solution:** Set the environment variable in Function App settings:
```bash
az functionapp config appsettings set \
  --name <app-name> \
  --resource-group <rg-name> \
  --settings AZURE_AI_PROJECT_ENDPOINT="https://..."
```

### Issue: "Agent not found on Foundry runtime"

**Solution:** Check that agents are being created on startup:
1. Check Function App logs
2. Verify agent registry is loaded correctly
3. Ensure `AZURE_STORAGE_CONNECTION_STRING` is set
4. Check that agents are enabled in `agent_registry.json`

### Issue: "Failed to create agent: Model not found"

**Solution:** Verify model deployment exists:
```bash
# List deployments
az ml online-deployment list \
  --workspace-name aos-ai-project \
  --resource-group aos-genesis
```

Update `AZURE_AI_MODEL_DEPLOYMENT` to match an existing deployment.

## What Stays the Same

✅ **Agent Configurations** - No changes to `agent_registry.json` format
✅ **Service Bus Communication** - Same topics and queues
✅ **MCPServers Function App** - Unchanged, continues to provide tools
✅ **Main AOS Kernel** - Unchanged, continues orchestration
✅ **Blob Storage** - Same storage structure
✅ **Development Workflow** - Same config-driven approach

## Next Steps

1. **Test Your Agents**: Verify all configured agents work correctly
2. **Monitor Performance**: Check Application Insights for metrics
3. **Update Documentation**: Update any custom docs that reference the old architecture
4. **Train Your Team**: Ensure team understands new Foundry concepts

## Additional Resources

- [Azure AI Agents Documentation](https://learn.microsoft.com/azure/ai-services/agents/)
- [Azure AI Projects SDK](https://pypi.org/project/azure-ai-projects/)
- [Agent Framework Integration](https://github.com/microsoft/agent-framework)

## Support

For issues or questions:
- Check Application Insights logs
- Review this migration guide
- Check the main AOS documentation
- Open an issue in the repository
