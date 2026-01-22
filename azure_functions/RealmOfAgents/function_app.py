"""
RealmOfAgents Azure Functions App - Foundry Agent Service Runtime

Plug-and-play infrastructure for onboarding PurposeDrivenAgent(s) using 
Microsoft Foundry Agent Service (Azure AI Agents runtime).

PurposeDrivenAgent remains the core architectural component - it now uses
Foundry Agent Service as its runtime with Llama 3.3 70B fine-tuned using
domain-specific LoRA adapters.

Developers provide only configuration - Purpose, domain knowledge, and MCP server tools.
All agents reside as configuration - no code changes needed to onboard new agents.

Communicates with AgentOperatingSystem kernel over Azure Service Bus.
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

# Import AOS infrastructure
# Note: AgentOperatingSystem package must be installed in the deployment environment
# Install with: pip install git+https://github.com/ASISaga/AgentOperatingSystem.git
try:
    from AgentOperatingSystem.agents import (
        PurposeDrivenAgent, 
        PurposeDrivenAgentFoundry,  # Foundry-enabled version
        PerpetualAgent, 
        LeadershipAgent
    )
    from AgentOperatingSystem.mcp.client_manager import MCPClientManager
    from AgentOperatingSystem.ml.pipeline_ops import trigger_lora_training
except ImportError as e:
    logger = logging.getLogger("RealmOfAgents")
    logger.error(f"Failed to import AgentOperatingSystem: {e}")
    logger.error("Please ensure AgentOperatingSystem is installed: pip install git+https://github.com/ASISaga/AgentOperatingSystem.git")
    raise

from agent_config_schema import AgentConfiguration, AgentRegistry, AgentType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RealmOfAgents.Foundry")

# Global state
agent_instances: Dict[str, Any] = {}
agent_registry: Optional[AgentRegistry] = None
mcp_client_manager: Optional[MCPClientManager] = None

# Foundry runtime configuration
USE_FOUNDRY_RUNTIME = os.getenv('USE_FOUNDRY_RUNTIME', 'true').lower() == 'true'


app = func.FunctionApp()

async def load_agent_registry() -> AgentRegistry:
    """
    Load agent registry from Azure Blob Storage.
    
    The registry contains all agent configurations.
    """
    global agent_registry
    
    try:
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        container_name = os.getenv('AGENT_CONFIG_BLOB_CONTAINER', 'agent-configs')
        
        if not connection_string:
            logger.warning("No storage connection string - using empty registry")
            return AgentRegistry(agents=[])
        
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="agent_registry.json"
        )
        
        # Download registry
        download_stream = await blob_client.download_blob()
        registry_data = await download_stream.readall()
        registry_json = json.loads(registry_data)
        
        agent_registry = AgentRegistry(**registry_json)
        logger.info(f"Loaded {len(agent_registry.agents)} agent configurations")
        
        return agent_registry
        
    except Exception as e:
        logger.error(f"Failed to load agent registry: {e}")
        return AgentRegistry(agents=[])


async def initialize_mcp_client_manager():
    """Initialize MCP client manager for accessing MCP tools"""
    global mcp_client_manager
    
    try:
        service_bus_conn = os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')
        if not service_bus_conn:
            logger.warning("No Service Bus connection - MCP tools unavailable")
            return
        
        mcp_client_manager = MCPClientManager()
        logger.info("MCP client manager initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP client manager: {e}")


async def instantiate_agent(config: AgentConfiguration) -> Optional[Any]:
    """
    Instantiate an agent from configuration.
    
    This is the core of the plug-and-play infrastructure - agents are
    created entirely from configuration, no code changes needed.
    
    When USE_FOUNDRY_RUNTIME is enabled, PurposeDrivenAgent uses Microsoft
    Foundry Agent Service with Llama 3.3 70B fine-tuned using domain-specific
    LoRA adapters.
    """
    try:
        logger.info(f"Instantiating agent {config.agent_id} of type {config.agent_type} "
                   f"(Foundry runtime: {USE_FOUNDRY_RUNTIME})")
        
        # Prepare MCP tools from registry
        tools = []
        if mcp_client_manager and config.mcp_tools:
            for tool_ref in config.mcp_tools:
                try:
                    # Get tool from MCP server via Service Bus
                    tool = await mcp_client_manager.get_tool(
                        server_name=tool_ref.server_name,
                        tool_name=tool_ref.tool_name
                    )
                    if tool:
                        tools.append(tool)
                except Exception as e:
                    logger.warning(f"Failed to load tool {tool_ref.tool_name}: {e}")
        
        # Instantiate agent based on type
        if config.agent_type == AgentType.PURPOSE_DRIVEN:
            if USE_FOUNDRY_RUNTIME:
                # Use PurposeDrivenAgentFoundry with Llama 3.3 70B + LoRA adapter
                agent = PurposeDrivenAgentFoundry(
                    agent_id=config.agent_id,
                    purpose=config.purpose,
                    purpose_scope=config.purpose_scope,
                    success_criteria=config.success_criteria,
                    tools=tools,
                    system_message=config.system_message,
                    adapter_name=config.domain_knowledge.domain,  # LoRA adapter name
                    foundry_endpoint=os.getenv('AZURE_AI_PROJECT_ENDPOINT'),
                    model_deployment=os.getenv('AZURE_AI_MODEL_DEPLOYMENT', 'llama-3.3-70b')
                )
                logger.info(f"Created {config.agent_id} with Foundry runtime "
                           f"(Llama 3.3 70B + {config.domain_knowledge.domain} LoRA)")
            else:
                # Use standard PurposeDrivenAgent (legacy mode)
                agent = PurposeDrivenAgent(
                    agent_id=config.agent_id,
                    purpose=config.purpose,
                    purpose_scope=config.purpose_scope,
                    success_criteria=config.success_criteria,
                    tools=tools,
                    system_message=config.system_message,
                    adapter_name=config.domain_knowledge.domain
                )
        elif config.agent_type == AgentType.PERPETUAL:
            agent = PerpetualAgent(
                agent_id=config.agent_id,
                tools=tools,
                system_message=config.system_message,
                adapter_name=config.domain_knowledge.domain
            )
        elif config.agent_type == AgentType.LEADERSHIP:
            agent = LeadershipAgent(
                agent_id=config.agent_id,
                name=config.agent_id.upper(),
                role=config.agent_id.upper()
            )
        else:
            logger.error(f"Unknown agent type: {config.agent_type}")
            return None
        
        # Initialize the agent
        # For Foundry agents, this creates the agent on Azure AI Agents runtime
        await agent.initialize()
        
        # Note: LoRA adapter training would be done separately via ML pipeline
        # The adapter_name (domain_knowledge.domain) is used to reference the
        # fine-tuned Llama 3.3 70B model deployment
        
        logger.info(f"Agent {config.agent_id} instantiated successfully")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to instantiate agent {config.agent_id}: {e}")
        return None


async def start_all_agents():
    """Start all enabled agents from the registry"""
    global agent_instances, agent_registry
    
    if not agent_registry:
        agent_registry = await load_agent_registry()
    
    enabled_agents = agent_registry.get_enabled_agents()
    logger.info(f"Starting {len(enabled_agents)} enabled agents")
    
    for config in enabled_agents:
        if config.agent_id not in agent_instances:
            agent = await instantiate_agent(config)
            if agent:
                agent_instances[config.agent_id] = agent
                # Start perpetual operation
                await agent.start()


@app.function_name(name="StartupTrigger")
@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=True)
async def startup_trigger(timer: func.TimerRequest) -> None:
    """
    Startup trigger - initializes and starts all agents on app startup.
    
    This function runs on app startup and periodically to ensure all
    configured agents are running.
    """
    logger.info("RealmOfAgents startup triggered")
    
    try:
        # Initialize MCP client manager
        if not mcp_client_manager:
            await initialize_mcp_client_manager()
        
        # Start all agents
        await start_all_agents()
        
        logger.info(f"RealmOfAgents running with {len(agent_instances)} active agents")
        
    except Exception as e:
        logger.error(f"Startup trigger failed: {e}", exc_info=True)


@app.function_name(name="AgentEventHandler")
@app.service_bus_topic_trigger(
    connection="AZURE_SERVICE_BUS_CONNECTION_STRING",
    topic_name="agent-events",
    subscription_name="genesis-agents",
    arg_name="message"
)
async def agent_event_handler(message: func.ServiceBusMessage) -> None:
    """
    Handle agent events from AOS kernel via Service Bus.
    
    Events are routed to the appropriate agent instance.
    """
    try:
        message_body = message.get_body().decode('utf-8')
        event_data = json.loads(message_body)
        
        agent_id = event_data.get('agent_id')
        event_type = event_data.get('event_type')
        payload = event_data.get('payload', {})
        
        logger.info(f"Received event {event_type} for agent {agent_id}")
        
        # Route to agent
        if agent_id in agent_instances:
            agent = agent_instances[agent_id]
            # Wake agent and process event
            if hasattr(agent, 'process_event'):
                await agent.process_event(event_type, payload)
        else:
            logger.warning(f"Agent {agent_id} not found in active instances")
            
    except Exception as e:
        logger.error(f"Failed to handle agent event: {e}", exc_info=True)


@app.function_name(name="AgentCommandHandler")
@app.service_bus_queue_trigger(
    connection="AZURE_SERVICE_BUS_CONNECTION_STRING",
    queue_name="agent-commands",
    arg_name="message"
)
async def agent_command_handler(message: func.ServiceBusMessage) -> None:
    """
    Handle agent commands from AOS kernel via Service Bus.
    
    Commands include lifecycle operations: start, stop, restart, configure.
    """
    try:
        message_body = message.get_body().decode('utf-8')
        command_data = json.loads(message_body)
        
        command = command_data.get('command')
        agent_id = command_data.get('agent_id')
        params = command_data.get('params', {})
        
        logger.info(f"Received command {command} for agent {agent_id}")
        
        if command == "start":
            # Load config and start agent
            if not agent_registry:
                await load_agent_registry()
            config = agent_registry.get_agent_by_id(agent_id)
            if config:
                agent = await instantiate_agent(config)
                if agent:
                    agent_instances[agent_id] = agent
                    await agent.start()
                    
        elif command == "stop":
            # Stop agent
            if agent_id in agent_instances:
                agent = agent_instances[agent_id]
                if hasattr(agent, 'stop'):
                    await agent.stop()
                del agent_instances[agent_id]
                
        elif command == "restart":
            # Restart agent
            if agent_id in agent_instances:
                agent = agent_instances[agent_id]
                if hasattr(agent, 'stop'):
                    await agent.stop()
                if hasattr(agent, 'start'):
                    await agent.start()
                    
        elif command == "reload_registry":
            # Reload agent registry
            await load_agent_registry()
            await start_all_agents()
            
        else:
            logger.warning(f"Unknown command: {command}")
            
    except Exception as e:
        logger.error(f"Failed to handle agent command: {e}", exc_info=True)


@app.function_name(name="HealthCheck")
@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    try:
        runtime_info = "Foundry Agent Service (Llama 3.3 70B + LoRA)" if USE_FOUNDRY_RUNTIME else "Custom Runtime"
        status = {
            "status": "healthy",
            "runtime": runtime_info,
            "active_agents": len(agent_instances),
            "agent_ids": list(agent_instances.keys())
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


@app.function_name(name="GetAgentStatus")
@app.route(route="agents/{agent_id}/status", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
async def get_agent_status(req: func.HttpRequest) -> func.HttpResponse:
    """Get status of a specific agent running on Foundry or custom runtime"""
    try:
        agent_id = req.route_params.get('agent_id')
        
        if agent_id in agent_instances:
            agent = agent_instances[agent_id]
            
            # Check if it's a Foundry agent
            is_foundry = isinstance(agent, PurposeDrivenAgentFoundry)
            
            status = {
                "agent_id": agent_id,
                "status": "running",
                "is_running": getattr(agent, 'is_running', False),
                "type": type(agent).__name__,
                "runtime": "Foundry Agent Service (Llama 3.3 70B + LoRA)" if is_foundry else "Custom Runtime"
            }
            
            # Add Foundry-specific details
            if is_foundry and hasattr(agent, 'foundry_agent'):
                status["foundry_agent_id"] = agent.foundry_agent.id if agent.foundry_agent else None
                status["foundry_thread_id"] = agent.foundry_thread.id if agent.foundry_thread else None
                status["lora_adapter"] = agent.lora_adapter_name
            
            return func.HttpResponse(
                json.dumps(status),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Agent not found"}),
                mimetype="application/json",
                status_code=404
            )
            
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
