from .workflow_step import WorkflowStep
from datetime import datetime, timezone

class Workflow:
    def __init__(self, workflow_id: str, steps: list):
        self.workflow_id = workflow_id
        self.steps = {step.step_id: step for step in steps}
        self.status = "pending"
        self.created_at = datetime.now(timezone.utc)
        self.started_at = None
        self.completed_at = None
