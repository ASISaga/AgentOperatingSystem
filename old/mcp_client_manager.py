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

# Azure Service Bus imports (optional)
AZURE_SERVICE_BUS_AVAILABLE = False
try:
    # Placeholder for Azure Service Bus imports
    pass
except ImportError:
    logging.warning("Azure Service Bus SDK not available")

# MCP Protocol imports (optional)
MCP_AVAILABLE = False
try:
    # Placeholder for MCP imports
    pass
except ImportError:
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
            # Placeholder for Azure Service Bus initialization
            self.logger.info("Azure Service Bus client would be initialized here")
            
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
            # For demo purposes, assume connection is successful
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
                self.response_processors[server_id] = task
    
    async def _process_responses(self, server_id: str, response_topic: str):
        """Process responses from an MCP server"""
        try:
            # Placeholder for response processing
            self.logger.info(f"Response processor for {server_id} would process {response_topic}")
        
        except Exception as e:
            self.logger.error(f"Error in response processor for {server_id}: {e}")
    
    async def send_mcp_request(self, 
                              server_id: str, 
                              method: str, 
                              params: Dict[str, Any], 
                              callback: Optional[Callable] = None,
                              timeout_seconds: Optional[int] = None) -> str:
        """
        Send request to MCP server
        
        Args:
            server_id: ID of the target MCP server
            method: MCP method to call
            params: Parameters for the method
            callback: Optional callback for response handling
            timeout_seconds: Optional timeout override
            
        Returns:
            Request ID for tracking
        """
        try:
            if server_id not in self.server_configs:
                raise ValueError(f"MCP server {server_id} not configured")
            
            if self.connection_status[server_id] != MCPConnectionStatus.CONNECTED:
                # For demo, return mock response instead of raising error
                self.logger.warning(f"MCP server {server_id} not connected, returning mock response")
            
            config = self.server_configs[server_id]
            request_id = str(uuid.uuid4())
            
            # Create request object
            request = MCPRequest(
                request_id=request_id,
                server_id=server_id,
                method=method,
                params=params,
                timeout=datetime.now() + timedelta(seconds=timeout_seconds or config.timeout_seconds),
                callback=callback
            )
            
            # Store request
            self.pending_requests[request_id] = request
            
            if callback:
                self.request_callbacks[request_id] = callback
            
            # Update statistics
            self.stats["total_requests"] += 1
            
            self.logger.debug(f"Sent MCP request {request_id} to {server_id}")
            
            # For demo, simulate success response
            asyncio.create_task(self._simulate_response(request_id, server_id))
            
            return request_id
            
        except Exception as e:
            self.logger.error(f"Failed to send MCP request: {e}")
            raise
    
    async def _simulate_response(self, request_id: str, server_id: str):
        """Simulate an MCP response (for demo purposes)"""
        try:
            # Simulate processing delay
            await asyncio.sleep(0.5)
            
            # Create mock response
            response = MCPResponse(
                request_id=request_id,
                server_id=server_id,
                success=True,
                data={"message": f"Mock response from {server_id}"}
            )
            
            # Process the response
            await self._handle_mcp_response(response)
            
        except Exception as e:
            self.logger.error(f"Error simulating response: {e}")
    
    async def _handle_mcp_response(self, response: MCPResponse):
        """Handle an MCP response"""
        try:
            request_id = response.request_id
            
            # Update statistics
            if response.success:
                self.stats["successful_requests"] += 1
            else:
                self.stats["failed_requests"] += 1
            
            # Call callback if registered
            if request_id in self.request_callbacks:
                callback = self.request_callbacks[request_id]
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(response)
                    else:
                        callback(response)
                except Exception as e:
                    self.logger.error(f"Error in response callback: {e}")
                
                del self.request_callbacks[request_id]
            
            # Remove from pending requests
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]
            
        except Exception as e:
            self.logger.error(f"Error handling MCP response: {e}")
    
    async def get_server_capabilities(self, server_id: str) -> List[str]:
        """Get capabilities of a specific MCP server"""
        if server_id not in self.server_configs:
            return []
        
        return self.server_configs[server_id].capabilities
    
    async def get_server_status(self, server_id: str) -> Dict[str, Any]:
        """Get status of a specific MCP server"""
        if server_id not in self.server_configs:
            return {"status": "not_found"}
        
        config = self.server_configs[server_id]
        status = self.connection_status[server_id]
        
        return {
            "server_id": server_id,
            "server_name": config.server_name,
            "server_type": config.server_type.value,
            "status": status.value,
            "enabled": config.enabled,
            "capabilities": config.capabilities,
            "azure_function_url": config.azure_function_url,
            "pending_requests": len([r for r in self.pending_requests.values() if r.server_id == server_id])
        }
    
    async def list_servers(self) -> List[Dict[str, Any]]:
        """List all configured MCP servers"""
        servers = []
        
        for server_id in self.server_configs.keys():
            status = await self.get_server_status(server_id)
            servers.append(status)
        
        return servers
    
    async def get_client_statistics(self) -> Dict[str, Any]:
        """Get MCP client statistics"""
        total_requests = self.stats["total_requests"]
        
        return {
            **self.stats,
            "success_rate": (self.stats["successful_requests"] / total_requests * 100) if total_requests > 0 else 0,
            "connected_servers": len([s for s in self.connection_status.values() if s == MCPConnectionStatus.CONNECTED]),
            "total_servers": len(self.server_configs),
            "pending_requests": len(self.pending_requests)
        }
    
    async def reconnect_server(self, server_id: str) -> bool:
        """Reconnect to a specific MCP server"""
        try:
            if server_id not in self.server_configs:
                return False
            
            self.connection_status[server_id] = MCPConnectionStatus.RECONNECTING
            await self._connect_to_server(server_id)
            
            return self.connection_status[server_id] == MCPConnectionStatus.CONNECTED
            
        except Exception as e:
            self.logger.error(f"Failed to reconnect to server {server_id}: {e}")
            return False
    
    async def shutdown(self):
        """Graceful shutdown of MCP Client Manager"""
        try:
            # Cancel response processors
            for task in self.response_processors.values():
                task.cancel()
            
            # Wait for tasks to complete
            if self.response_processors:
                await asyncio.gather(*self.response_processors.values(), return_exceptions=True)
            
            # Close Service Bus client
            if self.service_bus_client:
                # await self.service_bus_client.close()  # Would close in real implementation
                pass
            
            # Clear pending requests
            self.pending_requests.clear()
            self.request_callbacks.clear()
            
            self.logger.info("MCP Client Manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during MCP Client Manager shutdown: {e}")
    
    # Convenience methods for specific MCP servers
    
    async def linkedin_request(self, method: str, params: Dict[str, Any], callback: Optional[Callable] = None) -> str:
        """Send request to LinkedIn MCP server"""
        return await self.send_mcp_request("linkedin_mcp", method, params, callback)
    
    async def reddit_request(self, method: str, params: Dict[str, Any], callback: Optional[Callable] = None) -> str:
        """Send request to Reddit MCP server"""
        return await self.send_mcp_request("reddit_mcp", method, params, callback)
    
    async def erpnext_request(self, method: str, params: Dict[str, Any], callback: Optional[Callable] = None) -> str:
        """Send request to ERPNext MCP server"""
        return await self.send_mcp_request("erpnext_mcp", method, params, callback)