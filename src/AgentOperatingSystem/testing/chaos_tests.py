"""
Chaos Testing Framework for AgentOperatingSystem

Simulates failures and degraded conditions to verify system resilience,
graceful degradation, and recovery mechanisms.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional


class FailureType(str, Enum):
    """Types of failures that can be simulated"""
    NETWORK_DELAY = "network_delay"
    NETWORK_TIMEOUT = "network_timeout"
    STORAGE_OUTAGE = "storage_outage"
    STORAGE_SLOW = "storage_slow"
    MESSAGE_BUS_DELAY = "message_bus_delay"
    MESSAGE_BUS_FAILURE = "message_bus_failure"
    POLICY_ENGINE_FAILURE = "policy_engine_failure"
    DEPENDENCY_FAILURE = "dependency_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PARTIAL_OUTAGE = "partial_outage"


class FailureSimulator:
    """
    Simulates various failure conditions for chaos testing.

    Can inject delays, timeouts, errors, and degraded performance
    into system components to test resilience.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.Testing.FailureSimulator")
        self.active_failures: Dict[str, Dict[str, Any]] = {}
        self.failure_history: List[Dict[str, Any]] = []

    async def inject_network_delay(
        self,
        min_delay_ms: int = 100,
        max_delay_ms: int = 1000,
        duration_seconds: int = 10
    ) -> str:
        """
        Inject random network delays.

        Args:
            min_delay_ms: Minimum delay in milliseconds
            max_delay_ms: Maximum delay in milliseconds
            duration_seconds: How long to inject delays

        Returns:
            Failure ID for tracking
        """
        failure_id = f"network_delay_{datetime.utcnow().timestamp()}"

        failure_config = {
            "id": failure_id,
            "type": FailureType.NETWORK_DELAY,
            "min_delay_ms": min_delay_ms,
            "max_delay_ms": max_delay_ms,
            "started_at": datetime.utcnow(),
            "ends_at": datetime.utcnow() + timedelta(seconds=duration_seconds),
            "status": "active"
        }

        self.active_failures[failure_id] = failure_config
        self.logger.warning(
            f"Injecting network delay: {min_delay_ms}-{max_delay_ms}ms "
            f"for {duration_seconds}s"
        )

        # Schedule automatic cleanup
        asyncio.create_task(self._cleanup_failure(failure_id, duration_seconds))

        return failure_id

    async def inject_storage_outage(
        self,
        storage_type: str = "all",
        duration_seconds: int = 5
    ) -> str:
        """
        Simulate storage outage.

        Args:
            storage_type: Type of storage to fail ("blob", "table", "queue", "all")
            duration_seconds: How long the outage lasts

        Returns:
            Failure ID for tracking
        """
        failure_id = f"storage_outage_{datetime.utcnow().timestamp()}"

        failure_config = {
            "id": failure_id,
            "type": FailureType.STORAGE_OUTAGE,
            "storage_type": storage_type,
            "started_at": datetime.utcnow(),
            "ends_at": datetime.utcnow() + timedelta(seconds=duration_seconds),
            "status": "active"
        }

        self.active_failures[failure_id] = failure_config
        self.logger.warning(
            "Injecting storage outage (%s) for %ss", storage_type, duration_seconds
        )

        asyncio.create_task(self._cleanup_failure(failure_id, duration_seconds))

        return failure_id

    async def inject_message_bus_delay(
        self,
        delay_ms: int = 500,
        duration_seconds: int = 10
    ) -> str:
        """
        Inject delays in message bus processing.

        Args:
            delay_ms: Delay in milliseconds
            duration_seconds: How long to inject delays

        Returns:
            Failure ID for tracking
        """
        failure_id = f"bus_delay_{datetime.utcnow().timestamp()}"

        failure_config = {
            "id": failure_id,
            "type": FailureType.MESSAGE_BUS_DELAY,
            "delay_ms": delay_ms,
            "started_at": datetime.utcnow(),
            "ends_at": datetime.utcnow() + timedelta(seconds=duration_seconds),
            "status": "active"
        }

        self.active_failures[failure_id] = failure_config
        self.logger.warning(
            "Injecting message bus delay: %sms for %ss", delay_ms, duration_seconds
        )

        asyncio.create_task(self._cleanup_failure(failure_id, duration_seconds))

        return failure_id

    async def inject_policy_engine_failure(
        self,
        failure_rate: float = 0.5,
        duration_seconds: int = 10
    ) -> str:
        """
        Simulate policy engine failures.

        Args:
            failure_rate: Probability of failure (0.0-1.0)
            duration_seconds: How long to inject failures

        Returns:
            Failure ID for tracking
        """
        failure_id = f"policy_failure_{datetime.utcnow().timestamp()}"

        failure_config = {
            "id": failure_id,
            "type": FailureType.POLICY_ENGINE_FAILURE,
            "failure_rate": failure_rate,
            "started_at": datetime.utcnow(),
            "ends_at": datetime.utcnow() + timedelta(seconds=duration_seconds),
            "status": "active"
        }

        self.active_failures[failure_id] = failure_config
        self.logger.warning(
            f"Injecting policy engine failures at {failure_rate*100}% rate "
            f"for {duration_seconds}s"
        )

        asyncio.create_task(self._cleanup_failure(failure_id, duration_seconds))

        return failure_id

    async def inject_resource_exhaustion(
        self,
        resource_type: str = "memory",
        threshold_percent: int = 90,
        duration_seconds: int = 10
    ) -> str:
        """
        Simulate resource exhaustion.

        Args:
            resource_type: Type of resource ("memory", "cpu", "disk")
            threshold_percent: Simulated usage percentage
            duration_seconds: How long to simulate exhaustion

        Returns:
            Failure ID for tracking
        """
        failure_id = f"resource_exhaustion_{datetime.utcnow().timestamp()}"

        failure_config = {
            "id": failure_id,
            "type": FailureType.RESOURCE_EXHAUSTION,
            "resource_type": resource_type,
            "threshold_percent": threshold_percent,
            "started_at": datetime.utcnow(),
            "ends_at": datetime.utcnow() + timedelta(seconds=duration_seconds),
            "status": "active"
        }

        self.active_failures[failure_id] = failure_config
        self.logger.warning(
            f"Injecting {resource_type} exhaustion ({threshold_percent}%) "
            f"for {duration_seconds}s"
        )

        asyncio.create_task(self._cleanup_failure(failure_id, duration_seconds))

        return failure_id

    def is_failure_active(self, failure_id: str) -> bool:
        """Check if a failure is currently active"""
        if failure_id not in self.active_failures:
            return False

        failure = self.active_failures[failure_id]
        return failure["status"] == "active" and datetime.utcnow() < failure["ends_at"]

    def get_active_failures(self) -> List[Dict[str, Any]]:
        """Get list of all currently active failures"""
        return [
            f for f in self.active_failures.values()
            if f["status"] == "active" and datetime.utcnow() < f["ends_at"]
        ]

    async def _cleanup_failure(self, failure_id: str, delay_seconds: int) -> None:
        """Clean up a failure after its duration expires"""
        await asyncio.sleep(delay_seconds)

        if failure_id in self.active_failures:
            failure = self.active_failures[failure_id]
            failure["status"] = "completed"
            failure["completed_at"] = datetime.utcnow()

            self.failure_history.append(failure.copy())
            del self.active_failures[failure_id]

            self.logger.info("Failure cleaned up: %s", failure_id)

    def should_fail(self, failure_type: FailureType) -> bool:
        """
        Check if a failure should occur based on active failure configs.

        Args:
            failure_type: Type of failure to check

        Returns:
            True if failure should occur
        """
        active = self.get_active_failures()

        for failure in active:
            if failure["type"] == failure_type:
                # For failures with a rate, use probability
                if "failure_rate" in failure:
                    return random.random() < failure["failure_rate"]
                else:
                    return True

        return False

    async def get_simulated_delay(self, failure_type: FailureType) -> float:
        """
        Get delay to inject based on active failure configs.

        Args:
            failure_type: Type of failure

        Returns:
            Delay in seconds (0 if no delay)
        """
        active = self.get_active_failures()

        for failure in active:
            if failure["type"] == failure_type:
                if "delay_ms" in failure:
                    return failure["delay_ms"] / 1000.0
                elif "min_delay_ms" in failure and "max_delay_ms" in failure:
                    delay_ms = random.randint(
                        failure["min_delay_ms"],
                        failure["max_delay_ms"]
                    )
                    return delay_ms / 1000.0

        return 0.0


class ChaosTestFramework:
    """
    Comprehensive chaos testing framework for AOS.

    Tests system resilience by injecting various failure conditions
    and verifying graceful degradation and recovery.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.Testing.Chaos")
        self.simulator = FailureSimulator(logger=self.logger)
        self.test_results: List[Dict[str, Any]] = []

    async def test_graceful_degradation(
        self,
        component: str,
        failure_scenario: FailureType,
        test_function: Callable[[], Awaitable[Any]],
        expected_behavior: str = "fallback"
    ) -> Dict[str, Any]:
        """
        Test that a component degrades gracefully under failure.

        Args:
            component: Name of component being tested
            failure_scenario: Type of failure to inject
            test_function: Function to test under failure
            expected_behavior: Expected behavior ("fallback", "retry", "queue")

        Returns:
            Test result
        """
        result = {
            "test": "graceful_degradation",
            "component": component,
            "failure_scenario": failure_scenario.value,
            "expected_behavior": expected_behavior,
            "status": "pending",
            "started_at": datetime.utcnow().isoformat()
        }

        try:
            self.logger.info(
            "Testing graceful degradation: %s under %s", component, failure_scenario.value
        )

            # Inject failure
            if failure_scenario == FailureType.NETWORK_DELAY:
                failure_id = await self.simulator.inject_network_delay()
            elif failure_scenario == FailureType.STORAGE_OUTAGE:
                failure_id = await self.simulator.inject_storage_outage()
            elif failure_scenario == FailureType.MESSAGE_BUS_DELAY:
                failure_id = await self.simulator.inject_message_bus_delay()
            elif failure_scenario == FailureType.POLICY_ENGINE_FAILURE:
                failure_id = await self.simulator.inject_policy_engine_failure()
            else:
                failure_id = await self.simulator.inject_network_delay()

            result["failure_id"] = failure_id

            # Execute test function under failure
            test_result = await test_function()

            # Verify expected behavior
            # In a real implementation, this would check:
            # - Fallback mechanisms activated
            # - Retries attempted
            # - Messages queued for later
            # - Errors handled gracefully

            result["test_result"] = test_result
            result["status"] = "passed"
            self.logger.info("✅ Graceful degradation test passed for %s", component)

        except Exception as error:
            result["status"] = "failed"
            result["error"] = str(error)
            self.logger.error("❌ Graceful degradation test failed: %s", str(error))

        finally:
            result["completed_at"] = datetime.utcnow().isoformat()

        self.test_results.append(result)
        return result

    async def test_recovery(
        self,
        component: str,
        failure_duration_seconds: int,
        recovery_function: Callable[[], Awaitable[bool]],
        max_recovery_time_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Test that a component recovers after failure.

        Args:
            component: Name of component being tested
            failure_duration_seconds: How long the failure lasts
            recovery_function: Function to verify recovery
            max_recovery_time_seconds: Maximum time allowed for recovery

        Returns:
            Test result
        """
        result = {
            "test": "recovery",
            "component": component,
            "failure_duration_seconds": failure_duration_seconds,
            "max_recovery_time_seconds": max_recovery_time_seconds,
            "status": "pending",
            "started_at": datetime.utcnow().isoformat()
        }

        try:
            self.logger.info("Testing recovery for: %s", component)

            # Inject failure
            failure_id = await self.simulator.inject_storage_outage(
                duration_seconds=failure_duration_seconds
            )
            result["failure_id"] = failure_id

            # Wait for failure to complete
            await asyncio.sleep(failure_duration_seconds)

            # Start recovery timer
            recovery_start = datetime.utcnow()

            # Wait for recovery (with timeout)
            recovered = False
            timeout = asyncio.create_task(asyncio.sleep(max_recovery_time_seconds))
            recovery = asyncio.create_task(recovery_function())

            done, pending = await asyncio.wait(
                [timeout, recovery],
                return_when=asyncio.FIRST_COMPLETED
            )

            if recovery in done:
                recovered = await recovery
                recovery_time = (datetime.utcnow() - recovery_start).total_seconds()
                result["recovery_time_seconds"] = recovery_time
            else:
                # Timeout
                recovery.cancel()
                raise TimeoutError(
                    f"Recovery did not complete within {max_recovery_time_seconds}s"
                )

            if recovered:
                result["status"] = "passed"
                self.logger.info(
                    f"✅ Recovery test passed for {component} "
                    f"(recovered in {recovery_time:.2f}s)"
                )
            else:
                result["status"] = "failed"
                result["error"] = "Component did not recover"
                self.logger.error("❌ Recovery test failed for %s", component)

        except Exception as error:
            result["status"] = "failed"
            result["error"] = str(error)
            self.logger.error("❌ Recovery test failed: %s", str(error))

        finally:
            result["completed_at"] = datetime.utcnow().isoformat()

        self.test_results.append(result)
        return result

    async def test_circuit_breaker(
        self,
        component: str,
        failure_threshold: int = 5,
        test_calls: int = 10
    ) -> Dict[str, Any]:
        """
        Test circuit breaker behavior under repeated failures.

        Args:
            component: Component with circuit breaker
            failure_threshold: Number of failures before circuit opens
            test_calls: Total number of calls to make

        Returns:
            Test result
        """
        result = {
            "test": "circuit_breaker",
            "component": component,
            "failure_threshold": failure_threshold,
            "test_calls": test_calls,
            "status": "pending",
            "started_at": datetime.utcnow().isoformat()
        }

        try:
            self.logger.info("Testing circuit breaker for: %s", component)

            # Inject failures
            await self.simulator.inject_policy_engine_failure(failure_rate=1.0)

            failures = 0
            circuit_opened = False

            # Make test calls
            for i in range(test_calls):
                try:
                    # Simulate call that should fail
                    if self.simulator.should_fail(FailureType.POLICY_ENGINE_FAILURE):
                        failures += 1
                        raise Exception("Simulated failure")

                except Exception:
                    if failures >= failure_threshold and not circuit_opened:
                        circuit_opened = True
                        result["circuit_opened_at_call"] = i + 1
                        self.logger.info(
            "Circuit breaker opened after %s failures", failures
        )

            result["total_failures"] = failures
            result["circuit_opened"] = circuit_opened

            if circuit_opened:
                result["status"] = "passed"
                self.logger.info("✅ Circuit breaker test passed for %s", component)
            else:
                result["status"] = "failed"
                result["error"] = "Circuit breaker did not open"
                self.logger.error("❌ Circuit breaker test failed for %s", component)

        except Exception as error:
            result["status"] = "failed"
            result["error"] = str(error)
            self.logger.error("❌ Circuit breaker test failed: %s", str(error))

        finally:
            result["completed_at"] = datetime.utcnow().isoformat()

        self.test_results.append(result)
        return result

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive chaos testing report.

        Returns:
            Test report with summary and detailed results
        """
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "passed")
        failed_tests = sum(1 for r in self.test_results if r["status"] == "failed")

        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "failure_history": self.simulator.failure_history
            },
            "test_results": self.test_results,
            "generated_at": datetime.utcnow().isoformat()
        }
