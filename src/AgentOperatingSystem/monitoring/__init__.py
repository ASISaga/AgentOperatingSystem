"""
AOS Monitoring Module

System monitoring and metrics collection.
"""

from .monitor import SystemMonitor, MetricsCollector
# New refactored classes
from .observability import StructuredLogger, MetricsCollector as MetricsCollectorNew

try:
    from .audit_trail import (
        AuditTrailManager, AuditEvent, AuditEventType, AuditSeverity,
        audit_log, get_audit_manager, audit_context
    )
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False

# Generic audit trail from migration
try:
    from .audit_trail_generic import (
        AuditTrailManager as GenericAuditTrailManager,
        AuditEvent as GenericAuditEvent,
        AuditSeverity as GenericAuditSeverity
    )
    GENERIC_AUDIT_AVAILABLE = True
except ImportError:
    GENERIC_AUDIT_AVAILABLE = False

__all__ = [
    "SystemMonitor",
    "MetricsCollector",
    # New refactored classes
    "StructuredLogger",
    "MetricsCollectorNew"
]

if AUDIT_AVAILABLE:
    __all__.extend([
        "AuditTrailManager", "AuditEvent", "AuditEventType", "AuditSeverity",
        "audit_log", "get_audit_manager", "audit_context"
    ])

if GENERIC_AUDIT_AVAILABLE:
    __all__.extend([
        "GenericAuditTrailManager", "GenericAuditEvent", "GenericAuditSeverity"
    ])