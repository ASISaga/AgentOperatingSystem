"""
Standalone tests for Testing Infrastructure

Tests the testing framework features in isolation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import asyncio
from datetime import datetime

# Import only the testing module to avoid other module issues
from AgentOperatingSystem.testing.contract_tests import MessageSchemaValidator, ContractTestFramework
from AgentOperatingSystem.testing.integration_tests import IntegrationTestFramework, TestScenario
from AgentOperatingSystem.testing.chaos_tests import FailureSimulator, ChaosTestFramework, FailureType
from AgentOperatingSystem.testing.audit_tests import DecisionPathTester, AuditCompletenessValidator


class TestMessageSchemaValidator:
    """Test the MessageSchemaValidator"""
    
    def test_register_schema(self):
        """Test schema registration"""
        validator = MessageSchemaValidator()
        
        schema = {
            "type": "object",
            "properties": {
                "decision_id": {"type": "string"},
                "status": {"type": "string"}
            },
            "required": ["decision_id", "status"]
        }
        
        validator.register_schema("DecisionRequested", "1.0.0", schema)
        
        # Check that schema was registered
        assert "DecisionRequested:1.0.0" in validator.registered_schemas
        assert "DecisionRequested" in validator.version_history
    
    def test_validate_message(self):
        """Test message validation"""
        validator = MessageSchemaValidator()
        
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


class TestIntegrationFramework:
    """Test the IntegrationTestFramework"""
    
    @pytest.mark.asyncio
    async def test_scenario_registration(self):
        """Test scenario registration"""
        framework = IntegrationTestFramework()
        
        async def setup():
            pass
        
        async def execute():
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
        
        assert len(framework.scenarios) == 1
        assert framework.scenarios[0].name == "test_scenario"


class TestFailureSimulator:
    """Test the FailureSimulator"""
    
    @pytest.mark.asyncio
    async def test_inject_network_delay(self):
        """Test network delay injection"""
        simulator = FailureSimulator()
        
        failure_id = await simulator.inject_network_delay(
            min_delay_ms=100,
            max_delay_ms=200,
            duration_seconds=1
        )
        
        assert failure_id is not None
        assert simulator.is_failure_active(failure_id)
        assert len(simulator.get_active_failures()) == 1
        
        # Wait for cleanup
        await asyncio.sleep(1.1)
        
        assert not simulator.is_failure_active(failure_id)
    
    @pytest.mark.asyncio
    async def test_should_fail(self):
        """Test failure probability"""
        simulator = FailureSimulator()
        
        await simulator.inject_policy_engine_failure(failure_rate=1.0, duration_seconds=1)
        
        # Should always fail with rate = 1.0
        assert simulator.should_fail(FailureType.POLICY_ENGINE_FAILURE)


class TestDecisionPathTester:
    """Test the DecisionPathTester"""
    
    @pytest.mark.asyncio
    async def test_complete_decision_path(self):
        """Test decision path with all required artifacts"""
        tester = DecisionPathTester()
        
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
        assert "missing_artifacts" not in result
    
    @pytest.mark.asyncio
    async def test_incomplete_decision_path(self):
        """Test decision path missing artifacts"""
        tester = DecisionPathTester()
        
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
        assert len(result["missing_artifacts"]) == 2  # Missing 2 artifacts


class TestAuditCompletenessValidator:
    """Test the AuditCompletenessValidator"""
    
    @pytest.mark.asyncio
    async def test_validate_audit_trail_integrity(self):
        """Test audit trail integrity validation"""
        validator = AuditCompletenessValidator()
        
        # Valid chronological audit trail
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
        assert len(result["issues"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
