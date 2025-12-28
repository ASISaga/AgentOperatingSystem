"""
AgentOperatingSystem Azure Functions Application

This is the main entry point for the AgentOperatingSystem Azure Functions application.
It exposes AOS services via Azure Service Bus for consumption by other applications
like BusinessInfinity.

Architecture:
    ┌─────────────────────────────────────────────┐
    │         Client Applications                 │
    │  (BusinessInfinity, MCP Servers, etc.)      │
    └─────────────────────────────────────────────┘
                         │
                   Azure Service Bus
                         │
                         ▼
    ┌─────────────────────────────────────────────┐
    │     AgentOperatingSystem Functions          │
    │  • Service Bus triggers for requests        │
    │  • HTTP endpoints for health/status         │
    │  • Timer triggers for maintenance           │
    └─────────────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────┐
    │       AgentOperatingSystem Core             │
    │  • Agents, Storage, Orchestration           │
    │  • ML Pipeline, MCP, Monitoring             │
    └─────────────────────────────────────────────┘
"""

import logging
import json
import os
import asyncio
from typing import Optional
from datetime import datetime

import azure.functions as func

# Import AOS components
try:
    from AgentOperatingSystem import AgentOperatingSystem, AOSConfig
    from AgentOperatingSystem.messaging.contracts import (
        AOSMessage,
        AOSMessageType,
        AOSQueues,
    )
    from AgentOperatingSystem.messaging.servicebus_handlers import AOSServiceBusHandlers
    from AgentOperatingSystem.messaging.servicebus_manager import ServiceBusManager
    AOS_AVAILABLE = True
except ImportError as e:
    logging.error(f"Failed to import AOS: {e}")
    AOS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("AOS.Functions")

# Global state
aos_instance: Optional[AgentOperatingSystem] = None
handlers: Optional[AOSServiceBusHandlers] = None
servicebus_manager: Optional[ServiceBusManager] = None

# Create the Azure Functions app
app = func.FunctionApp()


async def initialize_aos() -> AgentOperatingSystem:
    """Initialize the AgentOperatingSystem instance."""
    global aos_instance, handlers, servicebus_manager
    
    if aos_instance:
        return aos_instance
    
    try:
        logger.info("Initializing AgentOperatingSystem...")
        
        # Create AOS config from environment
        config = AOSConfig(
            storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
            servicebus_connection_string=os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING"),
            app_insights_connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"),
            environment=os.getenv("APP_ENVIRONMENT", "production"),
        )
        
        # Initialize AOS
        aos_instance = AgentOperatingSystem(config)
        await aos_instance.initialize()
        
        # Initialize handlers
        handlers = AOSServiceBusHandlers(aos_instance)
        
        # Initialize Service Bus manager for sending responses
        servicebus_manager = ServiceBusManager(
            os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")
        )
        
        logger.info("AgentOperatingSystem initialized successfully")
        return aos_instance
        
    except Exception as e:
        logger.error(f"Failed to initialize AOS: {e}")
        raise


async def send_response(message: AOSMessage, queue_name: str):
    """Send response message to Service Bus queue."""
    global servicebus_manager
    
    if not servicebus_manager or not servicebus_manager.client:
        logger.warning("Service Bus client not available, cannot send response")
        return
    
    try:
        async with servicebus_manager.client.get_queue_sender(queue_name) as sender:
            from azure.servicebus import ServiceBusMessage
            sb_message = ServiceBusMessage(
                body=message.to_json(),
                content_type="application/json",
                correlation_id=message.header.correlation_id,
                message_id=message.header.message_id,
            )
            await sender.send_messages(sb_message)
            logger.info(f"Sent response to {queue_name}: {message.header.message_type}")
    except Exception as e:
        logger.error(f"Failed to send response: {e}")


# =============================================================================
# HTTP Endpoints
# =============================================================================

@app.function_name("health")
@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    try:
        global aos_instance
        
        status = "healthy" if aos_instance else "initializing"
        health_data = {
            "service": "AgentOperatingSystem",
            "status": status,
            "version": "1.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "aos_available": AOS_AVAILABLE,
        }
        
        status_code = 200 if status == "healthy" else 503
        return func.HttpResponse(
            body=json.dumps(health_data),
            status_code=status_code,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        return func.HttpResponse(
            body=json.dumps({"status": "error", "error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"},
        )


@app.function_name("status")
@app.route(route="status", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
async def status(req: func.HttpRequest) -> func.HttpResponse:
    """Detailed status endpoint."""
    try:
        global aos_instance
        
        if not aos_instance:
            return func.HttpResponse(
                body=json.dumps({"error": "AOS not initialized"}),
                status_code=503,
                headers={"Content-Type": "application/json"},
            )
        
        status_data = {
            "service": "AgentOperatingSystem",
            "status": "operational",
            "version": "1.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "storage": aos_instance.storage_manager is not None if hasattr(aos_instance, 'storage_manager') else False,
                "messaging": True,
                "ml_pipeline": aos_instance.ml_pipeline is not None if hasattr(aos_instance, 'ml_pipeline') else False,
            }
        }
        
        return func.HttpResponse(
            body=json.dumps(status_data),
            status_code=200,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"},
        )


@app.function_name("agents")
@app.route(route="agents", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
    """List available agents."""
    try:
        global aos_instance
        
        if aos_instance and hasattr(aos_instance, 'list_agents'):
            agents = aos_instance.list_agents()
        else:
            agents = [
                {"id": "ceo", "name": "CEO Agent", "status": "available"},
                {"id": "cto", "name": "CTO Agent", "status": "available"},
                {"id": "cfo", "name": "CFO Agent", "status": "available"},
            ]
        
        return func.HttpResponse(
            body=json.dumps({"agents": agents}),
            status_code=200,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"},
        )


# =============================================================================
# Service Bus Triggers
# =============================================================================

@app.function_name("process_aos_request")
@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="aos-requests",
    connection="AzureServiceBusConnectionString"
)
async def process_aos_request(msg: func.ServiceBusMessage):
    """
    Process incoming AOS requests from Service Bus queue.
    
    This is the main entry point for all requests from external applications.
    """
    global handlers
    
    try:
        # Initialize AOS if needed
        if not handlers:
            await initialize_aos()
        
        # Parse message
        message_body = msg.get_body().decode('utf-8')
        aos_message = AOSMessage.from_json(message_body)
        
        logger.info(f"Received request: {aos_message.header.message_type} from {aos_message.header.source}")
        
        # Process message
        response = await handlers.process_message(aos_message)
        
        # Determine response queue
        reply_to = aos_message.header.reply_to
        if not reply_to:
            # Default response queue based on source
            source = aos_message.header.source
            if source.lower() == "businessinfinity":
                reply_to = AOSQueues.BUSINESS_INFINITY_RESPONSES
            else:
                reply_to = f"{source.lower()}-responses"
        
        # Send response
        await send_response(response, reply_to)
        
        logger.info(f"Processed request: {aos_message.header.message_type}, sent response to {reply_to}")
        
    except Exception as e:
        logger.error(f"Error processing Service Bus message: {e}")
        raise


# =============================================================================
# Timer Triggers (Maintenance)
# =============================================================================

@app.function_name("maintenance")
@app.timer_trigger(schedule="0 */30 * * * *", arg_name="timer", run_on_startup=False)
async def maintenance(timer: func.TimerRequest):
    """
    Periodic maintenance tasks.
    
    Runs every 30 minutes to perform cleanup, health checks, etc.
    """
    global aos_instance
    
    try:
        logger.info("Running maintenance tasks...")
        
        if aos_instance:
            # Perform any maintenance tasks
            if hasattr(aos_instance, 'run_maintenance'):
                await aos_instance.run_maintenance()
        
        logger.info("Maintenance tasks completed")
        
    except Exception as e:
        logger.error(f"Error during maintenance: {e}")


# =============================================================================
# Startup
# =============================================================================

@app.function_name("startup")
@app.timer_trigger(schedule="0 0 0 1 1 *", arg_name="timer", run_on_startup=True)
async def startup(timer: func.TimerRequest):
    """
    Startup initialization.
    
    Triggered on function app startup to initialize AOS.
    """
    try:
        logger.info("AOS Functions starting up...")
        await initialize_aos()
        logger.info("AOS Functions startup complete")
    except Exception as e:
        logger.error(f"Startup error: {e}")
