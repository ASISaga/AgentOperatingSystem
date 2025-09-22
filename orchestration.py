"""
Generic Orchestration Module for Agent Operating System

This module provides domain-agnostic orchestration capabilities that can be reused
across different applications. It consolidates:
- Workflow definitions and management
- WorkflowStep definitions and execution
- OrchestrationEngine for workflow coordination
- Agent coordination strategies

This module should NOT contain any business-specific logic or domain knowledge.
All business logic should be implemented in the applications that use AOS.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
import asyncio
import logging

# Import core orchestration components
from .workflow import Workflow
from .workflow_step import WorkflowStep
from .orchestration_engine import OrchestrationEngine

# Export the core orchestration classes
__all__ = [
    'Workflow',
    'WorkflowStep', 
    'OrchestrationEngine',
    'BaseOrchestrator'
]

class BaseOrchestrator:
    """
    Base orchestrator class that provides generic orchestration capabilities.
    
    This class is designed to be extended by application-specific orchestrators
    that add their own business logic and domain-specific functionality.
    """
    
    def __init__(self, agent_manager=None):
        """
        Initialize the base orchestrator with an agent manager.
        
        Args:
            agent_manager: Agent management interface for executing agent tasks
        """
        self.orchestration_engine = OrchestrationEngine(agent_manager)
        self.agent_manager = agent_manager
        
        # Event handling system for extensibility
        self.event_handlers: Dict[str, List] = {}
        
        # Logging
        self.logger = logging.getLogger(self.__class__.__name__)
    
    # Workflow Management
    async def execute_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """
        Execute a workflow based on its definition.
        
        Args:
            workflow_definition: Dictionary defining the workflow steps and dependencies
            
        Returns:
            str: Workflow ID for tracking execution
        """
        return await self.orchestration_engine.execute_workflow(workflow_definition)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a workflow.
        
        Args:
            workflow_id: ID of the workflow to check
            
        Returns:
            Dict with workflow status information, or None if workflow not found
        """
        workflow = self.orchestration_engine.workflows.get(workflow_id)
        if not workflow:
            return None
        
        return {
            "workflow_id": workflow_id,
            "status": workflow.status,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": {
                step_id: {
                    "status": step.status,
                    "agent_id": step.agent_id,
                    "task": step.task,
                    "result": step.result,
                    "error": step.error,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None
                }
                for step_id, step in workflow.steps.items()
            }
        }
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all workflows with their current status.
        
        Returns:
            List of workflow status dictionaries
        """
        return [
            self.get_workflow_status(workflow_id) 
            for workflow_id in self.orchestration_engine.workflows.keys()
        ]
    
    # Agent Coordination
    async def coordinate_agents(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic agent coordination method.
        
        This method provides basic coordination capabilities and should be
        extended by application-specific orchestrators for domain-specific logic.
        
        Args:
            coordination_request: Request defining the coordination requirements
            
        Returns:
            Dict with coordination results
        """
        try:
            # Extract coordination parameters
            agents = coordination_request.get("agents", [])
            coordination_type = coordination_request.get("type", "sequential")
            
            if coordination_type == "workflow":
                # Convert coordination request to workflow definition
                workflow_def = self._convert_coordination_to_workflow(coordination_request)
                workflow_id = await self.execute_workflow(workflow_def)
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "message": f"Workflow {workflow_id} started successfully"
                }
            else:
                # Basic coordination logic
                results = []
                for agent_config in agents:
                    if self.agent_manager:
                        result = await self.agent_manager.execute_agent(
                            agent_config.get("id"),
                            agent_config.get("task")
                        )
                        results.append({
                            "agent_id": agent_config.get("id"),
                            "result": result
                        })
                
                return {
                    "status": "success",
                    "results": results
                }
                
        except Exception as e:
            self.logger.error(f"Agent coordination failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    # Event System
    def register_event_handler(self, event_type: str, handler):
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Callable to handle the event
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def emit_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Emit an event to all registered handlers.
        
        Args:
            event_type: Type of event being emitted
            event_data: Data associated with the event
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event_data)
                except Exception as e:
                    self.logger.error(f"Event handler failed for {event_type}: {str(e)}")
    
    # Helper Methods
    def _convert_coordination_to_workflow(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a coordination request to a workflow definition.
        
        Args:
            coordination_request: Request to convert
            
        Returns:
            Workflow definition dictionary
        """
        agents = coordination_request.get("agents", [])
        steps = []
        
        for i, agent_config in enumerate(agents):
            step = {
                "id": f"step_{i}",
                "agent": agent_config.get("id"),
                "task": agent_config.get("task"),
                "depends_on": [f"step_{i-1}"] if i > 0 else []
            }
            steps.append(step)
        
        return {
            "name": coordination_request.get("name", "Generated Workflow"),
            "steps": steps
        }
    
    # Status and Monitoring
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """
        Get the current status of the orchestration system.
        
        Returns:
            Dict with orchestration system status
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflows": {
                "total": len(self.orchestration_engine.workflows),
                "active": sum(1 for w in self.orchestration_engine.workflows.values() 
                             if w.status == "running"),
                "completed": sum(1 for w in self.orchestration_engine.workflows.values() 
                                if w.status == "completed"),
                "failed": sum(1 for w in self.orchestration_engine.workflows.values() 
                             if w.status == "failed")
            },
            "agent_manager": self.agent_manager is not None,
            "event_handlers": {
                event_type: len(handlers) 
                for event_type, handlers in self.event_handlers.items()
            }
        }