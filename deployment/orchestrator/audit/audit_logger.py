"""
Audit Logger

Records deployment execution for traceability and compliance.
"""

import json
import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import uuid


class AuditRecord:
    """Represents a single deployment audit record."""
    
    def __init__(self, deployment_id: str, git_sha: Optional[str] = None,
                 template_file: Optional[str] = None, parameters_file: Optional[str] = None):
        """
        Initialize audit record.
        
        Args:
            deployment_id: Unique deployment identifier
            git_sha: Git commit SHA
            template_file: Path to Bicep template
            parameters_file: Path to parameters file
        """
        self.deployment_id = deployment_id
        self.git_sha = git_sha
        self.template_file = template_file
        self.parameters_file = parameters_file
        self.timestamp = datetime.utcnow()
        self.events: List[Dict[str, Any]] = []
        self.result: Optional[Dict[str, Any]] = None
        self.resources: List[Dict[str, Any]] = []
    
    def add_event(self, event_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Add an event to the audit log.
        
        Args:
            event_type: Type of event (e.g., 'lint', 'deploy', 'verify')
            message: Event message
            details: Additional event details
        """
        self.events.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "message": message,
            "details": details or {}
        })
    
    def set_result(self, success: bool, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Set the deployment result.
        
        Args:
            success: Whether deployment succeeded
            message: Result message
            details: Additional result details
        """
        self.result = {
            "success": success,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
    
    def add_resource(self, resource_id: str, resource_type: str, 
                    health_status: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Add a deployed resource to the record.
        
        Args:
            resource_id: Azure resource ID
            resource_type: Type of resource
            health_status: Health status of resource
            details: Additional resource details
        """
        self.resources.append({
            "resource_id": resource_id,
            "resource_type": resource_type,
            "health_status": health_status,
            "details": details or {}
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "deployment_id": self.deployment_id,
            "git_sha": self.git_sha,
            "template_file": self.template_file,
            "parameters_file": self.parameters_file,
            "timestamp": self.timestamp.isoformat(),
            "events": self.events,
            "result": self.result,
            "resources": self.resources
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """
    Audit logger for deployment tracking.
    
    Supports both JSON file and SQLite database backends.
    """
    
    def __init__(self, storage_path: Path, use_sqlite: bool = True):
        """
        Initialize audit logger.
        
        Args:
            storage_path: Path to storage directory
            use_sqlite: Whether to use SQLite (True) or JSON files (False)
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.use_sqlite = use_sqlite
        
        if use_sqlite:
            self.db_path = self.storage_path / "audit.db"
            self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create deployments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                deployment_id TEXT PRIMARY KEY,
                git_sha TEXT,
                template_file TEXT,
                parameters_file TEXT,
                timestamp TEXT,
                success INTEGER,
                result_message TEXT,
                result_details TEXT
            )
        """)
        
        # Create events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployment_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployment_id TEXT,
                timestamp TEXT,
                event_type TEXT,
                message TEXT,
                details TEXT,
                FOREIGN KEY (deployment_id) REFERENCES deployments(deployment_id)
            )
        """)
        
        # Create resources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployment_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployment_id TEXT,
                resource_id TEXT,
                resource_type TEXT,
                health_status TEXT,
                details TEXT,
                FOREIGN KEY (deployment_id) REFERENCES deployments(deployment_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_record(self, git_sha: Optional[str] = None, 
                     template_file: Optional[str] = None,
                     parameters_file: Optional[str] = None) -> AuditRecord:
        """
        Create a new audit record.
        
        Args:
            git_sha: Git commit SHA
            template_file: Path to Bicep template
            parameters_file: Path to parameters file
            
        Returns:
            New AuditRecord instance
        """
        deployment_id = str(uuid.uuid4())
        return AuditRecord(deployment_id, git_sha, template_file, parameters_file)
    
    def save_record(self, record: AuditRecord):
        """
        Save an audit record.
        
        Args:
            record: AuditRecord to save
        """
        if self.use_sqlite:
            self._save_to_sqlite(record)
        else:
            self._save_to_json(record)
    
    def _save_to_sqlite(self, record: AuditRecord):
        """Save record to SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save deployment record
        result = record.result or {}
        cursor.execute("""
            INSERT OR REPLACE INTO deployments 
            (deployment_id, git_sha, template_file, parameters_file, timestamp, 
             success, result_message, result_details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.deployment_id,
            record.git_sha,
            record.template_file,
            record.parameters_file,
            record.timestamp.isoformat(),
            1 if result.get("success") else 0,
            result.get("message"),
            json.dumps(result.get("details", {}))
        ))
        
        # Save events
        for event in record.events:
            cursor.execute("""
                INSERT INTO deployment_events 
                (deployment_id, timestamp, event_type, message, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                record.deployment_id,
                event["timestamp"],
                event["event_type"],
                event["message"],
                json.dumps(event.get("details", {}))
            ))
        
        # Save resources
        for resource in record.resources:
            cursor.execute("""
                INSERT INTO deployment_resources 
                (deployment_id, resource_id, resource_type, health_status, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                record.deployment_id,
                resource["resource_id"],
                resource["resource_type"],
                resource.get("health_status"),
                json.dumps(resource.get("details", {}))
            ))
        
        conn.commit()
        conn.close()
    
    def _save_to_json(self, record: AuditRecord):
        """Save record to JSON file."""
        filename = f"{record.deployment_id}.json"
        filepath = self.storage_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(record.to_json())
    
    def get_record(self, deployment_id: str) -> Optional[AuditRecord]:
        """
        Retrieve an audit record by ID.
        
        Args:
            deployment_id: Deployment ID to retrieve
            
        Returns:
            AuditRecord if found, None otherwise
        """
        if self.use_sqlite:
            return self._get_from_sqlite(deployment_id)
        else:
            return self._get_from_json(deployment_id)
    
    def _get_from_sqlite(self, deployment_id: str) -> Optional[AuditRecord]:
        """Retrieve record from SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get deployment
        cursor.execute("""
            SELECT git_sha, template_file, parameters_file, timestamp, 
                   success, result_message, result_details
            FROM deployments WHERE deployment_id = ?
        """, (deployment_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        record = AuditRecord(
            deployment_id=deployment_id,
            git_sha=row[0],
            template_file=row[1],
            parameters_file=row[2]
        )
        record.timestamp = datetime.fromisoformat(row[3])
        
        # Set result
        if row[4] is not None:
            record.set_result(
                success=bool(row[4]),
                message=row[5] or "",
                details=json.loads(row[6]) if row[6] else {}
            )
        
        # Get events
        cursor.execute("""
            SELECT timestamp, event_type, message, details
            FROM deployment_events WHERE deployment_id = ?
            ORDER BY timestamp
        """, (deployment_id,))
        
        for event_row in cursor.fetchall():
            record.events.append({
                "timestamp": event_row[0],
                "event_type": event_row[1],
                "message": event_row[2],
                "details": json.loads(event_row[3]) if event_row[3] else {}
            })
        
        # Get resources
        cursor.execute("""
            SELECT resource_id, resource_type, health_status, details
            FROM deployment_resources WHERE deployment_id = ?
        """, (deployment_id,))
        
        for resource_row in cursor.fetchall():
            record.resources.append({
                "resource_id": resource_row[0],
                "resource_type": resource_row[1],
                "health_status": resource_row[2],
                "details": json.loads(resource_row[3]) if resource_row[3] else {}
            })
        
        conn.close()
        return record
    
    def _get_from_json(self, deployment_id: str) -> Optional[AuditRecord]:
        """Retrieve record from JSON file."""
        filename = f"{deployment_id}.json"
        filepath = self.storage_path / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        record = AuditRecord(
            deployment_id=data["deployment_id"],
            git_sha=data.get("git_sha"),
            template_file=data.get("template_file"),
            parameters_file=data.get("parameters_file")
        )
        record.timestamp = datetime.fromisoformat(data["timestamp"])
        record.events = data.get("events", [])
        record.result = data.get("result")
        record.resources = data.get("resources", [])
        
        return record
    
    def list_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List recent deployment records.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of deployment summaries
        """
        if self.use_sqlite:
            return self._list_from_sqlite(limit)
        else:
            return self._list_from_json(limit)
    
    def _list_from_sqlite(self, limit: int) -> List[Dict[str, Any]]:
        """List records from SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT deployment_id, git_sha, template_file, timestamp, success, result_message
            FROM deployments
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        records = []
        for row in cursor.fetchall():
            records.append({
                "deployment_id": row[0],
                "git_sha": row[1],
                "template_file": row[2],
                "timestamp": row[3],
                "success": bool(row[4]) if row[4] is not None else None,
                "result_message": row[5]
            })
        
        conn.close()
        return records
    
    def _list_from_json(self, limit: int) -> List[Dict[str, Any]]:
        """List records from JSON files."""
        files = sorted(self.storage_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        records = []
        
        for filepath in files[:limit]:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                records.append({
                    "deployment_id": data["deployment_id"],
                    "git_sha": data.get("git_sha"),
                    "template_file": data.get("template_file"),
                    "timestamp": data["timestamp"],
                    "success": data.get("result", {}).get("success"),
                    "result_message": data.get("result", {}).get("message")
                })
        
        return records
