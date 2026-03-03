"""Tests for FoundryOrchestrationEngine."""

import pytest

from AgentOperatingSystem.orchestration import FoundryOrchestrationEngine


class TestFoundryOrchestrationEngine:
    """FoundryOrchestrationEngine unit tests."""

    @pytest.mark.asyncio
    async def test_create_orchestration(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(
            agent_ids=["ceo", "cfo"],
            purpose="Strategic review",
        )
        assert orch["orchestration_id"]
        assert orch["agent_ids"] == ["ceo", "cfo"]
        assert orch["purpose"] == "Strategic review"
        assert orch["status"] == "active"
        assert orch["managed_by"] == "foundry_agent_service"

    @pytest.mark.asyncio
    async def test_create_orchestration_with_workflow(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(
            agent_ids=["ceo"],
            purpose="Review",
            workflow="sequential",
        )
        assert orch["workflow"] == "sequential"

    @pytest.mark.asyncio
    async def test_create_orchestration_with_context(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(
            agent_ids=["ceo"],
            purpose="Q1 Review",
            context={"quarter": "Q1-2026"},
        )
        assert orch["context"]["quarter"] == "Q1-2026"

    @pytest.mark.asyncio
    async def test_create_orchestration_with_purpose_scope(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(
            agent_ids=["ceo"],
            purpose="Strategic review",
            purpose_scope="C-suite coordination",
        )
        assert orch["purpose_scope"] == "C-suite coordination"

    @pytest.mark.asyncio
    async def test_create_orchestration_with_mcp_servers(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(
            agent_ids=["ceo"],
            purpose="Review",
            mcp_servers={"ceo": [{"server_name": "erp"}]},
        )
        assert orch["mcp_servers"]["ceo"] == [{"server_name": "erp"}]

    @pytest.mark.asyncio
    async def test_run_agent_turn(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(["ceo"], "Review")
        turn = await engine.run_agent_turn(
            orch["orchestration_id"],
            "ceo",
            "What is the strategy?",
        )
        assert turn["agent_id"] == "ceo"
        assert turn["status"] == "completed"
        assert turn["run_id"]

    @pytest.mark.asyncio
    async def test_run_agent_turn_not_found(self):
        engine = FoundryOrchestrationEngine()
        with pytest.raises(KeyError, match="not found"):
            await engine.run_agent_turn("bad-id", "ceo", "msg")

    @pytest.mark.asyncio
    async def test_get_status(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(["ceo"], "Review")
        status = await engine.get_status(orch["orchestration_id"])
        assert status["status"] == "active"
        assert status["purpose"] == "Review"

    @pytest.mark.asyncio
    async def test_get_status_not_found(self):
        engine = FoundryOrchestrationEngine()
        with pytest.raises(KeyError, match="not found"):
            await engine.get_status("bad-id")

    @pytest.mark.asyncio
    async def test_stop_orchestration(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(["ceo"], "Review")
        await engine.stop_orchestration(orch["orchestration_id"])
        status = await engine.get_status(orch["orchestration_id"])
        assert status["status"] == "stopped"

    @pytest.mark.asyncio
    async def test_stop_orchestration_not_found(self):
        engine = FoundryOrchestrationEngine()
        with pytest.raises(KeyError, match="not found"):
            await engine.stop_orchestration("bad-id")

    @pytest.mark.asyncio
    async def test_cancel_orchestration(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(["ceo"], "Review")
        await engine.cancel_orchestration(orch["orchestration_id"])
        status = await engine.get_status(orch["orchestration_id"])
        assert status["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_orchestration_not_found(self):
        engine = FoundryOrchestrationEngine()
        with pytest.raises(KeyError, match="not found"):
            await engine.cancel_orchestration("bad-id")

    @pytest.mark.asyncio
    async def test_list_orchestrations(self):
        engine = FoundryOrchestrationEngine()
        await engine.create_orchestration(["ceo"], "A")
        await engine.create_orchestration(["cfo"], "B")
        orchs = engine.list_orchestrations()
        assert len(orchs) == 2

    @pytest.mark.asyncio
    async def test_orchestration_count(self):
        engine = FoundryOrchestrationEngine()
        assert engine.orchestration_count == 0
        await engine.create_orchestration(["ceo"], "A")
        assert engine.orchestration_count == 1

    @pytest.mark.asyncio
    async def test_turns_accumulate(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(["ceo", "cfo"], "Review")
        oid = orch["orchestration_id"]
        await engine.run_agent_turn(oid, "ceo", "Strategy?")
        await engine.run_agent_turn(oid, "cfo", "Budget?")
        status = await engine.get_status(oid)
        assert len(status["turns"]) == 2
