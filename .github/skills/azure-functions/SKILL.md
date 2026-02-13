---
name: azure-functions
description: Expert knowledge for developing, deploying, and debugging Azure Functions in the Agent Operating System (AOS). Covers the serverless deployment model used by AOS for production workloads, including integration with Microsoft Foundry Agent Service (Azure AI Agents runtime).
---

# Azure Functions Development for AOS with Foundry Agent Runtime

## Description
Expert knowledge for developing, deploying, and debugging Azure Functions in the Agent Operating System (AOS). This skill covers the serverless deployment model used by AOS for production workloads, including integration with **Microsoft Foundry Agent Service (Azure AI Agents runtime)**.

## When to Use This Skill
- Deploying AOS to Azure Functions
- Working with function_app.py and RealmOfAgents
- Integrating with Azure AI Agents runtime (Foundry)
- Debugging Azure Functions triggers
- Configuring Azure Service Bus integration
- Managing Azure Functions host settings
- Testing Functions locally

## Key Concepts

### AOS on Azure Functions with Foundry Runtime
AOS is deployed as an Azure Functions application that:
- Exposes AOS services via Azure Service Bus
- **Orchestrates agents running on Azure AI Agents runtime (Foundry)**
- Provides HTTP endpoints for health/status
- Uses timer triggers for maintenance tasks
- Integrates with Azure Storage, Key Vault, and other services

### Architecture
```
┌─────────────────────────────────────┐
│   Client Applications               │
│   (BusinessInfinity, MCP, etc.)     │
└─────────────────────────────────────┘
              │
        Azure Service Bus
              │
              ▼
┌─────────────────────────────────────┐
│   AOS Azure Functions               │
│   • Service Bus triggers            │
│   • HTTP endpoints                  │
│   • Timer triggers                  │
│   • Orchestration layer             │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Azure AI Agents Runtime           │
│   (Foundry Agent Service)           │
│   • CEO, CFO, CMO, COO agents       │
│   • Stateful threads                │
│   • Managed lifecycle               │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   AgentOperatingSystem Core         │
│   • Storage, MCP, etc.              │
└─────────────────────────────────────┘
```

## File Structure

### Key Files
- `function_app.py` - Main Azure Functions entry point
- `host.json` - Azure Functions host configuration
- `local.settings.json` - Local development settings (not in git)
- `azure_functions/` - Azure-specific function implementations

### Configuration Files

**host.json**:
```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "extensions": {
    "serviceBus": {
      "prefetchCount": 100,
      "maxConcurrentCalls": 16
    }
  }
}
```

**local.settings.json** (create locally, not in git):
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_STORAGE_CONNECTION_STRING": "...",
    "AZURE_SERVICEBUS_CONNECTION_STRING": "...",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": "...",
    "APP_ENVIRONMENT": "development"
  }
}
```

## Function Types in AOS

### 1. Service Bus Triggered Functions
Handle messages from Azure Service Bus queues:

```python
@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name=AOSQueues.AGENT_REQUESTS,
    connection="AZURE_SERVICEBUS_CONNECTION_STRING"
)
async def agent_request_handler(msg: func.ServiceBusMessage):
    """Handle agent requests from Service Bus."""
    try:
        # Parse message
        message_data = json.loads(msg.get_body().decode('utf-8'))
        
        # Process with AOS
        aos = await initialize_aos()
        result = await aos.process_request(message_data)
        
        # Send response
        await send_response(result)
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise
```

### 2. HTTP Triggered Functions
HTTP endpoints for health checks and status:

```python
@app.route(route="health", methods=["GET"])
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    try:
        aos = await initialize_aos()
        health = await aos.get_health_status()
        
        return func.HttpResponse(
            json.dumps(health),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"status": "unhealthy", "error": str(e)}),
            status_code=503,
            mimetype="application/json"
        )
```

### 3. Timer Triggered Functions
Scheduled maintenance tasks:

```python
@app.timer_trigger(
    arg_name="timer",
    schedule="0 */5 * * * *",  # Every 5 minutes
    run_on_startup=False
)
async def maintenance_task(timer: func.TimerRequest):
    """Periodic maintenance."""
    try:
        aos = await initialize_aos()
        await aos.cleanup_old_data()
        await aos.refresh_agent_states()
        
        logger.info("Maintenance task completed")
    except Exception as e:
        logger.error(f"Maintenance error: {e}")
```

## Development Workflow

### Local Development Setup

1. **Install Azure Functions Core Tools**:
```bash
# macOS
brew tap azure/functions
brew install azure-functions-core-tools@4

# Windows (via npm)
npm install -g azure-functions-core-tools@4

# Linux
wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
```

2. **Create local.settings.json**:
```bash
cp local.settings.json.example local.settings.json
# Edit with your Azure credentials
```

3. **Install Dependencies**:
```bash
pip install -e ".[azure,full]"
```

4. **Run Locally**:
```bash
func start
```

### Testing Functions Locally

**Start Local Functions**:
```bash
# Start with verbose logging
func start --verbose

# Start on specific port
func start --port 7072
```

**Test HTTP Endpoint**:
```bash
curl http://localhost:7071/api/health
```

**Test Service Bus (requires Azurite or Azure)**:
```bash
# Install Azurite for local development
npm install -g azurite

# Start Azurite
azurite --silent --location /tmp/azurite --debug /tmp/azurite/debug.log

# Send test message to Service Bus
# (requires Azure CLI or SDK)
```

### Deployment

**Deploy to Azure**:
```bash
# Login to Azure
az login

# Create Function App (first time only)
az functionapp create \
  --resource-group <resource-group> \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name <function-app-name> \
  --storage-account <storage-account>

# Deploy
func azure functionapp publish <function-app-name>
```

**Configure App Settings**:
```bash
# Set environment variables
az functionapp config appsettings set \
  --name <function-app-name> \
  --resource-group <resource-group> \
  --settings \
    AZURE_STORAGE_CONNECTION_STRING="..." \
    AZURE_SERVICEBUS_CONNECTION_STRING="..." \
    APPLICATIONINSIGHTS_CONNECTION_STRING="..."
```

## Common Patterns

### Global State Management
```python
# Global AOS instance (initialized once, reused)
aos_instance: Optional[AgentOperatingSystem] = None

async def initialize_aos() -> AgentOperatingSystem:
    """Initialize or return existing AOS instance."""
    global aos_instance
    
    if aos_instance:
        return aos_instance
    
    config = AOSConfig(
        storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        servicebus_connection_string=os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING"),
        app_insights_connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"),
        environment=os.getenv("APP_ENVIRONMENT", "production"),
    )
    
    aos_instance = AgentOperatingSystem(config)
    await aos_instance.initialize()
    
    return aos_instance
```

### Error Handling
```python
@app.service_bus_queue_trigger(...)
async def handler(msg: func.ServiceBusMessage):
    try:
        # Process message
        result = await process(msg)
        
    except ValueError as e:
        # Invalid message - complete to avoid retry
        logger.warning(f"Invalid message: {e}")
        # Message auto-completes
        
    except Exception as e:
        # Unexpected error - let message retry
        logger.error(f"Processing error: {e}")
        raise  # Message will retry
```

### Logging
```python
import logging

logger = logging.getLogger("AOS.Functions")

@app.function_name("my_function")
async def my_function(req: func.HttpRequest):
    logger.info("Function started")
    logger.debug(f"Request: {req.url}")
    
    try:
        result = await process()
        logger.info("Function completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise
```

## Testing Azure Functions

### Unit Testing
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
import azure.functions as func

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check function."""
    # Create mock request
    req = func.HttpRequest(
        method='GET',
        url='/api/health',
        body=None
    )
    
    # Call function
    from function_app import health_check
    response = await health_check(req)
    
    # Assert
    assert response.status_code == 200
    assert 'status' in response.get_body().decode()

@pytest.mark.asyncio
async def test_service_bus_handler():
    """Test Service Bus message handler."""
    # Create mock message
    message_data = {"type": "test", "data": "test"}
    msg = MagicMock(spec=func.ServiceBusMessage)
    msg.get_body.return_value = json.dumps(message_data).encode()
    
    # Call handler
    from function_app import agent_request_handler
    await agent_request_handler(msg)
    
    # Verify processing (check logs, database, etc.)
```

### Integration Testing
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_flow():
    """Test complete flow through Azure Functions."""
    # Requires actual Azure resources or Azurite
    # Send message to Service Bus
    # Wait for processing
    # Verify result
```

## Common Issues and Solutions

### Issue: Function Not Triggering
**Problem**: Service Bus trigger not firing.

**Solution**:
1. Verify Service Bus connection string in settings
2. Check queue name matches configuration
3. Ensure messages are being sent to correct queue
4. Check Function App is running (not stopped)
5. Review Application Insights for errors

### Issue: Cold Start Delays
**Problem**: First request is slow.

**Solution**:
1. Use Premium or Dedicated plan instead of Consumption
2. Enable "Always On" setting
3. Implement warm-up function
4. Optimize initialization code
5. Consider pre-warming AOS instance

### Issue: Timeout Errors
**Problem**: Function times out before completing.

**Solution**:
1. Increase function timeout in host.json
2. Break long operations into smaller chunks
3. Use Durable Functions for long-running workflows
4. Optimize database queries
5. Use async/await properly

### Issue: Local Development Not Working
**Problem**: Functions fail to run locally.

**Solution**:
1. Ensure Azure Functions Core Tools is installed
2. Verify Python version matches (3.8+)
3. Check local.settings.json exists and is valid
4. Install all dependencies: `pip install -e ".[azure,full]"`
5. Use Azurite for local storage emulation

### Issue: Deployment Fails
**Problem**: `func azure functionapp publish` fails.

**Solution**:
1. Ensure logged in to Azure: `az login`
2. Verify Function App exists
3. Check Python version compatibility
4. Review deployment logs for specific errors
5. Ensure all dependencies in requirements.txt (generated from pyproject.toml)

## Best Practices

1. **Use Async/Await**: All handlers should be async for better performance
2. **Implement Proper Logging**: Use structured logging for debugging
3. **Handle Errors Gracefully**: Distinguish retryable vs non-retryable errors
4. **Monitor Performance**: Use Application Insights for monitoring
5. **Optimize Cold Starts**: Minimize initialization code
6. **Use Environment Variables**: Never hardcode secrets
7. **Test Locally**: Use Azure Functions Core Tools for local testing
8. **Implement Health Checks**: Provide health endpoints for monitoring
9. **Use Connection Pooling**: Reuse connections across invocations
10. **Set Appropriate Timeouts**: Configure based on expected execution time

## Monitoring and Debugging

### Application Insights Queries
```kusto
// Function executions
requests
| where cloud_RoleName == "AgentOperatingSystem"
| project timestamp, name, duration, success

// Errors
exceptions
| where cloud_RoleName == "AgentOperatingSystem"
| project timestamp, type, message, details

// Service Bus processing
dependencies
| where cloud_RoleName == "AgentOperatingSystem"
| where type == "Azure Service Bus"
| summarize count() by name, resultCode
```

### Live Metrics
- Monitor in Azure Portal → Function App → Application Insights
- View live request rate, failures, and performance
- Investigate failures in real-time

### Log Stream
```bash
# Stream logs from Azure
func azure functionapp logstream <function-app-name>

# Or use Azure Portal → Function App → Log Stream
```

## File Locations

### Core Files
- `function_app.py` - Main entry point with function definitions
- `host.json` - Host configuration
- `local.settings.json` - Local settings (gitignored)

### Related Directories
- `azure_functions/` - Azure-specific implementations
- `src/AgentOperatingSystem/messaging/` - Service Bus integration
- `tests/test_azure_functions_infrastructure.py` - Azure Functions tests

## Related Skills
- `perpetual-agents` - Understanding AOS agents
- `async-python` - Async programming patterns
- `testing-aos` - Testing strategies
- `azure-services` - Azure service integration

## Additional Resources
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- function_app.py - Implementation reference
- docs/FOUNDRY_AGENT_SERVICE.md - Foundry integration examples
