"""
Observability infrastructure for AgentOperatingSystem

Implements metrics collection, distributed tracing, structured logging,
and alerting as specified in features.md.
"""

from .metrics import MetricsCollector, Metric, MetricType
from .tracing import TracingContext, Span, TraceLevel
from .logging import StructuredLogger, LogEntry, LogLevel, LogSeparator
from .alerting import AlertingSystem, Alert, AlertSeverity, AlertRule

# Generic observability from migration
try:
    from .structured import (
        StructuredLogger as GenericStructuredLogger,
        correlation_scope,
        get_metrics_collector,
        get_health_check
    )
    HAS_STRUCTURED = True
except ImportError:
    HAS_STRUCTURED = False

# Advanced observability features
try:
    from .predictive import AnomalyDetector, PredictiveAlerter, CapacityPlanner
    from .dashboard import MetricsAggregator, DashboardBuilder, MetricType as AdvancedMetricType
    
    base_exports = [
        'MetricsCollector',
        'Metric',
        'MetricType',
        'TracingContext',
        'Span',
        'TraceLevel',
        'StructuredLogger',
        'LogEntry',
        'LogLevel',
        'LogSeparator',
        'AlertingSystem',
        'Alert',
        'AlertSeverity',
        'AlertRule',
        # Advanced features
        'AnomalyDetector',
        'PredictiveAlerter',
        'CapacityPlanner',
        'MetricsAggregator',
        'DashboardBuilder'
    ]
    
    if HAS_STRUCTURED:
        base_exports.extend([
            'GenericStructuredLogger',
            'correlation_scope',
            'get_metrics_collector',
            'get_health_check'
        ])
    
    __all__ = base_exports
except ImportError:
    base_exports = [
        'MetricsCollector',
        'Metric',
        'MetricType',
        'TracingContext',
        'Span',
        'TraceLevel',
        'StructuredLogger',
        'LogEntry',
        'LogLevel',
        'LogSeparator',
        'AlertingSystem',
        'Alert',
        'AlertSeverity',
        'AlertRule'
    ]
    
    if HAS_STRUCTURED:
        base_exports.extend([
            'GenericStructuredLogger',
            'correlation_scope',
            'get_metrics_collector',
            'get_health_check'
        ])
    
    __all__ = base_exports
