"""Tests for AOS Client SDK models."""

import pytest
from aos_client.models import (
    AgentDescriptor,
    OrchestrationPurpose,
    OrchestrationRequest,
    OrchestrationStatus,
    OrchestrationStatusEnum,
)


class TestAgentDescriptor:
    """AgentDescriptor model tests."""

    def test_create_minimal(self):
        agent = AgentDescriptor(
            agent_id="ceo",
            agent_type="LeadershipAgent",
            purpose="Strategic leadership",
            adapter_name="leadership",
        )
        assert agent.agent_id == "ceo"
        assert agent.capabilities == []
        assert agent.config == {}

    def test_create_full(self):
        agent = AgentDescriptor(
            agent_id="cmo-001",
            agent_type="CMOAgent",
            purpose="Marketing and brand strategy",
            adapter_name="marketing",
            capabilities=["marketing", "leadership", "brand_management"],
            config={"budget_authority": True},
        )
        assert agent.agent_type == "CMOAgent"
        assert len(agent.capabilities) == 3


class TestOrchestrationRequest:
    """OrchestrationRequest model tests."""

    def test_create_minimal(self):
        purpose = OrchestrationPurpose(purpose="Drive strategic growth")
        request = OrchestrationRequest(
            agent_ids=["ceo", "cmo"],
            purpose=purpose,
        )
        assert request.workflow == "collaborative"
        assert request.orchestration_id is None
        assert request.purpose.purpose == "Drive strategic growth"

    def test_requires_at_least_one_agent(self):
        purpose = OrchestrationPurpose(purpose="Test")
        with pytest.raises(Exception):
            OrchestrationRequest(agent_ids=[], purpose=purpose)

    def test_purpose_is_required(self):
        with pytest.raises(Exception):
            OrchestrationRequest(
                agent_ids=["ceo"],
            )

    def test_create_with_context(self):
        purpose = OrchestrationPurpose(
            purpose="Drive strategic review and continuous improvement",
            purpose_scope="C-suite quarterly review",
        )
        request = OrchestrationRequest(
            agent_ids=["ceo", "cfo", "cmo"],
            purpose=purpose,
            context={"quarter": "Q1-2026", "focus_areas": ["revenue"]},
        )
        assert request.purpose.purpose == "Drive strategic review and continuous improvement"
        assert request.context["quarter"] == "Q1-2026"


class TestOrchestrationPurpose:
    """OrchestrationPurpose model tests."""

    def test_create_minimal(self):
        purpose = OrchestrationPurpose(purpose="Drive strategic growth")
        assert purpose.purpose == "Drive strategic growth"
        assert purpose.purpose_scope == "General orchestration scope"

    def test_create_with_scope(self):
        purpose = OrchestrationPurpose(
            purpose="Govern budget allocation and ensure fiscal responsibility",
            purpose_scope="Finance department governance",
        )
        assert purpose.purpose_scope == "Finance department governance"

    def test_no_success_criteria(self):
        """Perpetual purposes do not have success criteria."""
        purpose = OrchestrationPurpose(purpose="Drive growth")
        assert not hasattr(purpose, "success_criteria")


class TestOrchestrationStatus:
    """OrchestrationStatus model tests."""

    def test_create_active(self):
        status = OrchestrationStatus(
            orchestration_id="orch-123",
            status=OrchestrationStatusEnum.ACTIVE,
            agent_ids=["ceo", "cfo"],
            purpose="Drive strategic growth",
        )
        assert status.status == OrchestrationStatusEnum.ACTIVE
        assert status.purpose == "Drive strategic growth"

    def test_perpetual_lifecycle_states(self):
        """Orchestrations are perpetual: PENDING → ACTIVE → STOPPED."""
        assert OrchestrationStatusEnum.PENDING == "pending"
        assert OrchestrationStatusEnum.ACTIVE == "active"
        assert OrchestrationStatusEnum.STOPPED == "stopped"
        assert OrchestrationStatusEnum.FAILED == "failed"
        assert OrchestrationStatusEnum.CANCELLED == "cancelled"

    def test_no_completed_state(self):
        """Perpetual orchestrations do not have a COMPLETED state."""
        values = [e.value for e in OrchestrationStatusEnum]
        assert "completed" not in values
