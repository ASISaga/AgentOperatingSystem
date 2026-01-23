# Architecture Changes: PurposeDrivenAgent Now Uses Infrastructure-Level Runtime

## Overview

The architecture has been refactored so that **PurposeDrivenAgent** remains the ONLY implementation and is pure Microsoft Agent Framework code. The **Foundry Agent Service runtime** with **Llama 3.3 70B Instruct and domain-specific LoRA adapters** is now provided by the AOS infrastructure layer (AgentRuntimeProvider), not as an agent extension.

**Key Change**: PurposeDrivenAgentFoundry has been removed. The Foundry runtime capability is now part of the AgentOperatingSystem infrastructure.

## What Changed

### Before
```
PurposeDrivenAgent (Base Implementation)
├── Pure Microsoft Agent Framework
└── No Foundry runtime

PurposeDrivenAgentFoundry (Extension)
├── Extends PurposeDrivenAgent
├── Adds Foundry Agent Service runtime
├── Llama 3.3 70B with LoRA adapters
└── Managed lifecycle by Foundry
```

### After  
```
PurposeDrivenAgent (ONLY Implementation)
├── Pure Microsoft Agent Framework code
└── No runtime awareness

AgentRuntimeProvider (AOS Infrastructure)
├── Foundry Agent Service integration
├── Llama 3.3 70B Instruct as base model
├── LoRA adapter selection and deployment
├── Stateful thread management
└── Transparent to PurposeDrivenAgent
```

## Architecture

### PurposeDrivenAgent Remains Pure

**PurposeDrivenAgent** is pure Microsoft Agent Framework code with no awareness of the runtime:

```python
# Pure Microsoft Agent Framework - no Foundry coupling
agent = PurposeDrivenAgent(
    agent_id="ceo",
    purpose="Strategic oversight and decision-making",
    purpose_scope="Strategic planning, major decisions",
    adapter_name="ceo"  # Infrastructure uses this for LoRA selection
)
await agent.initialize()
await agent.start()
```

### Infrastructure Provides Runtime

The AOS infrastructure (AgentRuntimeProvider) provides Foundry runtime transparently:

1. **Agent Creation**: PurposeDrivenAgent (pure MS Agent Framework)
2. **Infrastructure Deployment**: AgentRuntimeProvider deploys to Foundry runtime
3. **Model Selection**: Uses Llama 3.3 70B + domain LoRA adapter (e.g., llama-3.3-70b-ceo)
4. **Execution**: Runs on Foundry Agent Service (managed by Microsoft)
5. **State**: Stateful threads managed by Azure AI Agents

### How It Works

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent
from AgentOperatingSystem.runtime import AgentRuntimeProvider, RuntimeConfig

# 1. Create agent (pure MS Agent Framework)
agent = PurposeDrivenAgent(
    agent_id="ceo",
    purpose="Strategic oversight",
    adapter_name="ceo"
)
await agent.initialize()

# 2. Infrastructure provides Foundry runtime
runtime = AgentRuntimeProvider(RuntimeConfig.from_env())
await runtime.initialize()

# 3. Deploy agent to infrastructure runtime
foundry_agent = await runtime.deploy_agent(
    agent_id=agent.agent_id,
    purpose=agent.purpose,
    adapter_name="ceo"  # Uses llama-3.3-70b-ceo deployment
)

# Agent runs on Foundry with Llama 3.3 70B + CEO LoRA adapter
# But agent code remains pure MS Agent Framework
```

## Migration Steps

### Step 1: Update Dependencies

Dependencies remain the same - `azure-ai-agents` and `azure-ai-projects` are used internally by `AgentRuntimeProvider`:

```txt
# Already included
azure-ai-agents>=1.1.0
azure-ai-projects>=1.0.0
```

### Step 2: Deploy LoRA-tuned Llama 3.3 70B Models

For each domain/agent type, fine-tune and deploy Llama 3.3 70B with LoRA adapters:

```bash
# Example: Deploy CEO LoRA adapter
az ml online-deployment create \
  --name llama-3.3-70b-ceo \
  --workspace-name aos-ai-project \
  --resource-group aos-genesis \
  --model llama-3.3-70b \
  --lora-adapter path/to/ceo_adapter

# Deploy CFO LoRA adapter
az ml online-deployment create \
  --name llama-3.3-70b-cfo \
  --workspace-name aos-ai-project \
  --resource-group aos-genesis \
  --model llama-3.3-70b \
  --lora-adapter path/to/cfo_adapter
```

### Step 3: Update Configuration

Update `local.settings.json` (or Azure Function App Settings):

```json
{
  "Values": {
    "USE_FOUNDRY_RUNTIME": "true",
    "AZURE_AI_PROJECT_ENDPOINT": "https://<your-project>.services.ai.azure.com/api/projects/<project-name>",
    "AZURE_AI_MODEL_DEPLOYMENT": "llama-3.3-70b",
    "AZURE_SERVICE_BUS_CONNECTION_STRING": "<unchanged>",
    "AZURE_STORAGE_CONNECTION_STRING": "<unchanged>",
    "AGENT_CONFIG_BLOB_CONTAINER": "agent-configs"
  }
}
```

**Key Settings:**
- `USE_FOUNDRY_RUNTIME=true` - Enable Foundry runtime (default)
- `AZURE_AI_MODEL_DEPLOYMENT=llama-3.3-70b` - Base model name
- Agent-specific LoRA: Automatically appended as `{model}-{adapter_name}`

### Step 4: No Changes to Agent Configurations

Agent configurations in `agent_registry.json` remain **completely unchanged**:

```json
{
  "agent_id": "ceo",
  "agent_type": "purpose_driven",
  "purpose": "Strategic leadership and decision-making",
  "domain_knowledge": {
    "domain": "ceo",  // This becomes the LoRA adapter name
    "training_data_path": "training-data/ceo/scenarios.jsonl"
  },
  "mcp_tools": [...],
  "enabled": true
}
```

The system automatically:
1. Detects `USE_FOUNDRY_RUNTIME=true`
2. Creates `PurposeDrivenAgent` (pure MS Agent Framework)
3. Deploys agent to infrastructure runtime with `llama-3.3-70b-{domain}` LoRA adapter

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
  "runtime": "Infrastructure Runtime (Llama 3.3 70B + LoRA)",
  "active_agents": 4,
  "agent_ids": ["ceo", "cfo", "cmo", "coo"]
}

# Check specific agent
curl https://<your-app>.azurewebsites.net/api/agents/ceo/status

# Expected response:
{
  "agent_id": "ceo",
  "status": "running",
  "type": "PurposeDrivenAgent",
  "runtime": "Infrastructure Runtime (Llama 3.3 70B + LoRA)",
  "adapter_name": "ceo"
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
