"""
Unified entry point for AgentOperatingSystem (AOS).
Exposes orchestration, perpetual agent, ML pipeline, leadership, and team logic.

This class provides a domain-agnostic foundation for agent coordination and management.
Applications should extend this class to add their specific business logic.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio

# Import generic orchestration components
from .orchestration import BaseOrchestrator, Workflow, WorkflowStep, OrchestrationEngine
from .LeadershipAgent import LeadershipAgent
from .LeadershipOrchestrator import LeadershipOrchestrator

# Import and expose PerpetualAgent
from .PerpetualAgent import PerpetualAgent
# Import and expose ML pipeline manager
from .MLPipelineManager import MLPipelineManager

# Optionally, import and expose team/multi-agent logic if needed
# from .multi_agent import ...
# from .AgentTeam import ...


class AgentOperatingSystem(BaseOrchestrator):
    """
    Unified interface for AgentOperatingSystem (AOS).
    
    Inherits all generic orchestration, workflow, and agent coordination logic from BaseOrchestrator.
    This class adds AOS-specific components such as perpetual agents, ML pipeline management, and leadership orchestration.
    
    - Generic, reusable orchestration logic: see BaseOrchestrator (in orchestration.py)
    - AOS-specific extensions: perpetual agent, ML pipeline, leadership, and (optionally) team logic
    
    Applications should extend this class to add their own domain/business logic, keeping orchestration generic and reusable.
    """
    
    def __init__(self, agent_manager=None):
        # Initialize base orchestration capabilities
        super().__init__(agent_manager)
        
        # Initialize AOS-specific components
        try:
            self.perpetual_agent = PerpetualAgent()
        except Exception as e:
            self.logger.warning(f"Could not initialize PerpetualAgent: {e}")
            self.perpetual_agent = None
            
        try:
            self.ml_pipeline = MLPipelineManager()
        except Exception as e:
            self.logger.warning(f"Could not initialize MLPipelineManager: {e}")
            self.ml_pipeline = None
            
        # Initialize leadership orchestration (this should always work)
        self.leadership = LeadershipOrchestrator()
        
        # Add team/multi-agent logic as needed
        # self.team_manager = ...
    
    # Leadership Management Methods
    def register_leadership_agent(self, role: str, agent_config: Dict[str, Any] = None) -> bool:
        """
        Register a leadership agent with the AOS.
        
        Args:
            role: Leadership role (e.g., "CEO", "CFO", "CTO")
            agent_config: Optional configuration for the agent
            
        Returns:
            bool: Success status
        """
        try:
            agent = LeadershipAgent(config=agent_config, role=role)
            return self.leadership.register_leadership_agent(role, agent)
        except Exception as e:
            self.logger.error(f"Failed to register leadership agent {role}: {e}")
            return False
    
    def get_leadership_agent(self, role: str) -> Optional[LeadershipAgent]:
        """Get a specific leadership agent by role."""
        return self.leadership.get_leadership_agent(role)
    
    def list_leadership_agents(self) -> List[str]:
        """Get list of registered leadership agent roles."""
        return self.leadership.list_leadership_agents()
    
    async def orchestrate_leadership_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a leadership decision across multiple agents."""
        return await self.leadership.orchestrate_leadership_decision(decision_context)
    
    async def delegate_leadership_task(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate a task to the appropriate leadership agent."""
        return await self.leadership.delegate_task(task_context)
    
    # The workflow management methods are now inherited from BaseOrchestrator
    # No need to redefine get_workflow_status() and list_workflows()
    
    async def get_aos_status(self) -> Dict[str, Any]:
        """
        Get comprehensive AOS system status including all components.
        
        Returns:
            Dict with complete AOS status information
        """
        base_status = await self.get_orchestration_status()
        
        # Get leadership performance
        leadership_performance = await self.leadership.monitor_leadership_performance()
        
        # Add AOS-specific status information
        aos_status = {
            **base_status,
            "components": {
                "perpetual_agent": self.perpetual_agent is not None,
                "ml_pipeline": self.ml_pipeline is not None,
                "leadership": self.leadership is not None,
            },
            "leadership": leadership_performance,
            "system_type": "AgentOperatingSystem"
        }
        
        return aos_status
    
    # Add unified methods to launch workflows, perpetual agents, ML tasks, etc.
    async def launch_perpetual_agent(self, agent_config: Dict[str, Any]) -> str:
        """
        Launch a perpetual agent with the given configuration.
        
        Args:
            agent_config: Configuration for the perpetual agent
            
        Returns:
            Agent ID for tracking
        """
        if not self.perpetual_agent:
            return "error:perpetual_agent_not_available"
        
        # Implementation would go here
        # This is a placeholder for the actual perpetual agent launch logic
        return f"perpetual_agent_{datetime.now().timestamp()}"
    
    async def start_ml_pipeline(self, pipeline_config: Dict[str, Any]) -> str:
        """
        Start an ML pipeline with the given configuration.
        
        Args:
            pipeline_config: Configuration for the ML pipeline
            
        Returns:
            Pipeline ID for tracking
        """
        if not self.ml_pipeline:
            return "error:ml_pipeline_not_available"
        
        # Implementation would go here
        # This is a placeholder for the actual ML pipeline start logic
        return f"ml_pipeline_{datetime.now().timestamp()}"
