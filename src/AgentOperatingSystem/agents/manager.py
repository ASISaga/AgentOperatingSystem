"""
Unified Agent Manager - Generic agent lifecycle and orchestration.
Manages agent registration, discovery, health monitoring, and coordination.

Supports both traditional task-based agents and always-on persistent agents,
with a focus on the always-on model that differentiates AOS from traditional
AI frameworks.
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
    - Always-on agent lifecycle (start once, run indefinitely)
    - Event-driven agent awakening
    
    The AgentManager supports two operational models:
    
    1. Task-Based (Traditional): Agents are started for specific tasks
       and terminated when complete.
       
    2. Always-On (AOS Model): Agents are registered once and run
       indefinitely, responding to events. This is the recommended
       approach for AOS as it enables true continuous operations.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agents: Dict[str, BaseAgent] = {}
        self.always_on_agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("aos.agent_manager")
        
    async def register_agent(self, agent: BaseAgent, always_on: bool = False) -> bool:
        """
        Register an agent.
        
        Args:
            agent: Agent instance to register
            always_on: If True, agent will run indefinitely in always-on mode.
                      If False, agent uses traditional task-based lifecycle.
            
        Returns:
            True if successful
            
        Note:
            For always-on agents, this method also starts the agent's
            indefinite run loop. Always-on agents should only be stopped
            when explicitly deregistered or when the system shuts down.
        """
        try:
            await agent.initialize()
            self.agents[agent.agent_id] = agent
            
            if always_on:
                # Start the agent in always-on mode
                await agent.start()
                self.always_on_agents[agent.agent_id] = agent
                self.logger.info(
                    f"Registered ALWAYS-ON agent: {agent.agent_id} "
                    f"(will run indefinitely, responding to events)"
                )
            else:
                self.logger.info(
                    f"Registered task-based agent: {agent.agent_id} "
                    f"(traditional start/stop lifecycle)"
                )
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False
    
    async def deregister_agent(self, agent_id: str) -> bool:
        """
        Deregister an agent.
        
        For always-on agents, this stops their indefinite run loop.
        
        Args:
            agent_id: Agent ID to deregister
            
        Returns:
            True if successful
        """
        if agent_id in self.agents:
            try:
                await self.agents[agent_id].stop()
                del self.agents[agent_id]
                
                # Also remove from always-on registry if present
                if agent_id in self.always_on_agents:
                    del self.always_on_agents[agent_id]
                    self.logger.info(f"Deregistered always-on agent: {agent_id}")
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
    
    def list_always_on_agents(self) -> List[Dict[str, Any]]:
        """
        List all always-on agents.
        
        These agents run indefinitely and respond to events,
        representing the core AOS operational model.
        
        Returns:
            List of always-on agent metadata
        """
        return [
            {
                **agent.get_metadata(),
                "operational_mode": "always-on",
                "is_persistent": True
            }
            for agent in self.always_on_agents.values()
        ]
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about registered agents.
        
        Returns:
            Statistics including counts by operational mode
        """
        return {
            "total_agents": len(self.agents),
            "always_on_agents": len(self.always_on_agents),
            "task_based_agents": len(self.agents) - len(self.always_on_agents),
            "always_on_percentage": (
                len(self.always_on_agents) / len(self.agents) * 100
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
                "always-on" if agent_id in self.always_on_agents
                else "task-based"
            )
            health_status[agent_id] = agent_health
        return health_status
