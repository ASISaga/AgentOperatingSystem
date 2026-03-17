"""
Metrics collection for AgentOperatingSystem

Tracks decision latency (p50/p95), SLA compliance, incident MTTR,
policy evaluation time, and event lag.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from collections import defaultdict
import statistics


class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class Metric(BaseModel):
    """Individual metric data point"""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MetricsCollector:
    """
    Collector for system metrics with aggregation capabilities.

    Tracks:
    - Decision latency (p50, p95, p99)
    - SLA compliance rates
    - Incident MTTR (Mean Time To Resolution)
    - Policy evaluation time
    - Event lag
    """

    def __init__(self, retention_hours: int = 24):
        """
        Initialize metrics collector.

        Args:
            retention_hours: How long to retain metrics
        """
        self.retention_hours = retention_hours
        self._metrics: Dict[str, List[Metric]] = defaultdict(list)
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}

    def record_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """
        Record a counter metric (monotonically increasing).

        Args:
            name: Metric name
            value: Value to add
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        self._counters[key] += value

        metric = Metric(
            name=name,
            metric_type=MetricType.COUNTER,
            value=self._counters[key],
            tags=tags or {}
        )
        self._metrics[key].append(metric)
        self._cleanup_old_metrics()

    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a gauge metric (point-in-time value).

        Args:
            name: Metric name
            value: Current value
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        self._gauges[key] = value

        metric = Metric(
            name=name,
            metric_type=MetricType.GAUGE,
            value=value,
            tags=tags or {}
        )
        self._metrics[key].append(metric)
        self._cleanup_old_metrics()

    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a histogram metric (distribution of values).

        Args:
            name: Metric name
            value: Observed value
            tags: Optional tags
        """
        key = self._make_key(name, tags)

        metric = Metric(
            name=name,
            metric_type=MetricType.HISTOGRAM,
            value=value,
            tags=tags or {}
        )
        self._metrics[key].append(metric)
        self._cleanup_old_metrics()

    # Specific metric recording methods

    def record_decision_latency(self, decision_type: str, latency_ms: float):
        """Record decision latency in milliseconds"""
        self.record_histogram(
            "decision.latency_ms",
            latency_ms,
            tags={"type": decision_type}
        )

    def record_sla_compliance(self, sla_name: str, compliant: bool):
        """Record SLA compliance"""
        self.record_counter(
            "sla.total",
            tags={"name": sla_name}
        )
        if compliant:
            self.record_counter(
                "sla.compliant",
                tags={"name": sla_name}
            )

    def record_incident_resolution(self, incident_type: str, resolution_time_minutes: float):
        """Record incident MTTR"""
        self.record_histogram(
            "incident.mttr_minutes",
            resolution_time_minutes,
            tags={"type": incident_type}
        )

    def record_policy_evaluation(self, policy_id: str, evaluation_time_ms: float):
        """Record policy evaluation time"""
        self.record_histogram(
            "policy.evaluation_time_ms",
            evaluation_time_ms,
            tags={"policy_id": policy_id}
        )

    def record_event_lag(self, event_type: str, lag_seconds: float):
        """Record event processing lag"""
        self.record_histogram(
            "event.lag_seconds",
            lag_seconds,
            tags={"type": event_type}
        )

    # Query and aggregation methods

    def get_percentiles(
        self,
        name: str,
        percentiles: List[int] = [50, 95, 99],
        tags: Optional[Dict[str, str]] = None,
        time_window_minutes: Optional[int] = None
    ) -> Dict[int, float]:
        """
        Calculate percentiles for a histogram metric.

        Args:
            name: Metric name
            percentiles: List of percentiles to calculate (e.g., [50, 95, 99])
            tags: Optional tags to filter by
            time_window_minutes: Optional time window to consider

        Returns:
            Dictionary mapping percentile to value
        """
        key = self._make_key(name, tags)
        metrics = self._metrics.get(key, [])

        # Filter by time window if specified
        if time_window_minutes:
            cutoff = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            metrics = [m for m in metrics if m.timestamp >= cutoff]

        if not metrics:
            return {p: 0.0 for p in percentiles}

        values = [m.value for m in metrics]
        result = {}

        for p in percentiles:
            try:
                result[p] = statistics.quantiles(values, n=100)[p-1]
            except statistics.StatisticsError:
                result[p] = values[0] if len(values) == 1 else 0.0

        return result

    def get_sla_compliance_rate(
        self,
        sla_name: str,
        time_window_minutes: Optional[int] = None
    ) -> float:
        """
        Calculate SLA compliance rate.

        Args:
            sla_name: SLA name
            time_window_minutes: Optional time window

        Returns:
            Compliance rate (0.0 to 1.0)
        """
        total_key = self._make_key("sla.total", {"name": sla_name})
        compliant_key = self._make_key("sla.compliant", {"name": sla_name})

        total = self._counters.get(total_key, 0)
        compliant = self._counters.get(compliant_key, 0)

        if total == 0:
            return 1.0

        return compliant / total

    def get_average(
        self,
        name: str,
        tags: Optional[Dict[str, str]] = None,
        time_window_minutes: Optional[int] = None
    ) -> float:
        """Calculate average value for a metric"""
        key = self._make_key(name, tags)
        metrics = self._metrics.get(key, [])

        # Filter by time window if specified
        if time_window_minutes:
            cutoff = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            metrics = [m for m in metrics if m.timestamp >= cutoff]

        if not metrics:
            return 0.0

        return statistics.mean([m.value for m in metrics])

    def get_current_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get current value of a gauge metric"""
        key = self._make_key(name, tags)
        return self._gauges.get(key, 0.0)

    def get_counter_value(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get current value of a counter metric"""
        key = self._make_key(name, tags)
        return self._counters.get(key, 0.0)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        # Decision latencies
        decision_p50_p95 = self.get_percentiles("decision.latency_ms", [50, 95])

        # Average incident MTTR
        avg_mttr = self.get_average("incident.mttr_minutes")

        # Average policy evaluation time
        avg_policy_time = self.get_average("policy.evaluation_time_ms")

        # Average event lag
        avg_event_lag = self.get_average("event.lag_seconds")

        return {
            "decision_latency_p50_ms": decision_p50_p95.get(50, 0),
            "decision_latency_p95_ms": decision_p50_p95.get(95, 0),
            "avg_incident_mttr_minutes": avg_mttr,
            "avg_policy_evaluation_ms": avg_policy_time,
            "avg_event_lag_seconds": avg_event_lag,
            "total_metrics_tracked": len(self._metrics)
        }

    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a unique key for metric name and tags"""
        if not tags:
            return name

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"

    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period"""
        cutoff = datetime.utcnow() - timedelta(hours=self.retention_hours)

        for key in list(self._metrics.keys()):
            self._metrics[key] = [
                m for m in self._metrics[key]
                if m.timestamp >= cutoff
            ]

            # Remove empty lists
            if not self._metrics[key]:
                del self._metrics[key]
