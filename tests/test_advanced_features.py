"""
Integration tests for advanced orchestration and messaging features.

Tests the implementation of features from /docs/specifications.
"""

import pytest
import asyncio
from datetime import datetime, timedelta

# Orchestration tests
from AgentOperatingSystem.orchestration.dynamic import DynamicWorkflowComposer
from AgentOperatingSystem.orchestration.scheduler import IntelligentScheduler, WorkflowPriority
from AgentOperatingSystem.orchestration.events import EventDrivenOrchestrator, EventPattern
from AgentOperatingSystem.orchestration.optimization import WorkflowOptimizer

# Messaging tests
from AgentOperatingSystem.messaging.streaming import EventStream, StreamProcessor
from AgentOperatingSystem.messaging.saga import SagaOrchestrator, SagaStatus
from AgentOperatingSystem.messaging.routing import IntelligentRouter
from AgentOperatingSystem.messaging.priority import PriorityQueueManager

# Reliability tests
from AgentOperatingSystem.reliability.state_machine_advanced import DistributedStateMachine
from AgentOperatingSystem.reliability.chaos import ChaosOrchestrator, ChaosType

# Observability tests
from AgentOperatingSystem.observability.predictive import AnomalyDetector, PredictiveAlerter
from AgentOperatingSystem.observability.dashboard import MetricsAggregator, DashboardBuilder


class TestDynamicWorkflowComposer:
    """Test dynamic workflow composition"""
    
    @pytest.mark.asyncio
    async def test_generate_workflow(self):
        """Test workflow generation from goal"""
        composer = DynamicWorkflowComposer()
        
        workflow = await composer.generate_workflow(
            goal="optimize_business_operations",
            constraints={"budget": 50000, "timeline_days": 30},
            available_agents=["cfo", "coo", "analyst"],
            context={}
        )
        
        assert workflow is not None
        assert workflow.workflow_id.startswith("dynamic_")
        assert len(workflow.steps) > 0
    
    @pytest.mark.asyncio
    async def test_from_intent(self):
        """Test intent-based workflow creation"""
        composer = DynamicWorkflowComposer()
        
        intent = {
            "objective": "launch_new_product",
            "stakeholders": ["ceo", "cmo", "cto"],
            "timeline": "Q2_2026",
            "success_metrics": ["market_share", "revenue"]
        }
        
        workflow = await composer.from_intent(intent)
        
        assert workflow is not None
        assert workflow.workflow_id.startswith("intent_")
        assert len(workflow.steps) >= 3  # Plan, execute, review


class TestIntelligentScheduler:
    """Test intelligent scheduling"""
    
    @pytest.mark.asyncio
    async def test_schedule_workflow(self):
        """Test workflow scheduling"""
        scheduler = IntelligentScheduler()
        
        await scheduler.configure({
            "priority_levels": 5,
            "preemption_enabled": True,
            "resource_quotas": {}
        })
        
        await scheduler.schedule_workflow(
            workflow_id="test_wf_001",
            priority=WorkflowPriority.HIGH
        )
        
        assert "test_wf_001" in scheduler.scheduled_workflows


class TestEventDrivenOrchestrator:
    """Test event-driven orchestration"""
    
    @pytest.mark.asyncio
    async def test_register_pattern(self):
        """Test event pattern registration"""
        orchestrator = EventDrivenOrchestrator()
        
        pattern = EventPattern(
            name="market_opportunity",
            conditions=[
                {"event": "stock_price_drop", "threshold": 0.15},
                {"event": "competitor_news", "sentiment": "negative"}
            ],
            temporal_relationship="all_within",
            window_minutes=30
        )
        
        await orchestrator.register_pattern(
            pattern=pattern,
            workflow_trigger="strategic_analysis"
        )
        
        assert "market_opportunity" in orchestrator.patterns


class TestEventStream:
    """Test event streaming"""
    
    @pytest.mark.asyncio
    async def test_produce_consume(self):
        """Test event production and consumption"""
        stream = EventStream(
            name="test_stream",
            partitions=4
        )
        
        # Produce events
        await stream.produce(
            key="user_123",
            value={"action": "login", "timestamp": datetime.utcnow()},
            headers={"source": "web"}
        )
        
        await stream.produce(
            key="user_123",
            value={"action": "purchase", "amount": 99.99},
            headers={"source": "web"}
        )
        
        # Consume events
        partition = hash("user_123") % 4
        events = await stream.consume(partition, start_offset=0, max_events=10)
        
        assert len(events) == 2
        assert events[0]["value"]["action"] == "login"


class TestSagaOrchestrator:
    """Test saga orchestration"""
    
    @pytest.mark.asyncio
    async def test_define_and_execute_saga(self):
        """Test saga definition and execution"""
        # Mock message bus
        class MockMessageBus:
            pass
        
        orchestrator = SagaOrchestrator(MockMessageBus())
        
        # Define saga
        await orchestrator.define_saga(
            saga_id="customer_onboarding",
            steps=[
                {
                    "step": "create_account",
                    "service": "account_service",
                    "compensation": "delete_account"
                },
                {
                    "step": "setup_payment",
                    "service": "payment_service",
                    "compensation": "remove_payment"
                }
            ]
        )
        
        assert "customer_onboarding" in orchestrator.sagas
        
        # Execute saga
        result = await orchestrator.execute(
            saga_id="customer_onboarding",
            input_data={"user_email": "test@example.com"}
        )
        
        assert result["status"] == "completed"


class TestIntelligentRouter:
    """Test intelligent message routing"""
    
    @pytest.mark.asyncio
    async def test_route_message(self):
        """Test message routing"""
        # Mock message bus
        class MockMessageBus:
            pass
        
        router = IntelligentRouter(MockMessageBus())
        
        await router.configure_routing(
            strategy="load_balanced",
            factors=["agent_load", "performance"]
        )
        
        # Update agent stats
        router.update_agent_stats("agent_1", {"current_load": 0.3})
        router.update_agent_stats("agent_2", {"current_load": 0.7})
        
        # Route message
        agent = await router.route_message(
            message={"type": "task", "content": "test"},
            candidate_agents=["agent_1", "agent_2"],
            optimization_goal="minimize_latency"
        )
        
        # Should route to less loaded agent
        assert agent == "agent_1"


class TestPriorityQueueManager:
    """Test priority-based queuing"""
    
    @pytest.mark.asyncio
    async def test_priority_queuing(self):
        """Test multi-priority queuing"""
        queue_manager = PriorityQueueManager()
        
        await queue_manager.configure(
            levels=[
                {"priority": "critical", "weight": 1.0, "max_latency_ms": 100},
                {"priority": "high", "weight": 0.7, "max_latency_ms": 500},
                {"priority": "normal", "weight": 0.4, "max_latency_ms": 2000}
            ]
        )
        
        # Enqueue messages
        await queue_manager.enqueue(
            message={"id": 1},
            priority="normal"
        )
        
        await queue_manager.enqueue(
            message={"id": 2},
            priority="critical"
        )
        
        # Dequeue - should get critical first
        messages = await queue_manager.dequeue(count=2)
        
        assert len(messages) > 0


class TestDistributedStateMachine:
    """Test distributed state machine"""
    
    @pytest.mark.asyncio
    async def test_state_transitions(self):
        """Test state machine transitions"""
        sm = DistributedStateMachine(
            machine_id="workflow_001",
            initial_state="pending"
        )
        
        # Add states and transitions
        sm.add_transition("pending", "start", "running")
        sm.add_transition("running", "complete", "completed")
        sm.add_transition("running", "fail", "failed")
        
        # Trigger transitions
        success = await sm.trigger("start")
        assert success
        assert sm.current_state == "running"
        
        success = await sm.trigger("complete")
        assert success
        assert sm.current_state == "completed"


class TestChaosOrchestrator:
    """Test chaos engineering"""
    
    @pytest.mark.asyncio
    async def test_run_experiment(self):
        """Test chaos experiment"""
        orchestrator = ChaosOrchestrator()
        
        result = await orchestrator.run_experiment(
            target_workflow="test_workflow",
            failure_scenarios=[
                {
                    "type": ChaosType.NETWORK_LATENCY.value,
                    "increase_ms": 100
                }
            ],
            recovery_validation=True
        )
        
        assert result["status"] in ["completed", "rolled_back"]
        assert len(result["results"]) > 0


class TestAnomalyDetector:
    """Test anomaly detection"""
    
    @pytest.mark.asyncio
    async def test_detect_anomaly(self):
        """Test anomaly detection"""
        detector = AnomalyDetector()
        
        # Feed normal values
        for i in range(50):
            await detector.detect_anomaly("cpu_usage", 50.0 + (i % 10))
        
        # Feed anomalous value
        result = await detector.detect_anomaly("cpu_usage", 200.0)
        
        assert result["is_anomaly"] == True
        assert result["severity"] in ["low", "medium", "high", "critical"]


class TestMetricsAggregator:
    """Test metrics aggregation"""
    
    @pytest.mark.asyncio
    async def test_record_and_aggregate(self):
        """Test metric recording and aggregation"""
        aggregator = MetricsAggregator()
        
        # Record metrics
        for i in range(10):
            await aggregator.record("test_metric", float(i * 10))
        
        # Get aggregation
        avg = await aggregator.get_aggregation("test_metric", aggregation_type="avg")
        assert avg is not None
        assert avg == 45.0  # Average of 0, 10, 20, ..., 90
        
        max_val = await aggregator.get_aggregation("test_metric", aggregation_type="max")
        assert max_val == 90.0


class TestDashboardBuilder:
    """Test dashboard building"""
    
    @pytest.mark.asyncio
    async def test_create_dashboard(self):
        """Test dashboard creation"""
        aggregator = MetricsAggregator()
        builder = DashboardBuilder(aggregator)
        
        # Record some metrics
        await aggregator.record("cpu_usage", 50.0)
        await aggregator.record("memory_usage", 75.0)
        
        # Create dashboard
        await builder.create_dashboard(
            dashboard_id="test_dashboard",
            name="Test Dashboard",
            widgets=[
                {"type": "gauge", "metric": "cpu_usage", "title": "CPU"},
                {"type": "gauge", "metric": "memory_usage", "title": "Memory"}
            ]
        )
        
        # Render dashboard
        rendered = await builder.render_dashboard("test_dashboard")
        
        assert rendered["name"] == "Test Dashboard"
        assert len(rendered["widgets"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
