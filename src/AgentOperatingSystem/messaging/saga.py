"""
Saga Orchestration and Choreography

Provides distributed transaction management using the Saga pattern.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class SagaStatus(Enum):
    """Status of a saga execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaOrchestrator:
    """
    Orchestrates distributed sagas with automatic compensation.

    Features:
    - Multi-step distributed transactions
    - Automatic compensation on failure
    - Saga state persistence
    - Timeout handling
    """

    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.logger = logging.getLogger("AOS.SagaOrchestrator")
        self.sagas = {}
        self.executions = {}

    async def define_saga(
        self,
        saga_id: str,
        steps: List[Dict[str, Any]]
    ):
        """
        Define a saga with steps and compensations.

        Args:
            saga_id: Unique saga identifier
            steps: List of saga steps with compensations
        """
        self.logger.info(f"Defining saga: {saga_id}")

        saga = {
            "saga_id": saga_id,
            "steps": steps,
            "defined_at": datetime.utcnow()
        }

        self.sagas[saga_id] = saga

        # Validate saga definition
        await self._validate_saga(saga)

    async def execute(
        self,
        saga_id: str,
        input_data: Dict[str, Any],
        timeout: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """
        Execute a saga.

        Args:
            saga_id: Saga to execute
            input_data: Input data for saga
            timeout: Optional execution timeout

        Returns:
            Execution result
        """
        saga = self.sagas.get(saga_id)
        if not saga:
            raise ValueError(f"Saga {saga_id} not found")

        execution_id = f"{saga_id}_{datetime.utcnow().timestamp()}"

        self.logger.info(f"Executing saga {saga_id}, execution: {execution_id}")

        execution = {
            "execution_id": execution_id,
            "saga_id": saga_id,
            "status": SagaStatus.PENDING,
            "input_data": input_data,
            "completed_steps": [],
            "compensated_steps": [],
            "start_time": datetime.utcnow(),
            "end_time": None,
            "error": None
        }

        self.executions[execution_id] = execution

        try:
            execution["status"] = SagaStatus.RUNNING

            # Execute each step
            for step in saga["steps"]:
                await self._execute_step(execution, step, input_data)

                # Check timeout
                if timeout:
                    elapsed = datetime.utcnow() - execution["start_time"]
                    if elapsed > timeout:
                        raise TimeoutError(f"Saga execution timed out after {timeout}")

            # All steps completed successfully
            execution["status"] = SagaStatus.COMPLETED
            execution["end_time"] = datetime.utcnow()

            self.logger.info(f"Saga {saga_id} completed successfully")

            return {
                "status": "completed",
                "execution_id": execution_id,
                "completed_steps": execution["completed_steps"]
            }

        except Exception as e:
            self.logger.error(f"Saga {saga_id} failed: {e}")

            # Execute compensation
            execution["status"] = SagaStatus.COMPENSATING
            execution["error"] = str(e)

            await self._compensate(execution, saga)

            execution["status"] = SagaStatus.COMPENSATED
            execution["end_time"] = datetime.utcnow()

            return {
                "status": "failed",
                "execution_id": execution_id,
                "error": str(e),
                "compensated_steps": execution["compensated_steps"]
            }

    async def _execute_step(
        self,
        execution: Dict[str, Any],
        step: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """Execute a single saga step"""
        step_name = step["step"]
        service = step["service"]

        self.logger.debug(f"Executing step: {step_name} on service: {service}")

        # Send message to service to execute step
        # In real implementation, would call actual service
        # For now, simulate success

        result = {
            "step": step_name,
            "service": service,
            "completed_at": datetime.utcnow(),
            "status": "success"
        }

        execution["completed_steps"].append(result)

    async def _compensate(
        self,
        execution: Dict[str, Any],
        saga: Dict[str, Any]
    ):
        """
        Compensate completed steps in reverse order.

        Args:
            execution: Execution to compensate
            saga: Saga definition
        """
        self.logger.info(f"Compensating saga execution {execution['execution_id']}")

        # Compensate in reverse order
        completed_steps = execution["completed_steps"]
        steps = saga["steps"]

        for completed_step in reversed(completed_steps):
            step_name = completed_step["step"]

            # Find compensation action
            step_def = next(
                (s for s in steps if s["step"] == step_name),
                None
            )

            if step_def and "compensation" in step_def:
                compensation = step_def["compensation"]
                service = step_def["service"]

                self.logger.debug(
                    f"Compensating step {step_name} with {compensation}"
                )

                # Execute compensation
                # In real implementation, would call actual service

                compensation_result = {
                    "step": step_name,
                    "compensation": compensation,
                    "service": service,
                    "compensated_at": datetime.utcnow()
                }

                execution["compensated_steps"].append(compensation_result)

    async def _validate_saga(self, saga: Dict[str, Any]):
        """Validate saga definition"""
        steps = saga.get("steps", [])

        if not steps:
            raise ValueError("Saga must have at least one step")

        # Check each step has required fields
        for step in steps:
            if "step" not in step or "service" not in step:
                raise ValueError("Each step must have 'step' and 'service' fields")


class ChoreographyEngine:
    """
    Event-driven choreography without central orchestrator.

    Features:
    - Decentralized coordination
    - Event-based triggering
    - Autonomous service reactions
    - No single point of failure
    """

    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.logger = logging.getLogger("AOS.ChoreographyEngine")
        self.rules = []
        self.enabled = False

    async def add_rule(
        self,
        trigger_event: str,
        actions: List[Dict[str, Any]]
    ):
        """
        Add choreography rule.

        Args:
            trigger_event: Event that triggers actions
            actions: Actions to perform when event occurs
        """
        self.logger.info(f"Adding choreography rule for event: {trigger_event}")

        rule = {
            "trigger_event": trigger_event,
            "actions": actions,
            "added_at": datetime.utcnow()
        }

        self.rules.append(rule)

    async def enable(self):
        """Enable choreography engine"""
        self.logger.info("Enabling choreography engine")
        self.enabled = True

        # Start event listener
        asyncio.create_task(self._listen_for_events())

    async def disable(self):
        """Disable choreography engine"""
        self.logger.info("Disabling choreography engine")
        self.enabled = False

    async def _listen_for_events(self):
        """Listen for events and trigger actions"""
        while self.enabled:
            try:
                # In real implementation, would subscribe to message bus
                # and process incoming events
                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"Error in choreography engine: {e}")
                await asyncio.sleep(5)

    async def _process_event(self, event: Dict[str, Any]):
        """Process event and trigger matching rules"""
        event_type = event.get("type") or event.get("event_type")

        for rule in self.rules:
            if rule["trigger_event"] == event_type:
                self.logger.debug(
                    f"Event {event_type} triggered choreography rule"
                )

                # Execute actions
                for action in rule["actions"]:
                    await self._execute_action(action, event)

    async def _execute_action(
        self,
        action: Dict[str, Any],
        event: Dict[str, Any]
    ):
        """Execute a choreography action"""
        agent = action.get("agent")
        action_type = action.get("action")

        self.logger.debug(f"Executing action {action_type} on agent {agent}")

        # Send message to agent
        # In real implementation, would use message bus
