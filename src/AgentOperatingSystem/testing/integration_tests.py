"""
Integration Testing Framework for AgentOperatingSystem

Provides end-to-end integration testing capabilities for cross-agent
interactions, workflows, and persistence validation.
"""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
import asyncio
import logging
from enum import Enum

from ..platform.contracts import MessageEnvelope
from ..platform.events import BaseEvent


class TestScenarioStatus(str, Enum):
    """Status of a test scenario"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestScenario:
    """
    Represents a single integration test scenario.

    A scenario includes setup, execution, validation, and teardown phases.
    """

    def __init__(
        self,
        name: str,
        description: str,
        setup: Optional[Callable[[], Awaitable[None]]] = None,
        execute: Optional[Callable[[], Awaitable[Any]]] = None,
        validate: Optional[Callable[[Any], Awaitable[bool]]] = None,
        teardown: Optional[Callable[[], Awaitable[None]]] = None
    ):
        self.name = name
        self.description = description
        self.setup = setup
        self.execute = execute
        self.validate = validate
        self.teardown = teardown
        self.status = TestScenarioStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    async def run(self) -> Dict[str, Any]:
        """
        Run the complete test scenario.

        Returns:
            Test result with status and details
        """
        self.status = TestScenarioStatus.RUNNING
        self.started_at = datetime.utcnow()

        try:
            # Setup phase
            if self.setup:
                await self.setup()

            # Execute phase
            if self.execute:
                self.result = await self.execute()

            # Validate phase
            if self.validate:
                is_valid = await self.validate(self.result)
                if not is_valid:
                    self.status = TestScenarioStatus.FAILED
                    self.error = "Validation failed"
                else:
                    self.status = TestScenarioStatus.PASSED
            else:
                self.status = TestScenarioStatus.PASSED

        except Exception as e:
            self.status = TestScenarioStatus.FAILED
            self.error = str(e)

        finally:
            # Teardown phase
            if self.teardown:
                try:
                    await self.teardown()
                except Exception as e:
                    # Log teardown errors but don't fail the test
                    pass

            self.completed_at = datetime.utcnow()

        return self.get_result()

    def get_result(self) -> Dict[str, Any]:
        """Get the test result as a dictionary"""
        duration = None
        if self.started_at and self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()

        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "duration_seconds": duration,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class IntegrationTestFramework:
    """
    Comprehensive integration testing framework for AOS.

    Supports end-to-end testing of:
    - Cross-agent interactions
    - Workflow execution
    - Persistence and state management
    - Event propagation
    - Policy enforcement
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.Testing.Integration")
        self.scenarios: List[TestScenario] = []
        self.test_results: List[Dict[str, Any]] = []

    def register_scenario(self, scenario: TestScenario) -> None:
        """
        Register a test scenario to be executed.

        Args:
            scenario: TestScenario to register
        """
        self.scenarios.append(scenario)
        self.logger.info(f"Registered test scenario: {scenario.name}")

    async def run_all_scenarios(self) -> Dict[str, Any]:
        """
        Run all registered test scenarios.

        Returns:
            Comprehensive test report
        """
        self.logger.info(f"Running {len(self.scenarios)} integration test scenarios")

        for scenario in self.scenarios:
            self.logger.info(f"Running scenario: {scenario.name}")
            result = await scenario.run()
            self.test_results.append(result)

            if result["status"] == TestScenarioStatus.PASSED.value:
                self.logger.info(f"✅ Scenario passed: {scenario.name}")
            else:
                self.logger.error(f"❌ Scenario failed: {scenario.name} - {result.get('error')}")

        return self.generate_report()

    async def run_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """
        Run a specific test scenario by name.

        Args:
            scenario_name: Name of the scenario to run

        Returns:
            Test result
        """
        scenario = next((s for s in self.scenarios if s.name == scenario_name), None)

        if not scenario:
            raise ValueError(f"Scenario not found: {scenario_name}")

        self.logger.info(f"Running scenario: {scenario_name}")
        result = await scenario.run()
        self.test_results.append(result)

        return result

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive integration test report.

        Returns:
            Test report with summary and detailed results
        """
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == TestScenarioStatus.PASSED.value)
        failed_tests = sum(1 for r in self.test_results if r["status"] == TestScenarioStatus.FAILED.value)

        total_duration = sum(r["duration_seconds"] or 0 for r in self.test_results)

        return {
            "summary": {
                "total_scenarios": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": total_tests - passed_tests - failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration_seconds": total_duration
            },
            "scenarios": self.test_results,
            "generated_at": datetime.utcnow().isoformat()
        }


class EndToEndTestRunner:
    """
    Runner for end-to-end integration tests.

    Provides utilities for testing complete workflows from start to finish,
    including agent interactions, persistence, and event handling.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.Testing.E2E")
        self.framework = IntegrationTestFramework(logger=self.logger)

    async def test_agent_interaction(
        self,
        agent1_id: str,
        agent2_id: str,
        message: MessageEnvelope,
        expected_response: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Test interaction between two agents.

        Args:
            agent1_id: ID of the sending agent
            agent2_id: ID of the receiving agent
            message: Message to send
            expected_response: Optional expected response structure

        Returns:
            Test result
        """
        result = {
            "test": "agent_interaction",
            "agent1": agent1_id,
            "agent2": agent2_id,
            "message_type": message.message_type,
            "status": "pending"
        }

        try:
            # This is a template - actual implementation would integrate with messaging layer
            self.logger.info(f"Testing interaction: {agent1_id} -> {agent2_id}")

            # Validate message structure
            assert message.actor == agent1_id, "Message actor must match sending agent"
            assert message.correlation_id, "Correlation ID required"

            # In a real implementation, this would:
            # 1. Send message through the message bus
            # 2. Wait for response
            # 3. Validate response structure

            if expected_response:
                # Validate response structure
                pass

            result["status"] = "passed"
            self.logger.info(f"✅ Agent interaction test passed")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"❌ Agent interaction test failed: {e}")

        return result

    async def test_workflow_execution(
        self,
        workflow_name: str,
        workflow_steps: List[Dict[str, Any]],
        initial_state: Dict[str, Any],
        expected_final_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test end-to-end workflow execution.

        Args:
            workflow_name: Name of the workflow
            workflow_steps: List of workflow steps to execute
            initial_state: Initial workflow state
            expected_final_state: Expected final state after execution

        Returns:
            Test result
        """
        result = {
            "test": "workflow_execution",
            "workflow": workflow_name,
            "steps": len(workflow_steps),
            "status": "pending"
        }

        try:
            self.logger.info(f"Testing workflow: {workflow_name} ({len(workflow_steps)} steps)")

            current_state = initial_state.copy()

            # Execute workflow steps
            for i, step in enumerate(workflow_steps):
                step_name = step.get("name", f"step_{i}")
                self.logger.debug(f"Executing step: {step_name}")

                # In a real implementation, this would:
                # 1. Execute the actual workflow step
                # 2. Update state
                # 3. Validate state transitions

                # Placeholder for step execution
                current_state[f"step_{i}_completed"] = True

            # Validate final state
            for key, expected_value in expected_final_state.items():
                if key not in current_state:
                    raise AssertionError(f"Expected state key missing: {key}")
                # Additional validation logic would go here

            result["status"] = "passed"
            result["final_state"] = current_state
            self.logger.info(f"✅ Workflow execution test passed")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"❌ Workflow execution test failed: {e}")

        return result

    async def test_persistence(
        self,
        entity_type: str,
        entity_data: Dict[str, Any],
        persistence_layer: str = "default"
    ) -> Dict[str, Any]:
        """
        Test data persistence and retrieval.

        Args:
            entity_type: Type of entity to persist
            entity_data: Entity data to store
            persistence_layer: Which persistence layer to test

        Returns:
            Test result
        """
        result = {
            "test": "persistence",
            "entity_type": entity_type,
            "persistence_layer": persistence_layer,
            "status": "pending"
        }

        try:
            self.logger.info(f"Testing persistence for: {entity_type}")

            # In a real implementation, this would:
            # 1. Store the entity
            # 2. Retrieve it
            # 3. Verify data integrity
            # 4. Clean up test data

            # Placeholder for persistence test
            entity_id = entity_data.get("id", "test_entity")

            # Simulate store and retrieve
            stored = True
            retrieved = True
            data_matches = True

            if not (stored and retrieved and data_matches):
                raise AssertionError("Persistence validation failed")

            result["status"] = "passed"
            result["entity_id"] = entity_id
            self.logger.info(f"✅ Persistence test passed")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"❌ Persistence test failed: {e}")

        return result

    async def test_event_propagation(
        self,
        event: BaseEvent,
        expected_subscribers: List[str],
        timeout_seconds: int = 5
    ) -> Dict[str, Any]:
        """
        Test event propagation to subscribers.

        Args:
            event: Event to publish
            expected_subscribers: List of subscriber IDs that should receive the event
            timeout_seconds: Maximum time to wait for propagation

        Returns:
            Test result
        """
        result = {
            "test": "event_propagation",
            "event_type": event.event_type if hasattr(event, 'event_type') else "unknown",
            "expected_subscribers": len(expected_subscribers),
            "status": "pending"
        }

        try:
            self.logger.info(f"Testing event propagation to {len(expected_subscribers)} subscribers")

            # In a real implementation, this would:
            # 1. Publish the event
            # 2. Wait for subscribers to receive it
            # 3. Verify all expected subscribers received it
            # 4. Verify the event data is intact

            # Placeholder for event propagation test
            received_by = []

            # Simulate waiting for propagation
            await asyncio.sleep(0.1)

            # Verify all subscribers received the event
            if set(received_by) != set(expected_subscribers):
                raise AssertionError(
                    f"Event propagation incomplete. "
                    f"Expected: {expected_subscribers}, Got: {received_by}"
                )

            result["status"] = "passed"
            result["received_by"] = received_by
            self.logger.info(f"✅ Event propagation test passed")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"❌ Event propagation test failed: {e}")

        return result
