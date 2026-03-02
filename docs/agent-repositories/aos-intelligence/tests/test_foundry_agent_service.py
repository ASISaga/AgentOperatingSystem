"""
Tests for the refactored FoundryAgentServiceClient (azure-ai-projects v2).

All Azure SDK calls are mocked so no real credentials or network access
are required.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock

from aos_intelligence.ml.foundry_agent_service import (
    FoundryAgentServiceClient,
    FoundryAgentServiceConfig,
    FoundryResponse,
    ThreadInfo,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config():
    return FoundryAgentServiceConfig(
        endpoint_url="https://test.services.ai.azure.com/api/projects/test-project",
        agent_name="aos-test-agent",
        model="llama-3.3-70b",
        enable_stateful_threads=True,
        enable_foundry_tools=True,
        temperature=0.7,
        max_tokens=512,
        top_p=0.9,
        aos_orchestration_id="orch-001",
    )


@pytest.fixture
def mock_openai_client():
    """Minimal mock of the OpenAI-compatible client returned by get_openai_client()."""
    client = MagicMock()

    # --- threads ---
    thread_obj = MagicMock()
    thread_obj.id = "thread-abc"
    client.beta.threads.create.return_value = thread_obj
    client.beta.threads.delete.return_value = None

    # --- messages ---
    client.beta.threads.messages.create.return_value = MagicMock()

    # Build a fake assistant message list
    text_block = MagicMock()
    text_block.text.value = "Mocked assistant reply"
    msg_obj = MagicMock()
    msg_obj.role = "assistant"
    msg_obj.content = [text_block]
    client.beta.threads.messages.list.return_value = [msg_obj]

    # --- runs ---
    usage = MagicMock()
    usage.prompt_tokens = 10
    usage.completion_tokens = 20
    usage.total_tokens = 30
    run_obj = MagicMock()
    run_obj.id = "run-xyz"
    run_obj.status = "completed"
    run_obj.usage = usage
    client.beta.threads.runs.create_and_poll.return_value = run_obj

    # --- chat completions (single-turn) ---
    choice = MagicMock()
    choice.message.content = "Single-turn reply"
    completion_usage = MagicMock()
    completion_usage.prompt_tokens = 5
    completion_usage.completion_tokens = 10
    completion_usage.total_tokens = 15
    completion = MagicMock()
    completion.choices = [choice]
    completion.usage = completion_usage
    client.chat.completions.create.return_value = completion

    return client


@pytest.fixture
def mock_project_client(mock_openai_client):
    """Minimal mock of AIProjectClient."""
    pc = MagicMock()
    pc.get_openai_client.return_value = mock_openai_client

    # agents.list returns one fake agent
    fake_agent = MagicMock()
    fake_agent.name = "aos-test-agent"
    pc.agents.list.return_value = [fake_agent]

    # agents.get returns the fake agent details
    pc.agents.get.return_value = fake_agent

    # agents.create_version returns fake version details
    version = MagicMock()
    version.version = "1"
    version.name = "aos-test-agent"
    pc.agents.create_version.return_value = version

    return pc


@pytest.fixture
def initialized_client(config, mock_project_client, mock_openai_client):
    """Return a FoundryAgentServiceClient that is already initialised."""
    client = FoundryAgentServiceClient(config)
    client._project_client = mock_project_client
    client._openai_client = mock_openai_client
    client._initialized = True
    return client


# ---------------------------------------------------------------------------
# FoundryAgentServiceConfig tests
# ---------------------------------------------------------------------------

class TestFoundryAgentServiceConfig:
    def test_defaults(self):
        cfg = FoundryAgentServiceConfig()
        assert cfg.endpoint_url == ""
        assert cfg.agent_name == ""
        assert cfg.model == "llama-3.3-70b"
        assert cfg.enable_stateful_threads is True
        assert cfg.enable_foundry_tools is True
        assert cfg.temperature == 0.7
        assert cfg.max_tokens == 4096
        assert cfg.top_p == 0.9
        assert cfg.aos_orchestration_id == ""

    def test_from_env_defaults(self, monkeypatch):
        for key in (
            "FOUNDRY_ENDPOINT", "FOUNDRY_AGENT_NAME", "FOUNDRY_MODEL",
            "FOUNDRY_ENABLE_STATEFUL_THREADS", "FOUNDRY_ENABLE_FOUNDRY_TOOLS",
            "FOUNDRY_TIMEOUT", "FOUNDRY_MAX_RETRIES",
            "FOUNDRY_TEMPERATURE", "FOUNDRY_MAX_TOKENS", "FOUNDRY_TOP_P",
            "AOS_ORCHESTRATION_ID",
        ):
            monkeypatch.delenv(key, raising=False)

        cfg = FoundryAgentServiceConfig.from_env()
        assert cfg.endpoint_url == ""
        assert cfg.model == "llama-3.3-70b"
        assert cfg.enable_stateful_threads is True
        assert cfg.aos_orchestration_id == ""

    def test_from_env_overrides(self, monkeypatch):
        monkeypatch.setenv("FOUNDRY_ENDPOINT", "https://myproject.ai.azure.com")
        monkeypatch.setenv("FOUNDRY_AGENT_NAME", "my-agent")
        monkeypatch.setenv("FOUNDRY_MODEL", "gpt-4o")
        monkeypatch.setenv("FOUNDRY_ENABLE_STATEFUL_THREADS", "false")
        monkeypatch.setenv("AOS_ORCHESTRATION_ID", "orch-999")

        cfg = FoundryAgentServiceConfig.from_env()
        assert cfg.endpoint_url == "https://myproject.ai.azure.com"
        assert cfg.agent_name == "my-agent"
        assert cfg.model == "gpt-4o"
        assert cfg.enable_stateful_threads is False
        assert cfg.aos_orchestration_id == "orch-999"

    def test_no_api_key_field(self):
        """The refactored config must NOT have an api_key field."""
        cfg = FoundryAgentServiceConfig()
        assert not hasattr(cfg, "api_key"), "api_key must be removed; auth uses DefaultAzureCredential"

    def test_no_entra_agent_id_flag(self):
        """enable_entra_agent_id was removed; auth is always via DefaultAzureCredential."""
        cfg = FoundryAgentServiceConfig()
        assert not hasattr(cfg, "enable_entra_agent_id")


# ---------------------------------------------------------------------------
# ThreadInfo / FoundryResponse dataclasses
# ---------------------------------------------------------------------------

class TestDataclasses:
    def test_thread_info_defaults(self):
        ti = ThreadInfo(thread_id="t1", agent_name="agent-a")
        assert ti.thread_id == "t1"
        assert ti.agent_name == "agent-a"
        assert ti.message_count == 0
        assert ti.last_accessed is None

    def test_foundry_response_defaults(self):
        fr = FoundryResponse(content="hello")
        assert fr.success is True
        assert fr.error is None
        assert fr.tools_used == []

    def test_foundry_response_error(self):
        fr = FoundryResponse(content="", success=False, error="timeout")
        assert fr.success is False
        assert fr.error == "timeout"


# ---------------------------------------------------------------------------
# FoundryAgentServiceClient — initialisation
# ---------------------------------------------------------------------------

class TestInitialisation:
    @pytest.mark.asyncio
    async def test_initialize_raises_without_endpoint(self):
        client = FoundryAgentServiceClient(FoundryAgentServiceConfig(endpoint_url=""))
        with pytest.raises(ValueError, match="endpoint"):
            await client.initialize()

    @pytest.mark.asyncio
    async def test_initialize_uses_default_azure_credential(self, config):
        """initialize() must use DefaultAzureCredential, not an API key."""
        with (
            patch("azure.ai.projects.AIProjectClient") as mock_cls,
            patch("azure.identity.DefaultAzureCredential") as mock_cred,
        ):
            mock_instance = MagicMock()
            mock_instance.get_openai_client.return_value = MagicMock()
            mock_cls.return_value = mock_instance

            client = FoundryAgentServiceClient(config)
            await client.initialize()

            mock_cred.assert_called_once()
            mock_cls.assert_called_once_with(
                endpoint=config.endpoint_url,
                credential=mock_cred.return_value,
            )
            assert client._initialized is True

    @pytest.mark.asyncio
    async def test_initialize_idempotent(self, initialized_client):
        """Calling initialize() a second time must be a no-op."""
        initialized_client._project_client = MagicMock()  # replace to detect re-call
        await initialized_client.initialize()
        # If idempotent, we never replaced _project_client
        assert initialized_client._initialized is True

    def test_close_resets_state(self, initialized_client):
        initialized_client.close()
        assert initialized_client._project_client is None
        assert initialized_client._openai_client is None
        assert initialized_client._initialized is False


# ---------------------------------------------------------------------------
# Agent management
# ---------------------------------------------------------------------------

class TestAgentManagement:
    def test_create_or_update_agent(self, initialized_client, mock_project_client):
        version = initialized_client.create_or_update_agent(
            agent_name="aos-test-agent",
            instructions="Be helpful.",
            description="Test agent",
        )
        mock_project_client.agents.create_version.assert_called_once()
        assert version.version == "1"

    def test_create_or_update_agent_uses_config_name(self, initialized_client, mock_project_client):
        """If agent_name omitted, config.agent_name is used."""
        initialized_client.create_or_update_agent()
        call_kwargs = mock_project_client.agents.create_version.call_args
        assert call_kwargs.kwargs["agent_name"] == initialized_client.config.agent_name

    def test_create_or_update_agent_raises_without_name(self, initialized_client):
        initialized_client.config.agent_name = ""
        with pytest.raises(ValueError, match="agent_name"):
            initialized_client.create_or_update_agent()

    def test_get_agent(self, initialized_client, mock_project_client):
        result = initialized_client.get_agent()
        mock_project_client.agents.get.assert_called_once_with(agent_name="aos-test-agent")
        assert result.name == "aos-test-agent"

    def test_list_agents(self, initialized_client, mock_project_client):
        agents = initialized_client.list_agents(limit=5)
        mock_project_client.agents.list.assert_called_once_with(limit=5)
        assert len(agents) == 1

    def test_agent_management_requires_initialization(self, config):
        client = FoundryAgentServiceClient(config)
        with pytest.raises(RuntimeError, match="initialised"):
            client.get_agent()
        with pytest.raises(RuntimeError, match="initialised"):
            client.list_agents()
        with pytest.raises(RuntimeError, match="initialised"):
            client.create_or_update_agent(agent_name="x")


# ---------------------------------------------------------------------------
# Thread management
# ---------------------------------------------------------------------------

class TestThreadManagement:
    @pytest.mark.asyncio
    async def test_create_thread(self, initialized_client, mock_openai_client):
        thread_id = await initialized_client.create_thread()
        assert thread_id == "thread-abc"
        mock_openai_client.beta.threads.create.assert_called_once()
        assert thread_id in initialized_client.active_threads

    @pytest.mark.asyncio
    async def test_create_thread_disabled(self, initialized_client):
        initialized_client.config.enable_stateful_threads = False
        with pytest.raises(ValueError, match="disabled"):
            await initialized_client.create_thread()

    @pytest.mark.asyncio
    async def test_get_thread_info(self, initialized_client, mock_openai_client):
        thread_id = await initialized_client.create_thread()
        info = await initialized_client.get_thread_info(thread_id)
        assert info is not None
        assert info.thread_id == thread_id

    @pytest.mark.asyncio
    async def test_get_thread_info_unknown(self, initialized_client):
        info = await initialized_client.get_thread_info("nonexistent")
        assert info is None

    @pytest.mark.asyncio
    async def test_delete_thread(self, initialized_client, mock_openai_client):
        thread_id = await initialized_client.create_thread()
        result = await initialized_client.delete_thread(thread_id)
        assert result is True
        assert thread_id not in initialized_client.active_threads
        mock_openai_client.beta.threads.delete.assert_called_once_with(thread_id)

    @pytest.mark.asyncio
    async def test_delete_thread_missing(self, initialized_client):
        result = await initialized_client.delete_thread("ghost-thread")
        assert result is False


# ---------------------------------------------------------------------------
# send_message — stateful thread path
# ---------------------------------------------------------------------------

class TestSendMessageThread:
    @pytest.mark.asyncio
    async def test_send_message_with_thread(self, initialized_client, mock_openai_client):
        thread_id = await initialized_client.create_thread()
        response = await initialized_client.send_message(
            "Hello", thread_id=thread_id, domain="analytics"
        )
        assert response.success is True
        assert response.content == "Mocked assistant reply"
        assert response.thread_id == thread_id
        assert response.usage["total_tokens"] == 30

    @pytest.mark.asyncio
    async def test_send_message_updates_thread_info(self, initialized_client, mock_openai_client):
        thread_id = await initialized_client.create_thread()
        await initialized_client.send_message("Msg", thread_id=thread_id)
        info = await initialized_client.get_thread_info(thread_id)
        assert info.message_count == 1

    @pytest.mark.asyncio
    async def test_send_message_attaches_aos_orchestration_id(
        self, initialized_client, mock_openai_client
    ):
        thread_id = await initialized_client.create_thread()
        response = await initialized_client.send_message("Q", thread_id=thread_id)
        assert response.metadata.get("aos_orchestration_id") == "orch-001"

    @pytest.mark.asyncio
    async def test_send_message_with_system_prompt(self, initialized_client, mock_openai_client):
        thread_id = await initialized_client.create_thread()
        await initialized_client.send_message(
            "Tell me about risks",
            thread_id=thread_id,
            system_prompt="You are a risk analyst.",
        )
        run_call = mock_openai_client.beta.threads.runs.create_and_poll.call_args
        assert run_call.kwargs.get("additional_instructions") == "You are a risk analyst."


# ---------------------------------------------------------------------------
# send_message — single-turn (no thread) path
# ---------------------------------------------------------------------------

class TestSendMessageSingleTurn:
    @pytest.mark.asyncio
    async def test_send_message_no_thread(self, initialized_client, mock_openai_client):
        response = await initialized_client.send_message("Hello")
        assert response.success is True
        assert response.content == "Single-turn reply"
        assert response.thread_id is None
        assert response.usage["total_tokens"] == 15

    @pytest.mark.asyncio
    async def test_send_message_no_thread_with_domain(self, initialized_client, mock_openai_client):
        await initialized_client.send_message("Analyse KPIs", domain="finance")
        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args.kwargs.get("messages", call_args[1].get("messages", []))
        # Find system message
        system_msgs = [m for m in messages if m.get("role") == "system"]
        assert any("finance" in m["content"] for m in system_msgs)

    @pytest.mark.asyncio
    async def test_send_message_error_returns_failure_response(
        self, initialized_client, mock_openai_client
    ):
        mock_openai_client.chat.completions.create.side_effect = RuntimeError("network error")
        response = await initialized_client.send_message("Hi")
        assert response.success is False
        assert "network error" in response.error


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

class TestMetrics:
    @pytest.mark.asyncio
    async def test_metrics_track_success(self, initialized_client, mock_openai_client):
        await initialized_client.send_message("ping")
        metrics = initialized_client.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["failed_requests"] == 0

    @pytest.mark.asyncio
    async def test_metrics_track_failure(self, initialized_client, mock_openai_client):
        mock_openai_client.chat.completions.create.side_effect = RuntimeError("boom")
        await initialized_client.send_message("ping")
        metrics = initialized_client.get_metrics()
        assert metrics["failed_requests"] == 1

    def test_get_metrics_returns_copy(self, initialized_client):
        metrics = initialized_client.get_metrics()
        metrics["total_requests"] = 999
        assert initialized_client.metrics["total_requests"] == 0


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_success(self, initialized_client):
        assert await initialized_client.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, initialized_client, mock_project_client):
        mock_project_client.agents.list.side_effect = RuntimeError("unreachable")
        assert await initialized_client.health_check() is False
