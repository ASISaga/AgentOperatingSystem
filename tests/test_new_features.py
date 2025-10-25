"""
Direct tests for Testing Infrastructure modules

Tests the testing framework features by directly importing module files.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'AgentOperatingSystem'))

import asyncio
from datetime import datetime

# Import directly from module files to avoid __init__ issues
from testing.contract_tests import MessageSchemaValidator, ContractTestFramework
from testing.integration_tests import IntegrationTestFramework, TestScenario
from testing.chaos_tests import FailureSimulator, ChaosTestFramework, FailureType
from testing.audit_tests import DecisionPathTester, AuditCompletenessValidator


def test_message_schema_validator_registration():
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
    print("✅ Schema registration test passed")


def test_message_validation():
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
    print("✅ Message validation test passed")


async def test_scenario_registration():
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
    print("✅ Scenario registration test passed")


async def test_inject_network_delay():
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
    print("✅ Network delay injection test passed")
    
    # Wait for cleanup
    await asyncio.sleep(1.1)
    
    assert not simulator.is_failure_active(failure_id)
    print("✅ Failure cleanup test passed")


async def test_complete_decision_path():
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
    print("✅ Complete decision path test passed")


async def test_incomplete_decision_path():
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
    print("✅ Incomplete decision path test passed")


if __name__ == "__main__":
    # Run tests manually
    print("Running Testing Infrastructure Tests\n")
    
    print("1. Testing Schema Validator")
    test_message_schema_validator_registration()
    test_message_validation()
    
    print("\n2. Testing Integration Framework")
    asyncio.run(test_scenario_registration())
    
    print("\n3. Testing Failure Simulator")
    asyncio.run(test_inject_network_delay())
    
    print("\n4. Testing Decision Path Validator")
    asyncio.run(test_complete_decision_path())
    asyncio.run(test_incomplete_decision_path())
    
    print("\n✅ All tests passed!")
