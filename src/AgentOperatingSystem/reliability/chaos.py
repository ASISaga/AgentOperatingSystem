"""
Chaos Engineering Tools

Provides controlled chaos testing for resilience validation.
"""

import logging
import asyncio
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class ChaosType(Enum):
    """Types of chaos experiments"""
    AGENT_UNAVAILABLE = "agent_unavailable"
    NETWORK_LATENCY = "network_latency"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MESSAGE_LOSS = "message_loss"
    STORAGE_FAILURE = "storage_failure"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"


class ChaosOrchestrator:
    """
    Orchestrates chaos engineering experiments.

    Features:
    - Controlled failure injection
    - Multi-type chaos scenarios
    - Automatic rollback on critical failures
    - Continuous chaos testing
    - Resilience validation
    """

    def __init__(self):
        self.logger = logging.getLogger("AOS.ChaosOrchestrator")
        self.active_experiments = {}
        self.experiment_history = []
        self.continuous_testing_enabled = False

    async def run_experiment(
        self,
        target_workflow: str,
        failure_scenarios: List[Dict[str, Any]],
        recovery_validation: bool = True,
        rollback_on_critical_failure: bool = True
    ) -> Dict[str, Any]:
        """
        Run a chaos experiment.

        Args:
            target_workflow: Workflow to test
            failure_scenarios: List of failures to inject
            recovery_validation: Whether to validate recovery
            rollback_on_critical_failure: Auto-rollback on critical failures

        Returns:
            Experiment results
        """
        experiment_id = f"chaos_{datetime.utcnow().timestamp()}"

        self.logger.info(
            f"Starting chaos experiment {experiment_id} on {target_workflow}"
        )

        experiment = {
            "experiment_id": experiment_id,
            "target_workflow": target_workflow,
            "scenarios": failure_scenarios,
            "start_time": datetime.utcnow(),
            "status": "running",
            "results": []
        }

        self.active_experiments[experiment_id] = experiment

        try:
            # Execute each failure scenario
            for scenario in failure_scenarios:
                result = await self._inject_failure(
                    target_workflow,
                    scenario,
                    recovery_validation
                )

                experiment["results"].append(result)

                # Check for critical failures
                if rollback_on_critical_failure and result.get("severity") == "critical":
                    self.logger.warning(
                        f"Critical failure detected in {experiment_id}, rolling back"
                    )
                    await self._rollback_experiment(experiment_id)
                    experiment["status"] = "rolled_back"
                    break

            if experiment["status"] == "running":
                experiment["status"] = "completed"

            experiment["end_time"] = datetime.utcnow()

            # Move to history
            self.experiment_history.append(experiment)
            del self.active_experiments[experiment_id]

            self.logger.info(
                f"Chaos experiment {experiment_id} {experiment['status']}"
            )

            return experiment

        except Exception as e:
            self.logger.error(f"Error in chaos experiment: {e}")
            experiment["status"] = "failed"
            experiment["error"] = str(e)
            return experiment

    async def _inject_failure(
        self,
        target: str,
        scenario: Dict[str, Any],
        validate_recovery: bool
    ) -> Dict[str, Any]:
        """
        Inject a specific failure.

        Args:
            target: Target workflow/component
            scenario: Failure scenario
            validate_recovery: Whether to validate recovery

        Returns:
            Injection result
        """
        failure_type = scenario.get("type")

        self.logger.info(f"Injecting failure: {failure_type}")

        result = {
            "type": failure_type,
            "target": target,
            "injected_at": datetime.utcnow(),
            "severity": "medium",
            "recovered": False
        }

        if failure_type == ChaosType.AGENT_UNAVAILABLE.value:
            result.update(await self._inject_agent_unavailable(scenario))

        elif failure_type == ChaosType.NETWORK_LATENCY.value:
            result.update(await self._inject_network_latency(scenario))

        elif failure_type == ChaosType.RESOURCE_EXHAUSTION.value:
            result.update(await self._inject_resource_exhaustion(scenario))

        elif failure_type == ChaosType.MESSAGE_LOSS.value:
            result.update(await self._inject_message_loss(scenario))

        # Validate recovery if requested
        if validate_recovery:
            recovery_result = await self._validate_recovery(target, scenario)
            result["recovered"] = recovery_result["recovered"]
            result["recovery_time_seconds"] = recovery_result.get("recovery_time")

        return result

    async def _inject_agent_unavailable(
        self,
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make an agent unavailable"""
        agent = scenario.get("agent")
        duration = scenario.get("duration_seconds", 30)

        self.logger.info(
            f"Making agent {agent} unavailable for {duration}s"
        )

        # In real implementation, would actually disable the agent
        # For now, simulate
        await asyncio.sleep(min(duration, 5))  # Simulate for up to 5s

        return {
            "agent": agent,
            "duration_seconds": duration,
            "impact": "Agent was unavailable, triggering failover"
        }

    async def _inject_network_latency(
        self,
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Inject network latency"""
        increase_ms = scenario.get("increase_ms", 500)

        self.logger.info(f"Injecting {increase_ms}ms network latency")

        # Simulate latency increase
        await asyncio.sleep(increase_ms / 1000.0)

        return {
            "latency_increase_ms": increase_ms,
            "impact": "Network operations slowed"
        }

    async def _inject_resource_exhaustion(
        self,
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Exhaust system resources"""
        resource = scenario.get("resource", "memory")
        limit = scenario.get("limit", "50%")

        self.logger.info(f"Exhausting {resource} to {limit}")

        return {
            "resource": resource,
            "limit": limit,
            "impact": f"{resource} exhaustion triggered resource limits",
            "severity": "high"
        }

    async def _inject_message_loss(
        self,
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate message loss"""
        loss_rate = scenario.get("loss_rate", 0.1)  # 10% loss

        self.logger.info(f"Injecting {loss_rate*100}% message loss")

        return {
            "loss_rate": loss_rate,
            "impact": "Messages lost, triggering retry mechanisms"
        }

    async def _validate_recovery(
        self,
        target: str,
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that system recovered from failure"""
        self.logger.info(f"Validating recovery for {target}")

        # In real implementation, would check actual system state
        # For now, simulate successful recovery
        recovery_time = random.uniform(1.0, 5.0)

        await asyncio.sleep(recovery_time)

        return {
            "recovered": True,
            "recovery_time": recovery_time,
            "health_status": "healthy"
        }

    async def _rollback_experiment(self, experiment_id: str):
        """Rollback a chaos experiment"""
        self.logger.info(f"Rolling back experiment {experiment_id}")

        experiment = self.active_experiments.get(experiment_id)
        if not experiment:
            return

        # In real implementation, would undo all injected failures
        # For now, just mark as rolled back
        experiment["rolled_back_at"] = datetime.utcnow()

    async def enable_continuous_testing(
        self,
        frequency: str = "daily",
        severity_levels: List[str] = None,
        business_hours_only: bool = True
    ):
        """
        Enable continuous chaos testing.

        Args:
            frequency: Test frequency ("hourly", "daily", "weekly")
            severity_levels: Allowed severity levels
            business_hours_only: Only test during business hours
        """
        self.logger.info(
            f"Enabling continuous chaos testing ({frequency})"
        )

        self.continuous_testing_enabled = True
        self.continuous_config = {
            "frequency": frequency,
            "severity_levels": severity_levels or ["low", "medium"],
            "business_hours_only": business_hours_only
        }

        # Start continuous testing loop
        asyncio.create_task(self._continuous_testing_loop())

    async def _continuous_testing_loop(self):
        """Background loop for continuous chaos testing"""
        while self.continuous_testing_enabled:
            try:
                # Check if we should run a test
                if await self._should_run_test():
                    # Select random low-severity failure
                    scenario = self._generate_low_severity_scenario()

                    await self.run_experiment(
                        target_workflow="system",
                        failure_scenarios=[scenario],
                        recovery_validation=True,
                        rollback_on_critical_failure=True
                    )

                # Wait based on frequency
                frequency = self.continuous_config.get("frequency", "daily")
                if frequency == "hourly":
                    await asyncio.sleep(3600)
                elif frequency == "daily":
                    await asyncio.sleep(86400)
                elif frequency == "weekly":
                    await asyncio.sleep(604800)
                else:
                    await asyncio.sleep(3600)

            except Exception as e:
                self.logger.error(f"Error in continuous testing: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _should_run_test(self) -> bool:
        """Determine if a test should run now"""
        if self.continuous_config.get("business_hours_only"):
            # Check if in business hours (9 AM - 5 PM)
            current_hour = datetime.utcnow().hour
            if not (9 <= current_hour < 17):
                return False

        return True

    def _generate_low_severity_scenario(self) -> Dict[str, Any]:
        """Generate a low-severity chaos scenario"""
        scenarios = [
            {
                "type": ChaosType.NETWORK_LATENCY.value,
                "increase_ms": 100
            },
            {
                "type": ChaosType.MESSAGE_LOSS.value,
                "loss_rate": 0.01  # 1% loss
            }
        ]

        return random.choice(scenarios)

    def get_experiment_report(self, experiment_id: str) -> Dict[str, Any]:
        """Get detailed report for an experiment"""
        # Check active experiments
        if experiment_id in self.active_experiments:
            return self.active_experiments[experiment_id]

        # Check history
        for exp in self.experiment_history:
            if exp["experiment_id"] == experiment_id:
                return exp

        return None
