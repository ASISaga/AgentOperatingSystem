"""
AOS Monitoring - Comprehensive Audit Trail Manager

Provides rigorous audit logging for:
- Agent actions and decisions
- System operations and orchestration
- MCP server interactions
- Security events and access control
- Decision-making rationales and justifications
- Both qualitative and quantitative audit data

Supports compliance requirements (SOX, GDPR, HIPAA) and audit trail integrity.
This is the OS-level audit infrastructure.
"""

import hashlib
import json
import logging
import threading
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class AuditEventType(Enum):
    """Types of events that can be audited"""
    # Agent and system events
    AGENT_ACTION = "agent_action"
    AGENT_DECISION = "agent_decision"
    AGENT_COMMUNICATION = "agent_communication"
    AGENT_LIFECYCLE = "agent_lifecycle"

    # Boardroom events
    BOARDROOM_DECISION = "boardroom_decision"
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    DECISION_INITIATED = "decision_initiated"
    DECISION_COMPLETED = "decision_completed"
    DECISION_EXPIRED = "decision_expired"

    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"
    COMPONENT_STARTED = "component_started"
    COMPONENT_STOPPED = "component_stopped"

    # MCP interactions
    MCP_REQUEST = "mcp_request"
    MCP_RESPONSE = "mcp_response"
    MCP_ERROR = "mcp_error"
    MCP_ACCESS_DENIED = "mcp_access_denied"

    # Security events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    ACCESS_CONTROL = "access_control"
    PERMISSION_CHANGE = "permission_change"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"

    # Storage and data events
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    STORAGE_OPERATION = "storage_operation"

    # Orchestration events
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"

    # ML Pipeline events
    MODEL_LOADED = "model_loaded"
    MODEL_INFERENCE = "model_inference"
    PIPELINE_EXECUTED = "pipeline_executed"
    TRAINING_STARTED = "training_started"
    TRAINING_COMPLETED = "training_completed"

    # Messaging events
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_BROADCAST = "message_broadcast"
    MESSAGE_FAILED = "message_failed"


class AuditSeverity(Enum):
    """Severity levels for audit events"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Represents a single audit event with comprehensive metadata"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    severity: AuditSeverity

    # Subject information
    subject_id: str  # Agent ID, User ID, System ID
    subject_type: str  # "agent", "user", "system", "component"
    action: str  # What was done

    # Optional fields
    subject_role: Optional[str] = None  # Role or function
    target: Optional[str] = None  # What was acted upon
    component: Optional[str] = None  # Which AOS component was involved

    # Context and metadata
    context: Dict[str, Any] = field(default_factory=dict)
    rationale: Optional[str] = None  # Reasoning behind the action
    evidence: List[str] = field(default_factory=list)  # Supporting evidence
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    # Quantitative data
    metrics: Dict[str, float] = field(default_factory=dict)

    # Integrity protection
    checksum: Optional[str] = None
    signature: Optional[str] = None

    # Compliance and retention
    compliance_tags: Set[str] = field(default_factory=set)
    retention_until: Optional[datetime] = None

    def __post_init__(self):
        """Calculate checksum for integrity protection"""
        if not self.checksum:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate SHA-256 checksum for tamper detection"""
        # Create a copy without checksum and signature for hashing
        data = asdict(self)
        data.pop('checksum', None)
        data.pop('signature', None)

        # Convert sets to lists for JSON serialization
        if 'compliance_tags' in data:
            data['compliance_tags'] = list(data['compliance_tags'])

        # Serialize to JSON string with deterministic ordering
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify the integrity of this audit event"""
        expected_checksum = self._calculate_checksum()
        return self.checksum == expected_checksum


@dataclass
class AuditQuery:
    """Query parameters for audit log searches"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[AuditEventType]] = None
    subject_ids: Optional[List[str]] = None
    subject_types: Optional[List[str]] = None
    components: Optional[List[str]] = None
    severities: Optional[List[AuditSeverity]] = None
    compliance_tags: Optional[List[str]] = None
    limit: int = 1000
    offset: int = 0


class AuditTrailManager:
    """
    Comprehensive audit trail management with integrity protection and compliance support
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or "aos_audit_logs")
        self.storage_path.mkdir(exist_ok=True)

        self.logger = logging.getLogger(__name__)
        self._event_buffer: List[AuditEvent] = []
        self._buffer_lock = threading.Lock()
        self._buffer_max_size = 100
        self._initialized = False

        # Compliance retention policies (in days)
        self._retention_policies = {
            "sox": 2555,  # 7 years for SOX
            "gdpr": 2555,  # Up to 7 years for GDPR
            "hipaa": 2190,  # 6 years for HIPAA
            "pci": 365,  # 1 year for PCI DSS
            "default": 365  # 1 year default
        }

        self.logger.info("AOS AuditTrailManager initialized")

    async def initialize(self):
        """Initialize the audit trail manager"""
        if self._initialized:
            return

        # Ensure storage directory exists
        self.storage_path.mkdir(exist_ok=True)

        # Load any existing audit configuration
        await self._load_config()

        # Start background tasks
        await self._start_background_tasks()

        self._initialized = True
        self.logger.info("AuditTrailManager initialization complete")

    def log_event(self,
                  event_type: AuditEventType,
                  subject_id: str,
                  subject_type: str,
                  action: str,
                  severity: AuditSeverity = AuditSeverity.INFO,
                  **kwargs) -> str:
        """
        Log a single audit event

        Args:
            event_type: Type of event being logged
            subject_id: ID of the subject performing the action
            subject_type: Type of subject (agent, user, system, component)
            action: Description of the action taken
            severity: Severity level of the event
            **kwargs: Additional event data (context, rationale, evidence, etc.)

        Returns:
            The event ID of the logged event
        """
        event_id = str(uuid.uuid4())

        # Determine retention policy
        retention_until = None
        compliance_tags = set(kwargs.get('compliance_tags', []))
        if compliance_tags:
            max_retention_days = max(
                self._retention_policies.get(tag, self._retention_policies['default'])
                for tag in compliance_tags
            )
            retention_until = datetime.now() + timedelta(days=max_retention_days)

        # Create audit event
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now(),
            severity=severity,
            subject_id=subject_id,
            subject_type=subject_type,
            action=action,
            subject_role=kwargs.get('subject_role'),
            target=kwargs.get('target'),
            component=kwargs.get('component'),
            context=kwargs.get('context', {}),
            rationale=kwargs.get('rationale'),
            evidence=kwargs.get('evidence', []),
            metadata=kwargs.get('metadata', {}),
            metrics=kwargs.get('metrics', {}),
            compliance_tags=compliance_tags,
            retention_until=retention_until
        )

        # Add to buffer
        with self._buffer_lock:
            self._event_buffer.append(event)

            # Flush if buffer is full
            if len(self._event_buffer) >= self._buffer_max_size:
                self._flush_buffer()

        # Log critical events immediately
        if severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
            self._flush_buffer()

        self.logger.debug("Audit event logged: %s - %s", event_id, action)
        return event_id

    def _flush_buffer(self):
        """Flush the event buffer to storage"""
        if not self._event_buffer:
            return

        try:
            # Write events to daily log file
            today = datetime.now().date()
            log_file = self.storage_path / f"audit_{today.isoformat()}.jsonl"

            with log_file.open('a', encoding='utf-8') as f:
                for event in self._event_buffer:
                    f.write(json.dumps(asdict(event), default=str) + '\n')

            self._event_buffer.clear()

        except Exception as error:
            self.logger.error("Failed to flush audit buffer: %s", str(error))

    async def query_events(self, query: AuditQuery) -> List[AuditEvent]:
        """Query audit events based on specified criteria"""
        events = []

        # Determine which log files to check
        log_files = self._get_log_files_for_query(query)

        for log_file in log_files:
            if not log_file.exists():
                continue

            try:
                with log_file.open('r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue

                        event_data = json.loads(line)
                        event = self._dict_to_audit_event(event_data)

                        if self._matches_query(event, query):
                            events.append(event)

                            # Apply limit
                            if len(events) >= query.limit:
                                return events[query.offset:]

            except Exception as error:
                self.logger.error("Error reading log file %s: %s", log_file, str(error))

        return events[query.offset:]

    def _get_log_files_for_query(self, query: AuditQuery) -> List[Path]:
        """Get list of log files that might contain events for the query"""
        if not query.start_time and not query.end_time:
            # Return all log files if no time range specified
            return sorted(self.storage_path.glob("audit_*.jsonl"))

        files = []
        start_date = query.start_time.date() if query.start_time else datetime.min.date()
        end_date = query.end_time.date() if query.end_time else datetime.max.date()

        # Generate date range
        current_date = start_date
        while current_date <= end_date:
            log_file = self.storage_path / f"audit_{current_date.isoformat()}.jsonl"
            if log_file.exists():
                files.append(log_file)
            current_date += timedelta(days=1)

        return files

    def _dict_to_audit_event(self, data: Dict[str, Any]) -> AuditEvent:
        """Convert dictionary to AuditEvent object"""
        # Convert string enums back to enum objects
        data['event_type'] = AuditEventType(data['event_type'])
        data['severity'] = AuditSeverity(data['severity'])

        # Convert ISO timestamp back to datetime
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])

        if data.get('retention_until'):
            data['retention_until'] = datetime.fromisoformat(data['retention_until'])

        # Convert compliance_tags list back to set
        if 'compliance_tags' in data:
            data['compliance_tags'] = set(data['compliance_tags'])

        return AuditEvent(**data)

    def _matches_query(self, event: AuditEvent, query: AuditQuery) -> bool:
        """Check if event matches query criteria"""
        # Time range
        if query.start_time and event.timestamp < query.start_time:
            return False
        if query.end_time and event.timestamp > query.end_time:
            return False

        # Event types
        if query.event_types and event.event_type not in query.event_types:
            return False

        # Subject IDs
        if query.subject_ids and event.subject_id not in query.subject_ids:
            return False

        # Subject types
        if query.subject_types and event.subject_type not in query.subject_types:
            return False

        # Components
        if query.components and event.component not in query.components:
            return False

        # Severities
        if query.severities and event.severity not in query.severities:
            return False

        # Compliance tags
        if query.compliance_tags:
            if not any(tag in event.compliance_tags for tag in query.compliance_tags):
                return False

        return True

    async def _load_config(self):
        """Load audit configuration"""
        config_file = self.storage_path / "audit_config.json"
        if config_file.exists():
            try:
                with config_file.open('r', encoding="utf-8") as f:
                    config = json.load(f)
                    self._retention_policies.update(config.get('retention_policies', {}))
                    self._buffer_max_size = config.get('buffer_max_size', self._buffer_max_size)
            except Exception as error:
                self.logger.error("Failed to load audit config: %s", str(error))

    async def _start_background_tasks(self):
        """Start background maintenance tasks"""
        # Start periodic buffer flush
        # Start log rotation and cleanup
        # These would be implemented as asyncio tasks

    async def health_check(self) -> Dict[str, Any]:
        """Get health status of audit trail manager"""
        return {
            "initialized": self._initialized,
            "buffer_size": len(self._event_buffer),
            "storage_path": str(self.storage_path),
            "log_files_count": len(list(self.storage_path.glob("audit_*.jsonl")))
        }


# Global audit manager instance
_audit_manager: Optional[AuditTrailManager] = None

def get_audit_manager() -> AuditTrailManager:
    """Get the global audit manager instance"""
    global _audit_manager
    if _audit_manager is None:
        _audit_manager = AuditTrailManager()
    return _audit_manager

async def audit_log(event_type: AuditEventType,
                   action: str,
                   subject_id: str = "system",
                   subject_type: str = "system",
                   severity: AuditSeverity = AuditSeverity.INFO,
                   **kwargs) -> str:
    """Convenience function for logging audit events"""
    manager = get_audit_manager()
    return manager.log_event(
        event_type=event_type,
        subject_id=subject_id,
        subject_type=subject_type,
        action=action,
        severity=severity,
        **kwargs
    )


@contextmanager
def audit_context(action: str,
                  event_type: AuditEventType = AuditEventType.SYSTEM_ERROR,
                  subject_id: str = "system",
                  **kwargs):
    """Context manager for auditing operations with automatic success/failure logging"""
    start_time = datetime.now()

    try:
        yield

        # Log successful completion
        duration = (datetime.now() - start_time).total_seconds()
        audit_log(
            event_type,
            f"{action} completed successfully",
            subject_id=subject_id,
            severity=AuditSeverity.INFO,
            metrics={"duration_seconds": duration},
            **kwargs
        )

    except Exception as error:
        # Log failure
        duration = (datetime.now() - start_time).total_seconds()
        audit_log(
            AuditEventType.SYSTEM_ERROR,
            f"{action} failed: {str(error)}",
            subject_id=subject_id,
            severity=AuditSeverity.ERROR,
            context={"error": str(error), "error_type": type(error).__name__},
            metrics={"duration_seconds": duration},
            **kwargs
        )
        raise
