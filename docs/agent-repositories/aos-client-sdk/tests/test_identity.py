"""Tests for Entra Agent ID and Managed Identity support."""

import pytest

from aos_client.identity import (
    AgentIdentityProvider,
    EntraAgentIdentity,
    ManagedIdentityConfig,
    TokenResult,
)


class TestTokenResult:
    """TokenResult model tests."""

    def test_create(self):
        result = TokenResult(
            token="test-token",
            scope="https://cognitiveservices.azure.com/.default",
            identity_type="managed_identity",
        )
        assert result.token == "test-token"
        assert result.identity_type == "managed_identity"
        assert result.expires_on is None


class TestManagedIdentityConfig:
    """ManagedIdentityConfig model tests."""

    def test_defaults(self):
        config = ManagedIdentityConfig()
        assert config.identity_type == "system_assigned"
        assert config.client_id is None
        assert config.resource_id is None

    def test_user_assigned(self):
        config = ManagedIdentityConfig(
            client_id="user-mi-client-id",
            identity_type="user_assigned",
        )
        assert config.identity_type == "user_assigned"
        assert config.client_id == "user-mi-client-id"


class TestEntraAgentIdentity:
    """EntraAgentIdentity unit tests."""

    def test_init_managed_identity(self):
        identity = EntraAgentIdentity(
            agent_id="ceo-agent",
            tenant_id="tenant-123",
            client_id="client-456",
        )
        assert identity.agent_id == "ceo-agent"
        assert identity.managed_identity is True
        assert identity.identity_type == "managed_identity"

    def test_init_client_credentials(self):
        identity = EntraAgentIdentity(
            agent_id="ceo-agent",
            tenant_id="tenant-123",
            client_id="client-456",
            client_secret="secret-789",
            managed_identity=False,
        )
        assert identity.managed_identity is False
        assert identity.identity_type == "client_credentials"

    def test_default_scopes(self):
        identity = EntraAgentIdentity(
            agent_id="test", tenant_id="t", client_id="c",
        )
        assert "https://cognitiveservices.azure.com/.default" in identity.scopes

    def test_custom_scopes(self):
        identity = EntraAgentIdentity(
            agent_id="test",
            tenant_id="t",
            client_id="c",
            scopes=["https://custom.scope/.default"],
        )
        assert identity.scopes == ["https://custom.scope/.default"]

    @pytest.mark.asyncio
    async def test_get_token(self):
        identity = EntraAgentIdentity(
            agent_id="test", tenant_id="t", client_id="c",
        )
        result = await identity.get_token()
        assert isinstance(result, TokenResult)
        assert result.token != ""
        assert result.identity_type == "managed_identity"

    @pytest.mark.asyncio
    async def test_get_agent_headers(self):
        identity = EntraAgentIdentity(
            agent_id="ceo", tenant_id="t", client_id="c",
        )
        headers = await identity.get_agent_headers()
        assert "Authorization" in headers
        assert "X-Agent-ID" in headers
        assert headers["X-Agent-ID"] == "ceo"

    @pytest.mark.asyncio
    async def test_validate(self):
        identity = EntraAgentIdentity(
            agent_id="test", tenant_id="t", client_id="c",
        )
        valid = await identity.validate()
        assert valid is True


class TestAgentIdentityProvider:
    """AgentIdentityProvider unit tests."""

    def test_init(self):
        provider = AgentIdentityProvider(tenant_id="tenant-123")
        assert provider.tenant_id == "tenant-123"

    def test_register_agent(self):
        provider = AgentIdentityProvider(tenant_id="tenant-123")
        identity = provider.register_agent(
            agent_id="ceo", client_id="client-001"
        )
        assert isinstance(identity, EntraAgentIdentity)
        assert identity.agent_id == "ceo"

    def test_get_agent_identity(self):
        provider = AgentIdentityProvider(tenant_id="tenant-123")
        provider.register_agent(agent_id="ceo", client_id="c1")
        identity = provider.get_agent_identity("ceo")
        assert identity.agent_id == "ceo"

    def test_get_agent_identity_not_found(self):
        provider = AgentIdentityProvider(tenant_id="tenant-123")
        with pytest.raises(KeyError):
            provider.get_agent_identity("nonexistent")

    def test_list_agents(self):
        provider = AgentIdentityProvider(tenant_id="tenant-123")
        provider.register_agent("ceo", "c1")
        provider.register_agent("cmo", "c2")
        agents = provider.list_agents()
        assert "ceo" in agents
        assert "cmo" in agents
        assert len(agents) == 2

    def test_remove_agent(self):
        provider = AgentIdentityProvider(tenant_id="tenant-123")
        provider.register_agent("ceo", "c1")
        provider.remove_agent("ceo")
        assert "ceo" not in provider.list_agents()

    def test_remove_agent_not_found(self):
        provider = AgentIdentityProvider(tenant_id="tenant-123")
        with pytest.raises(KeyError):
            provider.remove_agent("nonexistent")
