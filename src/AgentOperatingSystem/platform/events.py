"""
Core business-agnostic event topics for AgentOperatingSystem

Defines standard event types as specified in features.md:
- DecisionRequested, DecisionApproved, DecisionRejected
- IncidentRaised
- SLAThresholdBreached
- RunbookTriggered
- PolicyUpdated
- AuditPackGenerated

All events follow versioned schemas with backward compatibility.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Core business-agnostic event topics"""
    DECISION_REQUESTED = "DecisionRequested"
    DECISION_APPROVED = "DecisionApproved"
    DECISION_REJECTED = "DecisionRejected"
    INCIDENT_RAISED = "IncidentRaised"
    SLA_THRESHOLD_BREACHED = "SLAThresholdBreached"
    RUNBOOK_TRIGGERED = "RunbookTriggered"
    POLICY_UPDATED = "PolicyUpdated"
    AUDIT_PACK_GENERATED = "AuditPackGenerated"


class BaseEvent(BaseModel):
    """Base class for all platform events"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    schema_version: str = "1.0.0"
    source: str  # Agent or system that emitted this event
    correlation_id: str
    causation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DecisionRequestedEvent(BaseEvent):
    """Event emitted when a decision is requested"""
    event_type: EventType = EventType.DECISION_REQUESTED
    decision_id: str
    requester: str
    decision_type: str
    context: Dict[str, Any]
    required_approvers: List[str] = Field(default_factory=list)
    deadline: Optional[datetime] = None
    priority: str = "normal"  # low, normal, high, critical


class DecisionApprovedEvent(BaseEvent):
    """Event emitted when a decision is approved"""
    event_type: EventType = EventType.DECISION_APPROVED
    decision_id: str
    approver: str
    rationale: str
    conditions: List[str] = Field(default_factory=list)
    approved_at: datetime = Field(default_factory=datetime.utcnow)


class DecisionRejectedEvent(BaseEvent):
    """Event emitted when a decision is rejected"""
    event_type: EventType = EventType.DECISION_REJECTED
    decision_id: str
    rejector: str
    reason: str
    alternatives: List[str] = Field(default_factory=list)
    rejected_at: datetime = Field(default_factory=datetime.utcnow)


class IncidentSeverity(str, Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentRaisedEvent(BaseEvent):
    """Event emitted when an incident is raised"""
    event_type: EventType = EventType.INCIDENT_RAISED
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    affected_systems: List[str] = Field(default_factory=list)
    assigned_to: Optional[str] = None
    raised_at: datetime = Field(default_factory=datetime.utcnow)


class SLAThresholdBreachedEvent(BaseEvent):
    """Event emitted when an SLA threshold is breached"""
    event_type: EventType = EventType.SLA_THRESHOLD_BREACHED
    sla_id: str
    sla_name: str
    metric_name: str
    threshold_value: float
    actual_value: float
    severity: str  # warning, critical
    affected_service: str
    breached_at: datetime = Field(default_factory=datetime.utcnow)


class RunbookTriggeredEvent(BaseEvent):
    """Event emitted when a runbook is triggered"""
    event_type: EventType = EventType.RUNBOOK_TRIGGERED
    runbook_id: str
    runbook_name: str
    trigger_reason: str
    trigger_context: Dict[str, Any] = Field(default_factory=dict)
    triggered_by: str
    triggered_at: datetime = Field(default_factory=datetime.utcnow)


class PolicyUpdatedEvent(BaseEvent):
    """Event emitted when a policy is updated"""
    event_type: EventType = EventType.POLICY_UPDATED
    policy_id: str
    policy_name: str
    previous_version: str
    new_version: str
    changes: List[str] = Field(default_factory=list)
    updated_by: str
    effective_date: datetime = Field(default_factory=datetime.utcnow)


class AuditPackGeneratedEvent(BaseEvent):
    """Event emitted when an audit pack is generated"""
    event_type: EventType = EventType.AUDIT_PACK_GENERATED
    audit_pack_id: str
    audit_period_start: datetime
    audit_period_end: datetime
    audit_scope: List[str] = Field(default_factory=list)
    generated_by: str
    storage_location: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
