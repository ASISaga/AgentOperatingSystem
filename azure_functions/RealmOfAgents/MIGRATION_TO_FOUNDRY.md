# Migration Guide: Custom Runtime → Microsoft Foundry Agent Service Runtime

## Overview

RealmOfAgents has been enhanced to support **Microsoft Foundry Agent Service** as the runtime for **PurposeDrivenAgent** - the core architectural component of AOS. 

**Important**: PurposeDrivenAgent is NOT being phased out. Instead, it has been enhanced with a new Foundry-enabled implementation (`PurposeDrivenAgentFoundry`) that uses Azure AI Agents runtime with **Llama 3.3 70B fine-tuned using domain-specific LoRA adapters**.

## What Changed

### Before
```
PurposeDrivenAgent (Custom Runtime)
├── Manual lifecycle management
├── Custom state management
└── Direct agent framework integration
```

### After  
```
PurposeDrivenAgent (Core Component - UNCHANGED)
├── Standard implementation (legacy mode)
└── New: PurposeDrivenAgentFoundry (Foundry-enabled)
    ├── Uses Azure AI Agents runtime
    ├── Llama 3.3 70B with LoRA adapters
    ├── Managed lifecycle by Foundry
    └── Built-in stateful threads
```

## Architecture

### PurposeDrivenAgent Remains the Core Component

**PurposeDrivenAgent** is the fundamental building block of AOS and continues to be the main API:

```python
# The API remains the same (use concrete implementation)
agent = LeadershipAgent(
    agent_id="ceo",
    purpose="Strategic oversight and decision-making",
    purpose_scope="Strategic planning, major decisions",
    adapter_name="ceo"  # Now references LoRA adapter
)
await agent.initialize()
await agent.start()
```

### How It Works

When `USE_FOUNDRY_RUNTIME=true` (default), the system uses **PurposeDrivenAgentFoundry**:

1. **Agent Creation**: Creates agent on Azure AI Agents runtime
2. **Model**: Uses Llama 3.3 70B fine-tuned with domain LoRA adapter
3. **Execution**: Runs on Foundry Agent Service (managed by Microsoft)
4. **State**: Stateful threads managed by Azure AI Agents

### Llama 3.3 70B with LoRA Adapters

Each PurposeDrivenAgent uses Llama 3.3 70B fine-tuned with a domain-specific LoRA adapter:

```python
agent = PurposeDrivenAgentFoundry(
    agent_id="ceo",
    purpose="Strategic oversight",
    adapter_name="ceo",  # LoRA adapter: llama-3.3-70b-ceo
    # Model deployment: llama-3.3-70b-{adapter_name}
)
```

**LoRA Adapters by Domain:**
- `ceo` → Llama 3.3 70B fine-tuned for CEO/strategic thinking
- `cfo` → Llama 3.3 70B fine-tuned for financial analysis
- `cto` → Llama 3.3 70B fine-tuned for technology strategy
- `cmo` → Llama 3.3 70B fine-tuned for marketing strategy

## Migration Steps

### Step 1: Update Dependencies

Dependencies remain the same - `azure-ai-agents` and `azure-ai-projects` are used internally by `PurposeDrivenAgentFoundry`:

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
2. Creates `PurposeDrivenAgentFoundry` instead of base `PurposeDrivenAgent`
3. Uses `llama-3.3-70b-{domain}` as the model deployment

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
  "runtime": "Foundry Agent Service (Llama 3.3 70B + LoRA)",
  "active_agents": 4,
  "agent_ids": ["ceo", "cfo", "cmo", "coo"]
}

# Check specific agent
curl https://<your-app>.azurewebsites.net/api/agents/ceo/status

# Expected response:
{
  "agent_id": "ceo",
  "status": "running",
  "type": "PurposeDrivenAgentFoundry",
  "runtime": "Foundry Agent Service (Llama 3.3 70B + LoRA)",
  "lora_adapter": "ceo"
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
