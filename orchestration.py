"""
Orchestration primitives for multi-agent workflows and coordination.
Moved from BusinessInfinity/core/orchestrator.py for reuse.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio

class WorkflowStep:
    """Represents a single step in a workflow"""
    def __init__(self, step_id: str, agent_id: str, task: str, depends_on: List[str] = None):
        self.step_id = step_id
        self.agent_id = agent_id
        self.task = task
        self.depends_on = depends_on or []
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None

class Workflow:
    """Represents a complete workflow with multiple steps"""
    def __init__(self, workflow_id: str, steps: List[WorkflowStep]):
        self.workflow_id = workflow_id
        self.steps = {step.step_id: step for step in steps}
        self.status = "pending"
        self.created_at = datetime.now(timezone.utc)
        self.started_at = None
        self.completed_at = None

class OrchestrationEngine:
    """
    Orchestration engine for multi-agent workflows and coordination.
    Provides dependency management, execution modes, and workflow status.
    """
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_counter = 0

    async def execute_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        workflow_id = f"workflow_{self.workflow_counter}"
        self.workflow_counter += 1
        steps = []
        for step_def in workflow_definition.get("steps", []):
            step = WorkflowStep(
                step_id=step_def["id"],
                agent_id=step_def["agent"],
                task=step_def["task"],
                depends_on=step_def.get("depends_on", [])
            )
            steps.append(step)
        workflow = Workflow(workflow_id, steps)
        self.workflows[workflow_id] = workflow
        await self._execute_workflow(workflow)
        return workflow_id

    async def _execute_workflow(self, workflow: Workflow):
        workflow.status = "running"
        workflow.started_at = datetime.now(timezone.utc)
        try:
            remaining_steps = set(workflow.steps.keys())
            while remaining_steps:
                ready_steps = []
                for step_id in remaining_steps:
                    step = workflow.steps[step_id]
                    if all(workflow.steps[dep_id].status == "completed" for dep_id in step.depends_on):
                        ready_steps.append(step)
                if not ready_steps:
                    for step_id in remaining_steps:
                        workflow.steps[step_id].status = "failed"
                        workflow.steps[step_id].error = "Dependency not satisfied"
                    break
                tasks = [self._execute_workflow_step(step) for step in ready_steps]
                await asyncio.gather(*tasks)
                for step in ready_steps:
                    remaining_steps.remove(step.step_id)
            if all(step.status == "completed" for step in workflow.steps.values()):
                workflow.status = "completed"
            else:
                workflow.status = "failed"
        except Exception as e:
            workflow.status = "failed"
        workflow.completed_at = datetime.now(timezone.utc)

    async def _execute_workflow_step(self, step: WorkflowStep):
        step.status = "running"
        step.started_at = datetime.now(timezone.utc)
        try:
            result = await self.agent_manager.execute_agent(step.agent_id, step.task)
            if result:
                step.result = result
                step.status = "completed"
            else:
                step.status = "failed"
                step.error = f"Agent {step.agent_id} not found or returned no result"
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
        step.completed_at = datetime.now(timezone.utc)

    async def coordinate_agents(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        task = coordination_request.get("task", "")
        agents = coordination_request.get("agents", [])
        mode = coordination_request.get("mode", "parallel")
        if not agents:
            return {"error": "No agents specified"}
        results = {}
        try:
            if mode == "parallel":
                tasks = [self.agent_manager.execute_agent(agent_id, task) for agent_id in agents]
                agent_results = await asyncio.gather(*tasks)
                for i, agent_id in enumerate(agents):
                    results[agent_id] = agent_results[i]
            elif mode == "sequential":
                context = task
                for agent_id in agents:
                    result = await self.agent_manager.execute_agent(agent_id, context)
                    results[agent_id] = result
                    if result:
                        context += f"\n\nPrevious result from {agent_id}: {result}"
            elif mode == "hierarchical":
                if len(agents) < 2:
                    return {"error": "Hierarchical mode requires at least 2 agents"}
                coordinator = agents[0]
                workers = agents[1:]
                coord_task = f"Coordinate this task among these agents {workers}: {task}"
                coord_result = await self.agent_manager.execute_agent(coordinator, coord_task)
                results[coordinator] = coord_result
                for agent_id in workers:
                    worker_task = f"Execute your part of this coordinated task:\nOriginal task: {task}\nCoordination guidance: {coord_result}"
                    worker_result = await self.agent_manager.execute_agent(agent_id, worker_task)
                    results[agent_id] = worker_result
            return {
                "status": "completed",
                "mode": mode,
                "results": results
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "partial_results": results
            }

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        workflow = self.workflows.get(workflow_id)
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
        return [self.get_workflow_status(wid) for wid in self.workflows.keys()]
