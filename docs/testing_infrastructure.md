# Testing Infrastructure Documentation

The AgentOperatingSystem includes a comprehensive testing infrastructure that supports contract testing, integration testing, chaos testing, and audit completeness validation.

## Overview

The testing infrastructure is located in `src/AgentOperatingSystem/testing/` and provides four main testing frameworks:

1. **Contract Testing** - Validates message schemas and contracts
2. **Integration Testing** - Tests end-to-end workflows and cross-agent interactions
3. **Chaos Testing** - Simulates failures to verify resilience
4. **Audit Testing** - Ensures audit completeness and compliance

## Contract Testing

### MessageSchemaValidator

Validates message schemas across versions to ensure backward compatibility.

```python
from AgentOperatingSystem.testing import MessageSchemaValidator

validator = MessageSchemaValidator()

# Register a schema version
schema_v1 = {
    "type": "object",
    "properties": {
        "decision_id": {"type": "string"},
        "status": {"type": "string"}
    },
    "required": ["decision_id", "status"]
}

validator.register_schema("DecisionRequested", "1.0.0", schema_v1)

# Validate a message
message = {
    "decision_id": "dec_123",
    "status": "pending"
}

is_valid = validator.validate_message("DecisionRequested", "1.0.0", message)

# Check backward compatibility
schema_v2 = {
    "type": "object",
    "properties": {
        "decision_id": {"type": "string"},
        "status": {"type": "string"},
        "priority": {"type": "string"}  # New optional field
    },
    "required": ["decision_id", "status"]
}

validator.register_schema("DecisionRequested", "2.0.0", schema_v2)

compatibility = validator.check_backward_compatibility(
    "DecisionRequested", "1.0.0", "2.0.0"
)

print(f"Compatible: {compatibility['compatible']}")
```

### ContractTestFramework

Tests message contracts, envelopes, commands, queries, and events.

```python
from AgentOperatingSystem.testing import ContractTestFramework

framework = ContractTestFramework()

# Test message envelope
envelope_data = {
    "message_type": "command",
    "correlation_id": "corr_123",
    "actor": "agent_1",
    "scope": "finance",
    "payload": {"action": "approve_budget"}
}

framework.test_message_envelope_contract(envelope_data)

# Test command contract
command_data = {
    "intent": "approve_budget",
    "preconditions": ["budget_submitted", "within_threshold"],
    "expected_outcomes": ["budget_approved"],
    "failure_modes": ["timeout", "validation_error"]
}

framework.test_command_contract(command_data)

# Generate report
report = framework.generate_report()
print(f"Success rate: {report['summary']['success_rate']}%")
```

## Integration Testing

### TestScenario

Defines structured test scenarios with setup, execution, validation, and teardown phases.

```python
from AgentOperatingSystem.testing import TestScenario, IntegrationTestFramework

async def setup():
    # Setup test environment
    pass

async def execute():
    # Execute the test
    return {"result": "success", "data": "test_data"}

async def validate(result):
    # Validate the result
    return result["result"] == "success"

async def teardown():
    # Cleanup
    pass

scenario = TestScenario(
    name="test_agent_workflow",
    description="Test agent decision workflow",
    setup=setup,
    execute=execute,
    validate=validate,
    teardown=teardown
)

# Run the scenario
result = await scenario.run()
print(f"Status: {result['status']}")
```

### IntegrationTestFramework

Manages and executes integration test scenarios.

```python
from AgentOperatingSystem.testing import IntegrationTestFramework

framework = IntegrationTestFramework()

# Register scenarios
framework.register_scenario(scenario1)
framework.register_scenario(scenario2)

# Run all scenarios
report = await framework.run_all_scenarios()

print(f"Total: {report['summary']['total_scenarios']}")
print(f"Passed: {report['summary']['passed']}")
print(f"Failed: {report['summary']['failed']}")
```

### EndToEndTestRunner

Tests complete end-to-end workflows.

```python
from AgentOperatingSystem.testing import EndToEndTestRunner
from AgentOperatingSystem.platform.contracts import MessageEnvelope

runner = EndToEndTestRunner()

# Test agent interaction
message = MessageEnvelope(
    message_type="command",
    correlation_id="test_corr_1",
    actor="agent_1",
    scope="test",
    payload={"action": "process"}
)

result = await runner.test_agent_interaction(
    agent1_id="agent_1",
    agent2_id="agent_2",
    message=message
)

# Test workflow execution
result = await runner.test_workflow_execution(
    workflow_name="decision_workflow",
    workflow_steps=[
        {"name": "submit", "action": "submit_decision"},
        {"name": "review", "action": "review_decision"},
        {"name": "approve", "action": "approve_decision"}
    ],
    initial_state={"status": "draft"},
    expected_final_state={"status": "approved"}
)
```

## Chaos Testing

### FailureSimulator

Injects various failure conditions for resilience testing.

```python
from AgentOperatingSystem.testing import FailureSimulator, FailureType

simulator = FailureSimulator()

# Inject network delay
failure_id = await simulator.inject_network_delay(
    min_delay_ms=100,
    max_delay_ms=500,
    duration_seconds=10
)

# Inject storage outage
failure_id = await simulator.inject_storage_outage(
    storage_type="blob",
    duration_seconds=5
)

# Inject message bus delay
failure_id = await simulator.inject_message_bus_delay(
    delay_ms=200,
    duration_seconds=10
)

# Check if failure is active
if simulator.is_failure_active(failure_id):
    print("Failure is currently active")

# Get all active failures
active = simulator.get_active_failures()
print(f"Active failures: {len(active)}")
```

### ChaosTestFramework

Tests system resilience under failure conditions.

```python
from AgentOperatingSystem.testing import ChaosTestFramework, FailureType

framework = ChaosTestFramework()

# Test graceful degradation
async def test_function():
    # Your component logic
    return {"status": "fallback_used"}

result = await framework.test_graceful_degradation(
    component="decision_engine",
    failure_scenario=FailureType.STORAGE_OUTAGE,
    test_function=test_function,
    expected_behavior="fallback"
)

# Test recovery
async def check_recovery():
    # Check if component has recovered
    return True

result = await framework.test_recovery(
    component="decision_engine",
    failure_duration_seconds=5,
    recovery_function=check_recovery,
    max_recovery_time_seconds=10
)

# Test circuit breaker
result = await framework.test_circuit_breaker(
    component="policy_engine",
    failure_threshold=5,
    test_calls=10
)

# Generate report
report = framework.generate_report()
```

## Audit Testing

### DecisionPathTester

Validates that decision paths produce all required artifacts.

```python
from AgentOperatingSystem.testing import DecisionPathTester

tester = DecisionPathTester()

# Test decision path completeness
artifacts_produced = {
    "audit_entry",
    "decision_rationale",
    "compliance_assertion",
    "risk_assessment",
    "evidence"
}

result = await tester.test_decision_path(
    decision_name="budget_approval",
    decision_data={"id": "dec_123", "amount": 50000},
    artifacts_produced=artifacts_produced
)

if result["status"] == "passed":
    print("Decision path is complete")
else:
    print(f"Missing artifacts: {result['missing_artifacts']}")
```

### AuditCompletenessValidator

Validates audit trail integrity and compliance coverage.

```python
from AgentOperatingSystem.testing import AuditCompletenessValidator

validator = AuditCompletenessValidator()

# Validate audit trail integrity
audit_entries = [
    {
        "timestamp": "2025-01-01T10:00:00",
        "actor": "agent_1",
        "action": "decision_requested",
        "context": {},
        "outcome": "success"
    },
    {
        "timestamp": "2025-01-01T10:01:00",
        "actor": "agent_2",
        "action": "decision_approved",
        "context": {},
        "outcome": "success"
    }
]

result = await validator.validate_audit_trail_integrity(audit_entries)

if result["status"] == "passed":
    print("Audit trail is intact")
else:
    print(f"Issues found: {result['issues']}")

# Validate compliance coverage
actions = ["action_1", "action_2", "action_3"]
compliance_assertions = [
    {"action_id": "action_1", "control": "SOC2"},
    {"action_id": "action_2", "control": "ISO27001"}
]

result = await validator.validate_compliance_coverage(
    actions=actions,
    compliance_assertions=compliance_assertions
)

print(f"Coverage: {result['coverage_percentage']}%")
```

## Best Practices

1. **Run contract tests** during development to catch schema incompatibilities early
2. **Run integration tests** before deploying to verify end-to-end functionality
3. **Run chaos tests** regularly to ensure system resilience
4. **Run audit tests** to maintain compliance and governance requirements

## Test Reporting

All testing frameworks provide comprehensive reports:

```python
# Get a summary report
report = framework.generate_report()

print(f"Total tests: {report['summary']['total_tests']}")
print(f"Passed: {report['summary']['passed']}")
print(f"Failed: {report['summary']['failed']}")
print(f"Success rate: {report['summary']['success_rate']}%")

# Access detailed results
for test_result in report['detailed_results']:
    print(f"{test_result['test']}: {test_result['status']}")
```

## Integration with CI/CD

The testing infrastructure can be integrated into CI/CD pipelines:

```python
import asyncio
from AgentOperatingSystem.testing import (
    ContractTestFramework,
    IntegrationTestFramework,
    ChaosTestFramework,
    AuditCompletenessValidator
)

async def run_all_tests():
    # Contract tests
    contract_framework = ContractTestFramework()
    # ... run contract tests ...
    contract_report = contract_framework.generate_report()
    
    # Integration tests
    integration_framework = IntegrationTestFramework()
    # ... register and run scenarios ...
    integration_report = await integration_framework.run_all_scenarios()
    
    # Chaos tests
    chaos_framework = ChaosTestFramework()
    # ... run chaos tests ...
    chaos_report = chaos_framework.generate_report()
    
    # Audit tests
    audit_validator = AuditCompletenessValidator()
    # ... run audit tests ...
    audit_report = audit_validator.generate_report()
    
    # Check if all tests passed
    all_passed = (
        contract_report['summary']['failed'] == 0 and
        integration_report['summary']['failed'] == 0 and
        chaos_report['summary']['failed'] == 0 and
        audit_report['summary']['failed'] == 0
    )
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
```
