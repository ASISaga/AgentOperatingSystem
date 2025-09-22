class WorkflowStep:
    def __init__(self, step_id: str, agent_id: str, task: str, depends_on=None):
        self.step_id = step_id
        self.agent_id = agent_id
        self.task = task
        self.depends_on = depends_on or []
        self.status = "pending"
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
