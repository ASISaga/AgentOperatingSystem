"""
Schema Registry for AgentOperatingSystem

Central governance for message and model version schemas with migration
guidance and backward compatibility tracking.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging
import json
from packaging import version


class SchemaStatus(str, Enum):
    """Status of a schema version"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class CompatibilityMode(str, Enum):
    """Backward compatibility modes"""
    BACKWARD = "backward"  # New schema can read old data
    FORWARD = "forward"  # Old schema can read new data
    FULL = "full"  # Both backward and forward compatible
    NONE = "none"  # No compatibility guarantee


class SchemaVersion:
    """
    Represents a specific version of a schema.
    """

    def __init__(
        self,
        schema_id: str,
        version_str: str,
        schema_definition: Dict[str, Any],
        status: SchemaStatus = SchemaStatus.DRAFT,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.schema_id = schema_id
        self.version_str = version_str
        self.schema_definition = schema_definition
        self.status = status
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.deprecated_at: Optional[datetime] = None
        self.retired_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "schema_id": self.schema_id,
            "version": self.version_str,
            "schema": self.schema_definition,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deprecated_at": self.deprecated_at.isoformat() if self.deprecated_at else None,
            "retired_at": self.retired_at.isoformat() if self.retired_at else None
        }


class SchemaMigration:
    """
    Represents a migration path between schema versions.
    """

    def __init__(
        self,
        from_version: str,
        to_version: str,
        migration_script: Optional[str] = None,
        guidance: Optional[str] = None
    ):
        self.from_version = from_version
        self.to_version = to_version
        self.migration_script = migration_script
        self.guidance = guidance
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "from_version": self.from_version,
            "to_version": self.to_version,
            "migration_script": self.migration_script,
            "guidance": self.guidance,
            "created_at": self.created_at.isoformat()
        }


class SchemaRegistry:
    """
    Central registry for all schemas in the system.

    Provides version management, compatibility tracking, and migration guidance
    for all message and model schemas.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.Extensibility.SchemaRegistry")
        self.schemas: Dict[str, Dict[str, SchemaVersion]] = {}  # schema_id -> version -> SchemaVersion
        self.migrations: Dict[str, List[SchemaMigration]] = {}  # schema_id -> [migrations]
        self.compatibility_mode: Dict[str, CompatibilityMode] = {}  # schema_id -> mode

    def register_schema(
        self,
        schema_id: str,
        version_str: str,
        schema_definition: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        compatibility_mode: CompatibilityMode = CompatibilityMode.BACKWARD
    ) -> bool:
        """
        Register a new schema version.

        Args:
            schema_id: Unique identifier for the schema
            version_str: Semantic version string (e.g., "1.0.0")
            schema_definition: JSON schema definition
            metadata: Optional metadata about this version
            compatibility_mode: Compatibility requirement

        Returns:
            True if registration successful
        """
        try:
            # Initialize schema tracking if needed
            if schema_id not in self.schemas:
                self.schemas[schema_id] = {}
                self.migrations[schema_id] = []
                self.compatibility_mode[schema_id] = compatibility_mode

            # Check if version already exists
            if version_str in self.schemas[schema_id]:
                self.logger.warning(
                    f"Schema version already exists: {schema_id} v{version_str}"
                )
                return False

            # Validate version format
            try:
                version.parse(version_str)
            except Exception as e:
                self.logger.error(f"Invalid version format: {version_str} - {e}")
                return False

            # Create schema version
            schema_version = SchemaVersion(
                schema_id=schema_id,
                version_str=version_str,
                schema_definition=schema_definition,
                status=SchemaStatus.DRAFT,
                metadata=metadata
            )

            self.schemas[schema_id][version_str] = schema_version

            self.logger.info(
                f"Registered schema: {schema_id} v{version_str} "
                f"(mode: {compatibility_mode.value})"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to register schema: {e}")
            return False

    def activate_schema(self, schema_id: str, version_str: str) -> bool:
        """
        Activate a schema version for use.

        Args:
            schema_id: Schema identifier
            version_str: Version to activate

        Returns:
            True if activation successful
        """
        if schema_id not in self.schemas or version_str not in self.schemas[schema_id]:
            self.logger.error(f"Schema not found: {schema_id} v{version_str}")
            return False

        schema_version = self.schemas[schema_id][version_str]
        schema_version.status = SchemaStatus.ACTIVE
        schema_version.updated_at = datetime.utcnow()

        self.logger.info(f"Activated schema: {schema_id} v{version_str}")
        return True

    def deprecate_schema(self, schema_id: str, version_str: str) -> bool:
        """
        Mark a schema version as deprecated.

        Args:
            schema_id: Schema identifier
            version_str: Version to deprecate

        Returns:
            True if deprecation successful
        """
        if schema_id not in self.schemas or version_str not in self.schemas[schema_id]:
            self.logger.error(f"Schema not found: {schema_id} v{version_str}")
            return False

        schema_version = self.schemas[schema_id][version_str]
        schema_version.status = SchemaStatus.DEPRECATED
        schema_version.deprecated_at = datetime.utcnow()
        schema_version.updated_at = datetime.utcnow()

        self.logger.info(f"Deprecated schema: {schema_id} v{version_str}")
        return True

    def retire_schema(self, schema_id: str, version_str: str) -> bool:
        """
        Retire a schema version (no longer supported).

        Args:
            schema_id: Schema identifier
            version_str: Version to retire

        Returns:
            True if retirement successful
        """
        if schema_id not in self.schemas or version_str not in self.schemas[schema_id]:
            self.logger.error(f"Schema not found: {schema_id} v{version_str}")
            return False

        schema_version = self.schemas[schema_id][version_str]
        schema_version.status = SchemaStatus.RETIRED
        schema_version.retired_at = datetime.utcnow()
        schema_version.updated_at = datetime.utcnow()

        self.logger.info(f"Retired schema: {schema_id} v{version_str}")
        return True

    def get_schema(self, schema_id: str, version_str: Optional[str] = None) -> Optional[SchemaVersion]:
        """
        Get a specific schema version, or latest active version if not specified.

        Args:
            schema_id: Schema identifier
            version_str: Optional specific version to retrieve

        Returns:
            SchemaVersion or None if not found
        """
        if schema_id not in self.schemas:
            return None

        if version_str:
            return self.schemas[schema_id].get(version_str)
        else:
            # Get latest active version
            return self.get_latest_version(schema_id, status=SchemaStatus.ACTIVE)

    def get_latest_version(
        self,
        schema_id: str,
        status: Optional[SchemaStatus] = None
    ) -> Optional[SchemaVersion]:
        """
        Get the latest version of a schema, optionally filtered by status.

        Args:
            schema_id: Schema identifier
            status: Optional status filter

        Returns:
            Latest SchemaVersion or None
        """
        if schema_id not in self.schemas:
            return None

        versions = self.schemas[schema_id].values()

        if status:
            versions = [v for v in versions if v.status == status]

        if not versions:
            return None

        # Sort by version number
        sorted_versions = sorted(
            versions,
            key=lambda v: version.parse(v.version_str),
            reverse=True
        )

        return sorted_versions[0] if sorted_versions else None

    def list_versions(self, schema_id: str) -> List[SchemaVersion]:
        """
        List all versions of a schema.

        Args:
            schema_id: Schema identifier

        Returns:
            List of SchemaVersion objects sorted by version
        """
        if schema_id not in self.schemas:
            return []

        versions = list(self.schemas[schema_id].values())

        # Sort by version number
        return sorted(
            versions,
            key=lambda v: version.parse(v.version_str)
        )

    def add_migration(
        self,
        schema_id: str,
        from_version: str,
        to_version: str,
        migration_script: Optional[str] = None,
        guidance: Optional[str] = None
    ) -> bool:
        """
        Add migration path between schema versions.

        Args:
            schema_id: Schema identifier
            from_version: Source version
            to_version: Target version
            migration_script: Optional migration script/code
            guidance: Optional human-readable migration guidance

        Returns:
            True if migration added successfully
        """
        if schema_id not in self.schemas:
            self.logger.error(f"Schema not found: {schema_id}")
            return False

        if from_version not in self.schemas[schema_id]:
            self.logger.error(f"Source version not found: {schema_id} v{from_version}")
            return False

        if to_version not in self.schemas[schema_id]:
            self.logger.error(f"Target version not found: {schema_id} v{to_version}")
            return False

        migration = SchemaMigration(
            from_version=from_version,
            to_version=to_version,
            migration_script=migration_script,
            guidance=guidance
        )

        self.migrations[schema_id].append(migration)

        self.logger.info(
            f"Added migration: {schema_id} v{from_version} -> v{to_version}"
        )

        return True

    def get_migration_path(
        self,
        schema_id: str,
        from_version: str,
        to_version: str
    ) -> Optional[List[SchemaMigration]]:
        """
        Get migration path between two versions.

        Args:
            schema_id: Schema identifier
            from_version: Source version
            to_version: Target version

        Returns:
            List of migrations to execute in order, or None if no path exists
        """
        if schema_id not in self.migrations:
            return None

        migrations = self.migrations[schema_id]

        # Simple direct migration check
        direct_migration = next(
            (m for m in migrations
             if m.from_version == from_version and m.to_version == to_version),
            None
        )

        if direct_migration:
            return [direct_migration]

        # For more complex migration paths, we would implement a graph search
        # This is a simplified version that finds direct migrations only

        return None

    def check_compatibility(
        self,
        schema_id: str,
        version1: str,
        version2: str
    ) -> Dict[str, Any]:
        """
        Check compatibility between two schema versions.

        Args:
            schema_id: Schema identifier
            version1: First version
            version2: Second version

        Returns:
            Compatibility report
        """
        if schema_id not in self.schemas:
            return {"error": f"Schema not found: {schema_id}"}

        if version1 not in self.schemas[schema_id]:
            return {"error": f"Version not found: {version1}"}

        if version2 not in self.schemas[schema_id]:
            return {"error": f"Version not found: {version2}"}

        schema1 = self.schemas[schema_id][version1]
        schema2 = self.schemas[schema_id][version2]

        mode = self.compatibility_mode.get(schema_id, CompatibilityMode.BACKWARD)

        # Basic compatibility check based on schema changes
        # In a real implementation, this would do deep schema comparison

        issues = []
        warnings = []

        # Check required fields
        schema1_required = set(schema1.schema_definition.get("required", []))
        schema2_required = set(schema2.schema_definition.get("required", []))

        if mode in [CompatibilityMode.BACKWARD, CompatibilityMode.FULL]:
            # Check backward compatibility
            new_required = schema2_required - schema1_required
            if new_required:
                issues.append(f"New required fields added: {new_required}")

        if mode in [CompatibilityMode.FORWARD, CompatibilityMode.FULL]:
            # Check forward compatibility
            removed_required = schema1_required - schema2_required
            if removed_required:
                issues.append(f"Required fields removed: {removed_required}")

        is_compatible = len(issues) == 0

        return {
            "schema_id": schema_id,
            "version1": version1,
            "version2": version2,
            "compatibility_mode": mode.value,
            "compatible": is_compatible,
            "issues": issues,
            "warnings": warnings
        }

    def export_schema(self, schema_id: str, version_str: str) -> Optional[str]:
        """
        Export a schema version as JSON.

        Args:
            schema_id: Schema identifier
            version_str: Version to export

        Returns:
            JSON string or None
        """
        schema_version = self.get_schema(schema_id, version_str)

        if not schema_version:
            return None

        return json.dumps(schema_version.to_dict(), indent=2)

    def get_registry_summary(self) -> Dict[str, Any]:
        """
        Get summary of all schemas in the registry.

        Returns:
            Summary report
        """
        total_schemas = len(self.schemas)
        total_versions = sum(len(versions) for versions in self.schemas.values())

        status_counts = {status.value: 0 for status in SchemaStatus}

        for schema_versions in self.schemas.values():
            for schema_version in schema_versions.values():
                status_counts[schema_version.status.value] += 1

        return {
            "total_schemas": total_schemas,
            "total_versions": total_versions,
            "status_counts": status_counts,
            "schemas": list(self.schemas.keys()),
            "generated_at": datetime.utcnow().isoformat()
        }
