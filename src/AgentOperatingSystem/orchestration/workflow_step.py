"""
Workflow Step for AOS Orchestration

Represents a single step in a workflow execution.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class WorkflowStep:
    """
    Represents a single step in a workflow execution.
    """
    step_id: str
    agent_id: str
    task: str
    depends_on: List[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []

    def start(self):
        """Mark step as started"""
        self.status = "running"
        self.started_at = datetime.now(timezone.utc)

    def complete(self, result: Dict[str, Any] = None):
        """Mark step as completed"""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)
        if result:
            self.result = result

    def fail(self, error: str):
        """Mark step as failed"""
        self.status = "failed"
        self.completed_at = datetime.now(timezone.utc)
        self.error = error

    def is_ready(self, completed_steps: set) -> bool:
        """Check if this step is ready to run based on dependencies"""
        return all(dep_id in completed_steps for dep_id in self.depends_on)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "step_id": self.step_id,
            "agent_id": self.agent_id,
            "task": self.task,
            "depends_on": self.depends_on,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
