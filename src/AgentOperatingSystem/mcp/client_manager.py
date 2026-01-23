"""
AOS MCP Client Manager

Centralized management of MCP (Model Context Protocol) server connections for AOS.
Handles connections to LinkedIn, Reddit, ERPNext, and other MCP servers through Azure Service Bus.
"""

import asyncio
import logging
import json
import os
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# Azure Service Bus imports
try:
    from azure.servicebus.aio import ServiceBusClient
    from azure.servicebus import ServiceBusMessage  # pylint: disable=unused-import
    from azure.identity.aio import DefaultAzureCredential
    AZURE_SERVICE_BUS_AVAILABLE = True
except ImportError:
    AZURE_SERVICE_BUS_AVAILABLE = False
    logging.warning("Azure Service Bus SDK not available")

# MCP Protocol imports
try:
    from mcp import ClientSession, StdioServerParameters  # pylint: disable=unused-import
    from mcp.client.stdio import stdio_client  # pylint: disable=unused-import
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP Python SDK not available")

from .protocol import MCPRequest, MCPResponse  # pylint: disable=unused-import


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
class MCPRequestWrapper:
    """MCP request wrapper"""
    request_id: str
    server_id: str
    method: str
    params: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    timeout: Optional[datetime] = None
    callback: Optional[Callable] = None


@dataclass
class MCPResponseWrapper:
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
        self.logger = logging.getLogger("AOS.MCPClientManager")

        # Azure Service Bus configuration
        self.service_bus_namespace = os.getenv("AZURE_SERVICE_BUS_NAMESPACE")
        self.service_bus_connection_string = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")

        # MCP server configurations
        self.server_configs: Dict[str, MCPServerConfig] = {}
        self.server_connections: Dict[str, Any] = {}  # MCP client sessions
        self.connection_status: Dict[str, MCPConnectionStatus] = {}

        # Request/response tracking
        self.pending_requests: Dict[str, MCPRequestWrapper] = {}
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

            # Initialize Azure Service Bus (if available)
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
        configs = []

        # LinkedIn MCP Server
        if os.getenv("LINKEDIN_MCP_FUNCTION_URL"):
            configs.append(MCPServerConfig(
                server_id="linkedin_mcp",
                server_type=MCPServerType.LINKEDIN,
                server_name="LinkedIn MCP Server",
                azure_function_url=os.getenv("LINKEDIN_MCP_FUNCTION_URL"),
                service_bus_topic="linkedin-mcp-topic",
                capabilities=["profile", "posts", "connections", "messaging"]
            ))

        # Reddit MCP Server
        if os.getenv("REDDIT_MCP_FUNCTION_URL"):
            configs.append(MCPServerConfig(
                server_id="reddit_mcp",
                server_type=MCPServerType.REDDIT,
                server_name="Reddit MCP Server",
                azure_function_url=os.getenv("REDDIT_MCP_FUNCTION_URL"),
                service_bus_topic="reddit-mcp-topic",
                capabilities=["posts", "comments", "subreddits", "search"]
            ))

        # ERPNext MCP Server
        if os.getenv("ERPNEXT_MCP_FUNCTION_URL"):
            configs.append(MCPServerConfig(
                server_id="erpnext_mcp",
                server_type=MCPServerType.ERPNEXT,
                server_name="ERPNext MCP Server",
                azure_function_url=os.getenv("ERPNEXT_MCP_FUNCTION_URL"),
                service_bus_topic="erpnext-mcp-topic",
                capabilities=["customers", "items", "sales", "purchasing", "accounting"]
            ))

        return configs

    async def _initialize_mcp_connections(self):
        """Initialize connections to MCP servers"""
        for server_id, config in self.server_configs.items():
            if config.enabled:
                await self._connect_to_server(server_id)

    async def _connect_to_server(self, server_id: str):
        """Connect to a specific MCP server"""
        try:
            config = self.server_configs[server_id]
            self.connection_status[server_id] = MCPConnectionStatus.CONNECTING

            # For now, simulate connection - would integrate with actual MCP client
            await asyncio.sleep(0.1)

            self.connection_status[server_id] = MCPConnectionStatus.CONNECTED
            self.logger.info(f"Connected to MCP server: {config.server_name}")

        except Exception as e:
            self.connection_status[server_id] = MCPConnectionStatus.ERROR
            self.logger.error(f"Failed to connect to MCP server {server_id}: {e}")

    async def _start_response_processors(self):
        """Start response processors for each server"""
        for server_id in self.server_configs.keys():
            task = asyncio.create_task(self._process_responses(server_id))
            self.response_processors[server_id] = task

    async def _process_responses(self, server_id: str):
        """Process responses from a specific MCP server"""
        while True:
            try:
                # Process pending responses
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing responses for {server_id}: {e}")

    async def send_request(self, server_id: str, method: str, params: Dict[str, Any] = None,
                          callback: Callable = None, timeout_seconds: int = 30) -> str:
        """Send a request to an MCP server"""
        if server_id not in self.server_configs:
            raise ValueError(f"Unknown MCP server: {server_id}")

        if self.connection_status[server_id] != MCPConnectionStatus.CONNECTED:
            raise ConnectionError(f"MCP server {server_id} is not connected")

        request_id = str(uuid.uuid4())

        request = MCPRequestWrapper(
            request_id=request_id,
            server_id=server_id,
            method=method,
            params=params or {},
            timeout=datetime.now() + timedelta(seconds=timeout_seconds),
            callback=callback
        )

        self.pending_requests[request_id] = request
        if callback:
            self.request_callbacks[request_id] = callback

        # Send request (placeholder - would integrate with actual MCP protocol)
        self.logger.debug(f"Sending MCP request {request_id} to {server_id}: {method}")

        self.stats["total_requests"] += 1

        return request_id

    async def get_server_capabilities(self, server_id: str) -> List[str]:
        """Get capabilities of an MCP server"""
        if server_id not in self.server_configs:
            return []

        return self.server_configs[server_id].capabilities

    def get_connection_status(self, server_id: str = None) -> Dict[str, Any]:
        """Get connection status for one or all servers"""
        if server_id:
            if server_id not in self.server_configs:
                return {"error": f"Unknown server: {server_id}"}

            return {
                "server_id": server_id,
                "status": self.connection_status[server_id].value,
                "config": self.server_configs[server_id]
            }

        return {
            server_id: {
                "status": status.value,
                "config": self.server_configs[server_id]
            }
            for server_id, status in self.connection_status.items()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get MCP client manager statistics"""
        return {
            **self.stats,
            "connected_servers": sum(1 for status in self.connection_status.values()
                                   if status == MCPConnectionStatus.CONNECTED),
            "total_servers": len(self.server_configs),
            "pending_requests": len(self.pending_requests)
        }

    async def shutdown(self):
        """Shutdown MCP Client Manager"""
        try:
            # Cancel response processors
            for task in self.response_processors.values():
                task.cancel()

            # Close Service Bus client
            if self.service_bus_client:
                await self.service_bus_client.close()

            # Clear connections
            self.server_connections.clear()
            self.connection_status.clear()

            self.logger.info("MCP Client Manager shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during MCP Client Manager shutdown: {e}")