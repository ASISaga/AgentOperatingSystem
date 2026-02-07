"""
Tests for Testing Infrastructure modules.
"""
import asyncio

import pytest

from AgentOperatingSystem.testing.contract_tests import MessageSchemaValidator, ContractTestFramework
from AgentOperatingSystem.testing.integration_tests import IntegrationTestFramework, TestScenario
from AgentOperatingSystem.testing.chaos_tests import FailureSimulator, ChaosTestFramework, FailureType
from AgentOperatingSystem.testing.audit_tests import DecisionPathTester, AuditCompletenessValidator


class TestMessageSchemaValidator:
    """Tests for contract schema validation."""

    def test_schema_registration(self):
        validator = MessageSchemaValidator()
        schema = {
            "type": "object",
            "properties": {
                "decision_id": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": ["decision_id", "status"],
        }
        validator.register_schema("DecisionRequested", "1.0.0", schema)
        assert "DecisionRequested:1.0.0" in validator.registered_schemas
        assert "DecisionRequested" in validator.version_history

    def test_message_validation(self):
        validator = MessageSchemaValidator()
        schema = {
            "type": "object",
            "properties": {
                "decision_id": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": ["decision_id", "status"],
        }
        validator.register_schema("DecisionRequested", "1.0.0", schema)
        valid_message = {"decision_id": "dec_123", "status": "pending"}
        assert validator.validate_message("DecisionRequested", "1.0.0", valid_message)


class TestIntegrationFramework:
    """Tests for the integration test framework."""

    async def test_scenario_registration(self):
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
            validate=validate,
        )
        framework.register_scenario(scenario)
        assert len(framework.scenarios) == 1
        assert framework.scenarios[0].name == "test_scenario"


class TestFailureSimulator:
    """Tests for chaos testing failure simulator."""

    async def test_inject_network_delay(self):
        simulator = FailureSimulator()
        failure_id = await simulator.inject_network_delay(
            min_delay_ms=100, max_delay_ms=200, duration_seconds=1
        )
        assert failure_id is not None
        assert simulator.is_failure_active(failure_id)
        assert len(simulator.get_active_failures()) == 1


class TestDecisionPathTester:
    """Tests for audit decision path testing."""

    async def test_complete_decision_path(self):
        tester = DecisionPathTester()
        complete_artifacts = {
            "audit_entry",
            "decision_rationale",
            "compliance_assertion",
            "risk_assessment",
        }
        result = await tester.test_decision_path(
            decision_name="test_decision",
            decision_data={"id": "dec_123"},
            artifacts_produced=complete_artifacts,
        )
        assert result["status"] == "passed"

    async def test_incomplete_decision_path(self):
        tester = DecisionPathTester()
        incomplete_artifacts = {"audit_entry", "decision_rationale"}
        result = await tester.test_decision_path(
            decision_name="incomplete_decision",
            decision_data={"id": "dec_456"},
            artifacts_produced=incomplete_artifacts,
        )
        assert result["status"] == "failed"
        assert "missing_artifacts" in result
        assert len(result["missing_artifacts"]) == 2
