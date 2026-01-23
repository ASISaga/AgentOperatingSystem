"""
Advanced Metrics Dashboard

Provides real-time metrics aggregation and dashboard capabilities.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class MetricType:
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricsAggregator:
    """
    Aggregates metrics for dashboard display.

    Features:
    - Real-time metric aggregation
    - Time-windowed statistics
    - Percentile calculations
    - Rate calculations
    """

    def __init__(self):
        self.logger = logging.getLogger("AOS.MetricsAggregator")
        self.metrics = defaultdict(list)
        self.aggregations = {}

    async def record(
        self,
        metric_name: str,
        value: float,
        metric_type: str = MetricType.GAUGE,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Record a metric value.

        Args:
            metric_name: Name of the metric
            value: Metric value
            metric_type: Type of metric
            tags: Optional tags for filtering
        """
        entry = {
            "name": metric_name,
            "value": value,
            "type": metric_type,
            "tags": tags or {},
            "timestamp": datetime.utcnow()
        }

        self.metrics[metric_name].append(entry)

        # Limit history size
        max_entries = 10000
        if len(self.metrics[metric_name]) > max_entries:
            self.metrics[metric_name] = self.metrics[metric_name][-max_entries:]

    async def get_aggregation(
        self,
        metric_name: str,
        time_window: Optional[timedelta] = None,
        aggregation_type: str = "avg"
    ) -> Optional[float]:
        """
        Get aggregated metric value.

        Args:
            metric_name: Metric to aggregate
            time_window: Optional time window
            aggregation_type: Type of aggregation (avg, sum, min, max, p95, p99)

        Returns:
            Aggregated value
        """
        if metric_name not in self.metrics:
            return None

        # Filter by time window
        entries = self.metrics[metric_name]
        if time_window:
            cutoff = datetime.utcnow() - time_window
            entries = [e for e in entries if e["timestamp"] >= cutoff]

        if not entries:
            return None

        values = [e["value"] for e in entries]

        if aggregation_type == "avg":
            return sum(values) / len(values)
        elif aggregation_type == "sum":
            return sum(values)
        elif aggregation_type == "min":
            return min(values)
        elif aggregation_type == "max":
            return max(values)
        elif aggregation_type == "p50":
            return self._percentile(values, 50)
        elif aggregation_type == "p95":
            return self._percentile(values, 95)
        elif aggregation_type == "p99":
            return self._percentile(values, 99)

        return None

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    async def get_rate(
        self,
        metric_name: str,
        time_window: timedelta = timedelta(minutes=1)
    ) -> Optional[float]:
        """
        Calculate rate of change for a counter metric.

        Args:
            metric_name: Counter metric name
            time_window: Time window for rate calculation

        Returns:
            Rate (events per second)
        """
        if metric_name not in self.metrics:
            return None

        cutoff = datetime.utcnow() - time_window
        recent_entries = [
            e for e in self.metrics[metric_name]
            if e["timestamp"] >= cutoff
        ]

        if len(recent_entries) < 2:
            return None

        # Calculate rate
        count = len(recent_entries)
        time_span = (
            recent_entries[-1]["timestamp"] - recent_entries[0]["timestamp"]
        ).total_seconds()

        if time_span == 0:
            return None

        rate = count / time_span
        return rate

    async def get_dashboard_data(
        self,
        metric_names: List[str],
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for multiple metrics.

        Args:
            metric_names: List of metrics to include
            time_window: Time window for data

        Returns:
            Dashboard data
        """
        dashboard = {
            "generated_at": datetime.utcnow(),
            "time_window_minutes": time_window.total_seconds() / 60,
            "metrics": {}
        }

        for metric_name in metric_names:
            metric_data = {
                "current": await self.get_aggregation(
                    metric_name,
                    timedelta(minutes=1),
                    "avg"
                ),
                "avg": await self.get_aggregation(
                    metric_name,
                    time_window,
                    "avg"
                ),
                "min": await self.get_aggregation(
                    metric_name,
                    time_window,
                    "min"
                ),
                "max": await self.get_aggregation(
                    metric_name,
                    time_window,
                    "max"
                ),
                "p95": await self.get_aggregation(
                    metric_name,
                    time_window,
                    "p95"
                ),
                "p99": await self.get_aggregation(
                    metric_name,
                    time_window,
                    "p99"
                )
            }

            # Add rate for counters
            if self._is_counter(metric_name):
                metric_data["rate"] = await self.get_rate(
                    metric_name,
                    timedelta(minutes=1)
                )

            dashboard["metrics"][metric_name] = metric_data

        return dashboard

    def _is_counter(self, metric_name: str) -> bool:
        """Check if metric is a counter"""
        if not self.metrics.get(metric_name):
            return False

        return self.metrics[metric_name][0]["type"] == MetricType.COUNTER


class DashboardBuilder:
    """
    Builds customizable dashboards for metrics visualization.

    Features:
    - Custom dashboard layouts
    - Widget configuration
    - Real-time updates
    - Export capabilities
    """

    def __init__(self, aggregator: MetricsAggregator):
        self.logger = logging.getLogger("AOS.DashboardBuilder")
        self.aggregator = aggregator
        self.dashboards = {}

    async def create_dashboard(
        self,
        dashboard_id: str,
        name: str,
        widgets: List[Dict[str, Any]]
    ):
        """
        Create a custom dashboard.

        Args:
            dashboard_id: Unique dashboard ID
            name: Dashboard name
            widgets: List of widget configurations
        """
        self.logger.info("Creating dashboard: %s", name)

        dashboard = {
            "id": dashboard_id,
            "name": name,
            "widgets": widgets,
            "created_at": datetime.utcnow()
        }

        self.dashboards[dashboard_id] = dashboard

    async def render_dashboard(
        self,
        dashboard_id: str
    ) -> Dict[str, Any]:
        """
        Render dashboard with current data.

        Args:
            dashboard_id: Dashboard to render

        Returns:
            Rendered dashboard data
        """
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return {"error": "Dashboard not found"}

        rendered = {
            "id": dashboard["id"],
            "name": dashboard["name"],
            "rendered_at": datetime.utcnow(),
            "widgets": []
        }

        # Render each widget
        for widget_config in dashboard["widgets"]:
            widget_data = await self._render_widget(widget_config)
            rendered["widgets"].append(widget_data)

        return rendered

    async def _render_widget(
        self,
        widget_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render a single widget"""
        widget_type = widget_config.get("type")
        metric_name = widget_config.get("metric")

        if widget_type == "gauge":
            value = await self.aggregator.get_aggregation(
                metric_name,
                timedelta(minutes=1),
                "avg"
            )

            return {
                "type": "gauge",
                "metric": metric_name,
                "value": value,
                "title": widget_config.get("title", metric_name)
            }

        elif widget_type == "graph":
            # Time series data
            entries = self.aggregator.metrics.get(metric_name, [])
            recent = entries[-100:]  # Last 100 points

            return {
                "type": "graph",
                "metric": metric_name,
                "data_points": [
                    {
                        "timestamp": e["timestamp"].isoformat(),
                        "value": e["value"]
                    }
                    for e in recent
                ],
                "title": widget_config.get("title", metric_name)
            }

        elif widget_type == "stat":
            stats = {
                "current": await self.aggregator.get_aggregation(
                    metric_name,
                    timedelta(minutes=1),
                    "avg"
                ),
                "avg_1h": await self.aggregator.get_aggregation(
                    metric_name,
                    timedelta(hours=1),
                    "avg"
                ),
                "p95": await self.aggregator.get_aggregation(
                    metric_name,
                    timedelta(hours=1),
                    "p95"
                )
            }

            return {
                "type": "stat",
                "metric": metric_name,
                "stats": stats,
                "title": widget_config.get("title", metric_name)
            }

        return {
            "type": "unknown",
            "error": f"Unknown widget type: {widget_type}"
        }

    async def create_standard_dashboard(self) -> str:
        """Create a standard AOS dashboard"""
        dashboard_id = "aos_standard"

        widgets = [
            {
                "type": "gauge",
                "metric": "cpu_usage_percent",
                "title": "CPU Usage"
            },
            {
                "type": "gauge",
                "metric": "memory_usage_percent",
                "title": "Memory Usage"
            },
            {
                "type": "graph",
                "metric": "message_throughput",
                "title": "Message Throughput"
            },
            {
                "type": "stat",
                "metric": "workflow_duration_seconds",
                "title": "Workflow Performance"
            }
        ]

        await self.create_dashboard(
            dashboard_id,
            "AOS Standard Dashboard",
            widgets
        )

        return dashboard_id
