"""Tests for Azure AI Foundry Agent Service integration (internal to AOS)."""

import pytest

from aos_client.foundry import (
    AIProjectClient,
    AzureAIAgent,
    FoundryAgentService,
    FoundryRun,
    FoundryThread,
)


class TestFoundryNotExportedFromSDK:
    """Foundry classes must NOT be in the public SDK API."""

    def test_foundry_classes_not_in_all(self):
        import aos_client

        for name in [
            "AIProjectClient", "AzureAIAgent", "FoundryAgentService",
            "FoundryThread", "FoundryRun", "FoundryAgentConfig",
            "FoundryOrchestrationRequest", "FoundryConnectionInfo",
            "AIGateway", "GatewayConfig",
            "AgentIdentityProvider", "EntraAgentIdentity",
            "ManagedIdentityConfig", "TokenResult",
        ]:
            assert name not in aos_client.__all__, (
                f"{name} must not be in the public SDK __all__"
            )

    def test_foundry_classes_not_importable_from_top_level(self):
        import aos_client

        for name in [
            "AIProjectClient", "AzureAIAgent", "FoundryAgentService",
            "FoundryThread", "FoundryRun",
            "AIGateway", "GatewayConfig",
            "AgentIdentityProvider", "EntraAgentIdentity",
            "ManagedIdentityConfig", "TokenResult",
        ]:
            assert not hasattr(aos_client, name), (
                f"{name} must not be importable from aos_client"
            )

    def test_foundry_models_not_importable_from_top_level(self):
        import aos_client

        for name in [
            "FoundryAgentConfig", "FoundryOrchestrationRequest",
            "FoundryConnectionInfo",
        ]:
            assert not hasattr(aos_client, name), (
                f"{name} must not be importable from aos_client"
            )

    def test_foundry_client_methods_not_on_sdk_client(self):
        """submit_foundry_orchestration etc. must not be on AOSClient."""
        from aos_client.client import AOSClient

        client = AOSClient(endpoint="https://example.com")
        for method_name in [
            "submit_foundry_orchestration",
            "get_foundry_connection",
            "list_foundry_agents",
            "create_foundry_agent",
        ]:
            assert not hasattr(client, method_name), (
                f"AOSClient must not have {method_name}"
            )


class TestAzureAIAgent:
    """AzureAIAgent unit tests."""

    def test_create_minimal(self):
        agent = AzureAIAgent(agent_id="a1", model="gpt-4o")
        assert agent.agent_id == "a1"
        assert agent.model == "gpt-4o"
        assert agent.name == ""
        assert agent.tools == []
        assert agent.tool_resources == {}
        assert agent.metadata == {}

    def test_create_full(self):
        agent = AzureAIAgent(
            agent_id="analyst-01",
            model="gpt-4o",
            name="Financial Analyst",
            instructions="You are a senior financial analyst.",
            tools=[{"type": "code_interpreter"}],
            tool_resources={"code_interpreter": {"file_ids": []}},
            metadata={"team": "finance"},
        )
        assert agent.name == "Financial Analyst"
        assert len(agent.tools) == 1
        assert agent.metadata["team"] == "finance"

    def test_update(self):
        agent = AzureAIAgent(agent_id="a1", model="gpt-4o", name="Old")
        agent.update(name="New", instructions="Updated instructions")
        assert agent.name == "New"
        assert agent.instructions == "Updated instructions"

    def test_update_partial(self):
        agent = AzureAIAgent(agent_id="a1", model="gpt-4o", name="Keep")
        agent.update(instructions="Only this changes")
        assert agent.name == "Keep"
        assert agent.instructions == "Only this changes"

    def test_to_dict(self):
        agent = AzureAIAgent(agent_id="a1", model="gpt-4o", name="Test")
        d = agent.to_dict()
        assert d["agent_id"] == "a1"
        assert d["model"] == "gpt-4o"
        assert d["name"] == "Test"
        assert "tools" in d
        assert "metadata" in d


class TestFoundryRun:
    """FoundryRun unit tests."""

    def test_create(self):
        run = FoundryRun(run_id="r1", thread_id="t1", agent_id="a1")
        assert run.status == "queued"

    @pytest.mark.asyncio
    async def test_cancel(self):
        run = FoundryRun(run_id="r1", thread_id="t1", agent_id="a1")
        await run.cancel()
        assert run.status == "cancelled"

    @pytest.mark.asyncio
    async def test_poll_does_not_error(self):
        run = FoundryRun(run_id="r1", thread_id="t1", agent_id="a1")
        await run.poll()
        assert run.status == "queued"

    def test_to_dict(self):
        run = FoundryRun(run_id="r1", thread_id="t1", agent_id="a1")
        d = run.to_dict()
        assert d["run_id"] == "r1"
        assert d["thread_id"] == "t1"
        assert d["agent_id"] == "a1"
        assert d["status"] == "queued"


class TestFoundryThread:
    """FoundryThread unit tests."""

    def test_create(self):
        thread = FoundryThread(thread_id="t1")
        assert thread.thread_id == "t1"
        assert thread.metadata == {}

    @pytest.mark.asyncio
    async def test_add_message(self):
        thread = FoundryThread(thread_id="t1")
        msg = await thread.add_message(role="user", content="Hello")
        assert msg["role"] == "user"
        assert msg["content"] == "Hello"
        assert msg["thread_id"] == "t1"

    @pytest.mark.asyncio
    async def test_list_messages(self):
        thread = FoundryThread(thread_id="t1")
        await thread.add_message(role="user", content="A")
        await thread.add_message(role="assistant", content="B")
        msgs = await thread.list_messages()
        assert len(msgs) == 2

    @pytest.mark.asyncio
    async def test_create_run(self):
        thread = FoundryThread(thread_id="t1")
        run = await thread.create_run(agent_id="a1")
        assert run.thread_id == "t1"
        assert run.agent_id == "a1"
        assert run.status == "queued"

    def test_to_dict(self):
        thread = FoundryThread(thread_id="t1", metadata={"key": "val"})
        d = thread.to_dict()
        assert d["thread_id"] == "t1"
        assert d["metadata"]["key"] == "val"


class TestAIProjectClient:
    """AIProjectClient unit tests."""

    def test_init(self):
        client = AIProjectClient(project_endpoint="https://example.com/api/v1")
        assert client.project_endpoint == "https://example.com/api/v1"

    def test_trailing_slash_stripped(self):
        client = AIProjectClient(project_endpoint="https://example.com/api/v1/")
        assert client.project_endpoint == "https://example.com/api/v1"

    @pytest.mark.asyncio
    async def test_create_agent(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        agent = await client.create_agent(
            model="gpt-4o",
            name="Test Agent",
            instructions="Be helpful.",
        )
        assert isinstance(agent, AzureAIAgent)
        assert agent.model == "gpt-4o"
        assert agent.name == "Test Agent"
        assert agent.agent_id in client._agents

    @pytest.mark.asyncio
    async def test_list_agents(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        await client.create_agent(model="gpt-4o", name="A1")
        await client.create_agent(model="gpt-4o", name="A2")
        agents = await client.list_agents()
        assert len(agents) == 2

    @pytest.mark.asyncio
    async def test_get_agent(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        created = await client.create_agent(model="gpt-4o", name="Lookup")
        retrieved = await client.get_agent(created.agent_id)
        assert retrieved.agent_id == created.agent_id

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        with pytest.raises(KeyError):
            await client.get_agent("nonexistent")

    @pytest.mark.asyncio
    async def test_delete_agent(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        agent = await client.create_agent(model="gpt-4o", name="Del")
        await client.delete_agent(agent.agent_id)
        assert agent.agent_id not in client._agents

    @pytest.mark.asyncio
    async def test_create_thread(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        thread = await client.create_thread()
        assert isinstance(thread, FoundryThread)
        assert thread.thread_id in client._threads

    @pytest.mark.asyncio
    async def test_get_thread(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        created = await client.create_thread()
        retrieved = await client.get_thread(created.thread_id)
        assert retrieved.thread_id == created.thread_id

    @pytest.mark.asyncio
    async def test_get_thread_not_found(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        with pytest.raises(KeyError):
            await client.get_thread("nonexistent")

    @pytest.mark.asyncio
    async def test_delete_thread(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        thread = await client.create_thread()
        await client.delete_thread(thread.thread_id)
        assert thread.thread_id not in client._threads

    @pytest.mark.asyncio
    async def test_health_check(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        health = await client.health_check()
        assert health["status"] == "ok"


class TestFoundryAgentService:
    """FoundryAgentService unit tests."""

    @pytest.mark.asyncio
    async def test_register_agent(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        service = FoundryAgentService(project_client=client)
        agent = await service.register_agent(
            agent_id="ceo",
            model="gpt-4o",
            name="CEO Agent",
            instructions="You are the CEO.",
        )
        assert agent.agent_id == "ceo"
        assert agent.name == "CEO Agent"

    @pytest.mark.asyncio
    async def test_register_agent_idempotent(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        service = FoundryAgentService(project_client=client)
        a1 = await service.register_agent("ceo", "gpt-4o", "CEO", "instructions")
        a2 = await service.register_agent("ceo", "gpt-4o", "CEO", "instructions")
        assert a1 is a2

    @pytest.mark.asyncio
    async def test_create_orchestration(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        service = FoundryAgentService(project_client=client)
        await service.register_agent("ceo", "gpt-4o", "CEO", "Lead")
        result = await service.create_orchestration(
            agent_ids=["ceo"],
            purpose="Strategic review",
            context={"quarter": "Q1"},
        )
        assert "orchestration_id" in result
        assert "thread_id" in result

    @pytest.mark.asyncio
    async def test_run_agent_turn(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        service = FoundryAgentService(project_client=client)
        await service.register_agent("ceo", "gpt-4o", "CEO", "Lead")
        orch = await service.create_orchestration(["ceo"], "Review")
        turn = await service.run_agent_turn(
            orch["orchestration_id"], "ceo", "What is the strategy?"
        )
        assert turn["agent_id"] == "ceo"
        assert "run_id" in turn

    @pytest.mark.asyncio
    async def test_run_agent_turn_unknown_orchestration(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        service = FoundryAgentService(project_client=client)
        with pytest.raises(KeyError):
            await service.run_agent_turn("nonexistent", "ceo", "msg")

    @pytest.mark.asyncio
    async def test_get_orchestration_status(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        service = FoundryAgentService(project_client=client)
        orch = await service.create_orchestration(["ceo"], "Review")
        status = await service.get_orchestration_status(orch["orchestration_id"])
        assert status["status"] == "active"
        assert status["purpose"] == "Review"

    @pytest.mark.asyncio
    async def test_stop_orchestration(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        service = FoundryAgentService(project_client=client)
        orch = await service.create_orchestration(["ceo"], "Review")
        await service.stop_orchestration(orch["orchestration_id"])
        status = await service.get_orchestration_status(orch["orchestration_id"])
        assert status["status"] == "stopped"

    @pytest.mark.asyncio
    async def test_stop_orchestration_unknown(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        service = FoundryAgentService(project_client=client)
        with pytest.raises(KeyError):
            await service.stop_orchestration("nonexistent")

    @pytest.mark.asyncio
    async def test_list_registered_agents(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        service = FoundryAgentService(project_client=client)
        await service.register_agent("ceo", "gpt-4o", "CEO", "Lead")
        await service.register_agent("cmo", "gpt-4o", "CMO", "Market")
        agents = await service.list_registered_agents()
        assert len(agents) == 2

    def test_gateway_url(self):
        client = AIProjectClient(project_endpoint="https://example.com")
        service = FoundryAgentService(
            project_client=client, gateway_url="https://gateway.example.com"
        )
        assert service.gateway_url == "https://gateway.example.com"
