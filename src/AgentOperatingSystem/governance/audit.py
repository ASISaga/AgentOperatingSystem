"""
Audit logging for AgentOperatingSystem

Append-only, tamper-evident audit logging with full context.
Mandatory for all side effects in the system.
"""

import hashlib
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AuditLevel(str, Enum):
    """Audit entry severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditEntry(BaseModel):
    """
    Single audit log entry with tamper-evident properties.
    """
    entry_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: str  # Who performed the action
    action: str  # What was done
    resource: str  # What was affected
    outcome: str  # Result of the action
    level: AuditLevel = AuditLevel.INFO
    context: Dict[str, Any] = Field(default_factory=dict)

    # Tamper-evident properties
    previous_hash: Optional[str] = None
    entry_hash: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def calculate_hash(self) -> str:
        """Calculate hash for this entry"""
        content = {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "outcome": self.outcome,
            "level": self.level.value,
            "context": self.context,
            "previous_hash": self.previous_hash
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify that this entry has not been tampered with"""
        if self.entry_hash is None:
            return False
        return self.calculate_hash() == self.entry_hash


class AuditLogger:
    """
    Append-only audit logger with tamper-evident chain.

    All entries are linked via hash chain to detect tampering.
    Supports mandatory logging for all side effects.
    """

    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize audit logger.

        Args:
            storage_backend: Optional persistent storage backend
        """
        self.storage_backend = storage_backend
        self._entries: List[AuditEntry] = []
        self._last_hash: Optional[str] = None

    def log(
        self,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        level: AuditLevel = AuditLevel.INFO,
        context: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """
        Log an audit entry.

        Args:
            actor: Who performed the action
            action: What was done
            resource: What was affected
            outcome: Result of the action
            level: Severity level
            context: Additional contextual information

        Returns:
            Created audit entry
        """
        import uuid

        entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            actor=actor,
            action=action,
            resource=resource,
            outcome=outcome,
            level=level,
            context=context or {},
            previous_hash=self._last_hash
        )

        # Calculate and store hash
        entry.entry_hash = entry.calculate_hash()
        self._last_hash = entry.entry_hash

        # Store entry
        self._entries.append(entry)

        # Persist if backend available
        if self.storage_backend:
            try:
                self.storage_backend.store_audit_entry(entry)
            except Exception as error:
                logger.error("Failed to persist audit entry: %s", str(error))

        logger.debug(
            f"Audit: {actor} performed {action} on {resource} -> {outcome}"
        )

        return entry

    def log_command(
        self,
        actor: str,
        command: str,
        resource: str,
        success: bool,
        context: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """Log a command execution"""
        outcome = "success" if success else "failure"
        level = AuditLevel.INFO if success else AuditLevel.WARNING
        return self.log(
            actor=actor,
            action=f"command:{command}",
            resource=resource,
            outcome=outcome,
            level=level,
            context=context
        )

    def log_decision(
        self,
        actor: str,
        decision_id: str,
        decision_type: str,
        outcome: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """Log a decision"""
        return self.log(
            actor=actor,
            action=f"decision:{decision_type}",
            resource=f"decision:{decision_id}",
            outcome=outcome,
            level=AuditLevel.INFO,
            context=context
        )

    def log_policy_evaluation(
        self,
        actor: str,
        policy_id: str,
        decision: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """Log a policy evaluation"""
        return self.log(
            actor=actor,
            action="policy:evaluate",
            resource=f"policy:{policy_id}",
            outcome=decision,
            level=AuditLevel.INFO,
            context=context
        )

    def query_entries(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        level: Optional[AuditLevel] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """
        Query audit entries with filters.

        Args:
            actor: Filter by actor
            action: Filter by action
            resource: Filter by resource
            level: Filter by level
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of entries to return

        Returns:
            List of matching audit entries
        """
        results = []

        for entry in self._entries:
            # Apply filters
            if actor and entry.actor != actor:
                continue
            if action and entry.action != action:
                continue
            if resource and entry.resource != resource:
                continue
            if level and entry.level != level:
                continue
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue

            results.append(entry)

            if len(results) >= limit:
                break

        return results

    def verify_chain_integrity(self) -> tuple[bool, Optional[str]]:
        """
        Verify integrity of the entire audit chain.

        Returns:
            Tuple of (is_valid, error_message)
        """
        for i, entry in enumerate(self._entries):
            # Verify entry hash
            if not entry.verify_integrity():
                return False, f"Entry {i} (ID: {entry.entry_id}) hash mismatch"

            # Verify chain linkage
            if i > 0:
                expected_prev_hash = self._entries[i-1].entry_hash
                if entry.previous_hash != expected_prev_hash:
                    return False, f"Entry {i} (ID: {entry.entry_id}) chain broken"

        return True, None

    def export_audit_pack(
        self,
        start_time: datetime,
        end_time: datetime,
        scope: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Export audit pack for compliance reporting.

        Args:
            start_time: Start of audit period
            end_time: End of audit period
            scope: Optional list of resources to include

        Returns:
            Audit pack as dictionary
        """
        entries = self.query_entries(
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )

        # Filter by scope if provided
        if scope:
            entries = [e for e in entries if any(s in e.resource for s in scope)]

        # Verify integrity
        is_valid, error = self.verify_chain_integrity()

        return {
            "audit_pack_id": str(uuid.uuid4()),
            "period_start": start_time.isoformat(),
            "period_end": end_time.isoformat(),
            "scope": scope,
            "entry_count": len(entries),
            "entries": [e.dict() for e in entries],
            "chain_valid": is_valid,
            "chain_error": error,
            "generated_at": datetime.utcnow().isoformat()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit log statistics"""
        level_counts = {}
        actor_counts = {}

        for entry in self._entries:
            level_counts[entry.level.value] = level_counts.get(entry.level.value, 0) + 1
            actor_counts[entry.actor] = actor_counts.get(entry.actor, 0) + 1

        return {
            "total_entries": len(self._entries),
            "by_level": level_counts,
            "by_actor": actor_counts,
            "oldest_entry": self._entries[0].timestamp.isoformat() if self._entries else None,
            "newest_entry": self._entries[-1].timestamp.isoformat() if self._entries else None
        }
