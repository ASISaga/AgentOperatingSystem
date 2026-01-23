"""
Governance primitives for AgentOperatingSystem

Implements core governance capabilities as specified in features.md:
- Audit logging (append-only, tamper-evident)
- Compliance assertions (SOC2, ISO 27001 mapping)
- Risk registry (likelihood, impact, owner, mitigation)
- Decision rationale (structured memos for precedent)
"""

from .audit import AuditEntry, AuditLevel, AuditLogger
from .compliance import ComplianceAssertion, ComplianceFramework, ControlMapping
from .decision_rationale import DecisionOutcome, DecisionRationale
from .risk import RiskEntry, RiskLevel, RiskRegistry, RiskStatus

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
