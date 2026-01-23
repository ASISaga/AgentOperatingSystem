import os
from dataclasses import dataclass


@dataclass
class OrchestrationConfig:
    """Configuration for AOS orchestration engine"""
    max_concurrent_workflows: int = 100
    workflow_timeout_seconds: int = 3600
    enable_workflow_persistence: bool = True
    retry_max_attempts: int = 3
    retry_delay_seconds: int = 5

    @classmethod
    def from_env(cls):
        return cls(
            max_concurrent_workflows=int(os.getenv("AOS_MAX_WORKFLOWS", "100")),
            workflow_timeout_seconds=int(os.getenv("AOS_WORKFLOW_TIMEOUT", "3600")),
            enable_workflow_persistence=os.getenv("AOS_WORKFLOW_PERSISTENCE", "true").lower() == "true",
            retry_max_attempts=int(os.getenv("AOS_RETRY_MAX_ATTEMPTS", "3")),
            retry_delay_seconds=int(os.getenv("AOS_RETRY_DELAY", "5"))
        )
