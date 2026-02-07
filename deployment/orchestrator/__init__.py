"""
Azure Bicep Deployment Orchestrator

A Python-based orchestration layer that governs Azure Bicep deployments
with strict quality and safety standards.
"""

from .core.orchestrator import BicepOrchestrator
from .core.state_machine import DeploymentState, DeploymentStateMachine
from .core.failure_classifier import FailureClassifier, FailureType

__version__ = "1.0.0"
__all__ = [
    "BicepOrchestrator",
    "DeploymentState",
    "DeploymentStateMachine",
    "FailureClassifier",
    "FailureType",
]
