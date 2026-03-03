"""Tests for FoundryMessageBridge."""

import pytest

from AgentOperatingSystem.messaging import FoundryMessageBridge
from AgentOperatingSystem.orchestration import FoundryOrchestrationEngine


class TestFoundryMessageBridge:
    """FoundryMessageBridge unit tests."""

    @pytest.mark.asyncio
    async def test_deliver_to_agent(self):
        bridge = FoundryMessageBridge()
        result = await bridge.deliver_to_agent(
            agent_id="ceo",
            message="What is the strategy?",
        )
        assert result["agent_id"] == "ceo"
        assert result["direction"] == "foundry_to_agent"
        assert result["status"] == "delivered"
        assert result["content"] == "What is the strategy?"

    @pytest.mark.asyncio
    async def test_deliver_to_agent_with_orchestration(self):
        bridge = FoundryMessageBridge()
        result = await bridge.deliver_to_agent(
            agent_id="ceo",
            message="Review Q1",
            orchestration_id="orch-123",
        )
        assert result["orchestration_id"] == "orch-123"

    @pytest.mark.asyncio
    async def test_deliver_to_agent_with_metadata(self):
        bridge = FoundryMessageBridge()
        result = await bridge.deliver_to_agent(
            agent_id="ceo",
            message="msg",
            metadata={"priority": "high"},
        )
        assert result["metadata"]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_send_to_foundry(self):
        bridge = FoundryMessageBridge()
        result = await bridge.send_to_foundry(
            agent_id="ceo",
            message="Strategy is growth-focused",
        )
        assert result["agent_id"] == "ceo"
        assert result["direction"] == "agent_to_foundry"
        assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_to_foundry_with_orchestration(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(["ceo"], "Review")
        oid = orch["orchestration_id"]

        bridge = FoundryMessageBridge(orchestration_engine=engine)
        result = await bridge.send_to_foundry(
            agent_id="ceo",
            message="Response from CEO",
            orchestration_id=oid,
        )
        assert result["orchestration_id"] == oid

        # Verify the turn was recorded in the orchestration
        status = await engine.get_status(oid)
        assert len(status["turns"]) == 1

    @pytest.mark.asyncio
    async def test_broadcast_purpose_alignment(self):
        engine = FoundryOrchestrationEngine()
        orch = await engine.create_orchestration(["ceo", "cfo"], "Initial")
        oid = orch["orchestration_id"]

        bridge = FoundryMessageBridge(orchestration_engine=engine)
        results = await bridge.broadcast_purpose_alignment(
            orchestration_id=oid,
            purpose="New strategic direction",
            purpose_scope="C-suite alignment",
        )
        assert len(results) == 2
        for r in results:
            assert r["direction"] == "foundry_to_agent"
            assert r["metadata"]["type"] == "purpose_alignment"

    @pytest.mark.asyncio
    async def test_broadcast_purpose_alignment_no_engine(self):
        bridge = FoundryMessageBridge()
        results = await bridge.broadcast_purpose_alignment("orch-123", "Purpose")
        assert results == []

    @pytest.mark.asyncio
    async def test_broadcast_purpose_alignment_bad_orchestration(self):
        engine = FoundryOrchestrationEngine()
        bridge = FoundryMessageBridge(orchestration_engine=engine)
        results = await bridge.broadcast_purpose_alignment("bad-id", "Purpose")
        assert results == []

    @pytest.mark.asyncio
    async def test_get_messages_all(self):
        bridge = FoundryMessageBridge()
        await bridge.deliver_to_agent("ceo", "msg1")
        await bridge.send_to_foundry("ceo", "msg2")
        msgs = bridge.get_messages()
        assert len(msgs) == 2

    @pytest.mark.asyncio
    async def test_get_messages_by_agent(self):
        bridge = FoundryMessageBridge()
        await bridge.deliver_to_agent("ceo", "msg1")
        await bridge.deliver_to_agent("cfo", "msg2")
        msgs = bridge.get_messages(agent_id="ceo")
        assert len(msgs) == 1
        assert msgs[0]["agent_id"] == "ceo"

    @pytest.mark.asyncio
    async def test_get_messages_by_direction(self):
        bridge = FoundryMessageBridge()
        await bridge.deliver_to_agent("ceo", "msg1")
        await bridge.send_to_foundry("ceo", "msg2")
        inbound = bridge.get_messages(direction="foundry_to_agent")
        assert len(inbound) == 1
        outbound = bridge.get_messages(direction="agent_to_foundry")
        assert len(outbound) == 1

    @pytest.mark.asyncio
    async def test_get_messages_by_orchestration(self):
        bridge = FoundryMessageBridge()
        await bridge.deliver_to_agent("ceo", "msg1", orchestration_id="orch-1")
        await bridge.deliver_to_agent("ceo", "msg2", orchestration_id="orch-2")
        msgs = bridge.get_messages(orchestration_id="orch-1")
        assert len(msgs) == 1

    @pytest.mark.asyncio
    async def test_message_count(self):
        bridge = FoundryMessageBridge()
        assert bridge.message_count == 0
        await bridge.deliver_to_agent("ceo", "msg1")
        assert bridge.message_count == 1
        await bridge.send_to_foundry("ceo", "msg2")
        assert bridge.message_count == 2
