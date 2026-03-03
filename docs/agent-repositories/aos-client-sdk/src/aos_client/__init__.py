"""AOS Client SDK — framework and client for Agent Operating System applications.

This SDK enables client applications to interact with the Agent Operating System
as an infrastructure service:

- **AOSApp** — Azure Functions application framework with workflow decorators
- **AOSClient** — HTTP/Service Bus client for agent discovery and orchestration
- **AOSAuth** — Azure IAM authentication and role-based access control
- **AOSServiceBus** — Async communication via Azure Service Bus
- **AOSRegistration** — Client app registration and infrastructure provisioning
- **AOSDeployer** — Code deployment to Azure Functions

All multi-agent orchestrations are managed internally by the **Foundry Agent
Service** (v7.0.0).  Foundry is an implementation detail of AOS and is not
exposed to client applications.

Enterprise capabilities:

- **Knowledge Base API** — document management and search
- **Risk Registry API** — risk identification, assessment, and mitigation
- **Audit Trail / Decision Ledger** — immutable decision logging
- **Covenant Management** — governance and compliance
- **Analytics & Metrics** — KPI tracking and dashboards
- **MCP Server Selection** — ``MCPServerConfig`` for selecting pre-registered MCP
  servers per agent in :class:`OrchestrationRequest`; transport details are
  managed internally by AOS
- **Reliability Patterns** — circuit breaker, retry, idempotency
- **Observability** — structured logging, correlation, health checks
- **Agent Interaction** — direct 1:1 agent messaging
- **Network Discovery** — peer app discovery and federation
- **Local Development Mocks** — ``MockAOSClient`` for testing
- **Workflow Templates** — composable workflow patterns
"""

__version__ = "7.0.0"

from aos_client.client import AOSClient
from aos_client.mcp import MCPServerConfig
from aos_client.models import (
    AgentDescriptor,
    AgentResponse,
    AuditEntry,
    Covenant,
    CovenantStatus,
    CovenantValidation,
    Dashboard,
    DecisionRecord,
    Document,
    DocumentStatus,
    DocumentType,
    KPI,
    MCPServer,
    MCPServerStatus,
    MetricDataPoint,
    MetricsSeries,
    Network,
    NetworkMembership,
    OrchestrationPurpose,
    OrchestrationRequest,
    OrchestrationStatus,
    OrchestrationStatusEnum,
    OrchestrationUpdate,
    PeerApp,
    Risk,
    RiskAssessment,
    RiskCategory,
    RiskSeverity,
    RiskStatus,
)
from aos_client.app import AOSApp, WorkflowRequest, workflow_template
from aos_client.auth import AOSAuth, TokenClaims
from aos_client.service_bus import AOSServiceBus
from aos_client.registration import AOSRegistration, AppRegistration
from aos_client.deployment import AOSDeployer, DeploymentResult

__all__ = [
    # Framework
    "AOSApp",
    "AOSClient",
    "AOSAuth",
    "AOSDeployer",
    "AOSRegistration",
    "AOSServiceBus",
    "WorkflowRequest",
    "workflow_template",
    # Core models
    "AgentDescriptor",
    "AppRegistration",
    "DeploymentResult",
    "OrchestrationPurpose",
    "OrchestrationRequest",
    "OrchestrationStatus",
    "OrchestrationStatusEnum",
    "OrchestrationUpdate",
    "TokenClaims",
    # MCP server selection (per-agent server names and client secrets only)
    "MCPServerConfig",
    # Knowledge Base
    "Document",
    "DocumentType",
    "DocumentStatus",
    # Risk Registry
    "Risk",
    "RiskAssessment",
    "RiskCategory",
    "RiskSeverity",
    "RiskStatus",
    # Audit Trail
    "DecisionRecord",
    "AuditEntry",
    # Covenant Management
    "Covenant",
    "CovenantStatus",
    "CovenantValidation",
    # Analytics
    "MetricDataPoint",
    "MetricsSeries",
    "KPI",
    "Dashboard",
    # MCP server status (infrastructure)
    "MCPServer",
    "MCPServerStatus",
    # Agent Interaction
    "AgentResponse",
    # Network Discovery
    "PeerApp",
    "NetworkMembership",
    "Network",
]
