"""
AOS Orchestration Engine

Manages workflow orchestration and execution for the Agent Operating System.
Handles complex multi-agent workflows with dependencies and error handling.
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from ..core.config import OrchestrationConfig


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Workflow step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep:
    """Individual step in a workflow"""
    
    def __init__(self, step_id: str, agent_id: str, task: Dict[str, Any], 
                 depends_on: List[str] = None):
        self.step_id = step_id
        self.agent_id = agent_id
        self.task = task
        self.depends_on = depends_on or []
        self.status = StepStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.retry_count = 0


class Workflow:
    """Workflow definition and execution state"""
    
    def __init__(self, workflow_id: str, steps: List[WorkflowStep]):
        self.workflow_id = workflow_id
        self.steps = {step.step_id: step for step in steps}
        self.status = WorkflowStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.metadata = {}


class OrchestrationEngine:
    """
    Orchestration engine for managing complex multi-agent workflows.
    
    Handles:
    - Workflow definition and execution
    - Step dependencies and parallel execution
    - Error handling and retries
    - Workflow persistence and recovery
    """
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.logger = logging.getLogger("AOS.OrchestrationEngine")
        
        # Active workflows
        self.workflows: Dict[str, Workflow] = {}
        
        # Execution state
        self.is_running = False
        self.executor_task = None
        
        # Metrics
        self.total_workflows = 0
        self.completed_workflows = 0
        self.failed_workflows = 0
    
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
            workflow_config: Workflow configuration including steps
            
        Returns:
            Workflow ID
        """
        try:
            workflow_id = str(uuid.uuid4())
            
            # Parse workflow steps
            steps = []
            for step_config in workflow_config.get("steps", []):
                step = WorkflowStep(
                    step_id=step_config["id"],
                    agent_id=step_config["agent_id"],
                    task=step_config["task"],
                    depends_on=step_config.get("depends_on", [])
                )
                steps.append(step)
            
            # Create workflow
            workflow = Workflow(workflow_id, steps)
            workflow.metadata = workflow_config.get("metadata", {})
            
            # Register workflow
            self.workflows[workflow_id] = workflow
            self.total_workflows += 1
            
            self.logger.info(f"Workflow {workflow_id} created with {len(steps)} steps")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to start workflow: {e}")
            raise
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        if workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            return False
        
        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_at = datetime.utcnow()
        
        self.logger.info(f"Workflow {workflow_id} cancelled")
        return True
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status and progress"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        step_statuses = {}
        for step_id, step in workflow.steps.items():
            step_statuses[step_id] = {
                "status": step.status.value,
                "agent_id": step.agent_id,
                "started_at": step.started_at.isoformat() if step.started_at else None,
                "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                "error": step.error,
                "retry_count": step.retry_count
            }
        
        return {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": step_statuses,
            "metadata": workflow.metadata
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get orchestration engine status"""
        active_workflows = sum(1 for w in self.workflows.values() 
                              if w.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING])
        
        return {
            "is_running": self.is_running,
            "total_workflows": self.total_workflows,
            "active_workflows": active_workflows,
            "completed_workflows": self.completed_workflows,
            "failed_workflows": self.failed_workflows,
            "config": {
                "max_concurrent_workflows": self.config.max_concurrent_workflows,
                "workflow_timeout_seconds": self.config.workflow_timeout_seconds
            }
        }
    
    async def _workflow_executor(self):
        """Background task to execute workflows"""
        while self.is_running:
            try:
                # Find workflows ready to run
                pending_workflows = [
                    w for w in self.workflows.values() 
                    if w.status == WorkflowStatus.PENDING
                ]
                
                # Limit concurrent workflows
                running_count = sum(1 for w in self.workflows.values() 
                                  if w.status == WorkflowStatus.RUNNING)
                
                available_slots = self.config.max_concurrent_workflows - running_count
                
                # Start workflows up to the limit
                for workflow in pending_workflows[:available_slots]:
                    asyncio.create_task(self._execute_workflow(workflow))
                
                await asyncio.sleep(1)  # Check every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in workflow executor: {e}")
    
    async def _execute_workflow(self, workflow: Workflow):
        """Execute a single workflow"""
        try:
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.utcnow()
            
            self.logger.info(f"Starting workflow execution: {workflow.workflow_id}")
            
            # Execute steps with dependency resolution
            remaining_steps = set(workflow.steps.keys())
            
            while remaining_steps and workflow.status == WorkflowStatus.RUNNING:
                # Find steps ready to run (dependencies satisfied)
                ready_steps = []
                for step_id in remaining_steps:
                    step = workflow.steps[step_id]
                    dependencies_satisfied = all(
                        workflow.steps[dep_id].status == StepStatus.COMPLETED
                        for dep_id in step.depends_on
                        if dep_id in workflow.steps
                    )
                    
                    if dependencies_satisfied:
                        ready_steps.append(step)
                
                if not ready_steps:
                    # Check for circular dependencies or failed dependencies
                    failed_deps = any(
                        workflow.steps[dep_id].status == StepStatus.FAILED
                        for step_id in remaining_steps
                        for dep_id in workflow.steps[step_id].depends_on
                        if dep_id in workflow.steps
                    )
                    
                    if failed_deps:
                        # Mark remaining steps as skipped due to failed dependencies
                        for step_id in remaining_steps:
                            workflow.steps[step_id].status = StepStatus.SKIPPED
                            workflow.steps[step_id].error = "Skipped due to failed dependency"
                        break
                    else:
                        self.logger.error(f"Workflow {workflow.workflow_id} has circular dependencies")
                        workflow.status = WorkflowStatus.FAILED
                        break
                
                # Execute ready steps in parallel
                tasks = [self._execute_step(step) for step in ready_steps]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Remove completed steps
                for step in ready_steps:
                    remaining_steps.remove(step.step_id)
            
            # Determine final status
            if workflow.status == WorkflowStatus.RUNNING:
                step_statuses = [step.status for step in workflow.steps.values()]
                
                if all(status in [StepStatus.COMPLETED, StepStatus.SKIPPED] for status in step_statuses):
                    workflow.status = WorkflowStatus.COMPLETED
                    self.completed_workflows += 1
                else:
                    workflow.status = WorkflowStatus.FAILED
                    self.failed_workflows += 1
            
            workflow.completed_at = datetime.utcnow()
            
            self.logger.info(f"Workflow {workflow.workflow_id} completed with status: {workflow.status.value}")
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.utcnow()
            self.failed_workflows += 1
            self.logger.error(f"Workflow {workflow.workflow_id} failed: {e}")
    
    async def _execute_step(self, step: WorkflowStep):
        """Execute a single workflow step"""
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()
        
        try:
            # This would integrate with the actual agent execution
            # For now, simulate step execution
            self.logger.info(f"Executing step {step.step_id} on agent {step.agent_id}")
            
            # Placeholder for actual agent task execution
            await asyncio.sleep(0.1)  # Simulate work
            
            step.result = {"status": "completed", "output": "Task completed successfully"}
            step.status = StepStatus.COMPLETED
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            self.logger.error(f"Step {step.step_id} failed: {e}")
        
        finally:
            step.completed_at = datetime.utcnow()