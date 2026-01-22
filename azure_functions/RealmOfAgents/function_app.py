"""
RealmOfAgents Azure Functions App - Foundry Agent Service Runtime

Plug-and-play infrastructure for onboarding PurposeDrivenAgent(s) using 
Microsoft Foundry Agent Service (Azure AI Agents runtime).

Developers provide only configuration - Purpose, domain knowledge, and MCP server tools.
Agents run on Azure AI Agents runtime instead of custom instantiation.

Communicates with AgentOperatingSystem kernel over Azure Service Bus.
"""

import logging
import json
import os
import asyncio
from typing import Dict, Any, Optional, List
import azure.functions as func
from azure.servicebus.aio import ServiceBusClient, ServiceBusMessage
from azure.storage.blob.aio import BlobServiceClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    Agent,
    AgentThread,
    ThreadRun,
    FunctionTool,
    FunctionDefinition,
    ToolSet,
)

# Import agent configuration schema
from agent_config_schema import AgentConfiguration, AgentRegistry, AgentType, MCPToolReference

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RealmOfAgents.Foundry")

# Global state
agent_clients: Dict[str, Agent] = {}  # Map of agent_id -> Agent object from Azure AI
agents_client: Optional[AgentsClient] = None  # Azure AI Agents runtime client
agent_registry: Optional[AgentRegistry] = None
agent_threads: Dict[str, AgentThread] = {}  # Map of agent_id -> active thread


app = func.FunctionApp()


async def get_agents_client() -> AgentsClient:
    """
    Initialize and return Azure AI Agents client.
    
    This replaces the custom agent instantiation with the official Azure AI Agents runtime.
    """
    global agents_client
    
    if agents_client:
        return agents_client
    
    try:
        # Get configuration from environment
        endpoint = os.getenv('AZURE_AI_PROJECT_ENDPOINT')
        if not endpoint:
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT not configured")
        
        # Use DefaultAzureCredential for authentication
        credential = DefaultAzureCredential()
        
        # Initialize AgentsClient - this is the Foundry Agent Service runtime
        agents_client = AgentsClient(endpoint=endpoint, credential=credential)
        
        logger.info(f"Initialized Azure AI Agents client with endpoint: {endpoint}")
        return agents_client
        
    except Exception as e:
        logger.error(f"Failed to initialize Azure AI Agents client: {e}")
        raise


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


async def convert_mcp_tools_to_function_tools(
    mcp_tools: List[MCPToolReference]
) -> List[FunctionTool]:
    """
    Convert MCP tool references to Azure AI Agents FunctionTool definitions.
    
    This bridges between MCP tools (hosted on MCPServers function app) and
    Azure AI Agents runtime.
    """
    function_tools = []
    
    for tool_ref in mcp_tools:
        try:
            # Create a function definition that will call the MCP server
            # The actual execution will be handled by Service Bus communication
            function_def = FunctionDefinition(
                name=f"{tool_ref.server_name}_{tool_ref.tool_name}",
                description=f"Execute {tool_ref.tool_name} from {tool_ref.server_name} MCP server",
                parameters={
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Input for the tool"
                        }
                    },
                    "required": ["input"]
                }
            )
            
            function_tool = FunctionTool(function=function_def)
            function_tools.append(function_tool)
            
            logger.debug(f"Converted MCP tool: {tool_ref.server_name}.{tool_ref.tool_name}")
            
        except Exception as e:
            logger.warning(f"Failed to convert MCP tool {tool_ref.tool_name}: {e}")
    
    return function_tools


async def create_agent_on_foundry(config: AgentConfiguration) -> Optional[Agent]:
    """
    Create an agent on Azure AI Agents runtime (Foundry Agent Service).
    
    This replaces custom PurposeDrivenAgent instantiation with native Azure AI Agents.
    
    Args:
        config: Agent configuration from registry
        
    Returns:
        Agent object from Azure AI Agents runtime
    """
    try:
        client = await get_agents_client()
        
        logger.info(f"Creating agent {config.agent_id} on Azure AI Agents runtime")
        
        # Convert MCP tools to function tools
        tools = await convert_mcp_tools_to_function_tools(config.mcp_tools)
        
        # Create toolset
        toolset = ToolSet() if tools else None
        if tools:
            for tool in tools:
                toolset.add_tool(tool)
        
        # Construct instructions from purpose
        instructions = f"""You are {config.agent_id}, a purpose-driven AI agent.

Purpose: {config.purpose}
"""
        
        if config.purpose_scope:
            instructions += f"\nScope: {config.purpose_scope}"
        
        if config.success_criteria:
            instructions += f"\n\nSuccess Criteria:"
            for criterion in config.success_criteria:
                instructions += f"\n- {criterion}"
        
        if config.system_message:
            instructions += f"\n\n{config.system_message}"
        
        # Get model deployment name from environment
        model = os.getenv('AZURE_AI_MODEL_DEPLOYMENT', 'gpt-4')
        
        # Create agent on Azure AI Agents runtime
        agent = await client.create_agent(
            model=model,
            name=config.agent_id,
            description=config.purpose,
            instructions=instructions,
            toolset=toolset,
            metadata={
                "agent_type": config.agent_type.value,
                "domain": config.domain_knowledge.domain,
                "aos_agent_id": config.agent_id,
            }
        )
        
        logger.info(f"Created agent {config.agent_id} on Foundry runtime: {agent.id}")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create agent {config.agent_id} on Foundry runtime: {e}")
        return None


async def start_all_agents():
    """
    Create all enabled agents on Azure AI Agents runtime.
    
    This replaces the custom agent instantiation with Foundry Agent Service.
    """
    global agent_clients, agent_registry
    
    if not agent_registry:
        agent_registry = await load_agent_registry()
    
    enabled_agents = agent_registry.get_enabled_agents()
    logger.info(f"Creating {len(enabled_agents)} enabled agents on Azure AI Agents runtime")
    
    for config in enabled_agents:
        if config.agent_id not in agent_clients:
            agent = await create_agent_on_foundry(config)
            if agent:
                agent_clients[config.agent_id] = agent
                logger.info(f"Agent {config.agent_id} running on Foundry runtime")


async def get_or_create_thread(agent_id: str) -> Optional[AgentThread]:
    """
    Get or create a thread for an agent.
    
    Threads in Azure AI Agents provide stateful conversation context.
    """
    global agent_threads
    
    try:
        if agent_id in agent_threads:
            return agent_threads[agent_id]
        
        client = await get_agents_client()
        
        # Create new thread
        thread = await client.create_thread()
        agent_threads[agent_id] = thread
        
        logger.info(f"Created thread {thread.id} for agent {agent_id}")
        return thread
        
    except Exception as e:
        logger.error(f"Failed to create thread for agent {agent_id}: {e}")
        return None


async def process_agent_event(agent_id: str, event_type: str, payload: Dict[str, Any]):
    """
    Process an event for an agent using Azure AI Agents runtime.
    
    This replaces the custom agent event processing with Foundry Agent Service.
    """
    try:
        if agent_id not in agent_clients:
            logger.warning(f"Agent {agent_id} not found in Foundry runtime")
            return
        
        agent = agent_clients[agent_id]
        thread = await get_or_create_thread(agent_id)
        
        if not thread:
            logger.error(f"No thread available for agent {agent_id}")
            return
        
        client = await get_agents_client()
        
        # Format the event as a message
        message_content = f"Event: {event_type}\nPayload: {json.dumps(payload, indent=2)}"
        
        # Create and run using Azure AI Agents runtime
        run = await client.create_thread_and_process_run(
            agent_id=agent.id,
            thread=thread,
            additional_messages=[{"role": "user", "content": message_content}]
        )
        
        logger.info(f"Agent {agent_id} processed event {event_type} on Foundry runtime: {run.status}")
        
        # TODO: Extract response and send back via Service Bus
        
    except Exception as e:
        logger.error(f"Failed to process event for agent {agent_id}: {e}")


@app.function_name(name="StartupTrigger")
@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=True)
async def startup_trigger(timer: func.TimerRequest) -> None:
    """
    Startup trigger - initializes and creates all agents on Azure AI Agents runtime.
    
    This function runs on app startup and periodically to ensure all
    configured agents are running on Foundry Agent Service.
    """
    logger.info("RealmOfAgents startup triggered - using Azure AI Agents runtime")
    
    try:
        # Initialize Azure AI Agents client
        await get_agents_client()
        
        # Create all agents on Foundry runtime
        await start_all_agents()
        
        logger.info(f"RealmOfAgents running with {len(agent_clients)} agents on Foundry runtime")
        
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
    
    Events are processed by agents running on Azure AI Agents runtime.
    """
    try:
        message_body = message.get_body().decode('utf-8')
        event_data = json.loads(message_body)
        
        agent_id = event_data.get('agent_id')
        event_type = event_data.get('event_type')
        payload = event_data.get('payload', {})
        
        logger.info(f"Received event {event_type} for agent {agent_id}")
        
        # Process event on Foundry Agent Service
        await process_agent_event(agent_id, event_type, payload)
            
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
    Uses Azure AI Agents runtime for agent management.
    """
    try:
        message_body = message.get_body().decode('utf-8')
        command_data = json.loads(message_body)
        
        command = command_data.get('command')
        agent_id = command_data.get('agent_id')
        params = command_data.get('params', {})
        
        logger.info(f"Received command {command} for agent {agent_id}")
        
        client = await get_agents_client()
        
        if command == "start":
            # Load config and create agent on Foundry runtime
            if not agent_registry:
                await load_agent_registry()
            config = agent_registry.get_agent_by_id(agent_id)
            if config:
                agent = await create_agent_on_foundry(config)
                if agent:
                    agent_clients[agent_id] = agent
                    
        elif command == "stop":
            # Delete agent from Foundry runtime
            if agent_id in agent_clients:
                agent = agent_clients[agent_id]
                await client.delete_agent(agent.id)
                del agent_clients[agent_id]
                logger.info(f"Deleted agent {agent_id} from Foundry runtime")
                
        elif command == "restart":
            # Restart = stop + start on Foundry runtime
            if agent_id in agent_clients:
                agent = agent_clients[agent_id]
                await client.delete_agent(agent.id)
                del agent_clients[agent_id]
            
            if not agent_registry:
                await load_agent_registry()
            config = agent_registry.get_agent_by_id(agent_id)
            if config:
                agent = await create_agent_on_foundry(config)
                if agent:
                    agent_clients[agent_id] = agent
                    
        elif command == "reload_registry":
            # Reload agent registry and recreate all agents
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
        status = {
            "status": "healthy",
            "runtime": "Azure AI Agents (Foundry Agent Service)",
            "active_agents": len(agent_clients),
            "agent_ids": list(agent_clients.keys())
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
    """Get status of a specific agent running on Azure AI Agents runtime"""
    try:
        agent_id = req.route_params.get('agent_id')
        
        if agent_id in agent_clients:
            agent = agent_clients[agent_id]
            status = {
                "agent_id": agent_id,
                "runtime": "Azure AI Agents (Foundry)",
                "status": "running",
                "foundry_agent_id": agent.id,
                "model": agent.model
            }
            return func.HttpResponse(
                json.dumps(status),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Agent not found on Foundry runtime"}),
                mimetype="application/json",
                status_code=404
            )
            
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
