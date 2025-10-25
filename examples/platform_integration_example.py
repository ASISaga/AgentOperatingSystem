"""
Example integration demonstrating AgentOperatingSystem platform features.

This example shows how the new platform, reliability, governance, observability,
and knowledge modules work together to support a decision workflow.
"""

import asyncio
from datetime import datetime, timedelta

# Platform imports
from AgentOperatingSystem.platform.contracts import MessageEnvelope, CommandContract, AgentIdentity
from AgentOperatingSystem.platform.events import (
    DecisionRequestedEvent, DecisionApprovedEvent, EventType
)

# Reliability imports
from AgentOperatingSystem.reliability.idempotency import IdempotencyHandler, IdempotencyKey
from AgentOperatingSystem.reliability.retry import RetryHandler, RetryPolicy
from AgentOperatingSystem.reliability.circuit_breaker import CircuitBreaker
from AgentOperatingSystem.reliability.state_machine import create_decision_state_machine

# Governance imports
from AgentOperatingSystem.governance.audit import AuditLogger, AuditLevel
from AgentOperatingSystem.governance.compliance import ComplianceEngine, register_soc2_controls
from AgentOperatingSystem.governance.risk import RiskRegistry, RiskLikelihood, RiskImpact
from AgentOperatingSystem.governance.decision_rationale import DecisionRationaleStore, DecisionOutcome

# Observability imports
from AgentOperatingSystem.observability.metrics import MetricsCollector
from AgentOperatingSystem.observability.tracing import TracingContext
from AgentOperatingSystem.observability.logging import StructuredLogger, LogLevel, LogSeparator
from AgentOperatingSystem.observability.alerting import AlertingSystem, AlertSeverity

# Knowledge imports
from AgentOperatingSystem.knowledge.evidence import EvidenceRetrieval, EvidenceType
from AgentOperatingSystem.knowledge.indexing import IndexingEngine, SearchQuery
from AgentOperatingSystem.knowledge.precedent import PrecedentEngine, PrecedentQuery


async def example_decision_workflow():
    """
    Example decision workflow using all platform components.
    
    Demonstrates:
    1. Creating a decision request with full tracing
    2. Idempotent processing
    3. Audit logging
    4. Risk assessment
    5. Compliance checks
    6. Metrics collection
    7. Precedent lookup
    8. State machine transitions
    """
    
    print("\n=== AgentOperatingSystem Platform Integration Example ===\n")
    
    # Initialize all components
    print("1. Initializing platform components...")
    
    audit_logger = AuditLogger()
    compliance_engine = ComplianceEngine()
    register_soc2_controls(compliance_engine)
    risk_registry = RiskRegistry()
    decision_store = DecisionRationaleStore()
    metrics_collector = MetricsCollector()
    structured_logger = StructuredLogger()
    alerting_system = AlertingSystem()
    evidence_retrieval = EvidenceRetrieval()
    indexing_engine = IndexingEngine()
    precedent_engine = PrecedentEngine()
    
    # Reliability components
    idempotency = IdempotencyHandler()
    retry_handler = RetryHandler(RetryPolicy(max_attempts=3))
    circuit_breaker = CircuitBreaker("decision_service")
    state_machine = create_decision_state_machine()
    
    print("✓ All components initialized\n")
    
    # 2. Create a decision request
    print("2. Creating decision request...")
    
    correlation_id = "corr-001"
    tracing_ctx = TracingContext(correlation_id=correlation_id)
    
    # Create message envelope
    envelope = MessageEnvelope(
        message_type="event",
        correlation_id=correlation_id,
        actor="agent:ceo",
        scope="strategic",
        payload={
            "decision_type": "budget_approval",
            "amount": 500000,
            "department": "engineering"
        }
    )
    
    # Create decision event
    decision_event = DecisionRequestedEvent(
        source="agent:ceo",
        correlation_id=correlation_id,
        decision_id="dec-001",
        requester="agent:cfo",
        decision_type="budget_approval",
        context=envelope.payload
    )
    
    print(f"✓ Decision request created: {decision_event.decision_id}\n")
    
    # 3. Create tracing span
    print("3. Creating distributed tracing span...")
    
    span = tracing_ctx.create_span("process_decision_request")
    
    print(f"✓ Span created: {span.span_id}\n")
    
    # 4. Idempotent processing
    print("4. Testing idempotency...")
    
    def process_decision():
        metrics_collector.record_decision_latency("budget_approval", 150.5)
        return {"status": "processed", "decision_id": decision_event.decision_id}
    
    key = IdempotencyKey(
        message_id=decision_event.event_id,
        business_key=decision_event.decision_id
    )
    
    result1 = idempotency.execute(key, process_decision)
    result2 = idempotency.execute(key, process_decision)  # Should return cached result
    
    print(f"✓ First call: {result1}")
    print(f"✓ Second call (cached): {result2}\n")
    
    # 5. Audit logging
    print("5. Recording audit entries...")
    
    audit_logger.log_decision(
        actor="agent:ceo",
        decision_id=decision_event.decision_id,
        decision_type="budget_approval",
        outcome="pending_review",
        context={"correlation_id": correlation_id}
    )
    
    # Verify audit chain
    is_valid, error = audit_logger.verify_chain_integrity()
    print(f"✓ Audit log entry created")
    print(f"✓ Audit chain integrity: {is_valid}\n")
    
    # 6. Risk assessment
    print("6. Performing risk assessment...")
    
    risk = risk_registry.register_risk(
        title="High budget allocation without historical precedent",
        description="Engineering budget increase of $500k requires validation",
        likelihood=RiskLikelihood.POSSIBLE,
        impact=RiskImpact.MAJOR,
        owner="agent:cfo",
        identified_by="agent:risk_manager",
        category="financial"
    )
    
    risk_registry.link_to_decision(risk.risk_id, decision_event.decision_id)
    
    print(f"✓ Risk registered: {risk.risk_id}")
    print(f"✓ Risk level: {risk.level.value}\n")
    
    # 7. Compliance assertions
    print("7. Checking compliance...")
    
    assertion = compliance_engine.assert_compliance(
        action="decision:budget_approval",
        resource=f"decision:{decision_event.decision_id}",
        actor="agent:ceo",
        pre_conditions={"authorization_verified": True, "within_authority": True},
        post_conditions={"audit_logged": True}
    )
    
    print(f"✓ Compliance assertion created")
    print(f"✓ Controls checked: {len(assertion.controls)}")
    print(f"✓ Is compliant: {assertion.is_compliant}\n")
    
    # 8. Create decision rationale
    print("8. Creating decision rationale...")
    
    rationale = decision_store.create_rationale(
        title="Engineering Budget Increase Q2 2025",
        description="Increase engineering budget by $500k for new hires",
        decision_type="budget_approval",
        requester="agent:cfo",
        problem_statement="Need to expand engineering team to meet roadmap",
        proposed_solution="Approve additional $500k for hiring",
        approvers=["agent:ceo", "agent:cfo"]
    )
    
    decision_store.add_risk(rationale.decision_id, risk.title)
    decision_store.add_evidence(rationale.decision_id, "Q1 revenue exceeded targets by 20%")
    
    print(f"✓ Decision rationale created: {rationale.decision_id}\n")
    
    # 9. Search for precedents
    print("9. Searching for precedent decisions...")
    
    # Register some precedent decisions
    precedent_engine.register_decision(
        decision_id="dec-000",
        decision_type="budget_approval",
        title="Marketing Budget Increase Q1 2025",
        description="Approved $400k for marketing expansion",
        outcome="approved",
        tags=["budget", "expansion"]
    )
    
    # Find similar precedents
    query = PrecedentQuery(
        decision_type="budget_approval",
        tags=["budget"],
        keywords=["increase", "expansion"],
        min_similarity=0.3
    )
    
    precedents = precedent_engine.find_precedents(query)
    
    print(f"✓ Found {len(precedents)} precedent decisions")
    if precedents:
        print(f"✓ Best match: {precedents[0].match_reason}\n")
    else:
        print("✓ No precedents found\n")
    
    # 10. State machine workflow
    print("10. Managing decision lifecycle with state machine...")
    
    instance = state_machine.create_instance(
        instance_id=decision_event.decision_id,
        initial_context={"requester": "agent:cfo", "amount": 500000}
    )
    
    print(f"✓ State machine instance created")
    print(f"✓ Initial state: {instance.current_state}")
    
    # Transition through states
    state_machine.transition(instance, "start_review")
    print(f"✓ Transitioned to: {instance.current_state}")
    
    state_machine.transition(instance, "approve")
    print(f"✓ Transitioned to: {instance.current_state}")
    print(f"✓ Is terminal: {state_machine.is_terminal(instance)}\n")
    
    # 11. Record metrics
    print("11. Collecting metrics...")
    
    metrics_collector.record_decision_latency("budget_approval", 245.7)
    metrics_collector.record_sla_compliance("decision_sla", True)
    metrics_collector.record_policy_evaluation("policy_001", 12.3)
    
    # Get percentiles
    percentiles = metrics_collector.get_percentiles("decision.latency_ms", [50, 95])
    
    print(f"✓ Decision latency p50: {percentiles[50]:.2f}ms")
    print(f"✓ Decision latency p95: {percentiles[95]:.2f}ms")
    print(f"✓ SLA compliance rate: {metrics_collector.get_sla_compliance_rate('decision_sla'):.1%}\n")
    
    # 12. Structured logging
    print("12. Structured logging...")
    
    structured_logger.audit(
        "Decision approved with full governance compliance",
        context={
            "decision_id": decision_event.decision_id,
            "approver": "agent:ceo",
            "compliance_assertion": assertion.assertion_id
        },
        correlation_id=correlation_id
    )
    
    # Add redaction rule for sensitive data
    structured_logger.add_redaction_rule(r'\d{3}-\d{2}-\d{4}', '***SSN***')
    
    print("✓ Audit log entry created")
    print("✓ Redaction rules configured\n")
    
    # 13. Alerting
    print("13. Configuring alerting...")
    
    # Add alert rule
    alerting_system.add_rule(
        name="High Decision Latency",
        metric_name="decision.latency_ms",
        condition="greater_than",
        threshold=200.0,
        severity=AlertSeverity.WARNING,
        owner="platform_team",
        playbook_url="https://wiki.example.com/playbooks/decision-latency"
    )
    
    # Check metric (this will trigger alert)
    alerting_system.check_metric("decision.latency_ms", 245.7)
    
    active_alerts = alerting_system.get_active_alerts()
    print(f"✓ Alert rule configured")
    print(f"✓ Active alerts: {len(active_alerts)}\n")
    
    # 14. Finish tracing span
    span.finish()
    print(f"14. Tracing span completed")
    print(f"✓ Duration: {span.duration_ms:.2f}ms\n")
    
    # 15. Summary
    print("=== Summary ===\n")
    print(f"Decision ID: {decision_event.decision_id}")
    print(f"Final State: {instance.current_state}")
    print(f"Audit Entries: {audit_logger.get_statistics()['total_entries']}")
    print(f"Compliance: {'✓ Compliant' if assertion.is_compliant else '✗ Non-compliant'}")
    print(f"Risks Identified: {risk_registry.get_risk_summary()['total_risks']}")
    print(f"Precedents Found: {len(precedents)}")
    print(f"Metrics Tracked: {len(metrics_collector._metrics)}")
    print(f"Active Alerts: {len(active_alerts)}")
    print("\n✓ Decision workflow completed successfully!\n")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_decision_workflow())
