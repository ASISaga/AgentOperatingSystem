"""
Distributed tracing for AgentOperatingSystem

Correlation and causation propagation across agents with detailed spans.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class TraceLevel(str, Enum):
    """Trace detail levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Span(BaseModel):
    """Individual span in a trace"""
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: Optional[str] = None
    operation_name: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = Field(default_factory=dict)
    logs: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def finish(self):
        """Mark span as finished"""
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000


class TracingContext(BaseModel):
    """Tracing context with correlation and causation IDs"""
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str  # Links related operations
    causation_id: Optional[str] = None  # What caused this trace
    spans: List[Span] = Field(default_factory=list)

    def create_span(self, operation_name: str, parent_span_id: Optional[str] = None) -> Span:
        """Create a new span in this trace"""
        span = Span(
            operation_name=operation_name,
            parent_span_id=parent_span_id
        )
        self.spans.append(span)
        return span

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
