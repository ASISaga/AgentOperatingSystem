"""
Observability infrastructure for AgentOperatingSystem

Implements metrics collection, distributed tracing, structured logging,
and alerting as specified in features.md.
"""

from .metrics import MetricsCollector, Metric, MetricType
from .tracing import TracingContext, Span, TraceLevel
from .logging import StructuredLogger, LogEntry, LogLevel, LogSeparator
from .alerting import AlertingSystem, Alert, AlertSeverity, AlertRule

# Advanced observability features
try:
    from .predictive import AnomalyDetector, PredictiveAlerter, CapacityPlanner
    from .dashboard import MetricsAggregator, DashboardBuilder, MetricType as AdvancedMetricType
    
    __all__ = [
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
except ImportError:
    __all__ = [
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
