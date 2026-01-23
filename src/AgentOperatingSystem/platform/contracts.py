"""
Platform-level contracts for AgentOperatingSystem

Core contract definitions for commands, queries, events, messages, agent identity,
and policy interfaces as specified in features.md.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class MessageEnvelope(BaseModel):
    """
    Universal message format for all platform communications.

    Standardized envelope with type, version, timestamp, correlation/causation IDs,
    actor, scope, attributes, and payload.
    """
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: str  # command, query, event
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str  # Links related messages in a flow
    causation_id: Optional[str] = None  # ID of message that caused this one
    actor: str  # Agent or user who initiated this message
    scope: str  # Domain/context scope (e.g., "finance", "operations")
    attributes: Dict[str, Any] = Field(default_factory=dict)  # Metadata
    payload: Dict[str, Any]  # Actual message content

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FailureMode(str, Enum):
    """Standard failure modes for operations"""
    VALIDATION_ERROR = "validation_error"
    PRECONDITION_FAILED = "precondition_failed"
    POSTCONDITION_FAILED = "postcondition_failed"
    TIMEOUT = "timeout"
    DEPENDENCY_FAILURE = "dependency_failure"
    POLICY_VIOLATION = "policy_violation"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    UNKNOWN = "unknown"


class CommandContract(BaseModel):
    """
    Command contract: intent, preconditions, expected outcomes, failure modes.

    Commands represent actions to be performed with clear intent and expectations.
    """
    command_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    intent: str  # What this command aims to accomplish
    required_preconditions: List[str] = Field(default_factory=list)
    expected_outcomes: List[str] = Field(default_factory=list)
    failure_modes: List[FailureMode] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    actor: str  # Who is executing this command
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    idempotency_key: Optional[str] = None  # For idempotent execution

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConsistencyLevel(str, Enum):
    """Consistency guarantees for queries"""
    EVENTUAL = "eventual"
    STRONG = "strong"
    BOUNDED_STALENESS = "bounded_staleness"


class QueryContract(BaseModel):
    """
    Query contract: selectors, filters, projections, pagination, consistency.

    Queries retrieve data with specific selection criteria and consistency requirements.
    """
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    selectors: Dict[str, Any]  # What to select
    filters: Dict[str, Any] = Field(default_factory=dict)  # Filtering criteria
    projections: List[str] = Field(default_factory=list)  # Fields to return
    page_size: int = 100
    page_token: Optional[str] = None
    consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DeliverySemantics(str, Enum):
    """Event delivery semantics"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE_INTENT = "exactly_once_intent"  # via outbox pattern


class EventContract(BaseModel):
    """
    Event contract: topic, schema version, source, causality, delivery semantics.

    Events represent things that have happened in the system.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str  # Event topic/type
    schema_version: str = "1.0.0"
    source: str  # Agent or system that emitted the event
    correlation_id: str
    causation_id: Optional[str] = None
    delivery_semantics: DeliverySemantics = DeliverySemantics.AT_LEAST_ONCE
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentIdentity(BaseModel):
    """
    Agent identity: unique ID, human owner(s), service principal, role taxonomy, domain scopes.
    """
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    human_owners: List[str] = Field(default_factory=list)  # User IDs or emails
    service_principal: Optional[str] = None  # Azure AD service principal
    roles: List[str] = Field(default_factory=list)  # Role taxonomy
    domain_scopes: List[str] = Field(default_factory=list)  # Domains this agent operates in
    capabilities: List[str] = Field(default_factory=list)  # What this agent can do
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PolicyDecision(str, Enum):
    """Policy evaluation decisions"""
    ALLOW = "allow"
    DENY = "deny"
    ALLOW_WITH_CONDITIONS = "allow_with_conditions"


class PolicyInterface(BaseModel):
    """
    Policy interface: evaluate, enforce, assert, explain.

    Supports rule sets, exceptions with expiry, and evidence links.
    """
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    rule_sets: List[Dict[str, Any]] = Field(default_factory=list)
    exceptions: List[Dict[str, Any]] = Field(default_factory=list)  # With expiry dates
    evidence_links: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def evaluate(self, context: Dict[str, Any]) -> PolicyDecision:
        """Evaluate policy against given context"""
        # Implementation would check rules and exceptions
        # This is a placeholder for the interface
        return PolicyDecision.ALLOW

    def enforce(self, context: Dict[str, Any]) -> bool:
        """Enforce policy, returning True if allowed"""
        decision = self.evaluate(context)
        return decision in [PolicyDecision.ALLOW, PolicyDecision.ALLOW_WITH_CONDITIONS]

    def assert_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assert compliance and return assertion details"""
        decision = self.evaluate(context)
        return {
            "policy_id": self.policy_id,
            "decision": decision.value,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context
        }

    def explain(self, context: Dict[str, Any]) -> str:
        """Explain policy decision for given context"""
        decision = self.evaluate(context)
        return f"Policy {self.name} evaluated to {decision.value} for context: {context}"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
