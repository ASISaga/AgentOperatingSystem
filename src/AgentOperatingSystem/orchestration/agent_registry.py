"""
Enhanced Agent Registry for AOS

Integrated from SelfLearningAgent - provides agent registration,
implementation tracking, and status management capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from ..agents import LeadershipAgent


class AgentRegistry:
    """
    Enhanced agent registry that tracks agents, implementations, and provides
    advanced coordination capabilities.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.AgentRegistry")
        
        # Agent management
        self.domain_agents: Dict[str, LeadershipAgent] = {}
        self.agent_functions: Dict[str, Callable] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        
        # Implementation tracking
        self.pending_implementations: Dict[str, Dict[str, Any]] = {}
        self.completed_implementations: Dict[str, Dict[str, Any]] = {}
        
        # Status tracking
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.last_activity: Dict[str, datetime] = {}
    
    async def register_domain_agent(self, domain: str, agent: LeadershipAgent, capabilities: List[str] = None) -> Dict[str, Any]:
        """Register a domain-specific agent with optional capabilities"""
        self.domain_agents[domain] = agent
        self.agent_capabilities[domain] = capabilities or []
        self.last_activity[domain] = datetime.utcnow()
        
        # Update agent status
        self.agent_status[domain] = {
            "agent_id": agent.agent_id,
            "domain": domain,
            "status": "active",
            "registered_at": datetime.utcnow().isoformat(),
            "capabilities": capabilities or []
        }
        
        self.logger.info(f"Registered domain agent for: {domain} (Agent ID: {agent.agent_id})")
        
        return {
            "success": True,
            "domain": domain,
            "agent_id": agent.agent_id,
            "capabilities": capabilities or [],
            "registered_at": datetime.utcnow().isoformat()
        }
    
    async def register_agent_function(self, domain: str, function_name: str, function: Callable) -> None:
        """Register a specific function for a domain"""
        key = f"{domain}.{function_name}"
        self.agent_functions[key] = function
        
        # Add to capabilities if not already present
        if domain in self.agent_capabilities:
            if function_name not in self.agent_capabilities[domain]:
                self.agent_capabilities[domain].append(function_name)
        else:
            self.agent_capabilities[domain] = [function_name]
        
        self.logger.debug(f"Registered function {function_name} for domain {domain}")
    
    async def get_domain_agent(self, domain: str) -> Optional[LeadershipAgent]:
        """Get the agent for a specific domain"""
        return self.domain_agents.get(domain)
    
    async def get_agent_capabilities(self, domain: str) -> List[str]:
        """Get capabilities for a domain agent"""
        return self.agent_capabilities.get(domain, [])
    
    async def invoke_agent_function(self, domain: str, function_name: str, parameters: Dict[str, Any] = None) -> Any:
        """Invoke a specific agent function"""
        key = f"{domain}.{function_name}"
        
        if key not in self.agent_functions:
            raise ValueError(f"Function {function_name} not found for domain {domain}")
        
        function = self.agent_functions[key]
        parameters = parameters or {}
        
        try:
            # Update last activity
            self.last_activity[domain] = datetime.utcnow()
            
            # Invoke function
            if asyncio.iscoroutinefunction(function):
                result = await function(**parameters)
            else:
                result = function(**parameters)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error invoking {domain}.{function_name}: {e}")
            raise
    
    async def track_implementation(self, impl_id: str, domain: str, function_name: str, 
                                 github_issue: Optional[str] = None, metadata: Dict[str, Any] = None) -> None:
        """Track a pending implementation"""
        self.pending_implementations[impl_id] = {
            "domain": domain,
            "function_name": function_name,
            "github_issue": github_issue,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.logger.info(f"Tracking implementation {impl_id} for {domain}.{function_name}")
    
    async def mark_implementation_complete(self, impl_id: str, result: Dict[str, Any] = None) -> None:
        """Mark an implementation as complete"""
        if impl_id not in self.pending_implementations:
            self.logger.warning(f"Implementation {impl_id} not found in pending list")
            return
        
        impl_data = self.pending_implementations.pop(impl_id)
        impl_data.update({
            "completed_at": datetime.utcnow().isoformat(),
            "result": result or {}
        })
        
        self.completed_implementations[impl_id] = impl_data
        
        self.logger.info(f"Implementation {impl_id} marked as complete")
    
    async def check_implementation_status(self, mcp_clients: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check status of all pending implementations"""
        status = {
            "total_pending": len(self.pending_implementations),
            "total_completed": len(self.completed_implementations),
            "implementations": []
        }
        
        for impl_id, impl_data in self.pending_implementations.items():
            domain = impl_data["domain"]
            function_name = impl_data["function_name"]
            is_complete = False
            
            # Check if implementation is actually available
            if mcp_clients and domain in mcp_clients:
                try:
                    client = mcp_clients[domain]
                    await client.invoke_function(function_name, {})
                    is_complete = True
                    # Auto-mark as complete if working
                    await self.mark_implementation_complete(impl_id, {"auto_detected": True})
                except Exception:
                    is_complete = False
            
            # Check via agent functions
            elif f"{domain}.{function_name}" in self.agent_functions:
                is_complete = True
                await self.mark_implementation_complete(impl_id, {"via_agent_function": True})
            
            if not is_complete:  # Only add to status if still pending
                status["implementations"].append({
                    "id": impl_id,
                    "domain": domain,
                    "function_name": function_name,
                    "github_issue": impl_data.get("github_issue"),
                    "is_complete": is_complete,
                    "created_at": impl_data["created_at"],
                    "metadata": impl_data.get("metadata", {})
                })
        
        return status
    
    async def get_agent_status(self, domain: str = None) -> Dict[str, Any]:
        """Get status for specific domain or all agents"""
        if domain:
            return self.agent_status.get(domain, {})
        
        return {
            "total_agents": len(self.domain_agents),
            "domains": list(self.domain_agents.keys()),
            "agent_status": self.agent_status.copy(),
            "last_activity": {k: v.isoformat() for k, v in self.last_activity.items()},
            "total_capabilities": sum(len(caps) for caps in self.agent_capabilities.values())
        }
    
    async def update_agent_status(self, domain: str, status_update: Dict[str, Any]) -> None:
        """Update agent status information"""
        if domain in self.agent_status:
            self.agent_status[domain].update(status_update)
            self.last_activity[domain] = datetime.utcnow()
        else:
            self.logger.warning(f"Cannot update status for unregistered domain: {domain}")
    
    async def deregister_agent(self, domain: str) -> bool:
        """Deregister an agent and clean up associated data"""
        try:
            # Remove from all registries
            self.domain_agents.pop(domain, None)
            self.agent_capabilities.pop(domain, None)
            self.agent_status.pop(domain, None)
            self.last_activity.pop(domain, None)
            
            # Remove associated functions
            keys_to_remove = [key for key in self.agent_functions.keys() if key.startswith(f"{domain}.")]
            for key in keys_to_remove:
                del self.agent_functions[key]
            
            self.logger.info(f"Deregistered agent for domain: {domain}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deregistering agent for {domain}: {e}")
            return False
    
    async def list_domains(self) -> List[str]:
        """Get list of all registered domains"""
        return list(self.domain_agents.keys())
    
    async def list_capabilities(self) -> Dict[str, List[str]]:
        """Get all capabilities by domain"""
        return self.agent_capabilities.copy()
    
    async def find_capable_agents(self, required_capability: str) -> List[str]:
        """Find all agents that have a specific capability"""
        capable_domains = []
        
        for domain, capabilities in self.agent_capabilities.items():
            if required_capability in capabilities:
                capable_domains.append(domain)
        
        return capable_domains
    
    async def get_registry_statistics(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        active_agents = len([d for d, status in self.agent_status.items() if status.get("status") == "active"])
        
        return {
            "total_domains": len(self.domain_agents),
            "active_agents": active_agents,
            "total_functions": len(self.agent_functions),
            "pending_implementations": len(self.pending_implementations),
            "completed_implementations": len(self.completed_implementations),
            "total_capabilities": sum(len(caps) for caps in self.agent_capabilities.values()),
            "domains_by_capability_count": {
                domain: len(caps) for domain, caps in self.agent_capabilities.items()
            }
        }