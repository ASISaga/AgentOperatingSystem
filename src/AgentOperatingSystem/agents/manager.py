"""
Unified Agent Manager - Generic agent lifecycle and orchestration.
Manages agent registration, discovery, health monitoring, and coordination.

UnifiedAgentManager runs in perpetual operation mode by default, except in
development/testing scenarios. This aligns with the AOS architecture where
PerpetualAgents (and PurposeDrivenAgents that inherit from them) are the
fundamental building blocks.
"""

from typing import Dict, Any, List, Optional
import logging
from .base_agent import BaseAgent

class UnifiedAgentManager:
    """
    Manages agent lifecycle in perpetual operation mode.
    
    - Agent registration and deregistration
    - Agent discovery and lookup  
    - Health monitoring
    - Fallback and degradation patterns
    - Perpetual agent lifecycle (register once, run indefinitely)
    - Event-driven agent awakening
    
    The AgentManager operates primarily in perpetual mode where agents are
    registered once and run indefinitely, responding to events. This is the
    core AOS architecture.
    
    Task-based mode is supported only for development/testing purposes.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agents: Dict[str, BaseAgent] = {}
        self.perpetual_agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("aos.agent_manager")
        
    async def register_agent(self, agent: BaseAgent, perpetual: bool = True) -> bool:
        """
        Register an agent.
        
        Args:
            agent: Agent instance to register
            perpetual: If True (default), agent runs in perpetual mode.
                      If False, agent uses task-based mode (dev/testing only).
            
        Returns:
            True if successful
            
        Note:
            For perpetual agents, this method also starts the agent's
            indefinite run loop. Perpetual agents should only be stopped
            when explicitly deregistered or when the system shuts down.
            
            Perpetual mode is the default and recommended operational mode
            for AOS. Task-based mode should only be used in development/testing.
        """
        try:
            await agent.initialize()
            self.agents[agent.agent_id] = agent
            
            if perpetual:
                # Start the agent in perpetual mode (default for AOS)
                await agent.start()
                self.perpetual_agents[agent.agent_id] = agent
                self.logger.info(
                    f"Registered PERPETUAL agent: {agent.agent_id} "
                    f"(will run indefinitely, responding to events)"
                )
            else:
                # Task-based mode (dev/testing only)
                self.logger.info(
                    f"Registered task-based agent: {agent.agent_id} "
                    f"(development/testing mode)"
                )
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False
    
    async def deregister_agent(self, agent_id: str) -> bool:
        """
        Deregister an agent.
        
        For perpetual agents, this stops their indefinite run loop.
        
        Args:
            agent_id: Agent ID to deregister
            
        Returns:
            True if successful
        """
        if agent_id in self.agents:
            try:
                await self.agents[agent_id].stop()
                del self.agents[agent_id]
                
                # Also remove from perpetual registry if present
                if agent_id in self.perpetual_agents:
                    del self.perpetual_agents[agent_id]
                    self.logger.info(f"Deregistered perpetual agent: {agent_id}")
                else:
                    self.logger.info(f"Deregistered task-based agent: {agent_id}")
                
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
    
    def list_perpetual_agents(self) -> List[Dict[str, Any]]:
        """
        List all perpetual agents.
        
        These agents run indefinitely and respond to events,
        representing the core AOS operational model.
        
        Returns:
            List of perpetual agent metadata
        """
        return [
            {
                **agent.get_metadata(),
                "operational_mode": "perpetual",
                "is_persistent": True
            }
            for agent in self.perpetual_agents.values()
        ]
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about registered agents.
        
        Returns:
            Statistics including counts by operational mode
        """
        return {
            "total_agents": len(self.agents),
            "perpetual_agents": len(self.perpetual_agents),
            "task_based_agents": len(self.agents) - len(self.perpetual_agents),
            "perpetual_percentage": (
                len(self.perpetual_agents) / len(self.agents) * 100
                if self.agents else 0
            )
        }
    
    async def health_check_all(self) -> Dict[str, Any]:
        """
        Perform health check on all agents.
        
        Returns:
            Health status for each agent, including operational mode
        """
        health_status = {}
        for agent_id, agent in self.agents.items():
            agent_health = await agent.health_check()
            agent_health["operational_mode"] = (
                "perpetual" if agent_id in self.perpetual_agents
                else "task-based"
            )
            health_status[agent_id] = agent_health
        return health_status
