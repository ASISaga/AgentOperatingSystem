"""Observability integration for AOS client applications.

Provides structured logging, correlation context propagation, metrics
collection, and health checks that can be wired into :class:`AOSApp`
automatically.

Usage::

    from aos_client.observability import (
        ObservabilityConfig,
        CorrelationContext,
        StructuredLogger,
        MetricsCollector,
        HealthCheck,
    )

    app = AOSApp(
        name="business-infinity",
        observability=ObservabilityConfig(
            structured_logging=True,
            correlation_tracking=True,
        ),
    )
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class ObservabilityConfig:
    """Configuration for observability features on an :class:`AOSApp`.

    Args:
        structured_logging: Enable JSON-structured log output.
        correlation_tracking: Propagate correlation IDs across calls.
        metrics_endpoint: Optional route for a ``/metrics`` endpoint.
        health_checks: List of subsystem names to include in health probes.
    """

    structured_logging: bool = True
    correlation_tracking: bool = True
    metrics_endpoint: Optional[str] = None
    health_checks: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Correlation context
# ---------------------------------------------------------------------------

import threading

_correlation_local = threading.local()


@dataclass
class CorrelationContext:
    """Correlation context for distributed tracing."""

    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    causation_id: Optional[str] = None
    operation_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "operation_name": self.operation_name,
            "metadata": self.metadata,
            "duration_ms": (time.time() - self.start_time) * 1000,
        }


def get_correlation_context() -> Optional[CorrelationContext]:
    """Return the current thread-local correlation context."""
    return getattr(_correlation_local, "current", None)


def set_correlation_context(ctx: Optional[CorrelationContext]) -> None:
    """Set the thread-local correlation context."""
    _correlation_local.current = ctx


@contextmanager
def correlation_scope(
    correlation_id: Optional[str] = None,
    operation_name: Optional[str] = None,
):
    """Context manager that establishes a correlation scope."""
    parent = get_correlation_context()
    ctx = CorrelationContext(
        correlation_id=correlation_id or (parent.correlation_id if parent else str(uuid.uuid4())),
        causation_id=parent.correlation_id if parent else None,
        operation_name=operation_name,
    )
    previous = get_correlation_context()
    set_correlation_context(ctx)
    try:
        yield ctx
    finally:
        set_correlation_context(previous)


# ---------------------------------------------------------------------------
# Structured logger
# ---------------------------------------------------------------------------


class StructuredLogger:
    """Logger that emits JSON-structured entries with correlation IDs.

    Args:
        name: Logger name (usually the module name).
    """

    def __init__(self, name: str) -> None:
        self._logger = logging.getLogger(name)
        self.name = name

    def _entry(self, level: str, message: str, **kwargs: Any) -> Dict[str, Any]:
        entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
        }
        ctx = get_correlation_context()
        if ctx:
            entry["correlation_id"] = ctx.correlation_id
            if ctx.causation_id:
                entry["causation_id"] = ctx.causation_id
            if ctx.operation_name:
                entry["operation"] = ctx.operation_name
        if kwargs:
            entry["data"] = kwargs
        return entry

    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        entry = self._entry(level, message, **kwargs)
        getattr(self._logger, level.lower())(json.dumps(entry, default=str))

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log("CRITICAL", message, **kwargs)


# ---------------------------------------------------------------------------
# Metrics collector
# ---------------------------------------------------------------------------


class MetricsCollector:
    """In-process metrics collector (counters, gauges, histograms)."""

    def __init__(self) -> None:
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.last_reset = time.time()

    def _key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"

    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        self.counters[self._key(name, tags)] += value

    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        self.gauges[self._key(name, tags)] = value

    def record(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        self.histograms[self._key(name, tags)].append(value)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                k: {
                    "count": len(v),
                    "min": min(v) if v else 0,
                    "max": max(v) if v else 0,
                    "avg": sum(v) / len(v) if v else 0,
                }
                for k, v in self.histograms.items()
            },
            "collection_duration_s": time.time() - self.last_reset,
        }

    def reset(self) -> None:
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.last_reset = time.time()


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------


class HealthCheck:
    """Aggregated health / readiness probe."""

    def __init__(self) -> None:
        self._checks: Dict[str, Callable] = {}

    def register(self, name: str, check_fn: Callable) -> None:
        """Register an async health-check function."""
        self._checks[name] = check_fn

    async def check(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        all_healthy = True
        for name, fn in self._checks.items():
            try:
                result = await fn()
                healthy = result if isinstance(result, bool) else result.get("healthy", False)
                results[name] = (
                    {"healthy": result, "timestamp": datetime.utcnow().isoformat()}
                    if isinstance(result, bool)
                    else result
                )
                if not healthy:
                    all_healthy = False
            except Exception as exc:
                results[name] = {
                    "healthy": False,
                    "error": str(exc),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                all_healthy = False
        return {
            "healthy": all_healthy,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results,
        }


# ---------------------------------------------------------------------------
# Convenience singletons
# ---------------------------------------------------------------------------

_metrics = MetricsCollector()
_health = HealthCheck()


def get_metrics_collector() -> MetricsCollector:
    """Return the global :class:`MetricsCollector`."""
    return _metrics


def get_health_check() -> HealthCheck:
    """Return the global :class:`HealthCheck`."""
    return _health


def create_structured_logger(name: str) -> StructuredLogger:
    """Create a :class:`StructuredLogger`."""
    return StructuredLogger(name)
