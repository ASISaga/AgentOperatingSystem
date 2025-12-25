"""
Unified Agent Manager - Generic agent lifecycle and orchestration.
Manages agent registration, discovery, health monitoring, and coordination.
"""

from typing import Dict, Any, List, Optional
import logging
from .base_agent import BaseAgent

class UnifiedAgentManager:
    """
    Manages agent lifecycle:
    - Agent registration and deregistration
    - Agent discovery and lookup
    - Health monitoring
    - Fallback and degradation patterns
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("aos.agent_manager")
        
    async def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent.
        
        Args:
            agent: Agent instance to register
            
        Returns:
            True if successful
        """
        try:
            await agent.initialize()
            self.agents[agent.agent_id] = agent
            self.logger.info(f"Registered agent: {agent.agent_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False
    
    async def deregister_agent(self, agent_id: str) -> bool:
        """
        Deregister an agent.
        
        Args:
            agent_id: Agent ID to deregister
            
        Returns:
            True if successful
        """
        if agent_id in self.agents:
            try:
                await self.agents[agent_id].stop()
                del self.agents[agent_id]
                self.logger.info(f"Deregistered agent: {agent_id}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to deregister agent {agent_id}: {e}")
                return False
        return False
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents."""
        return [agent.get_metadata() for agent in self.agents.values()]
    
    async def health_check_all(self) -> Dict[str, Any]:
        """
        Perform health check on all agents.
        
        Returns:
            Health status for each agent
        """
        health_status = {}
        for agent_id, agent in self.agents.items():
            health_status[agent_id] = await agent.health_check()
        return health_status
