from .workflow import Workflow
from .workflow_step import WorkflowStep
from datetime import datetime, timezone
import asyncio

class OrchestrationEngine:
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.workflows = {}
        self.workflow_counter = 0

    async def execute_workflow(self, workflow_definition):
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

    async def _execute_workflow(self, workflow):
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

    async def _execute_workflow_step(self, step):
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
        finally:
            step.completed_at = datetime.now(timezone.utc)
