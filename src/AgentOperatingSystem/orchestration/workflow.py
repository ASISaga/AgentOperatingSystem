"""
Workflow for AOS Orchestration

Represents a complete workflow with multiple steps and dependencies.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field
from .workflow_step import WorkflowStep


@dataclass
class Workflow:
    """
    Represents a complete workflow with multiple steps and dependencies.
    """
    workflow_id: str
    steps: Dict[str, WorkflowStep] = field(default_factory=dict)
    status: str = "pending"
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    @classmethod
    def from_steps(cls, workflow_id: str, steps: List[WorkflowStep]) -> 'Workflow':
        """Create workflow from a list of steps"""
        workflow = cls(workflow_id=workflow_id)
        workflow.steps = {step.step_id: step for step in steps}
        return workflow

    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow"""
        self.steps[step.step_id] = step

    def start(self):
        """Mark workflow as started"""
        self.status = "running"
        self.started_at = datetime.now(timezone.utc)

    def complete(self):
        """Mark workflow as completed"""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)

    def fail(self):
        """Mark workflow as failed"""
        self.status = "failed"
        self.completed_at = datetime.now(timezone.utc)

    def get_ready_steps(self) -> List[WorkflowStep]:
        """Get steps that are ready to run"""
        completed_steps = {step_id for step_id, step in self.steps.items()
                          if step.status == "completed"}

        ready_steps = []
        for step in self.steps.values():
            if step.status == "pending" and step.is_ready(completed_steps):
                ready_steps.append(step)

        return ready_steps

    def is_complete(self) -> bool:
        """Check if all steps are completed"""
        return all(step.status == "completed" for step in self.steps.values())

    def has_failed(self) -> bool:
        """Check if any step has failed"""
        return any(step.status == "failed" for step in self.steps.values())

    def get_progress(self) -> Dict[str, Any]:
        """Get workflow progress information"""
        total_steps = len(self.steps)
        completed_steps = sum(1 for step in self.steps.values() if step.status == "completed")
        failed_steps = sum(1 for step in self.steps.values() if step.status == "failed")
        running_steps = sum(1 for step in self.steps.values() if step.status == "running")

        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "running_steps": running_steps,
            "progress_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "steps": {step_id: step.to_dict() for step_id, step in self.steps.items()},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }