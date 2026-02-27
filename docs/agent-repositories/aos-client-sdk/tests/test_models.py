"""Tests for AOS Client SDK models."""

import pytest
from aos_client.models import (
    AgentDescriptor,
    OrchestrationPurpose,
    OrchestrationRequest,
    OrchestrationResult,
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
        request = OrchestrationRequest(
            agent_ids=["ceo", "cmo"],
            task={"type": "strategic_review"},
        )
        assert request.workflow == "collaborative"
        assert request.orchestration_id is None

    def test_requires_at_least_one_agent(self):
        with pytest.raises(Exception):
            OrchestrationRequest(agent_ids=[], task={"type": "test"})

    def test_create_with_purpose(self):
        purpose = OrchestrationPurpose(
            purpose="Evaluate Q1 strategic direction",
            purpose_scope="C-suite quarterly review",
            success_criteria=["All departments reviewed", "Action items identified"],
        )
        request = OrchestrationRequest(
            agent_ids=["ceo", "cfo", "cmo"],
            task={"type": "strategic_review"},
            purpose=purpose,
        )
        assert request.purpose is not None
        assert request.purpose.purpose == "Evaluate Q1 strategic direction"
        assert len(request.purpose.success_criteria) == 2

    def test_purpose_is_optional(self):
        request = OrchestrationRequest(
            agent_ids=["ceo"],
            task={"type": "test"},
        )
        assert request.purpose is None


class TestOrchestrationPurpose:
    """OrchestrationPurpose model tests."""

    def test_create_minimal(self):
        purpose = OrchestrationPurpose(purpose="Drive strategic growth")
        assert purpose.purpose == "Drive strategic growth"
        assert purpose.purpose_scope == "General orchestration scope"
        assert purpose.success_criteria == []

    def test_create_full(self):
        purpose = OrchestrationPurpose(
            purpose="Quarterly budget review and approval",
            purpose_scope="Finance department Q2 planning",
            success_criteria=["Budget approved", "Allocations finalized", "Timeline set"],
        )
        assert purpose.purpose_scope == "Finance department Q2 planning"
        assert len(purpose.success_criteria) == 3


class TestOrchestrationStatus:
    """OrchestrationStatus model tests."""

    def test_create(self):
        status = OrchestrationStatus(
            orchestration_id="orch-123",
            status=OrchestrationStatusEnum.RUNNING,
            agent_ids=["ceo", "cfo"],
            progress=0.5,
        )
        assert status.status == OrchestrationStatusEnum.RUNNING
        assert status.progress == 0.5


class TestOrchestrationResult:
    """OrchestrationResult model tests."""

    def test_create_completed(self):
        result = OrchestrationResult(
            orchestration_id="orch-123",
            status=OrchestrationStatusEnum.COMPLETED,
            agent_ids=["ceo", "cmo"],
            results={
                "ceo": {"decision": "approve"},
                "cmo": {"analysis": "positive outlook"},
            },
            summary="Strategic review completed — expansion approved",
        )
        assert result.status == OrchestrationStatusEnum.COMPLETED
        assert "ceo" in result.results
        assert result.summary is not None
