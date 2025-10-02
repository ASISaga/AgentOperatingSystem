"""
MCP Integration Enhancements for AOS

Enhanced Model Context Protocol integration system from SelfLearningAgent.
Provides advanced MCP client management and GitHub integration capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
import json
from pathlib import Path

class MCPClientManager:
    """
    Enhanced MCP client management system that provides advanced
    Model Context Protocol integration capabilities.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.MCPClientManager")
        
        # MCP client registry
        self.mcp_clients: Dict[str, Any] = {}
        self.client_configs: Dict[str, Dict[str, Any]] = {}
        self.client_status: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.request_metrics: Dict[str, Dict[str, Any]] = {}
        self.client_health: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.max_concurrent_requests = 10
        self.request_timeout = 30
        self.health_check_interval = 300  # 5 minutes
        
        # Default client configurations
        self.default_configs = {
            "github": {
                "name": "GitHub MCP Client",
                "description": "Integration with GitHub repositories and APIs",
                "capabilities": ["repository_access", "issue_management", "pull_requests"],
                "auth_required": True,
                "rate_limit": {"requests_per_minute": 60}
            },
            "linkedin": {
                "name": "LinkedIn MCP Client", 
                "description": "Professional networking and content management",
                "capabilities": ["profile_access", "post_management", "network_analysis"],
                "auth_required": True,
                "rate_limit": {"requests_per_minute": 30}
            },
            "reddit": {
                "name": "Reddit MCP Client",
                "description": "Reddit community interaction and content management",
                "capabilities": ["post_management", "comment_interaction", "subreddit_analysis"],
                "auth_required": True,
                "rate_limit": {"requests_per_minute": 100}
            },
            "erpnext": {
                "name": "ERPNext MCP Client",
                "description": "Enterprise Resource Planning system integration", 
                "capabilities": ["data_access", "workflow_management", "reporting"],
                "auth_required": True,
                "rate_limit": {"requests_per_minute": 120}
            }
        }
    
    async def register_mcp_client(self, client_id: str, client_instance: Any, 
                                 config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register an MCP client with the manager"""
        
        try:
            # Use default config if none provided
            client_config = config or self.default_configs.get(client_id, {
                "name": f"{client_id.title()} MCP Client",
                "description": f"MCP client for {client_id}",
                "capabilities": ["general"],
                "auth_required": False,
                "rate_limit": {"requests_per_minute": 60}
            })
            
            # Validate client instance
            if not hasattr(client_instance, '__call__') and not hasattr(client_instance, 'process_request'):
                self.logger.warning(f"MCP client {client_id} may not have proper interface")
            
            # Register client
            self.mcp_clients[client_id] = client_instance
            self.client_configs[client_id] = client_config
            self.client_status[client_id] = {
                "status": "registered",
                "registered_at": datetime.utcnow().isoformat(),
                "last_health_check": None,
                "request_count": 0,
                "error_count": 0
            }
            
            # Initialize metrics
            self.request_metrics[client_id] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0,
                "last_request": None
            }
            
            self.logger.info(f"Registered MCP client: {client_id}")
            
            return {
                "success": True,
                "client_id": client_id,
                "config": client_config,
                "registered_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to register MCP client {client_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def unregister_mcp_client(self, client_id: str) -> Dict[str, Any]:
        """Unregister an MCP client"""
        
        try:
            if client_id not in self.mcp_clients:
                return {"success": False, "error": f"Client {client_id} not found"}
            
            # Clean up client data
            del self.mcp_clients[client_id]
            del self.client_configs[client_id] 
            del self.client_status[client_id]
            del self.request_metrics[client_id]
            
            if client_id in self.client_health:
                del self.client_health[client_id]
            
            self.logger.info(f"Unregistered MCP client: {client_id}")
            
            return {
                "success": True,
                "client_id": client_id,
                "unregistered_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to unregister MCP client {client_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_mcp_request(self, client_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process request through specified MCP client"""
        
        if client_id not in self.mcp_clients:
            return {
                "success": False,
                "error": f"MCP client {client_id} not registered",
                "client_id": client_id
            }
        
        start_time = datetime.utcnow()
        
        try:
            # Get client and prepare request
            client = self.mcp_clients[client_id]
            prepared_request = await self._prepare_mcp_request(client_id, request)
            
            # Execute request with timeout
            response = await asyncio.wait_for(
                self._execute_mcp_request(client, prepared_request),
                timeout=self.request_timeout
            )
            
            # Record successful request
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            await self._record_request_success(client_id, execution_time)
            
            return {
                "success": True,
                "client_id": client_id,
                "response": response,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            await self._record_request_failure(client_id, "Request timeout", execution_time)
            
            return {
                "success": False,
                "client_id": client_id,
                "error": "Request timeout",
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            await self._record_request_failure(client_id, str(e), execution_time)
            
            return {
                "success": False,
                "client_id": client_id,
                "error": str(e),
                "execution_time": execution_time
            }
    
    async def _prepare_mcp_request(self, client_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request for specific MCP client"""
        
        client_config = self.client_configs[client_id]
        
        # Add client-specific metadata
        prepared = request.copy()
        prepared.update({
            "client_id": client_id,
            "client_capabilities": client_config.get("capabilities", []),
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": f"{client_id}_{datetime.utcnow().timestamp()}"
        })
        
        return prepared
    
    async def _execute_mcp_request(self, client: Any, request: Dict[str, Any]) -> Any:
        """Execute request with MCP client"""
        
        # Try different client interfaces
        if hasattr(client, 'process_request'):
            return await client.process_request(request)
        elif hasattr(client, 'handle_request'):
            return await client.handle_request(request)
        elif callable(client):
            return await client(request)
        else:
            raise ValueError("MCP client does not have recognizable interface")
    
    async def _record_request_success(self, client_id: str, execution_time: float) -> None:
        """Record successful request metrics"""
        
        # Update client status
        if client_id in self.client_status:
            self.client_status[client_id]["request_count"] += 1
            self.client_status[client_id]["status"] = "active"
        
        # Update request metrics
        if client_id in self.request_metrics:
            metrics = self.request_metrics[client_id]
            metrics["total_requests"] += 1
            metrics["successful_requests"] += 1
            metrics["last_request"] = datetime.utcnow().isoformat()
            
            # Update average response time
            if metrics["total_requests"] == 1:
                metrics["average_response_time"] = execution_time
            else:
                metrics["average_response_time"] = (
                    (metrics["average_response_time"] * (metrics["total_requests"] - 1) + execution_time)
                    / metrics["total_requests"]
                )
    
    async def _record_request_failure(self, client_id: str, error: str, execution_time: float) -> None:
        """Record failed request metrics"""
        
        # Update client status
        if client_id in self.client_status:
            self.client_status[client_id]["error_count"] += 1
            self.client_status[client_id]["last_error"] = error
            self.client_status[client_id]["last_error_time"] = datetime.utcnow().isoformat()
        
        # Update request metrics
        if client_id in self.request_metrics:
            metrics = self.request_metrics[client_id]
            metrics["total_requests"] += 1
            metrics["failed_requests"] += 1
            metrics["last_request"] = datetime.utcnow().isoformat()
    
    async def batch_process_requests(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple MCP requests in batch"""
        
        results = []
        
        # Group requests by client
        client_requests = {}
        for request in requests:
            client_id = request.get("client_id")
            if not client_id:
                results.append({
                    "success": False,
                    "error": "No client_id specified",
                    "request": request
                })
                continue
            
            if client_id not in client_requests:
                client_requests[client_id] = []
            client_requests[client_id].append(request)
        
        # Process requests for each client
        for client_id, client_request_list in client_requests.items():
            client_results = await self._process_client_batch(client_id, client_request_list)
            results.extend(client_results)
        
        return {
            "total_requests": len(requests),
            "processed_requests": len(results),
            "successful_requests": len([r for r in results if r.get("success")]),
            "failed_requests": len([r for r in results if not r.get("success")]),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _process_client_batch(self, client_id: str, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process batch of requests for specific client"""
        
        results = []
        
        # Limit concurrent requests per client
        semaphore = asyncio.Semaphore(min(self.max_concurrent_requests, len(requests)))
        
        async def process_single_request(request):
            async with semaphore:
                return await self.process_mcp_request(client_id, request)
        
        # Execute all requests concurrently
        tasks = [process_single_request(req) for req in requests]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                results.append({
                    "success": False,
                    "error": str(result),
                    "request": requests[i],
                    "client_id": client_id
                })
            else:
                results.append(result)
        
        return results
    
    async def health_check_all_clients(self) -> Dict[str, Any]:
        """Perform health check on all registered MCP clients"""
        
        health_results = {}
        overall_health = True
        
        for client_id in self.mcp_clients.keys():
            try:
                # Simple health check - try to process a basic request
                health_request = {
                    "type": "health_check",
                    "message": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                result = await self.process_mcp_request(client_id, health_request)
                
                health_results[client_id] = {
                    "status": "healthy" if result.get("success") else "unhealthy",
                    "response_time": result.get("execution_time", 0),
                    "last_check": datetime.utcnow().isoformat(),
                    "error": result.get("error") if not result.get("success") else None
                }
                
                if not result.get("success"):
                    overall_health = False
                
            except Exception as e:
                health_results[client_id] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                overall_health = False
        
        # Update client health tracking
        self.client_health.update(health_results)
        
        return {
            "overall_health": "healthy" if overall_health else "degraded",
            "client_health": health_results,
            "total_clients": len(self.mcp_clients),
            "healthy_clients": len([h for h in health_results.values() if h["status"] == "healthy"]),
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def get_client_metrics(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for MCP clients"""
        
        if client_id:
            if client_id not in self.mcp_clients:
                return {"error": f"Client {client_id} not found"}
            
            return {
                "client_id": client_id,
                "config": self.client_configs.get(client_id, {}),
                "status": self.client_status.get(client_id, {}),
                "metrics": self.request_metrics.get(client_id, {}),
                "health": self.client_health.get(client_id, {})
            }
        else:
            # Return metrics for all clients
            all_metrics = {}
            
            for cid in self.mcp_clients.keys():
                all_metrics[cid] = {
                    "config": self.client_configs.get(cid, {}),
                    "status": self.client_status.get(cid, {}),
                    "metrics": self.request_metrics.get(cid, {}),
                    "health": self.client_health.get(cid, {})
                }
            
            return {
                "total_clients": len(self.mcp_clients),
                "clients": all_metrics,
                "summary": self._calculate_summary_metrics()
            }
    
    def _calculate_summary_metrics(self) -> Dict[str, Any]:
        """Calculate summary metrics across all clients"""
        
        total_requests = sum(
            metrics.get("total_requests", 0) 
            for metrics in self.request_metrics.values()
        )
        
        successful_requests = sum(
            metrics.get("successful_requests", 0) 
            for metrics in self.request_metrics.values()
        )
        
        failed_requests = sum(
            metrics.get("failed_requests", 0) 
            for metrics in self.request_metrics.values()
        )
        
        avg_response_times = [
            metrics.get("average_response_time", 0) 
            for metrics in self.request_metrics.values()
            if metrics.get("average_response_time", 0) > 0
        ]
        
        overall_avg_response_time = (
            sum(avg_response_times) / len(avg_response_times) 
            if avg_response_times else 0
        )
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "average_response_time": overall_avg_response_time,
            "active_clients": len([
                status for status in self.client_status.values() 
                if status.get("status") == "active"
            ])
        }
    
    async def get_mcp_status(self) -> Dict[str, Any]:
        """Get comprehensive MCP system status"""
        
        return {
            "registered_clients": len(self.mcp_clients),
            "client_list": list(self.mcp_clients.keys()),
            "system_metrics": self._calculate_summary_metrics(),
            "health_status": await self.health_check_all_clients(),
            "configuration": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "request_timeout": self.request_timeout,
                "health_check_interval": self.health_check_interval
            },
            "timestamp": datetime.utcnow().isoformat()
        }