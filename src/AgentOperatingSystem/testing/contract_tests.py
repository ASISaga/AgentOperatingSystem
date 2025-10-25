"""
Contract Testing Framework for AgentOperatingSystem

Validates message schemas and topic envelopes across versions to ensure
backward compatibility and proper evolution of contracts.
"""

from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import jsonschema
from jsonschema import validate, ValidationError
from pydantic import BaseModel, ValidationError as PydanticValidationError
import logging

from ..platform.contracts import MessageEnvelope, CommandContract, QueryContract, EventContract
from ..platform.events import BaseEvent


class MessageSchemaValidator:
    """
    Validates message schemas across versions to ensure compatibility.
    
    Ensures that message schemas evolve in a backward-compatible way and
    follow versioning best practices.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.Testing.SchemaValidator")
        self.registered_schemas: Dict[str, Dict[str, Any]] = {}
        self.version_history: Dict[str, List[str]] = {}
    
    def register_schema(self, message_type: str, version: str, schema: Dict[str, Any]) -> None:
        """
        Register a message schema for a specific version.
        
        Args:
            message_type: Type of message (e.g., "DecisionRequested")
            version: Semantic version (e.g., "1.0.0")
            schema: JSON schema definition
        """
        key = f"{message_type}:{version}"
        self.registered_schemas[key] = schema
        
        if message_type not in self.version_history:
            self.version_history[message_type] = []
        if version not in self.version_history[message_type]:
            self.version_history[message_type].append(version)
            self.version_history[message_type].sort()
        
        self.logger.info(f"Registered schema: {key}")
    
    def validate_message(self, message_type: str, version: str, payload: Dict[str, Any]) -> bool:
        """
        Validate a message payload against its registered schema.
        
        Args:
            message_type: Type of message
            version: Schema version to validate against
            payload: Message payload to validate
            
        Returns:
            True if valid, raises ValidationError otherwise
        """
        key = f"{message_type}:{version}"
        
        if key not in self.registered_schemas:
            raise ValueError(f"Schema not registered: {key}")
        
        schema = self.registered_schemas[key]
        
        try:
            validate(instance=payload, schema=schema)
            self.logger.debug(f"Message validated successfully: {key}")
            return True
        except ValidationError as e:
            self.logger.error(f"Schema validation failed for {key}: {e}")
            raise
    
    def check_backward_compatibility(self, message_type: str, old_version: str, new_version: str) -> Dict[str, Any]:
        """
        Check if a new schema version is backward compatible with an old version.
        
        Backward compatibility means:
        - No required fields are removed
        - No field types are changed incompatibly
        - Only additive changes (new optional fields)
        
        Args:
            message_type: Type of message
            old_version: Previous schema version
            new_version: New schema version
            
        Returns:
            Dict with compatibility report
        """
        old_key = f"{message_type}:{old_version}"
        new_key = f"{message_type}:{new_version}"
        
        if old_key not in self.registered_schemas:
            raise ValueError(f"Old schema not registered: {old_key}")
        if new_key not in self.registered_schemas:
            raise ValueError(f"New schema not registered: {new_key}")
        
        old_schema = self.registered_schemas[old_key]
        new_schema = self.registered_schemas[new_key]
        
        issues = []
        warnings = []
        
        # Check required fields
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))
        
        removed_required = old_required - new_required
        if removed_required:
            issues.append(f"Required fields removed: {removed_required}")
        
        added_required = new_required - old_required
        if added_required:
            issues.append(f"New required fields added (breaks compatibility): {added_required}")
        
        # Check field types
        old_properties = old_schema.get("properties", {})
        new_properties = new_schema.get("properties", {})
        
        for field_name in old_properties:
            if field_name not in new_properties:
                warnings.append(f"Field removed: {field_name}")
            else:
                old_type = old_properties[field_name].get("type")
                new_type = new_properties[field_name].get("type")
                if old_type != new_type:
                    issues.append(f"Field type changed: {field_name} ({old_type} -> {new_type})")
        
        is_compatible = len(issues) == 0
        
        return {
            "compatible": is_compatible,
            "old_version": old_version,
            "new_version": new_version,
            "issues": issues,
            "warnings": warnings
        }


class ContractTestFramework:
    """
    Comprehensive contract testing framework for AgentOperatingSystem.
    
    Tests message contracts, event schemas, and ensures proper versioning
    and backward compatibility across the platform.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.Testing.ContractTests")
        self.schema_validator = MessageSchemaValidator(logger=self.logger)
        self.test_results: List[Dict[str, Any]] = []
    
    def test_message_envelope_contract(self, envelope_data: Dict[str, Any]) -> bool:
        """
        Test that a message envelope conforms to the MessageEnvelope contract.
        
        Args:
            envelope_data: Raw envelope data to test
            
        Returns:
            True if valid
        """
        try:
            envelope = MessageEnvelope(**envelope_data)
            
            # Validate required fields
            assert envelope.message_type, "message_type is required"
            assert envelope.correlation_id, "correlation_id is required"
            assert envelope.actor, "actor is required"
            assert envelope.scope, "scope is required"
            assert envelope.payload, "payload is required"
            
            # Validate types
            assert isinstance(envelope.timestamp, datetime), "timestamp must be datetime"
            assert isinstance(envelope.attributes, dict), "attributes must be dict"
            assert isinstance(envelope.payload, dict), "payload must be dict"
            
            self.logger.info("Message envelope contract test passed")
            self.test_results.append({
                "test": "message_envelope_contract",
                "status": "passed",
                "timestamp": datetime.utcnow().isoformat()
            })
            return True
            
        except (PydanticValidationError, AssertionError) as e:
            self.logger.error(f"Message envelope contract test failed: {e}")
            self.test_results.append({
                "test": "message_envelope_contract",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            raise
    
    def test_event_schema_versioning(self, event_type: str, versions: List[str]) -> Dict[str, Any]:
        """
        Test that event schemas are properly versioned and compatible.
        
        Args:
            event_type: Type of event to test
            versions: List of versions to test compatibility between
            
        Returns:
            Compatibility report
        """
        results = {
            "event_type": event_type,
            "versions_tested": versions,
            "compatibility_checks": []
        }
        
        # Test pairwise compatibility
        for i in range(len(versions) - 1):
            old_version = versions[i]
            new_version = versions[i + 1]
            
            try:
                compatibility = self.schema_validator.check_backward_compatibility(
                    event_type, old_version, new_version
                )
                results["compatibility_checks"].append(compatibility)
                
                if not compatibility["compatible"]:
                    self.logger.warning(
                        f"Backward compatibility issue: {event_type} "
                        f"{old_version} -> {new_version}"
                    )
            except Exception as e:
                self.logger.error(f"Compatibility check failed: {e}")
                results["compatibility_checks"].append({
                    "old_version": old_version,
                    "new_version": new_version,
                    "error": str(e)
                })
        
        self.test_results.append({
            "test": "event_schema_versioning",
            "status": "completed",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return results
    
    def test_command_contract(self, command_data: Dict[str, Any]) -> bool:
        """
        Test that a command follows the CommandContract specification.
        
        Args:
            command_data: Raw command data to test
            
        Returns:
            True if valid
        """
        try:
            from ..platform.contracts import CommandContract
            
            command = CommandContract(**command_data)
            
            # Validate command-specific requirements
            assert command.intent, "intent is required"
            assert command.preconditions is not None, "preconditions must be specified"
            assert command.expected_outcomes, "expected_outcomes is required"
            
            self.logger.info(f"Command contract test passed: {command.intent}")
            self.test_results.append({
                "test": "command_contract",
                "command": command.intent,
                "status": "passed",
                "timestamp": datetime.utcnow().isoformat()
            })
            return True
            
        except (PydanticValidationError, AssertionError) as e:
            self.logger.error(f"Command contract test failed: {e}")
            self.test_results.append({
                "test": "command_contract",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            raise
    
    def test_query_contract(self, query_data: Dict[str, Any]) -> bool:
        """
        Test that a query follows the QueryContract specification.
        
        Args:
            query_data: Raw query data to test
            
        Returns:
            True if valid
        """
        try:
            from ..platform.contracts import QueryContract
            
            query = QueryContract(**query_data)
            
            # Validate query-specific requirements
            assert query.selectors, "selectors is required"
            
            self.logger.info("Query contract test passed")
            self.test_results.append({
                "test": "query_contract",
                "status": "passed",
                "timestamp": datetime.utcnow().isoformat()
            })
            return True
            
        except (PydanticValidationError, AssertionError) as e:
            self.logger.error(f"Query contract test failed: {e}")
            self.test_results.append({
                "test": "query_contract",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            raise
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive test report.
        
        Returns:
            Test report with summary and detailed results
        """
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get("status") == "passed")
        failed_tests = sum(1 for r in self.test_results if r.get("status") == "failed")
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "detailed_results": self.test_results,
            "generated_at": datetime.utcnow().isoformat()
        }
