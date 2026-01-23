"""
Observability - Structured logging, metrics, tracing.
"""

import logging
from datetime import datetime
from typing import Any, Dict


class StructuredLogger:
    """Structured logger with context and correlation."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context = {}

    def with_context(self, **kwargs) -> 'StructuredLogger':
        """Create logger with additional context."""
        new_logger = StructuredLogger(self.logger.name)
        new_logger.context = {**self.context, **kwargs}
        return new_logger

    def _log(self, level: int, message: str, **kwargs):
        """Log with structured context."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "context": {**self.context, **kwargs}
        }
        self.logger.log(level, log_data)

    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

class MetricsCollector:
    """Metrics collection for observability."""

    def __init__(self):
        self.metrics = {}

    def record_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Record counter metric."""
        key = f"counter_{name}"
        if key not in self.metrics:
            self.metrics[key] = 0
        self.metrics[key] += value

    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record gauge metric."""
        key = f"gauge_{name}"
        self.metrics[key] = value

    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record histogram metric."""
        key = f"histogram_{name}"
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(value)

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return self.metrics
