"""
AgentOperatingSystem Platform Infrastructure

Core platform-level contracts, patterns, and infrastructure for agent-based systems.
This module implements the foundational capabilities required by BusinessInfinity and
other agent-based applications.
"""

__all__ = [
    # Contracts
    'CommandContract',
    'QueryContract',
    'EventContract',
    'MessageEnvelope',
    'AgentIdentity',
    'PolicyInterface',
    # Events
    'EventType',
    'DecisionRequestedEvent',
    'DecisionApprovedEvent',
    'DecisionRejectedEvent',
    'IncidentRaisedEvent',
    'SLAThresholdBreachedEvent',
    'RunbookTriggeredEvent',
    'PolicyUpdatedEvent',
    'AuditPackGeneratedEvent'
]
