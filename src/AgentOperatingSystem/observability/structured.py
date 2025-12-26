"""
Generic Observability Infrastructure for Agent Operating System

This module provides generic, reusable observability capabilities for any agent-based system:
- Structured logging with correlation IDs
- Distributed tracing
- Metrics collection (counters, gauges, histograms)
- Health checks and readiness probes

These capabilities provide visibility into system behavior and performance.

This implementation uses contextvars for correlation context, which properly
handles both synchronous and asynchronous code execution.

Usage:
    from AgentOperatingSystem.observability.structured import (
        correlation_scope, StructuredLogger, get_metrics_collector
    )
    
    # Structured logging with correlation
    logger = StructuredLogger(__name__)
    with correlation_scope(operation_name="process_request"):
        logger.info("Processing started", user_id="123")
    
    # Metrics collection
    metrics = get_metrics_collector()
    metrics.increment_counter("requests_processed")
    metrics.set_gauge("queue_size", 42)
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import contextmanager
from collections import defaultdict
import json
import contextvars


# Use contextvars for proper async context propagation
# This works for both sync and async code, unlike threading.local()
_correlation_context = contextvars.ContextVar('correlation_context', default=None)


class CorrelationContext:
    """
    Correlation Context for Distributed Tracing
    
    Maintains correlation ID, causation ID, and other trace metadata
    across async operations. This enables tracking of requests across
    service boundaries and async operation chains.
    """
    
    def __init__(
        self,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        operation_name: Optional[str] = None
    ):
        """
        Initialize correlation context.
        
        Args:
            correlation_id: Unique ID for the entire operation chain
            causation_id: ID of the immediate parent operation
            operation_name: Name of the current operation
        """
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.causation_id = causation_id
        self.operation_name = operation_name
        self.metadata: Dict[str, Any] = {}
        self.start_time = time.time()
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to context."""
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "operation_name": self.operation_name,
            "metadata": self.metadata,
            "duration_ms": (time.time() - self.start_time) * 1000
        }


def get_correlation_context() -> Optional[CorrelationContext]:
    """Get current correlation context from contextvars."""
    return _correlation_context.get()


def set_correlation_context(context: CorrelationContext):
    """Set correlation context in contextvars."""
    _correlation_context.set(context)


@contextmanager
def correlation_scope(
    correlation_id: Optional[str] = None,
    operation_name: Optional[str] = None
):
    """
    Context manager for correlation scope.
    
    Creates a new correlation context for the duration of the scope,
    automatically propagating correlation IDs to nested operations.
    
    Example:
        with correlation_scope(operation_name="process_workflow"):
            # All operations in this scope share the correlation ID
            logger.info("Processing workflow")
            await step1()
            await step2()
    """
    # Get parent context if exists
    parent_context = get_correlation_context()
    
    # Create new context
    context = CorrelationContext(
        correlation_id=correlation_id or (parent_context.correlation_id if parent_context else None),
        causation_id=parent_context.correlation_id if parent_context else None,
        operation_name=operation_name
    )
    
    # Set as current context
    old_context = get_correlation_context()
    set_correlation_context(context)
    
    try:
        yield context
    finally:
        # Restore previous context
        set_correlation_context(old_context)


class StructuredLogger:
    """
    Structured Logger with Correlation IDs
    
    Provides structured logging with automatic correlation ID injection
    and JSON formatting for better log analysis and aggregation.
    
    Example:
        logger = StructuredLogger(__name__)
        logger.info("User logged in", user_id="123", ip="192.168.1.1")
    """
    
    def __init__(self, name: str):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (usually module name)
        """
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _create_log_entry(
        self,
        level: str,
        message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create structured log entry with correlation metadata."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
        }
        
        # Add correlation context if available
        context = get_correlation_context()
        if context:
            entry["correlation_id"] = context.correlation_id
            if context.causation_id:
                entry["causation_id"] = context.causation_id
            if context.operation_name:
                entry["operation"] = context.operation_name
        
        # Add custom fields
        if kwargs:
            entry["data"] = kwargs
        
        return entry
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal log method."""
        entry = self._create_log_entry(level, message, **kwargs)
        log_message = json.dumps(entry)
        
        # Get appropriate log level method
        log_method = getattr(self.logger, level.lower())
        log_method(log_message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log("CRITICAL", message, **kwargs)


class MetricsCollector:
    """
    Metrics Collector
    
    Collects and tracks metrics (counters, gauges, histograms) for
    monitoring system performance and behavior.
    
    Example:
        metrics = MetricsCollector()
        metrics.increment_counter("api_calls", tags={"endpoint": "/users"})
        metrics.set_gauge("queue_depth", 42.0)
        metrics.record_histogram("response_time_ms", 125.5)
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.last_reset = time.time()
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """
        Increment a counter metric.
        
        Counters are cumulative values that only increase (e.g., request count).
        
        Args:
            name: Metric name
            value: Increment value (default 1)
            tags: Optional tags for metric dimensionality
        """
        key = self._make_key(name, tags)
        self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """
        Set a gauge metric.
        
        Gauges represent point-in-time values that can go up or down (e.g., queue size).
        
        Args:
            name: Metric name
            value: Gauge value
            tags: Optional tags for metric dimensionality
        """
        key = self._make_key(name, tags)
        self.gauges[key] = value
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """
        Record a value in a histogram.
        
        Histograms track distributions of values (e.g., response times, payload sizes).
        
        Args:
            name: Metric name
            value: Value to record
            tags: Optional tags for metric dimensionality
        """
        key = self._make_key(name, tags)
        self.histograms[key].append(value)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.
        
        Returns:
            Dictionary containing all counters, gauges, and histogram summaries
        """
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                name: {
                    "count": len(values),
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "avg": sum(values) / len(values) if values else 0,
                }
                for name, values in self.histograms.items()
            },
            "collection_duration_seconds": time.time() - self.last_reset
        }
    
    def reset(self):
        """Reset all metrics."""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.last_reset = time.time()
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """
        Create metric key with tags.
        
        Uses colon-separated format to avoid conflicts with metric systems
        that use special characters like square brackets for labels.
        Format: metric_name:tag1=value1,tag2=value2
        """
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}:{tag_str}"


class HealthCheck:
    """
    Health Check and Readiness Probe
    
    Provides health status for the application and its dependencies.
    Useful for Kubernetes readiness/liveness probes and monitoring.
    
    Example:
        health = HealthCheck()
        
        async def check_database():
            # Check database connection
            return await db.ping()
        
        health.register_check("database", check_database)
        status = await health.check_health()
    """
    
    def __init__(self):
        """Initialize health check."""
        self.checks: Dict[str, callable] = {}
        self.logger = StructuredLogger(__name__)
    
    def register_check(self, name: str, check_func: callable):
        """
        Register a health check function.
        
        Args:
            name: Check name (e.g., "database", "cache", "external_api")
            check_func: Async function that returns bool or dict with health info
        """
        self.checks[name] = check_func
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Health status dictionary with:
            - healthy: Overall health status (bool)
            - timestamp: When check was performed
            - checks: Individual check results
        """
        results = {}
        all_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                
                if isinstance(result, bool):
                    results[name] = {
                        "healthy": result,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    results[name] = result
                
                if not (result if isinstance(result, bool) else result.get("healthy", False)):
                    all_healthy = False
                    
            except Exception as e:
                self.logger.error(f"Health check {name} failed", error=str(e))
                results[name] = {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                all_healthy = False
        
        return {
            "healthy": all_healthy,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results
        }


# Global instances for convenience
_metrics_collector = MetricsCollector()
_health_check = HealthCheck()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    return _metrics_collector


def get_health_check() -> HealthCheck:
    """Get global health check instance."""
    return _health_check


# Convenience function
def create_structured_logger(name: str) -> StructuredLogger:
    """
    Create a structured logger.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)
