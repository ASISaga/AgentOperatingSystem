"""
MCPServers Azure Functions App

Plug-and-play infrastructure for MCP server deployment.
Provides common Azure and MCP related infrastructure.

This app communicates with the AgentOperatingSystem kernel over Azure Service Bus.
"""

import logging
import json
import os
import asyncio
from typing import Dict, Any, Optional
import azure.functions as func
from azure.servicebus.aio import ServiceBusClient, ServiceBusMessage
from azure.storage.blob.aio import BlobServiceClient
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

# Import AOS infrastructure
# Note: AgentOperatingSystem package must be installed in the deployment environment
# Install with: pip install git+https://github.com/ASISaga/AgentOperatingSystem.git
try:
    from AgentOperatingSystem.mcp.client import MCPClient
    from AgentOperatingSystem.mcp.protocol.request import MCPRequest
    from AgentOperatingSystem.mcp.protocol.response import MCPResponse
except ImportError as e:
    logger = logging.getLogger("MCPServers")
    logger.error(f"Failed to import AgentOperatingSystem: {e}")
    logger.error("Please ensure AgentOperatingSystem is installed: pip install git+https://github.com/ASISaga/AgentOperatingSystem.git")
    raise

from mcp_server_schema import MCPServerConfiguration, MCPServerRegistry, MCPServerType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCPServers")

# Global state
mcp_server_instances: Dict[str, Any] = {}
server_registry: Optional[MCPServerRegistry] = None
service_bus_client: Optional[ServiceBusClient] = None
secret_client: Optional[SecretClient] = None


app = func.FunctionApp()


async def load_server_registry() -> MCPServerRegistry:
    """
    Load MCP server registry from Azure Blob Storage.
    
    The registry contains all MCP server configurations.
    """
    global server_registry
    
    try:
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        container_name = os.getenv('MCP_REGISTRY_BLOB_CONTAINER', 'mcp-registry')
        
        if not connection_string:
            logger.warning("No storage connection string - using empty registry")
            return MCPServerRegistry(servers=[])
        
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="mcp_server_registry.json"
        )
        
        # Download registry
        download_stream = await blob_client.download_blob()
        registry_data = await download_stream.readall()
        registry_json = json.loads(registry_data)
        
        server_registry = MCPServerRegistry(**registry_json)
        logger.info(f"Loaded {len(server_registry.servers)} MCP server configurations")
        
        return server_registry
        
    except Exception as e:
        logger.error(f"Failed to load MCP server registry: {e}")
        return MCPServerRegistry(servers=[])


async def initialize_secret_client():
    """Initialize Azure Key Vault client for secret resolution"""
    global secret_client
    
    try:
        key_vault_url = os.getenv('AZURE_KEY_VAULT_URL')
        if not key_vault_url:
            logger.warning("No Key Vault URL - secret resolution unavailable")
            return
        
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
        logger.info("Secret client initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize secret client: {e}")


async def initialize_service_bus():
    """Initialize Service Bus client for kernel communication"""
    global service_bus_client
    
    try:
        connection_string = os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')
        if not connection_string:
            logger.warning("No Service Bus connection string")
            return
        
        service_bus_client = ServiceBusClient.from_connection_string(connection_string)
        logger.info("Service Bus client initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize Service Bus client: {e}")


async def resolve_environment_variables(env: Dict[str, str]) -> Dict[str, str]:
    """
    Resolve environment variables with Key Vault secret substitution.
    
    Supports ${VAR_NAME} syntax for Key Vault secrets.
    """
    resolved = {}
    
    for key, value in env.items():
        if value.startswith("${") and value.endswith("}"):
            # Extract secret name
            secret_name = value[2:-1]
            
            # Try to get from Key Vault
            if secret_client:
                try:
                    secret = await secret_client.get_secret(secret_name)
                    resolved[key] = secret.value
                    continue
                except Exception as e:
                    logger.warning(f"Failed to get secret {secret_name}: {e}")
            
            # Fallback to environment variable
            resolved[key] = os.getenv(secret_name, value)
        else:
            resolved[key] = value
    
    return resolved


async def instantiate_mcp_server(config: MCPServerConfiguration) -> Optional[MCPClient]:
    """
    Instantiate an MCP server from configuration.
    
    This is the core of the plug-and-play infrastructure - servers are
    created entirely from configuration, no code changes needed.
    """
    try:
        logger.info(f"Instantiating MCP server {config.server_id}")
        
        # Resolve environment variables
        env = await resolve_environment_variables(config.env)
        
        # Create MCP client based on server type
        if config.server_type == MCPServerType.STDIO:
            client = MCPClient(
                server_name=config.server_id,
                command=config.command,
                args=config.args,
                env=env
            )
        else:
            logger.warning(f"Server type {config.server_type} not yet implemented")
            return None
        
        # Initialize the client
        await client.initialize()
        
        logger.info(f"MCP server {config.server_id} instantiated successfully")
        return client
        
    except Exception as e:
        logger.error(f"Failed to instantiate MCP server {config.server_id}: {e}")
        return None


async def start_all_servers():
    """Start all enabled MCP servers from the registry"""
    global mcp_server_instances, server_registry
    
    if not server_registry:
        server_registry = await load_server_registry()
    
    auto_start_servers = server_registry.get_auto_start_servers()
    logger.info(f"Starting {len(auto_start_servers)} auto-start MCP servers")
    
    for config in auto_start_servers:
        if config.server_id not in mcp_server_instances:
            client = await instantiate_mcp_server(config)
            if client:
                mcp_server_instances[config.server_id] = {
                    'client': client,
                    'config': config
                }


@app.function_name(name="StartupTrigger")
@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=True)
async def startup_trigger(timer: func.TimerRequest) -> None:
    """
    Startup trigger - initializes and starts all MCP servers on app startup.
    """
    logger.info("MCPServers startup triggered")
    
    try:
        # Initialize clients
        if not secret_client:
            await initialize_secret_client()
        if not service_bus_client:
            await initialize_service_bus()
        
        # Start all servers
        await start_all_servers()
        
        logger.info(f"MCPServers running with {len(mcp_server_instances)} active servers")
        
    except Exception as e:
        logger.error(f"Startup trigger failed: {e}", exc_info=True)


@app.function_name(name="MCPRequestHandler")
@app.service_bus_topic_trigger(
    connection="AZURE_SERVICE_BUS_CONNECTION_STRING",
    topic_name="mcp-requests",
    subscription_name="mcp-servers",
    arg_name="message"
)
async def mcp_request_handler(message: func.ServiceBusMessage) -> None:
    """
    Handle MCP requests from AOS kernel via Service Bus.
    
    Routes requests to the appropriate MCP server instance.
    """
    try:
        message_body = message.get_body().decode('utf-8')
        request_data = json.loads(message_body)
        
        server_id = request_data.get('server_id')
        method = request_data.get('method')
        params = request_data.get('params', {})
        request_id = request_data.get('request_id')
        
        logger.info(f"Received MCP request for server {server_id}, method {method}")
        
        response_data = None
        
        # Route to server
        if server_id in mcp_server_instances:
            server_instance = mcp_server_instances[server_id]
            client = server_instance['client']
            
            # Execute MCP request
            if method == "list_tools":
                result = await client.list_tools()
                response_data = {"tools": result}
            elif method == "call_tool":
                tool_name = params.get('tool_name')
                tool_params = params.get('tool_params', {})
                result = await client.call_tool(tool_name, tool_params)
                response_data = {"result": result}
            elif method == "list_resources":
                result = await client.list_resources()
                response_data = {"resources": result}
            elif method == "read_resource":
                uri = params.get('uri')
                result = await client.read_resource(uri)
                response_data = {"content": result}
            else:
                logger.warning(f"Unknown method: {method}")
                response_data = {"error": f"Unknown method: {method}"}
        else:
            logger.warning(f"MCP server {server_id} not found")
            response_data = {"error": f"Server {server_id} not found"}
        
        # Send response back via Service Bus
        if service_bus_client and request_id:
            async with service_bus_client:
                sender = service_bus_client.get_topic_sender(topic_name="mcp-responses")
                async with sender:
                    response_message = ServiceBusMessage(
                        json.dumps({
                            "request_id": request_id,
                            "server_id": server_id,
                            "response": response_data
                        })
                    )
                    await sender.send_messages(response_message)
        
    except Exception as e:
        logger.error(f"Failed to handle MCP request: {e}", exc_info=True)


@app.function_name(name="MCPServerCommandHandler")
@app.service_bus_queue_trigger(
    connection="AZURE_SERVICE_BUS_CONNECTION_STRING",
    queue_name="mcp-server-commands",
    arg_name="message"
)
async def mcp_server_command_handler(message: func.ServiceBusMessage) -> None:
    """
    Handle MCP server lifecycle commands from AOS kernel.
    
    Commands include: start, stop, restart, reload_registry.
    """
    try:
        message_body = message.get_body().decode('utf-8')
        command_data = json.loads(message_body)
        
        command = command_data.get('command')
        server_id = command_data.get('server_id')
        
        logger.info(f"Received command {command} for server {server_id}")
        
        if command == "start":
            if not server_registry:
                await load_server_registry()
            config = server_registry.get_server_by_id(server_id)
            if config:
                client = await instantiate_mcp_server(config)
                if client:
                    mcp_server_instances[server_id] = {
                        'client': client,
                        'config': config
                    }
        
        elif command == "stop":
            if server_id in mcp_server_instances:
                server_instance = mcp_server_instances[server_id]
                client = server_instance['client']
                if hasattr(client, 'cleanup'):
                    await client.cleanup()
                del mcp_server_instances[server_id]
        
        elif command == "restart":
            if server_id in mcp_server_instances:
                # Stop
                server_instance = mcp_server_instances[server_id]
                client = server_instance['client']
                if hasattr(client, 'cleanup'):
                    await client.cleanup()
                
                # Start
                config = server_instance['config']
                client = await instantiate_mcp_server(config)
                if client:
                    mcp_server_instances[server_id] = {
                        'client': client,
                        'config': config
                    }
        
        elif command == "reload_registry":
            await load_server_registry()
            await start_all_servers()
        
        else:
            logger.warning(f"Unknown command: {command}")
        
    except Exception as e:
        logger.error(f"Failed to handle MCP server command: {e}", exc_info=True)


@app.function_name(name="HealthCheck")
@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    try:
        status = {
            "status": "healthy",
            "active_servers": len(mcp_server_instances),
            "server_ids": list(mcp_server_instances.keys())
        }
        return func.HttpResponse(
            json.dumps(status),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"status": "unhealthy", "error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.function_name(name="GetServerStatus")
@app.route(route="servers/{server_id}/status", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
async def get_server_status(req: func.HttpRequest) -> func.HttpResponse:
    """Get status of a specific MCP server"""
    try:
        server_id = req.route_params.get('server_id')
        
        if server_id in mcp_server_instances:
            server_instance = mcp_server_instances[server_id]
            status = {
                "server_id": server_id,
                "status": "running",
                "server_name": server_instance['config'].server_name
            }
            return func.HttpResponse(
                json.dumps(status),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Server not found"}),
                mimetype="application/json",
                status_code=404
            )
    
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.function_name(name="ListServers")
@app.route(route="servers", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
async def list_servers(req: func.HttpRequest) -> func.HttpResponse:
    """List all registered MCP servers"""
    try:
        if not server_registry:
            await load_server_registry()
        
        servers = [
            {
                "server_id": config.server_id,
                "server_name": config.server_name,
                "server_type": config.server_type,
                "enabled": config.enabled,
                "status": "running" if config.server_id in mcp_server_instances else "stopped"
            }
            for config in server_registry.servers
        ]
        
        return func.HttpResponse(
            json.dumps({"servers": servers}),
            mimetype="application/json",
            status_code=200
        )
    
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
