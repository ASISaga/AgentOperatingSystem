"""Data models for the AOS Client SDK.

All orchestration models follow the **purpose-driven, perpetual** paradigm:
orchestrations are started with a purpose and run indefinitely until
explicitly stopped.  There are no completion criteria or finite task
payloads — agents work toward the overarching purpose continuously.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentDescriptor(BaseModel):
    """Describes an agent available in the RealmOfAgents catalog."""

    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Agent class name (e.g. LeadershipAgent, CMOAgent)")
    purpose: str = Field(..., description="The agent's long-term purpose")
    adapter_name: str = Field(..., description="LoRA adapter providing domain expertise")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific configuration")


class OrchestrationPurpose(BaseModel):
    """The overarching purpose that drives an orchestration.

    When set on an :class:`OrchestrationRequest`, participating
    :class:`PurposeDrivenAgent` instances align their working purposes to
    achieve this overarching goal while retaining their own domain-specific
    knowledge, skills, and personas.

    Purposes are **perpetual** — they have no success criteria because a
    purpose-driven orchestration runs indefinitely.
    """

    purpose: str = Field(..., description="The overarching purpose of the orchestration")
    purpose_scope: str = Field(
        default="General orchestration scope",
        description="Boundaries/scope for the orchestration purpose",
    )


class OrchestrationRequest(BaseModel):
    """Request to start a purpose-driven agent orchestration via AOS.

    Orchestrations are perpetual: they run until explicitly stopped.
    The ``purpose`` drives agent alignment; ``context`` supplies initial
    data that informs the agents' work.
    """

    orchestration_id: Optional[str] = Field(None, description="Client-supplied ID (auto-generated if omitted)")
    agent_ids: List[str] = Field(..., min_length=1, description="Agent IDs to include in the orchestration")
    workflow: str = Field(default="collaborative", description="Workflow pattern: collaborative, sequential, hierarchical")
    purpose: OrchestrationPurpose = Field(..., description="Overarching purpose that drives the orchestration and guides agent alignment")
    context: Dict[str, Any] = Field(default_factory=dict, description="Initial context data for the orchestration")
    config: Dict[str, Any] = Field(default_factory=dict, description="Orchestration-level configuration")
    callback_url: Optional[str] = Field(None, description="Webhook URL for status notifications")


class OrchestrationStatusEnum(str, Enum):
    """Orchestration lifecycle states.

    Orchestrations are perpetual — they transition from ``PENDING`` to
    ``ACTIVE`` and remain active until explicitly ``STOPPED`` or
    ``CANCELLED``, or until a ``FAILED`` state is reached.
    """

    PENDING = "pending"
    ACTIVE = "active"
    STOPPED = "stopped"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OrchestrationStatus(BaseModel):
    """Status of a submitted orchestration."""

    orchestration_id: str
    status: OrchestrationStatusEnum
    agent_ids: List[str] = Field(default_factory=list)
    purpose: Optional[str] = Field(None, description="The orchestration's driving purpose")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Knowledge Base models
# ---------------------------------------------------------------------------


class DocumentType(str, Enum):
    """Types of documents stored in the knowledge base."""

    DECISION = "decision"
    POLICY = "policy"
    PROCEDURE = "procedure"
    TEMPLATE = "template"
    MEMO = "memo"
    REPORT = "report"
    ANALYSIS = "analysis"
    LESSON = "lesson"
    REFERENCE = "reference"


class DocumentStatus(str, Enum):
    """Lifecycle status of a knowledge-base document."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class Document(BaseModel):
    """A document stored in the AOS knowledge base."""

    id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    doc_type: str = Field(..., description="Document type classification")
    status: DocumentStatus = Field(default=DocumentStatus.DRAFT, description="Current document lifecycle status")
    content: Dict[str, Any] = Field(..., description="Document content payload")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary document metadata")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None


# ---------------------------------------------------------------------------
# Risk Registry models
# ---------------------------------------------------------------------------


class RiskSeverity(str, Enum):
    """Severity level of an identified risk."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RiskStatus(str, Enum):
    """Lifecycle status of a risk entry."""

    IDENTIFIED = "identified"
    ASSESSING = "assessing"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"


class RiskCategory(str, Enum):
    """High-level category for risk classification."""

    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    REPUTATIONAL = "reputational"
    TECHNICAL = "technical"
    MARKET = "market"


class RiskAssessment(BaseModel):
    """Quantitative assessment attached to a risk."""

    likelihood: float = Field(..., description="Probability of occurrence (0-1)")
    impact: float = Field(..., description="Impact magnitude (0-1)")
    severity: RiskSeverity = Field(..., description="Assessed severity level")
    assessed_at: Optional[datetime] = None
    assessor: Optional[str] = None
    notes: Optional[str] = None


class Risk(BaseModel):
    """A risk entry in the AOS risk registry."""

    id: str = Field(..., description="Unique risk identifier")
    title: str = Field(..., description="Short risk title")
    description: str = Field(..., description="Detailed risk description")
    category: RiskCategory = Field(..., description="Risk category")
    status: RiskStatus = Field(default=RiskStatus.IDENTIFIED, description="Current risk status")
    owner: str = Field(..., description="Risk owner identifier")
    assessment: Optional[RiskAssessment] = None
    mitigation_plan: Optional[str] = None
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional risk context")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Audit Trail / Decision Ledger models
# ---------------------------------------------------------------------------


class DecisionRecord(BaseModel):
    """Record of a decision made during an orchestration."""

    id: str = Field(..., description="Unique decision record identifier")
    orchestration_id: Optional[str] = None
    agent_id: Optional[str] = None
    decision_type: str = Field(default="", description="Classification of the decision")
    title: str = Field(default="", description="Short decision title")
    description: str = Field(default="", description="Detailed decision description")
    rationale: Optional[str] = None
    outcome: Optional[str] = None
    confidence: Optional[float] = None
    context: Dict[str, Any] = Field(default_factory=dict, description="Decision context data")
    created_at: Optional[datetime] = None


class AuditEntry(BaseModel):
    """Immutable audit-trail entry for system or agent actions."""

    id: str = Field(..., description="Unique audit entry identifier")
    event_type: str = Field(..., description="Type of audited event")
    subject_id: str = Field(..., description="Identifier of the acting subject")
    subject_type: str = Field(default="system", description="Type of the acting subject")
    action: str = Field(..., description="Action that was performed")
    severity: str = Field(default="medium", description="Event severity level")
    target: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict, description="Event context data")
    timestamp: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Covenant Management models
# ---------------------------------------------------------------------------


class CovenantStatus(str, Enum):
    """Lifecycle status of a covenant."""

    DRAFT = "draft"
    PROPOSED = "proposed"
    ACTIVE = "active"
    AMENDED = "amended"
    REVOKED = "revoked"


class Covenant(BaseModel):
    """A governance covenant between agents or system components."""

    id: str = Field(..., description="Unique covenant identifier")
    title: str = Field(..., description="Covenant title")
    version: str = Field(default="1.0", description="Covenant version")
    status: CovenantStatus = Field(default=CovenantStatus.DRAFT, description="Current covenant status")
    parties: List[str] = Field(default_factory=list, description="Parties bound by the covenant")
    terms: Dict[str, Any] = Field(default_factory=dict, description="Covenant terms and conditions")
    signers: List[str] = Field(default_factory=list, description="Identifiers of signers")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CovenantValidation(BaseModel):
    """Result of validating an action against a covenant."""

    covenant_id: str = Field(..., description="Identifier of the validated covenant")
    valid: bool = Field(..., description="Whether the covenant constraints are satisfied")
    violations: List[str] = Field(default_factory=list, description="List of detected violations")
    checked_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Analytics models
# ---------------------------------------------------------------------------


class MetricDataPoint(BaseModel):
    """A single timestamped metric observation."""

    timestamp: Optional[datetime] = None
    value: float = Field(..., description="Observed metric value")
    tags: Dict[str, str] = Field(default_factory=dict, description="Dimensional tags for the data point")


class MetricsSeries(BaseModel):
    """A named time-series of metric data points."""

    name: str = Field(..., description="Metric series name")
    data_points: List[MetricDataPoint] = Field(default_factory=list, description="Ordered data points")
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class KPI(BaseModel):
    """Key Performance Indicator tracked by the analytics subsystem."""

    id: str = Field(..., description="Unique KPI identifier")
    name: str = Field(..., description="KPI display name")
    description: str = Field(default="", description="KPI description")
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: str = Field(default="", description="Unit of measurement")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional KPI metadata")


class Dashboard(BaseModel):
    """Snapshot dashboard containing KPIs."""

    kpis: List[KPI] = Field(default_factory=list, description="KPIs displayed on the dashboard")
    generated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# MCP models
# ---------------------------------------------------------------------------


class MCPServer(BaseModel):
    """Representation of a registered MCP server."""

    name: str = Field(..., description="MCP server name")
    status: str = Field(default="unknown", description="Current server status")
    tools: List[str] = Field(default_factory=list, description="Tools exposed by the server")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Server metadata")


class MCPServerStatus(BaseModel):
    """Health-check status of an MCP server."""

    name: str = Field(..., description="MCP server name")
    status: str = Field(..., description="Reported status string")
    healthy: bool = Field(default=True, description="Whether the server is considered healthy")
    last_checked: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Orchestration Update model
# ---------------------------------------------------------------------------


class OrchestrationUpdate(BaseModel):
    """An incremental update emitted during an orchestration."""

    orchestration_id: str = Field(..., description="Orchestration this update belongs to")
    agent_id: Optional[str] = None
    update_type: str = Field(default="status", description="Type of update")
    output: Optional[Any] = None
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Update metadata")


# ---------------------------------------------------------------------------
# Agent Interaction models
# ---------------------------------------------------------------------------


class AgentResponse(BaseModel):
    """Response payload returned by an agent."""

    agent_id: str = Field(..., description="Identifier of the responding agent")
    message: str = Field(default="", description="Response message content")
    context: Dict[str, Any] = Field(default_factory=dict, description="Response context data")
    timestamp: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Network Discovery models
# ---------------------------------------------------------------------------


class PeerApp(BaseModel):
    """An application discovered on the agent network."""

    app_id: str = Field(..., description="Unique application identifier")
    name: str = Field(..., description="Application display name")
    description: str = Field(default="", description="Application description")
    endpoint: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Application metadata")


class NetworkMembership(BaseModel):
    """Membership record linking an application to a network."""

    network_id: str = Field(..., description="Network identifier")
    app_id: str = Field(..., description="Application identifier")
    joined_at: Optional[datetime] = None
    status: str = Field(default="active", description="Membership status")


class Network(BaseModel):
    """An agent network that applications can join."""

    id: str = Field(..., description="Unique network identifier")
    name: str = Field(..., description="Network display name")
    description: str = Field(default="", description="Network description")
    members: List[str] = Field(default_factory=list, description="Member application identifiers")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Network metadata")
