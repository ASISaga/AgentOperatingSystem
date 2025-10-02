"""
Agent Operating System (AOS) - Main Entry Point

This module provides the main AOS class that serves as the operating system
for all leadership agents. It integrates all core components and provides
a unified interface for agent management.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio
import logging

# Import the new core AOS components
from .aos_core import AgentOperatingSystem as AOSCore, BaseAgent
from .config import AOSConfig, default_config

# Import legacy components for backward compatibility
from .orchestration import BaseOrchestrator, OrchestrationEngine
from .LeadershipAgent import LeadershipAgent
from .LeadershipOrchestrator import LeadershipOrchestrator

# Import specific AOS components
try:
    from .PerpetualAgent import PerpetualAgent
except ImportError:
    PerpetualAgent = None

try:
    from .MLPipelineManager import MLPipelineManager
except ImportError:
    MLPipelineManager = None


class AgentOperatingSystem(AOSCore):
    """
    Enhanced Agent Operating System with backward compatibility.
    
    This class extends the core AOS with additional features and maintains
    backward compatibility with existing implementations.
    """
    
    def __init__(self, config: AOSConfig = None):
        # Use default config if none provided
        if config is None:
            config = default_config
        
        # Initialize core AOS
        super().__init__(config)
        
        # Legacy components for backward compatibility
        self.legacy_orchestrator = None
        self.legacy_leadership = None
        self.legacy_perpetual_agent = None
        self.legacy_ml_pipeline = None
        
        # Initialize legacy components if needed
        self._initialize_legacy_components()
    
    def _initialize_legacy_components(self):
        """Initialize legacy components for backward compatibility"""
        try:
            # Legacy orchestrator
            self.legacy_orchestrator = BaseOrchestrator()
            
            # Legacy leadership orchestrator
            self.legacy_leadership = LeadershipOrchestrator()
            
            # Legacy perpetual agent
            if PerpetualAgent:
                try:
                    self.legacy_perpetual_agent = PerpetualAgent()
                except Exception as e:
                    self.logger.warning(f"Could not initialize legacy PerpetualAgent: {e}")
            
            # Legacy ML pipeline
            if MLPipelineManager:
                try:
                    self.legacy_ml_pipeline = MLPipelineManager()
                except Exception as e:
                    self.logger.warning(f"Could not initialize legacy MLPipelineManager: {e}")
            
            self.logger.info("Legacy components initialized for backward compatibility")
            
        except Exception as e:
            self.logger.error(f"Error initializing legacy components: {e}")
    
    # Enhanced agent registration with leadership support
    async def register_leadership_agent(self, role: str, agent_config: Dict[str, Any] = None) -> bool:
        """
        Register a leadership agent with the AOS.
        
        Args:
            role: Leadership role (e.g., "CEO", "CFO", "CTO")
            agent_config: Optional configuration for the agent
            
        Returns:
            bool: Success status
        """
        try:
            # Create leadership agent
            agent = LeadershipAgent(config=agent_config, role=role)
            
            # Register with core AOS
            success = await self.register_agent(agent)
            
            # Also register with legacy leadership orchestrator
            if success and self.legacy_leadership:
                self.legacy_leadership.register_leadership_agent(role, agent)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to register leadership agent {role}: {e}")
            return False
    
    def get_leadership_agent(self, role: str) -> Optional[LeadershipAgent]:
        """Get a specific leadership agent by role."""
        # Try to find in registered agents
        for agent in self.agents.values():
            if isinstance(agent, LeadershipAgent) and agent.role == role:
                return agent
        
        # Fallback to legacy leadership orchestrator
        if self.legacy_leadership:
            return self.legacy_leadership.get_leadership_agent(role)
        
        return None
    
    def list_leadership_agents(self) -> List[str]:
        """Get list of registered leadership agent roles."""
        roles = []
        
        # Get from registered agents
        for agent in self.agents.values():
            if isinstance(agent, LeadershipAgent):
                roles.append(agent.role)
        
        # Also get from legacy orchestrator
        if self.legacy_leadership:
            legacy_roles = self.legacy_leadership.list_leadership_agents()
            roles.extend(r for r in legacy_roles if r not in roles)
        
        return roles
    
    async def orchestrate_leadership_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a leadership decision across multiple agents."""
        # Use legacy leadership orchestrator for now
        if self.legacy_leadership:
            return await self.legacy_leadership.orchestrate_leadership_decision(decision_context)
        
        # Fallback to core decision engine
        return await self.make_decision(decision_context)
    
    async def delegate_leadership_task(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate a task to the appropriate leadership agent."""
        # Use legacy leadership orchestrator for now
        if self.legacy_leadership:
            return await self.legacy_leadership.delegate_task(task_context)
        
        # Fallback implementation
        return {"status": "delegated", "context": task_context}
    
    # Legacy workflow methods for backward compatibility
    async def execute_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """Execute a workflow (legacy compatibility)"""
        if self.legacy_orchestrator:
            return await self.legacy_orchestrator.execute_workflow(workflow_definition)
        
        # Use core orchestration engine
        return await self.orchestrate_workflow(workflow_definition)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status (legacy compatibility)"""
        if self.legacy_orchestrator:
            workflow = self.legacy_orchestrator.orchestration_engine.workflows.get(workflow_id)
            if workflow:
                return workflow.to_dict()
        
        # Fallback to checking orchestration engine
        return None
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows (legacy compatibility)"""
        if self.legacy_orchestrator:
            workflows = []
            for workflow_id in self.legacy_orchestrator.orchestration_engine.workflows.keys():
                status = self.get_workflow_status(workflow_id)
                if status:
                    workflows.append(status)
            return workflows
        
        return []
    
    async def get_aos_status(self) -> Dict[str, Any]:
        """
        Get comprehensive AOS system status including all components.
        
        Returns:
            Dict with complete AOS status information
        """
        # Get core AOS status
        base_status = await self.get_system_status()
        
        # Add legacy component status
        legacy_status = {}
        if self.legacy_leadership:
            try:
                leadership_performance = await self.legacy_leadership.monitor_leadership_performance()
                legacy_status["legacy_leadership"] = leadership_performance
            except Exception as e:
                legacy_status["legacy_leadership"] = {"error": str(e)}
        
        # Enhanced status with legacy information
        enhanced_status = {
            **base_status,
            "legacy_components": {
                "orchestrator": self.legacy_orchestrator is not None,
                "leadership": self.legacy_leadership is not None,
                "perpetual_agent": self.legacy_perpetual_agent is not None,
                "ml_pipeline": self.legacy_ml_pipeline is not None,
            },
            "legacy_status": legacy_status,
            "system_type": "Enhanced_AgentOperatingSystem",
            "version": "2.0"
        }
        
        return enhanced_status
    
    # Legacy perpetual agent methods
    async def launch_perpetual_agent(self, agent_config: Dict[str, Any]) -> str:
        """
        Launch a perpetual agent with the given configuration.
        
        Args:
            agent_config: Configuration for the perpetual agent
            
        Returns:
            Agent ID for tracking
        """
        if self.legacy_perpetual_agent:
            # Use legacy perpetual agent
            return f"legacy_perpetual_agent_{datetime.now().timestamp()}"
        
        return f"perpetual_agent_{datetime.now().timestamp()}"
    
    async def start_ml_pipeline(self, pipeline_config: Dict[str, Any]) -> str:
        """
        Start an ML pipeline with the given configuration.
        
        Args:
            pipeline_config: Configuration for the ML pipeline
            
        Returns:
            Pipeline ID for tracking
        """
        if self.legacy_ml_pipeline:
            # Use legacy ML pipeline
            return f"legacy_ml_pipeline_{datetime.now().timestamp()}"
        
        return f"ml_pipeline_{datetime.now().timestamp()}"


# Backward compatibility exports
__all__ = [
    'AgentOperatingSystem',
    'BaseAgent',
    'LeadershipAgent',
    'AOSConfig'
]