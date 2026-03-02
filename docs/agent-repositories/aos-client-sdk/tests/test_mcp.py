"""Tests for the SDK MCP client types and OrchestrationRequest.mcp_servers.

The SDK only exposes MCPServerConfig (server selection + secrets).
Transport implementation details (MCPTransportType, urls, gateway, etc.)
are internal to AOS and are NOT part of the SDK.
"""

import pytest

from aos_client import MCPServerConfig
from aos_client.models import OrchestrationPurpose, OrchestrationRequest


# ---------------------------------------------------------------------------
# MCPServerConfig
# ---------------------------------------------------------------------------


class TestMCPServerConfig:
    def test_server_name_required(self) -> None:
        cfg = MCPServerConfig(server_name="erp")
        assert cfg.server_name == "erp"

    def test_secrets_default_empty(self) -> None:
        cfg = MCPServerConfig(server_name="erp")
        assert cfg.secrets == {}

    def test_secrets_provided(self) -> None:
        cfg = MCPServerConfig(
            server_name="erp",
            secrets={"api_key": "secret-key", "api_secret": "secret-value"},
        )
        assert cfg.secrets["api_key"] == "secret-key"
        assert cfg.secrets["api_secret"] == "secret-value"

    def test_pydantic_serialisation(self) -> None:
        cfg = MCPServerConfig(server_name="crm", secrets={"token": "tok123"})
        data = cfg.model_dump()
        assert data["server_name"] == "crm"
        assert data["secrets"] == {"token": "tok123"}

    def test_pydantic_deserialisation(self) -> None:
        cfg = MCPServerConfig.model_validate({"server_name": "analytics"})
        assert cfg.server_name == "analytics"
        assert cfg.secrets == {}

    def test_no_transport_type_field(self) -> None:
        """Transport details are internal to AOS and must not be on MCPServerConfig."""
        cfg = MCPServerConfig(server_name="erp")
        assert not hasattr(cfg, "transport_type")

    def test_no_url_field(self) -> None:
        """Server URLs are internal to AOS."""
        cfg = MCPServerConfig(server_name="erp")
        assert not hasattr(cfg, "url")

    def test_no_gateway_url_field(self) -> None:
        """AI Gateway URLs are internal to AOS."""
        cfg = MCPServerConfig(server_name="erp")
        assert not hasattr(cfg, "gateway_url")

    def test_no_command_field(self) -> None:
        """Subprocess commands are internal to AOS."""
        cfg = MCPServerConfig(server_name="local-fs")
        assert not hasattr(cfg, "command")

    def test_json_round_trip(self) -> None:
        cfg = MCPServerConfig(server_name="erp", secrets={"api_key": "k"})
        data = cfg.model_dump(mode="json")
        cfg2 = MCPServerConfig.model_validate(data)
        assert cfg2.server_name == "erp"
        assert cfg2.secrets["api_key"] == "k"


# ---------------------------------------------------------------------------
# OrchestrationRequest.mcp_servers
# ---------------------------------------------------------------------------


class TestOrchestrationRequestMCPServers:
    def test_mcp_servers_defaults_to_empty(self) -> None:
        request = OrchestrationRequest(
            agent_ids=["ceo"],
            purpose=OrchestrationPurpose(purpose="Drive growth"),
        )
        assert request.mcp_servers == {}

    def test_mcp_servers_single_agent(self) -> None:
        cfg = MCPServerConfig(server_name="erp", secrets={"api_key": "k"})
        request = OrchestrationRequest(
            agent_ids=["ceo"],
            purpose=OrchestrationPurpose(purpose="Drive growth"),
            mcp_servers={"ceo": [cfg]},
        )
        assert "ceo" in request.mcp_servers
        assert request.mcp_servers["ceo"][0].server_name == "erp"
        assert request.mcp_servers["ceo"][0].secrets["api_key"] == "k"

    def test_mcp_servers_multiple_agents(self) -> None:
        request = OrchestrationRequest(
            agent_ids=["ceo", "cmo"],
            purpose=OrchestrationPurpose(purpose="Drive strategic growth"),
            mcp_servers={
                "ceo": [
                    MCPServerConfig(
                        server_name="erp",
                        secrets={"api_key": "erp-secret"},
                    ),
                ],
                "cmo": [
                    MCPServerConfig(server_name="crm"),
                    MCPServerConfig(server_name="analytics"),
                ],
            },
        )
        assert len(request.mcp_servers["ceo"]) == 1
        assert request.mcp_servers["ceo"][0].server_name == "erp"
        assert len(request.mcp_servers["cmo"]) == 2
        assert request.mcp_servers["cmo"][0].server_name == "crm"
        assert request.mcp_servers["cmo"][1].server_name == "analytics"

    def test_mcp_servers_serialises_to_json(self) -> None:
        request = OrchestrationRequest(
            agent_ids=["ceo"],
            purpose=OrchestrationPurpose(purpose="Drive growth"),
            mcp_servers={
                "ceo": [
                    MCPServerConfig(
                        server_name="erp",
                        secrets={"api_key": "secret"},
                    )
                ]
            },
        )
        data = request.model_dump(mode="json")
        assert "mcp_servers" in data
        assert data["mcp_servers"]["ceo"][0]["server_name"] == "erp"
        assert data["mcp_servers"]["ceo"][0]["secrets"]["api_key"] == "secret"

    def test_backward_compat_no_mcp_servers(self) -> None:
        """OrchestrationRequest without mcp_servers still works — backward compat."""
        request = OrchestrationRequest(
            agent_ids=["ceo", "cfo"],
            purpose=OrchestrationPurpose(purpose="Budget governance"),
            context={"department": "Marketing"},
        )
        assert request.mcp_servers == {}
        assert request.context["department"] == "Marketing"


# ---------------------------------------------------------------------------
# SDK package-level exports
# ---------------------------------------------------------------------------


class TestSDKExports:
    def test_mcp_server_config_exported(self) -> None:
        import aos_client

        assert hasattr(aos_client, "MCPServerConfig")

    def test_mcp_server_config_in_all(self) -> None:
        import aos_client

        assert "MCPServerConfig" in aos_client.__all__

    def test_mcp_transport_type_not_exported(self) -> None:
        """Transport types are internal to AOS and must not be in the SDK public API."""
        import aos_client

        assert not hasattr(aos_client, "MCPTransportType")
        assert "MCPTransportType" not in aos_client.__all__

    def test_mcp_tool_definition_not_exported(self) -> None:
        """Tool definitions are internal to AOS and must not be in the SDK public API."""
        import aos_client

        assert not hasattr(aos_client, "MCPToolDefinition")
        assert "MCPToolDefinition" not in aos_client.__all__
