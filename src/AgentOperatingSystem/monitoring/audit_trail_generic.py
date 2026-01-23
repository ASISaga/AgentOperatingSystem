"""
Generic Audit Trail Infrastructure for Agent Operating System

This module provides generic, reusable audit trail capabilities for any agent-based system:
- Tamper-evident event logging with cryptographic checksums
- Compliance-aware retention policies
- Structured event storage and querying
- Integrity verification

Domain-specific event types and business logic should be implemented in the
application layer (e.g., BusinessInfinity).

Usage:
    from AgentOperatingSystem.monitoring.audit_trail_generic import AuditTrailManager, AuditEvent

    # Create manager
    audit = AuditTrailManager(storage_path="./audit_logs")

    # Log generic event
    event_id = audit.log_event(
        event_type="action_performed",
        subject_id="agent_123",
        subject_type="agent",
        action="Executed workflow",
        context={"workflow_id": "onboarding"}
    )

    # Query events
    events = audit.query_events(subject_id="agent_123", limit=10)
"""

import hashlib
import json
import logging
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class AuditSeverity(Enum):
    """Severity levels for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """
    Represents a single audit event with comprehensive metadata and integrity protection.

    This is a generic audit event that can be extended by application-specific
    implementations.
    """
    event_id: str
    event_type: str  # Generic string type - applications define their own types
    timestamp: datetime
    severity: AuditSeverity

    # Subject information
    subject_id: str  # Agent ID, User ID, System ID
    subject_type: str  # "agent", "user", "system", etc.
    action: str  # What was done

    # Optional fields
    subject_role: Optional[str] = None  # Role or function
    target: Optional[str] = None  # What was acted upon

    # Context and metadata
    context: Dict[str, Any] = field(default_factory=dict)
    rationale: Optional[str] = None  # Reasoning behind the action
    evidence: List[str] = field(default_factory=list)  # Supporting evidence

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

        # Convert datetime objects to ISO format for deterministic serialization
        if 'timestamp' in data and isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        if 'retention_until' in data and data['retention_until'] and isinstance(data['retention_until'], datetime):
            data['retention_until'] = data['retention_until'].isoformat()

        # Serialize to JSON string with deterministic ordering
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify the integrity of this audit event"""
        expected_checksum = self._calculate_checksum()
        return self.checksum == expected_checksum

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = asdict(self)
        # Convert enums and sets to serializable types
        data['severity'] = data['severity'].value if isinstance(data['severity'], AuditSeverity) else data['severity']
        data['compliance_tags'] = list(data['compliance_tags'])
        data['timestamp'] = data['timestamp'].isoformat() if isinstance(data['timestamp'], datetime) else data['timestamp']
        if data.get('retention_until'):
            data['retention_until'] = data['retention_until'].isoformat() if isinstance(data['retention_until'], datetime) else data['retention_until']
        return data


@dataclass
class AuditQuery:
    """Query parameters for audit log searches"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[str]] = None  # Generic string types
    subject_ids: Optional[List[str]] = None
    subject_types: Optional[List[str]] = None
    severities: Optional[List[AuditSeverity]] = None
    compliance_tags: Optional[List[str]] = None
    limit: int = 1000
    offset: int = 0


class AuditTrailManager:
    """
    Generic audit trail management with integrity protection and compliance support.

    This is a base implementation that applications can extend with domain-specific
    event types and business logic.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize audit trail manager.

        Args:
            storage_path: Path to store audit logs (defaults to "./audit_logs")
        """
        self.storage_path = Path(storage_path or "audit_logs")
        self.storage_path.mkdir(exist_ok=True)

        self.logger = logging.getLogger(__name__)
        self._event_buffer: List[AuditEvent] = []
        self._buffer_lock = threading.Lock()
        self._buffer_max_size = 100

        # Compliance retention policies (in days)
        # Applications can override or extend these
        self._retention_policies = {
            "sox": 2555,  # 7 years for SOX
            "gdpr": 2555,  # Up to 7 years for GDPR
            "hipaa": 2190,  # 6 years for HIPAA
            "pci_dss": 365,  # 1 year for PCI DSS
            "default": 365  # 1 year default
        }

        self.logger.info("AuditTrailManager initialized")

    def set_retention_policy(self, tag: str, days: int):
        """
        Set or update a retention policy.

        Args:
            tag: Compliance tag
            days: Retention period in days
        """
        self._retention_policies[tag] = days

    def _calculate_retention(self, compliance_tags: Set[str]) -> datetime:
        """
        Calculate retention period based on compliance tags.

        Args:
            compliance_tags: Set of compliance tags

        Returns:
            Retention deadline datetime
        """
        if not compliance_tags:
            days = self._retention_policies["default"]
        else:
            # Use the longest retention period among applicable tags
            days = max(
                (self._retention_policies.get(tag, self._retention_policies["default"])
                 for tag in compliance_tags),
                default=self._retention_policies["default"]
            )

        return datetime.utcnow() + timedelta(days=days)

    def log_event(self,
                  event_type: str,
                  subject_id: str,
                  subject_type: str,
                  action: str,
                  severity: AuditSeverity = AuditSeverity.MEDIUM,
                  **kwargs) -> str:
        """
        Log a single audit event.

        Args:
            event_type: Type of event being logged (application-defined)
            subject_id: ID of the subject performing the action
            subject_type: Type of subject (agent, user, system, etc.)
            action: Description of the action taken
            severity: Severity level of the event
            **kwargs: Additional event data (context, rationale, evidence, etc.)

        Returns:
            The event ID of the logged event
        """
        event_id = str(uuid.uuid4())

        # Calculate retention based on compliance tags
        compliance_tags = set(kwargs.get('compliance_tags', []))
        retention_until = self._calculate_retention(compliance_tags)

        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            severity=severity,
            subject_id=subject_id,
            subject_type=subject_type,
            subject_role=kwargs.get('subject_role'),
            action=action,
            target=kwargs.get('target'),
            context=kwargs.get('context', {}),
            rationale=kwargs.get('rationale'),
            evidence=kwargs.get('evidence', []),
            metrics=kwargs.get('metrics', {}),
            compliance_tags=compliance_tags,
            retention_until=retention_until
        )

        self._add_to_buffer(event)

        # Log to standard logging as well
        log_message = f"AUDIT: {event_type} by {subject_id} ({subject_type}): {action}"
        if event.severity == AuditSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif event.severity == AuditSeverity.HIGH:
            self.logger.error(log_message)
        elif event.severity == AuditSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

        return event_id

    def _add_to_buffer(self, event: AuditEvent):
        """Add event to buffer and flush if needed"""
        with self._buffer_lock:
            self._event_buffer.append(event)
            if len(self._event_buffer) >= self._buffer_max_size:
                self._flush_buffer()

    def _flush_buffer(self):
        """Flush buffered events to storage"""
        if not self._event_buffer:
            return

        # Write to daily log file
        today = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = self.storage_path / f"audit_{today}.jsonl"

        try:
            with open(log_file, 'a', encoding="utf-8") as file_obj:
                for event in self._event_buffer:
                    json_line = json.dumps(event.to_dict())
                    file_obj.write(json_line + '\n')

            self.logger.debug("Flushed %s events to %s", len(self._event_buffer), log_file)
            self._event_buffer.clear()

        except Exception as error:
            self.logger.error("Failed to flush audit events: %s", str(error))

    def flush(self):
        """Manually flush buffered events"""
        with self._buffer_lock:
            self._flush_buffer()

    def query_events(self,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    event_types: Optional[List[str]] = None,
                    subject_id: Optional[str] = None,
                    subject_type: Optional[str] = None,
                    severity: Optional[AuditSeverity] = None,
                    limit: int = 1000) -> List[AuditEvent]:
        """
        Query audit events.

        Args:
            start_time: Start of time range
            end_time: End of time range
            event_types: Filter by event types
            subject_id: Filter by subject ID
            subject_type: Filter by subject type
            severity: Filter by severity
            limit: Maximum number of events to return

        Returns:
            List of matching audit events
        """
        events = []

        # Determine which log files to scan
        if start_time and end_time:
            days_to_scan = (end_time.date() - start_time.date()).days + 1
            dates = [start_time.date() + timedelta(days=i) for i in range(days_to_scan)]
        else:
            # Scan all available log files
            dates = [f.stem.replace('audit_', '') for f in self.storage_path.glob('audit_*.jsonl')]
            dates = [datetime.strptime(d, '%Y-%m-%d').date() for d in dates]

        # Read and filter events
        for date in dates:
            log_file = self.storage_path / f"audit_{date.strftime('%Y-%m-%d')}.jsonl"
            if not log_file.exists():
                continue

            try:
                with open(log_file, 'r', encoding="utf-8") as file_obj:
                    for line in f:
                        try:
                            data = json.loads(line)

                            # Convert back to AuditEvent
                            # Parse timestamp
                            if isinstance(data.get('timestamp'), str):
                                data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

                            # Parse severity
                            if isinstance(data.get('severity'), str):
                                data['severity'] = AuditSeverity(data['severity'])

                            # Parse compliance tags
                            if isinstance(data.get('compliance_tags'), list):
                                data['compliance_tags'] = set(data['compliance_tags'])

                            # Parse retention_until
                            if data.get('retention_until') and isinstance(data['retention_until'], str):
                                data['retention_until'] = datetime.fromisoformat(data['retention_until'].replace('Z', '+00:00'))

                            event = AuditEvent(**data)

                            # Apply filters
                            if start_time and event.timestamp < start_time:
                                continue
                            if end_time and event.timestamp > end_time:
                                continue
                            if event_types and event.event_type not in event_types:
                                continue
                            if subject_id and event.subject_id != subject_id:
                                continue
                            if subject_type and event.subject_type != subject_type:
                                continue
                            if severity and event.severity != severity:
                                continue

                            events.append(event)

                            if len(events) >= limit:
                                return events

                        except Exception as error:
                            self.logger.warning("Failed to parse audit event: %s", str(error))
                            continue

            except Exception as error:
                self.logger.error("Failed to read audit log %s: %s", log_file, str(error))

        return events[:limit]

    def verify_integrity(self, event_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify the integrity of audit events.

        Args:
            event_id: Specific event ID to verify, or None to verify all

        Returns:
            Verification result with statistics
        """
        total = 0
        valid = 0
        invalid = []

        for log_file in self.storage_path.glob('audit_*.jsonl'):
            try:
                with open(log_file, 'r', encoding="utf-8") as file_obj:
                    for line in f:
                        try:
                            data = json.loads(line)

                            # Skip if looking for specific event
                            if event_id and data.get('event_id') != event_id:
                                continue

                            # Parse and verify
                            if isinstance(data.get('timestamp'), str):
                                data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                            if isinstance(data.get('severity'), str):
                                data['severity'] = AuditSeverity(data['severity'])
                            if isinstance(data.get('compliance_tags'), list):
                                data['compliance_tags'] = set(data['compliance_tags'])
                            if data.get('retention_until') and isinstance(data['retention_until'], str):
                                data['retention_until'] = datetime.fromisoformat(data['retention_until'].replace('Z', '+00:00'))

                            event = AuditEvent(**data)
                            total += 1

                            if event.verify_integrity():
                                valid += 1
                            else:
                                invalid.append(event.event_id)

                            # If looking for specific event, stop after finding it
                            if event_id and event.event_id == event_id:
                                break

                        except Exception as error:
                            self.logger.warning("Failed to verify event: %s", str(error))

            except Exception as error:
                self.logger.error("Failed to read audit log %s: %s", log_file, str(error))

        return {
            "total_verified": total,
            "valid": valid,
            "invalid_count": len(invalid),
            "invalid_event_ids": invalid,
            "integrity_rate": (valid / total * 100) if total > 0 else 0
        }

    def cleanup_expired(self) -> int:
        """
        Remove events that have exceeded their retention period.

        Returns:
            Number of events removed
        """
        removed = 0
        now = datetime.utcnow()

        for log_file in self.storage_path.glob('audit_*.jsonl'):
            temp_file = log_file.with_suffix('.tmp')

            try:
                with open(log_file, 'r', encoding="utf-8") as infile, open(temp_file, 'w', encoding="utf-8") as outfile:
                    for line in infile:
                        try:
                            data = json.loads(line)

                            # Check retention
                            retention_until = data.get('retention_until')
                            if retention_until:
                                if isinstance(retention_until, str):
                                    retention_until = datetime.fromisoformat(retention_until.replace('Z', '+00:00'))

                                if retention_until < now:
                                    removed += 1
                                    continue  # Skip this event (remove it)

                            # Keep this event
                            outfile.write(line)

                        except Exception as error:
                            self.logger.warning("Failed to process event during cleanup: %s", str(error))
                            outfile.write(line)  # Keep on error

                # Replace original with cleaned file
                temp_file.replace(log_file)

            except Exception as error:
                self.logger.error("Failed to cleanup audit log %s: %s", log_file, str(error))
                if temp_file.exists():
                    temp_file.unlink()

        self.logger.info("Removed %s expired audit events", removed)
        return removed
