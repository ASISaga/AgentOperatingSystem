"""
AOS Monitoring Module

System monitoring and metrics collection.
"""

from .monitor import MetricsCollector, SystemMonitor

# New refactored classes
from .observability import MetricsCollector as MetricsCollectorNew
from .observability import StructuredLogger

try:
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False

# Generic audit trail from migration
try:
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
