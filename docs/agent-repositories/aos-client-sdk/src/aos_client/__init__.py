"""AOS Client SDK — framework and client for Agent Operating System applications.

This SDK enables client applications to interact with the Agent Operating System
as an infrastructure service:

- **AOSApp** — Azure Functions application framework with workflow decorators
- **AOSClient** — HTTP/Service Bus client for agent discovery and orchestration
- **AOSAuth** — Azure IAM authentication and role-based access control
- **AOSServiceBus** — Async communication via Azure Service Bus
- **AOSRegistration** — Client app registration and infrastructure provisioning
- **AOSDeployer** — Code deployment to Azure Functions
"""

__version__ = "3.0.0"

from aos_client.client import AOSClient
from aos_client.models import (
    AgentDescriptor,
    OrchestrationPurpose,
    OrchestrationRequest,
    OrchestrationStatus,
)
from aos_client.app import AOSApp, WorkflowRequest
from aos_client.auth import AOSAuth, TokenClaims
from aos_client.service_bus import AOSServiceBus
from aos_client.registration import AOSRegistration, AppRegistration
from aos_client.deployment import AOSDeployer, DeploymentResult

__all__ = [
    "AOSApp",
    "AOSClient",
    "AOSAuth",
    "AOSDeployer",
    "AOSRegistration",
    "AOSServiceBus",
    "AgentDescriptor",
    "AppRegistration",
    "DeploymentResult",
    "OrchestrationPurpose",
    "OrchestrationRequest",
    "OrchestrationStatus",
    "TokenClaims",
    "WorkflowRequest",
]
