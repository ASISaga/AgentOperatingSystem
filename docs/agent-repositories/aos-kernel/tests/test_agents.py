"""Tests for FoundryAgentManager."""

import pytest

from AgentOperatingSystem.agents import FoundryAgentManager


class TestFoundryAgentManager:
    """FoundryAgentManager unit tests."""

    @pytest.mark.asyncio
    async def test_register_agent_basic(self):
        manager = FoundryAgentManager()
        record = await manager.register_agent(
            agent_id="ceo",
            purpose="Strategic leadership",
            name="CEO Agent",
        )
        assert record["agent_id"] == "ceo"
        assert record["name"] == "CEO Agent"
        assert record["purpose"] == "Strategic leadership"
        assert record["managed_by"] == "foundry_agent_service"
        assert record["foundry_agent_id"]  # non-empty

    @pytest.mark.asyncio
    async def test_register_agent_with_adapter(self):
        manager = FoundryAgentManager()
        record = await manager.register_agent(
            agent_id="cfo",
            purpose="Financial oversight",
            adapter_name="finance",
        )
        assert record["adapter_name"] == "finance"

    @pytest.mark.asyncio
    async def test_register_agent_idempotent(self):
        manager = FoundryAgentManager()
        r1 = await manager.register_agent("ceo", "Lead")
        r2 = await manager.register_agent("ceo", "Lead")
        assert r1["foundry_agent_id"] == r2["foundry_agent_id"]

    @pytest.mark.asyncio
    async def test_register_agent_with_model(self):
        manager = FoundryAgentManager()
        record = await manager.register_agent(
            agent_id="analyst",
            purpose="Data analysis",
            model="gpt-35-turbo",
        )
        assert record["model"] == "gpt-35-turbo"

    @pytest.mark.asyncio
    async def test_register_agent_with_capabilities(self):
        manager = FoundryAgentManager()
        record = await manager.register_agent(
            agent_id="ceo",
            purpose="Leadership",
            capabilities=["strategic_planning", "decision_making"],
        )
        assert record["capabilities"] == ["strategic_planning", "decision_making"]

    @pytest.mark.asyncio
    async def test_unregister_agent(self):
        manager = FoundryAgentManager()
        await manager.register_agent("ceo", "Lead")
        assert manager.agent_count == 1
        await manager.unregister_agent("ceo")
        assert manager.agent_count == 0

    @pytest.mark.asyncio
    async def test_unregister_agent_not_found(self):
        manager = FoundryAgentManager()
        with pytest.raises(KeyError, match="not registered"):
            await manager.unregister_agent("nonexistent")

    def test_get_registration(self):
        import asyncio
        manager = FoundryAgentManager()
        asyncio.get_event_loop().run_until_complete(
            manager.register_agent("ceo", "Lead")
        )
        reg = manager.get_registration("ceo")
        assert reg["agent_id"] == "ceo"

    def test_get_registration_not_found(self):
        manager = FoundryAgentManager()
        with pytest.raises(KeyError, match="not registered"):
            manager.get_registration("nonexistent")

    @pytest.mark.asyncio
    async def test_get_foundry_agent_id(self):
        manager = FoundryAgentManager()
        await manager.register_agent("ceo", "Lead")
        fid = manager.get_foundry_agent_id("ceo")
        assert isinstance(fid, str)
        assert len(fid) > 0

    @pytest.mark.asyncio
    async def test_list_registered_agents(self):
        manager = FoundryAgentManager()
        await manager.register_agent("ceo", "Lead")
        await manager.register_agent("cfo", "Finance")
        agents = manager.list_registered_agents()
        assert len(agents) == 2
        ids = {a["agent_id"] for a in agents}
        assert ids == {"ceo", "cfo"}

    @pytest.mark.asyncio
    async def test_agent_count(self):
        manager = FoundryAgentManager()
        assert manager.agent_count == 0
        await manager.register_agent("ceo", "Lead")
        assert manager.agent_count == 1
        await manager.register_agent("cfo", "Finance")
        assert manager.agent_count == 2

    @pytest.mark.asyncio
    async def test_default_model(self):
        manager = FoundryAgentManager(default_model="gpt-4o-mini")
        record = await manager.register_agent("agent1", "Purpose")
        assert record["model"] == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_register_with_tools(self):
        manager = FoundryAgentManager()
        tools = [{"type": "code_interpreter"}]
        record = await manager.register_agent(
            agent_id="dev",
            purpose="Development",
            tools=tools,
        )
        assert record["tools"] == tools
