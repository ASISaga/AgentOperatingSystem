"""
AOS Orchestration Engine

Provides workflow orchestration and service coordination for the Agent Operating System.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    id: str
    name: str
    type: str  # agent_task, system_call, conditional, parallel
    config: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_attempts: int = 3
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "config": self.config,
            "depends_on": self.depends_on,
            "timeout_seconds": self.timeout_seconds,
            "retry_attempts": self.retry_attempts,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "result": self.result,
            "error": self.error
        }


@dataclass
class Workflow:
    """Workflow definition and execution state"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    config: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_seconds: int = 3600
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "config": self.config,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "timeout_seconds": self.timeout_seconds,
            "context": self.context
        }
    
    def get_ready_steps(self) -> List[WorkflowStep]:
        """Get steps that are ready to execute"""
        ready_steps = []
        completed_step_ids = {step.id for step in self.steps if step.status == StepStatus.COMPLETED}
        
        for step in self.steps:
            if step.status == StepStatus.PENDING:
                # Check if all dependencies are completed
                if all(dep_id in completed_step_ids for dep_id in step.depends_on):
                    ready_steps.append(step)
        
        return ready_steps
    
    def is_complete(self) -> bool:
        """Check if workflow is complete"""
        return all(step.status in [StepStatus.COMPLETED, StepStatus.SKIPPED] for step in self.steps)
    
    def has_failed(self) -> bool:
        """Check if workflow has failed"""
        return any(step.status == StepStatus.FAILED for step in self.steps)


class OrchestrationEngine:
    """
    Core orchestration engine for AOS.
    
    Manages workflow execution, step coordination, and resource scheduling.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("AOS.OrchestrationEngine")
        
        # Active workflows
        self.workflows: Dict[str, Workflow] = {}
        
        # Step executors (step_type -> executor_function)
        self.step_executors: Dict[str, Callable] = {}
        
        # Execution state
        self.is_running = False
        self.executor_task = None
        self.max_concurrent_workflows = getattr(config, 'max_concurrent_workflows', 100)
        
        # Register default step executors
        self._register_default_executors()
    
    def _register_default_executors(self):
        """Register default step executor functions"""
        self.step_executors.update({
            "agent_task": self._execute_agent_task,
            "system_call": self._execute_system_call,
            "conditional": self._execute_conditional,
            "parallel": self._execute_parallel,
            "delay": self._execute_delay
        })
    
    async def start(self):
        """Start the orchestration engine"""
        if self.is_running:
            return
        
        self.is_running = True
        self.executor_task = asyncio.create_task(self._workflow_executor())
        self.logger.info("OrchestrationEngine started")
    
    async def stop(self):
        """Stop the orchestration engine"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel running workflows
        for workflow in self.workflows.values():
            if workflow.status == WorkflowStatus.RUNNING:
                workflow.status = WorkflowStatus.CANCELLED
        
        if self.executor_task:
            self.executor_task.cancel()
            try:
                await self.executor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("OrchestrationEngine stopped")
    
    async def start_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """
        Start a new workflow.
        
        Args:
            workflow_config: Workflow configuration
            
        Returns:
            Workflow ID
        """
        try:
            workflow = self._create_workflow_from_config(workflow_config)
            self.workflows[workflow.id] = workflow
            
            self.logger.info(f"Started workflow {workflow.id}: {workflow.name}")
            return workflow.id
            
        except Exception as e:
            self.logger.error(f"Failed to start workflow: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get orchestration engine status"""
        status_counts = {}
        for workflow in self.workflows.values():
            status = workflow.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "is_running": self.is_running,
            "total_workflows": len(self.workflows),
            "max_concurrent_workflows": self.max_concurrent_workflows,
            "workflow_status_counts": status_counts,
            "registered_executors": list(self.step_executors.keys())
        }
    
    def _create_workflow_from_config(self, config: Dict[str, Any]) -> Workflow:
        """Create workflow instance from configuration"""
        workflow_id = config.get("id", str(uuid.uuid4()))
        
        # Create steps
        steps = []
        for step_config in config.get("steps", []):
            step = WorkflowStep(
                id=step_config.get("id", str(uuid.uuid4())),
                name=step_config.get("name", "Unnamed Step"),
                type=step_config.get("type", "agent_task"),
                config=step_config.get("config", {}),
                depends_on=step_config.get("depends_on", []),
                timeout_seconds=step_config.get("timeout_seconds", 300),
                retry_attempts=step_config.get("retry_attempts", 3)
            )
            steps.append(step)
        
        return Workflow(
            id=workflow_id,
            name=config.get("name", "Unnamed Workflow"),
            description=config.get("description", ""),
            steps=steps,
            config=config.get("workflow_config", {}),
            timeout_seconds=config.get("timeout_seconds", 3600),
            context=config.get("context", {})
        )
    
    async def _workflow_executor(self):
        """Main workflow execution loop"""
        while self.is_running:
            try:
                await self._process_workflows()
                await asyncio.sleep(1)  # Process workflows every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in workflow executor: {e}")
    
    async def _process_workflows(self):
        """Process all active workflows"""
        running_count = 0
        
        for workflow in self.workflows.values():
            if workflow.status == WorkflowStatus.RUNNING:
                running_count += 1
            elif workflow.status == WorkflowStatus.PENDING and running_count < self.max_concurrent_workflows:
                # Start new workflow
                workflow.status = WorkflowStatus.RUNNING
                workflow.started_at = datetime.utcnow()
                running_count += 1
                self.logger.info(f"Started executing workflow {workflow.id}")
            
            # Process running workflows
            if workflow.status == WorkflowStatus.RUNNING:
                await self._execute_workflow_steps(workflow)
    
    async def _execute_workflow_steps(self, workflow: Workflow):
        """Execute ready steps in a workflow"""
        try:
            # Check for workflow timeout
            if workflow.started_at:
                elapsed = (datetime.utcnow() - workflow.started_at).total_seconds()
                if elapsed > workflow.timeout_seconds:
                    workflow.status = WorkflowStatus.FAILED
                    workflow.completed_at = datetime.utcnow()
                    self.logger.error(f"Workflow {workflow.id} timed out after {elapsed} seconds")
                    return
            
            # Get ready steps
            ready_steps = workflow.get_ready_steps()
            
            # Execute ready steps
            for step in ready_steps:
                await self._execute_step(workflow, step)
            
            # Check if workflow is complete
            if workflow.is_complete():
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.utcnow()
                self.logger.info(f"Workflow {workflow.id} completed successfully")
            elif workflow.has_failed():
                workflow.status = WorkflowStatus.FAILED
                workflow.completed_at = datetime.utcnow()
                self.logger.error(f"Workflow {workflow.id} failed")
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.utcnow()
            self.logger.error(f"Error executing workflow {workflow.id}: {e}")
    
    async def _execute_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute a single workflow step"""
        step.status = StepStatus.RUNNING
        step.start_time = datetime.utcnow()
        
        try:
            self.logger.debug(f"Executing step {step.id} ({step.type}) in workflow {workflow.id}")
            
            # Get executor for step type
            if step.type not in self.step_executors:
                raise ValueError(f"No executor found for step type: {step.type}")
            
            executor = self.step_executors[step.type]
            
            # Execute with timeout
            result = await asyncio.wait_for(
                executor(workflow, step),
                timeout=step.timeout_seconds
            )
            
            step.result = result
            step.status = StepStatus.COMPLETED
            step.end_time = datetime.utcnow()
            
            self.logger.debug(f"Step {step.id} completed successfully")
            
        except asyncio.TimeoutError:
            step.status = StepStatus.FAILED
            step.error = f"Step timed out after {step.timeout_seconds} seconds"
            step.end_time = datetime.utcnow()
            self.logger.error(f"Step {step.id} timed out")
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.end_time = datetime.utcnow()
            self.logger.error(f"Step {step.id} failed: {e}")
    
    # Default step executors
    async def _execute_agent_task(self, workflow: Workflow, step: WorkflowStep) -> Dict[str, Any]:
        """Execute an agent task step"""
        agent_id = step.config.get("agent_id")
        task = step.config.get("task")
        
        if not agent_id or not task:
            raise ValueError("agent_task step requires 'agent_id' and 'task' in config")
        
        # This would typically send a message to the agent via the message bus
        # For now, return a mock result
        return {
            "agent_id": agent_id,
            "task": task,
            "result": "Task completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_system_call(self, workflow: Workflow, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a system call step"""
        command = step.config.get("command")
        
        if not command:
            raise ValueError("system_call step requires 'command' in config")
        
        # This would typically execute a system command
        # For now, return a mock result
        return {
            "command": command,
            "result": "Command executed",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_conditional(self, workflow: Workflow, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a conditional step"""
        condition = step.config.get("condition")
        
        if not condition:
            raise ValueError("conditional step requires 'condition' in config")
        
        # Evaluate condition (simplified)
        result = eval(condition, {"context": workflow.context})
        
        return {
            "condition": condition,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_parallel(self, workflow: Workflow, step: WorkflowStep) -> Dict[str, Any]:
        """Execute parallel sub-steps"""
        sub_steps = step.config.get("sub_steps", [])
        
        if not sub_steps:
            raise ValueError("parallel step requires 'sub_steps' in config")
        
        # Execute sub-steps concurrently
        tasks = []
        for sub_step_config in sub_steps:
            sub_step = WorkflowStep(
                id=str(uuid.uuid4()),
                name=sub_step_config.get("name", "Parallel Sub-step"),
                type=sub_step_config.get("type", "agent_task"),
                config=sub_step_config.get("config", {})
            )
            tasks.append(self._execute_step(workflow, sub_step))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "sub_step_count": len(sub_steps),
            "results": [str(result) for result in results],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_delay(self, workflow: Workflow, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a delay step"""
        delay_seconds = step.config.get("delay_seconds", 1)
        
        await asyncio.sleep(delay_seconds)
        
        return {
            "delay_seconds": delay_seconds,
            "timestamp": datetime.utcnow().isoformat()
        }


# Legacy compatibility
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
        from .config import default_config
        self.orchestration_engine = OrchestrationEngine(default_config.orchestration_config)
        self.agent_manager = agent_manager
        
        # Event handling system for extensibility
        self.event_handlers: Dict[str, List] = {}
        
        # Logging
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def execute_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """
        Execute a workflow based on its definition.
        
        Args:
            workflow_definition: Dictionary defining the workflow steps and dependencies
            
        Returns:
            str: Workflow ID for tracking execution
        """
        return await self.orchestration_engine.start_workflow(workflow_definition)
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get orchestration engine status"""
        return await self.orchestration_engine.get_status()


# Export the core orchestration classes
__all__ = [
    'Workflow',
    'WorkflowStep', 
    'OrchestrationEngine',
    'BaseOrchestrator',
    'WorkflowStatus',
    'StepStatus'
]
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