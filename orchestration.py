"""
Unified entry point for AgentOperatingSystem (AOS).
Exposes orchestration, perpetual agent, ML pipeline, leadership, and team logic.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio


from .workflow_step import WorkflowStep
from .workflow import Workflow
from .orchestration_engine import OrchestrationEngine

# Import and expose PerpetualAgent
from .PerpetualAgent import PerpetualAgent
# Import and expose ML pipeline manager
from .MLPipelineManager import MLPipelineManager
# Import and expose Leadership orchestrator
from .LeadershipOrchestrator import LeadershipOrchestrator

# Optionally, import and expose team/multi-agent logic if needed
# from .multi_agent import ...
# from .AgentTeam import ...

class AgentOperatingSystem:
    """
    Unified interface for AOS. Entry point for orchestration, agent management, ML pipeline, and leadership.
    """
    def __init__(self, agent_manager=None):
        self.orchestrator = OrchestrationEngine(agent_manager)
        self.perpetual_agent = PerpetualAgent()
        self.ml_pipeline = MLPipelineManager()
        self.leadership = LeadershipOrchestrator()
        # Add team/multi-agent logic as needed

    # Add unified methods to launch workflows, perpetual agents, ML tasks, etc.


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
