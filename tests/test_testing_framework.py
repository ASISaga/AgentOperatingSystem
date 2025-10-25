"""
Tests for the Testing Infrastructure

Tests the contract tests, integration tests, chaos tests, and audit tests frameworks.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import asyncio
from datetime import datetime

from AgentOperatingSystem.testing import (
    ContractTestFramework,
    MessageSchemaValidator,
    IntegrationTestFramework,
    TestScenario,
    ChaosTestFramework,
    FailureSimulator,
    FailureType,
    AuditCompletenessValidator,
    DecisionPathTester
)


class TestMessageSchemaValidator:
    """Test the MessageSchemaValidator"""
    
    def test_register_and_validate_schema(self):
        """Test schema registration and validation"""
        validator = MessageSchemaValidator()
        
        # Register a schema
        schema = {
            "type": "object",
            "properties": {
                "decision_id": {"type": "string"},
                "status": {"type": "string"}
            },
            "required": ["decision_id", "status"]
        }
        
        validator.register_schema("DecisionRequested", "1.0.0", schema)
        
        # Valid message
        valid_message = {
            "decision_id": "dec_123",
            "status": "pending"
        }
        assert validator.validate_message("DecisionRequested", "1.0.0", valid_message)
        
        # Invalid message (missing required field)
        invalid_message = {
            "decision_id": "dec_123"
        }
        with pytest.raises(Exception):
            validator.validate_message("DecisionRequested", "1.0.0", invalid_message)
    
    def test_backward_compatibility(self):
        """Test backward compatibility checking"""
        validator = MessageSchemaValidator()
        
        # Version 1.0.0
        schema_v1 = {
            "type": "object",
            "properties": {
                "field1": {"type": "string"}
            },
            "required": ["field1"]
        }
        
        # Version 2.0.0 - backward compatible (added optional field)
        schema_v2 = {
            "type": "object",
            "properties": {
                "field1": {"type": "string"},
                "field2": {"type": "string"}
            },
            "required": ["field1"]
        }
        
        validator.register_schema("TestMessage", "1.0.0", schema_v1)
        validator.register_schema("TestMessage", "2.0.0", schema_v2)
        
        result = validator.check_backward_compatibility("TestMessage", "1.0.0", "2.0.0")
        assert result["compatible"] is True


class TestContractTestFramework:
    """Test the ContractTestFramework"""
    
    def test_message_envelope_contract(self):
        """Test message envelope validation"""
        framework = ContractTestFramework()
        
        valid_envelope = {
            "message_type": "command",
            "correlation_id": "corr_123",
            "actor": "agent_1",
            "scope": "test",
            "payload": {"data": "value"}
        }
        
        assert framework.test_message_envelope_contract(valid_envelope)


class TestIntegrationTestFramework:
    """Test the IntegrationTestFramework"""
    
    @pytest.mark.asyncio
    async def test_scenario_execution(self):
        """Test scenario execution"""
        framework = IntegrationTestFramework()
        
        test_executed = False
        
        async def setup():
            pass
        
        async def execute():
            nonlocal test_executed
            test_executed = True
            return {"result": "success"}
        
        async def validate(result):
            return result["result"] == "success"
        
        scenario = TestScenario(
            name="test_scenario",
            description="Test scenario description",
            setup=setup,
            execute=execute,
            validate=validate
        )
        
        framework.register_scenario(scenario)
        result = await framework.run_all_scenarios()
        
        assert test_executed
        assert result["summary"]["passed"] == 1
        assert result["summary"]["failed"] == 0


class TestChaosTestFramework:
    """Test the ChaosTestFramework"""
    
    @pytest.mark.asyncio
    async def test_failure_injection(self):
        """Test failure injection"""
        simulator = FailureSimulator()
        
        failure_id = await simulator.inject_network_delay(
            min_delay_ms=100,
            max_delay_ms=200,
            duration_seconds=1
        )
        
        assert simulator.is_failure_active(failure_id)
        assert len(simulator.get_active_failures()) == 1
        
        # Wait for failure to complete
        await asyncio.sleep(1.1)
        
        assert not simulator.is_failure_active(failure_id)
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test graceful degradation testing"""
        framework = ChaosTestFramework()
        
        async def test_function():
            return {"status": "fallback_activated"}
        
        result = await framework.test_graceful_degradation(
            component="test_component",
            failure_scenario=FailureType.NETWORK_DELAY,
            test_function=test_function,
            expected_behavior="fallback"
        )
        
        assert result["status"] == "passed"


class TestAuditCompletenessValidator:
    """Test the AuditCompletenessValidator"""
    
    @pytest.mark.asyncio
    async def test_decision_path_completeness(self):
        """Test decision path completeness validation"""
        tester = DecisionPathTester()
        
        # Complete decision path
        complete_artifacts = {
            "audit_entry",
            "decision_rationale",
            "compliance_assertion",
            "risk_assessment"
        }
        
        result = await tester.test_decision_path(
            decision_name="test_decision",
            decision_data={"id": "dec_123"},
            artifacts_produced=complete_artifacts
        )
        
        assert result["status"] == "passed"
        
        # Incomplete decision path
        incomplete_artifacts = {
            "audit_entry",
            "decision_rationale"
        }
        
        result = await tester.test_decision_path(
            decision_name="incomplete_decision",
            decision_data={"id": "dec_456"},
            artifacts_produced=incomplete_artifacts
        )
        
        assert result["status"] == "failed"
        assert "missing_artifacts" in result
    
    @pytest.mark.asyncio
    async def test_audit_trail_integrity(self):
        """Test audit trail integrity validation"""
        validator = AuditCompletenessValidator()
        
        # Valid audit trail
        audit_entries = [
            {
                "timestamp": "2025-01-01T10:00:00",
                "actor": "agent_1",
                "action": "decision_requested"
            },
            {
                "timestamp": "2025-01-01T10:01:00",
                "actor": "agent_1",
                "action": "decision_approved"
            }
        ]
        
        result = await validator.validate_audit_trail_integrity(audit_entries)
        
        assert result["status"] == "passed"
        assert result["issues"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
