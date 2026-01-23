"""
Structured logging for AgentOperatingSystem

Context-aware logs with redaction rules and separation of audit/operational logs.
"""

import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """Log severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogSeparator(str, Enum):
    """Log separation categories"""
    OPERATIONAL = "operational"  # Day-to-day operations
    AUDIT = "audit"  # Audit trail (compliance)
    SECURITY = "security"  # Security events


class LogEntry(BaseModel):
    """Structured log entry"""
    log_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: LogLevel
    separator: LogSeparator
    message: str
    context: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RedactionRule(BaseModel):
    """Rule for redacting sensitive data"""
    pattern: str  # Regex pattern to match
    replacement: str = "***REDACTED***"
    fields: Optional[List[str]] = None  # Specific fields to redact


class StructuredLogger:
    """
    Structured logger with context awareness and redaction.

    Separates operational and audit logs for compliance.
    """

    def __init__(self):
        """Initialize structured logger"""
        self._logs: Dict[LogSeparator, List[LogEntry]] = {
            LogSeparator.OPERATIONAL: [],
            LogSeparator.AUDIT: [],
            LogSeparator.SECURITY: []
        }
        self._redaction_rules: List[RedactionRule] = []
        self._python_logger = logging.getLogger(__name__)

    def add_redaction_rule(self, pattern: str, replacement: str = "***REDACTED***", fields: Optional[List[str]] = None):
        """Add a redaction rule for sensitive data"""
        self._redaction_rules.append(RedactionRule(
            pattern=pattern,
            replacement=replacement,
            fields=fields
        ))

    def log(
        self,
        level: LogLevel,
        message: str,
        separator: LogSeparator = LogSeparator.OPERATIONAL,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None
    ) -> LogEntry:
        """
        Log a structured entry.

        Args:
            level: Log level
            message: Log message
            separator: Log category
            context: Additional context
            correlation_id: Correlation ID
            causation_id: Causation ID

        Returns:
            Created log entry
        """
        # Redact sensitive data
        redacted_message = self._redact(message)
        redacted_context = self._redact_context(context or {})

        entry = LogEntry(
            level=level,
            separator=separator,
            message=redacted_message,
            context=redacted_context,
            correlation_id=correlation_id,
            causation_id=causation_id
        )

        self._logs[separator].append(entry)

        # Also log to Python logger
        python_level = getattr(logging, level.value.upper())
        self._python_logger.log(
            python_level,
            f"[{separator.value}] {redacted_message}",
            extra={"context": redacted_context}
        )

        return entry

    def info(self, message: str, **kwargs):
        """Log info level"""
        return self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning level"""
        return self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error level"""
        return self.log(LogLevel.ERROR, message, **kwargs)

    def audit(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log audit entry"""
        return self.log(
            LogLevel.INFO,
            message,
            separator=LogSeparator.AUDIT,
            context=context,
            **kwargs
        )

    def security(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log security event"""
        return self.log(
            LogLevel.WARNING,
            message,
            separator=LogSeparator.SECURITY,
            context=context,
            **kwargs
        )

    def query_logs(
        self,
        separator: Optional[LogSeparator] = None,
        level: Optional[LogLevel] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[LogEntry]:
        """Query logs with filters"""
        results = []

        # Determine which separators to search
        separators = [separator] if separator else list(LogSeparator)

        for sep in separators:
            for entry in self._logs[sep]:
                if level and entry.level != level:
                    continue
                if start_time and entry.timestamp < start_time:
                    continue
                if end_time and entry.timestamp > end_time:
                    continue

                results.append(entry)

                if len(results) >= limit:
                    return results

        return results

    def _redact(self, text: str) -> str:
        """Apply redaction rules to text"""
        for rule in self._redaction_rules:
            text = re.sub(rule.pattern, rule.replacement, text)
        return text

    def _redact_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply redaction rules to context"""
        redacted = {}

        for key, value in context.items():
            # Check if this field should be redacted
            should_redact = False
            for rule in self._redaction_rules:
                if rule.fields and key in rule.fields:
                    should_redact = True
                    break

            if should_redact:
                redacted[key] = "***REDACTED***"
            elif isinstance(value, str):
                redacted[key] = self._redact(value)
            else:
                redacted[key] = value

        return redacted
