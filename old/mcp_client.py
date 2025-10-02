"""
MCP (Model Context Protocol) Client Manager for AOS

Provides centralized MCP client functionality for Business Infinity to connect
legendary agents to LinkedIn, Reddit, ERPNext and other business integration
MCP servers through Azure Service Bus messaging.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Azure Service Bus imports
try:
    from azure.servicebus.aio import ServiceBusClient
    from azure.servicebus import ServiceBusMessage
    from azure.identity.aio import DefaultAzureCredential
    AZURE_SERVICE_BUS_AVAILABLE = True
except ImportError:
    AZURE_SERVICE_BUS_AVAILABLE = False
    logging.warning("Azure Service Bus SDK not available")

# MCP Protocol imports (assuming mcp-python package)
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP Python SDK not available")


class MCPServerType(Enum):
    """Types of MCP servers supported"""
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    ERPNEXT = "erpnext"
    CUSTOM = "custom"


class MCPConnectionStatus(Enum):
    """MCP connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection"""
    server_id: str
    server_type: MCPServerType
    server_name: str
    azure_function_url: str
    service_bus_topic: str
    connection_params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    capabilities: List[str] = field(default_factory=list)


@dataclass
class MCPRequest:
    """MCP request wrapper"""
    request_id: str
    server_id: str
    method: str
    params: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    timeout: Optional[datetime] = None
    callback: Optional[Callable] = None


@dataclass
class MCPResponse:
    """MCP response wrapper"""
    request_id: str
    server_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class MCPClientManager:
    """
    MCP Client Manager for AOS integration with Business Infinity.
    
    Manages connections to multiple MCP servers through Azure Service Bus,
    providing unified interface for business data integration across
    LinkedIn, Reddit, ERPNext, and custom MCP servers.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Azure Service Bus configuration
        self.service_bus_namespace = os.getenv("AZURE_SERVICE_BUS_NAMESPACE")
        self.service_bus_connection_string = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")
        
        # MCP server configurations
        self.server_configs: Dict[str, MCPServerConfig] = {}
        self.server_connections: Dict[str, Any] = {}  # MCP client sessions
        self.connection_status: Dict[str, MCPConnectionStatus] = {}
        
        # Request/response tracking
        self.pending_requests: Dict[str, MCPRequest] = {}
        self.request_callbacks: Dict[str, Callable] = {}
        
        # Service Bus clients
        self.service_bus_client = None
        self.response_processors: Dict[str, asyncio.Task] = {}
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        }
    
    async def initialize(self):
        """Initialize MCP Client Manager"""
        try:
            self.logger.info("Initializing AOS MCP Client Manager...")
            
            # Initialize Azure Service Bus
            if AZURE_SERVICE_BUS_AVAILABLE and (self.service_bus_connection_string or self.service_bus_namespace):
                await self._initialize_service_bus()
            
            # Load MCP server configurations
            await self._load_server_configurations()
            
            # Initialize MCP server connections
            await self._initialize_mcp_connections()
            
            # Start response processors
            await self._start_response_processors()
            
            self.logger.info("MCP Client Manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP Client Manager: {e}")
            raise
    
    async def _initialize_service_bus(self):
        """Initialize Azure Service Bus client"""
        try:
            if self.service_bus_connection_string:
                self.service_bus_client = ServiceBusClient.from_connection_string(
                    self.service_bus_connection_string
                )
            elif self.service_bus_namespace:
                credential = DefaultAzureCredential()
                self.service_bus_client = ServiceBusClient(
                    fully_qualified_namespace=f"{self.service_bus_namespace}.servicebus.windows.net",
                    credential=credential
                )
            
            self.logger.info("Azure Service Bus client initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Service Bus: {e}")
            raise
    
    async def _load_server_configurations(self):
        """Load MCP server configurations"""
        try:
            # Built-in server configurations
            builtin_configs = self._get_builtin_server_configs()
            
            for config in builtin_configs:
                self.server_configs[config.server_id] = config
                self.connection_status[config.server_id] = MCPConnectionStatus.DISCONNECTED
            
            # Load custom configurations from environment or config file
            custom_config_path = os.getenv("MCP_SERVER_CONFIG_PATH", "config/mcp_servers.json")
            if os.path.exists(custom_config_path):
                with open(custom_config_path, 'r', encoding='utf-8') as f:
                    custom_configs = json.load(f)
                
                for config_data in custom_configs:
                    config = MCPServerConfig(
                        server_id=config_data["server_id"],
                        server_type=MCPServerType(config_data["server_type"]),
                        server_name=config_data["server_name"],
                        azure_function_url=config_data["azure_function_url"],
                        service_bus_topic=config_data["service_bus_topic"],
                        connection_params=config_data.get("connection_params", {}),
                        enabled=config_data.get("enabled", True),
                        max_retries=config_data.get("max_retries", 3),
                        timeout_seconds=config_data.get("timeout_seconds", 30),
                        capabilities=config_data.get("capabilities", [])
                    )
                    
                    self.server_configs[config.server_id] = config
                    self.connection_status[config.server_id] = MCPConnectionStatus.DISCONNECTED
            
            self.logger.info(f"Loaded {len(self.server_configs)} MCP server configurations")
            
        except Exception as e:
            self.logger.error(f"Failed to load server configurations: {e}")
    
    def _get_builtin_server_configs(self) -> List[MCPServerConfig]:
        """Get built-in MCP server configurations"""
        return [
            MCPServerConfig(
                server_id="linkedin_mcp",
                server_type=MCPServerType.LINKEDIN,
                server_name="LinkedIn MCP Server",
                azure_function_url=os.getenv("LINKEDIN_MCP_FUNCTION_URL", "https://linkedin-mcp.azurewebsites.net"),
                service_bus_topic="linkedin-requests",
                connection_params={
                    "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
                    "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET")
                },
                capabilities=[
                    "profile_access",
                    "connection_management",
                    "content_publishing",
                    "analytics_access"
                ]
            ),
            MCPServerConfig(
                server_id="reddit_mcp",
                server_type=MCPServerType.REDDIT,
                server_name="Reddit MCP Server",
                azure_function_url=os.getenv("REDDIT_MCP_FUNCTION_URL", "https://reddit-mcp.azurewebsites.net"),
                service_bus_topic="reddit-requests",
                connection_params={
                    "client_id": os.getenv("REDDIT_CLIENT_ID"),
                    "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
                    "user_agent": "BusinessInfinity/1.0"
                },
                capabilities=[
                    "subreddit_access",
                    "post_management",
                    "comment_management",
                    "user_analytics"
                ]
            ),
            MCPServerConfig(
                server_id="erpnext_mcp",
                server_type=MCPServerType.ERPNEXT,
                server_name="ERPNext MCP Server",
                azure_function_url=os.getenv("ERPNEXT_MCP_FUNCTION_URL", "https://erpnext-mcp.azurewebsites.net"),
                service_bus_topic="erpnext-requests",
                connection_params={
                    "server_url": os.getenv("ERPNEXT_SERVER_URL"),
                    "api_key": os.getenv("ERPNEXT_API_KEY"),
                    "api_secret": os.getenv("ERPNEXT_API_SECRET")
                },
                capabilities=[
                    "customer_management",
                    "sales_analytics",
                    "inventory_access",
                    "financial_reporting"
                ]
            )
        ]
    
    async def _initialize_mcp_connections(self):
        """Initialize connections to MCP servers"""
        connection_tasks = []
        
        for server_id, config in self.server_configs.items():
            if config.enabled:
                task = asyncio.create_task(self._connect_to_server(server_id))
                connection_tasks.append(task)
        
        if connection_tasks:
            await asyncio.gather(*connection_tasks, return_exceptions=True)
    
    async def _connect_to_server(self, server_id: str):
        """Connect to a specific MCP server"""
        try:
            config = self.server_configs[server_id]
            self.connection_status[server_id] = MCPConnectionStatus.CONNECTING
            
            # For Azure Functions-based MCP servers, we use HTTP requests via Service Bus
            # rather than direct MCP connections
            
            # Test connection to Azure Function
            test_result = await self._test_server_connection(config)
            
            if test_result:
                self.connection_status[server_id] = MCPConnectionStatus.CONNECTED
                self.logger.info(f"Connected to MCP server: {config.server_name} ({server_id})")
            else:
                self.connection_status[server_id] = MCPConnectionStatus.ERROR
                self.logger.error(f"Failed to connect to MCP server: {config.server_name} ({server_id})")
            
        except Exception as e:
            self.connection_status[server_id] = MCPConnectionStatus.ERROR
            self.logger.error(f"Error connecting to MCP server {server_id}: {e}")
    
    async def _test_server_connection(self, config: MCPServerConfig) -> bool:
        """Test connection to an MCP server"""
        try:
            # For demo purposes, we'll assume connection is successful
            # In production, this would make an actual HTTP request to the Azure Function
            await asyncio.sleep(0.1)  # Simulate connection test
            return True
            
        except Exception as e:
            self.logger.error(f"Connection test failed for {config.server_name}: {e}")
            return False
    
    async def _start_response_processors(self):
        """Start response processors for each MCP server"""
        if not self.service_bus_client:
            return
        
        for server_id, config in self.server_configs.items():
            if config.enabled and self.connection_status[server_id] == MCPConnectionStatus.CONNECTED:
                task = asyncio.create_task(
                    self._process_responses(server_id, config.service_bus_topic + "-responses")
                )
                self.response_processors[server_id] = task\n    \n    async def _process_responses(self, server_id: str, response_topic: str):\n        \"\"\"Process responses from an MCP server\"\"\"\n        try:\n            async with self.service_bus_client.get_subscription_receiver(\n                topic_name=response_topic,\n                subscription_name=\"aos-client\"\n            ) as receiver:\n                \n                async for message in receiver:\n                    try:\n                        # Parse response message\n                        response_data = json.loads(str(message))\n                        \n                        # Create MCP response object\n                        response = MCPResponse(\n                            request_id=response_data[\"request_id\"],\n                            server_id=server_id,\n                            success=response_data.get(\"success\", False),\n                            data=response_data.get(\"data\"),\n                            error=response_data.get(\"error\")\n                        )\n                        \n                        # Process response\n                        await self._handle_mcp_response(response)\n                        \n                        # Complete the message\n                        await receiver.complete_message(message)\n                        \n                    except Exception as e:\n                        self.logger.error(f\"Error processing response from {server_id}: {e}\")\n                        await receiver.abandon_message(message)\n        \n        except Exception as e:\n            self.logger.error(f\"Error in response processor for {server_id}: {e}\")\n    \n    async def _handle_mcp_response(self, response: MCPResponse):\n        \"\"\"Handle an MCP response\"\"\"\n        try:\n            request_id = response.request_id\n            \n            # Update statistics\n            if response.success:\n                self.stats[\"successful_requests\"] += 1\n            else:\n                self.stats[\"failed_requests\"] += 1\n            \n            # Call callback if registered\n            if request_id in self.request_callbacks:\n                callback = self.request_callbacks[request_id]\n                try:\n                    if asyncio.iscoroutinefunction(callback):\n                        await callback(response)\n                    else:\n                        callback(response)\n                except Exception as e:\n                    self.logger.error(f\"Error in response callback: {e}\")\n                \n                del self.request_callbacks[request_id]\n            \n            # Remove from pending requests\n            if request_id in self.pending_requests:\n                del self.pending_requests[request_id]\n            \n        except Exception as e:\n            self.logger.error(f\"Error handling MCP response: {e}\")\n    \n    async def send_mcp_request(self, \n                              server_id: str, \n                              method: str, \n                              params: Dict[str, Any], \n                              callback: Optional[Callable] = None,\n                              timeout_seconds: Optional[int] = None) -> str:\n        \"\"\"\n        Send request to MCP server\n        \n        Args:\n            server_id: ID of the target MCP server\n            method: MCP method to call\n            params: Parameters for the method\n            callback: Optional callback for response handling\n            timeout_seconds: Optional timeout override\n            \n        Returns:\n            Request ID for tracking\n        \"\"\"\n        try:\n            if server_id not in self.server_configs:\n                raise ValueError(f\"MCP server {server_id} not configured\")\n            \n            if self.connection_status[server_id] != MCPConnectionStatus.CONNECTED:\n                raise RuntimeError(f\"MCP server {server_id} not connected\")\n            \n            config = self.server_configs[server_id]\n            request_id = str(uuid.uuid4())\n            \n            # Create request object\n            request = MCPRequest(\n                request_id=request_id,\n                server_id=server_id,\n                method=method,\n                params=params,\n                timeout=datetime.now() + timedelta(seconds=timeout_seconds or config.timeout_seconds),\n                callback=callback\n            )\n            \n            # Store request\n            self.pending_requests[request_id] = request\n            \n            if callback:\n                self.request_callbacks[request_id] = callback\n            \n            # Send request via Service Bus\n            if self.service_bus_client:\n                await self._send_request_via_service_bus(config, request)\n            else:\n                # Fallback to direct HTTP if Service Bus not available\n                await self._send_request_via_http(config, request)\n            \n            # Update statistics\n            self.stats[\"total_requests\"] += 1\n            \n            self.logger.debug(f\"Sent MCP request {request_id} to {server_id}\")\n            return request_id\n            \n        except Exception as e:\n            self.logger.error(f\"Failed to send MCP request: {e}\")\n            raise\n    \n    async def _send_request_via_service_bus(self, config: MCPServerConfig, request: MCPRequest):\n        \"\"\"Send MCP request via Azure Service Bus\"\"\"\n        try:\n            message_data = {\n                \"request_id\": request.request_id,\n                \"method\": request.method,\n                \"params\": request.params,\n                \"timestamp\": request.timestamp.isoformat(),\n                \"timeout\": request.timeout.isoformat() if request.timeout else None\n            }\n            \n            message = ServiceBusMessage(\n                json.dumps(message_data),\n                content_type=\"application/json\",\n                message_id=request.request_id\n            )\n            \n            async with self.service_bus_client.get_topic_sender(config.service_bus_topic) as sender:\n                await sender.send_messages(message)\n            \n        except Exception as e:\n            self.logger.error(f\"Failed to send request via Service Bus: {e}\")\n            raise\n    \n    async def _send_request_via_http(self, config: MCPServerConfig, request: MCPRequest):\n        \"\"\"Send MCP request via HTTP (fallback)\"\"\"\n        try:\n            # This would be implemented to send direct HTTP requests to Azure Functions\n            # For now, we'll just log the attempt\n            self.logger.info(f\"HTTP fallback not implemented for {config.server_name}\")\n            \n        except Exception as e:\n            self.logger.error(f\"Failed to send request via HTTP: {e}\")\n            raise\n    \n    async def get_server_capabilities(self, server_id: str) -> List[str]:\n        \"\"\"Get capabilities of a specific MCP server\"\"\"\n        if server_id not in self.server_configs:\n            return []\n        \n        return self.server_configs[server_id].capabilities\n    \n    async def get_server_status(self, server_id: str) -> Dict[str, Any]:\n        \"\"\"Get status of a specific MCP server\"\"\"\n        if server_id not in self.server_configs:\n            return {\"status\": \"not_found\"}\n        \n        config = self.server_configs[server_id]\n        status = self.connection_status[server_id]\n        \n        return {\n            \"server_id\": server_id,\n            \"server_name\": config.server_name,\n            \"server_type\": config.server_type.value,\n            \"status\": status.value,\n            \"enabled\": config.enabled,\n            \"capabilities\": config.capabilities,\n            \"azure_function_url\": config.azure_function_url,\n            \"pending_requests\": len([r for r in self.pending_requests.values() if r.server_id == server_id])\n        }\n    \n    async def list_servers(self) -> List[Dict[str, Any]]:\n        \"\"\"List all configured MCP servers\"\"\"\n        servers = []\n        \n        for server_id in self.server_configs.keys():\n            status = await self.get_server_status(server_id)\n            servers.append(status)\n        \n        return servers\n    \n    async def get_client_statistics(self) -> Dict[str, Any]:\n        \"\"\"Get MCP client statistics\"\"\"\n        total_requests = self.stats[\"total_requests\"]\n        \n        return {\n            **self.stats,\n            \"success_rate\": (self.stats[\"successful_requests\"] / total_requests * 100) if total_requests > 0 else 0,\n            \"connected_servers\": len([s for s in self.connection_status.values() if s == MCPConnectionStatus.CONNECTED]),\n            \"total_servers\": len(self.server_configs),\n            \"pending_requests\": len(self.pending_requests)\n        }\n    \n    async def reconnect_server(self, server_id: str) -> bool:\n        \"\"\"Reconnect to a specific MCP server\"\"\"\n        try:\n            if server_id not in self.server_configs:\n                return False\n            \n            self.connection_status[server_id] = MCPConnectionStatus.RECONNECTING\n            await self._connect_to_server(server_id)\n            \n            return self.connection_status[server_id] == MCPConnectionStatus.CONNECTED\n            \n        except Exception as e:\n            self.logger.error(f\"Failed to reconnect to server {server_id}: {e}\")\n            return False\n    \n    async def shutdown(self):\n        \"\"\"Graceful shutdown of MCP Client Manager\"\"\"\n        try:\n            # Cancel response processors\n            for task in self.response_processors.values():\n                task.cancel()\n            \n            # Wait for tasks to complete\n            if self.response_processors:\n                await asyncio.gather(*self.response_processors.values(), return_exceptions=True)\n            \n            # Close Service Bus client\n            if self.service_bus_client:\n                await self.service_bus_client.close()\n            \n            # Clear pending requests\n            self.pending_requests.clear()\n            self.request_callbacks.clear()\n            \n            self.logger.info(\"MCP Client Manager shutdown completed\")\n            \n        except Exception as e:\n            self.logger.error(f\"Error during MCP Client Manager shutdown: {e}\")\n    \n    # Convenience methods for specific MCP servers\n    \n    async def linkedin_request(self, method: str, params: Dict[str, Any], callback: Optional[Callable] = None) -> str:\n        \"\"\"Send request to LinkedIn MCP server\"\"\"\n        return await self.send_mcp_request(\"linkedin_mcp\", method, params, callback)\n    \n    async def reddit_request(self, method: str, params: Dict[str, Any], callback: Optional[Callable] = None) -> str:\n        \"\"\"Send request to Reddit MCP server\"\"\"\n        return await self.send_mcp_request(\"reddit_mcp\", method, params, callback)\n    \n    async def erpnext_request(self, method: str, params: Dict[str, Any], callback: Optional[Callable] = None) -> str:\n        \"\"\"Send request to ERPNext MCP server\"\"\"\n        return await self.send_mcp_request(\"erpnext_mcp\", method, params, callback)