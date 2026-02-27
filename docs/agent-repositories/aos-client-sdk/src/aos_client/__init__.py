"""AOS Client SDK — framework and client for Agent Operating System applications.

This SDK enables client applications to interact with the Agent Operating System
as an infrastructure service:

- **AOSApp** — Azure Functions application framework with workflow decorators
- **AOSClient** — HTTP/Service Bus client for agent discovery and orchestration
- **AOSMultiTenantClient** — Multi-tenant client routing
- **AOSAuth** — Azure IAM authentication and role-based access control
- **AOSServiceBus** — Async communication via Azure Service Bus
- **AOSRegistration** — Client app registration and infrastructure provisioning
- **AOSDeployer** — Code deployment to Azure Functions

Enterprise capabilities (v5.0.0):

- **Knowledge Base API** — document management, batch operations, versioning
- **Risk Registry API** — risk CRUD, heatmaps, summaries, trends
- **Audit Trail / Decision Ledger** — immutable logging, compliance reports
- **Covenant Management** — governance, lifecycle events, federation
- **Analytics & Metrics** — KPI tracking, dashboards, alerts
- **MCP Server Integration** — tool invocation, bidirectional events
- **Reliability Patterns** — circuit breaker, retry, idempotency
- **Observability** — structured logging, correlation, health checks
- **Agent Interaction** — direct 1:1 agent messaging
- **Network Discovery** — peer discovery, covenant-based federation
- **Local Development Mocks** — ``MockAOSClient`` for testing
- **Workflow Templates** — composable patterns with versioning and A/B
- **Orchestration Streaming** — per-instance update subscriptions
- **Multi-Tenant Support** — tenant-isolated client routing
- **Webhook Support** — outbound external notifications
- **CLI Tool** — ``aos`` command-line interface
"""

__version__ = "5.0.0"

from aos_client.client import AOSClient, AOSMultiTenantClient
from aos_client.models import (
    AgentDescriptor,
    AgentResponse,
    Alert,
    AuditEntry,
    ComplianceReport,
    Covenant,
    CovenantEvent,
    CovenantStatus,
    CovenantValidation,
    Dashboard,
    DecisionChain,
    DecisionRecord,
    Document,
    DocumentStatus,
    DocumentType,
    KPI,
    MCPEvent,
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
    PeerVerification,
    Risk,
    RiskAssessment,
    RiskCategory,
    RiskHeatmap,
    RiskHeatmapCell,
    RiskSeverity,
    RiskStatus,
    RiskSummary,
    RiskTrend,
    Subscription,
    Webhook,
    WebhookEvent,
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
    "AOSMultiTenantClient",
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
    "Subscription",
    "TokenClaims",
    # Knowledge Base
    "Document",
    "DocumentType",
    "DocumentStatus",
    # Risk Registry
    "Risk",
    "RiskAssessment",
    "RiskCategory",
    "RiskHeatmap",
    "RiskHeatmapCell",
    "RiskSeverity",
    "RiskStatus",
    "RiskSummary",
    "RiskTrend",
    # Audit Trail
    "DecisionRecord",
    "AuditEntry",
    "ComplianceReport",
    "DecisionChain",
    # Covenant Management
    "Covenant",
    "CovenantEvent",
    "CovenantStatus",
    "CovenantValidation",
    # Analytics
    "MetricDataPoint",
    "MetricsSeries",
    "KPI",
    "Dashboard",
    "Alert",
    # MCP
    "MCPServer",
    "MCPServerStatus",
    "MCPEvent",
    # Agent Interaction
    "AgentResponse",
    # Network Discovery
    "PeerApp",
    "PeerVerification",
    "NetworkMembership",
    "Network",
    # Webhook
    "Webhook",
    "WebhookEvent",
]
