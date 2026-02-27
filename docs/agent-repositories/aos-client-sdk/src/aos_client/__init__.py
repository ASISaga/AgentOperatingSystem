"""AOS Client SDK — lightweight client for Agent Operating System services.

This SDK enables client applications to interact with the Agent Operating System
as an infrastructure service:

- Browse available agents from the RealmOfAgents catalog
- Compose orchestrations by selecting agents
- Submit orchestration requests to AOS
- Monitor orchestration status and retrieve results
"""

__version__ = "1.0.0"

from aos_client.client import AOSClient
from aos_client.models import (
    AgentDescriptor,
    OrchestrationRequest,
    OrchestrationResult,
    OrchestrationStatus,
)

__all__ = [
    "AOSClient",
    "AgentDescriptor",
    "OrchestrationRequest",
    "OrchestrationResult",
    "OrchestrationStatus",
]
