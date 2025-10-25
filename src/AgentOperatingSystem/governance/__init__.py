"""
Governance primitives for AgentOperatingSystem

Implements core governance capabilities as specified in features.md:
- Audit logging (append-only, tamper-evident)
- Compliance assertions (SOC2, ISO 27001 mapping)
- Risk registry (likelihood, impact, owner, mitigation)
- Decision rationale (structured memos for precedent)
"""

from .audit import AuditLogger, AuditEntry, AuditLevel
from .compliance import ComplianceAssertion, ComplianceFramework, ControlMapping
from .risk import RiskRegistry, RiskEntry, RiskLevel, RiskStatus
from .decision_rationale import DecisionRationale, DecisionOutcome

__all__ = [
    'AuditLogger',
    'AuditEntry',
    'AuditLevel',
    'ComplianceAssertion',
    'ComplianceFramework',
    'ControlMapping',
    'RiskRegistry',
    'RiskEntry',
    'RiskLevel',
    'RiskStatus',
    'DecisionRationale',
    'DecisionOutcome'
]
