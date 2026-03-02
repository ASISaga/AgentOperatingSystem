"""Tests for the SDK MCP contract types and OrchestrationRequest.mcp_servers."""

import pytest

from aos_client import MCPServerConfig, MCPToolDefinition, MCPTransportType
from aos_client.models import OrchestrationPurpose, OrchestrationRequest


# ---------------------------------------------------------------------------
# MCPTransportType
# ---------------------------------------------------------------------------


class TestMCPTransportType:
    def test_enum_values(self) -> None:
        assert MCPTransportType.STDIO == "stdio"
        assert MCPTransportType.STREAMABLE_HTTP == "streamable_http"
        assert MCPTransportType.WEBSOCKET == "websocket"

    def test_is_string_enum(self) -> None:
        assert isinstance(MCPTransportType.STDIO, str)

    def test_three_variants(self) -> None:
        variants = set(MCPTransportType)
        assert len(variants) == 3


# ---------------------------------------------------------------------------
# MCPToolDefinition
# ---------------------------------------------------------------------------


class TestMCPToolDefinition:
    def test_name_only(self) -> None:
        tool = MCPToolDefinition(name="read_file")
        assert tool.name == "read_file"
        assert tool.description == ""
        assert tool.input_schema == {}

    def test_all_fields(self) -> None:
        schema = {"type": "object", "properties": {"q": {"type": "string"}}}
        tool = MCPToolDefinition(name="search", description="Search web", input_schema=schema)
        assert tool.description == "Search web"
        assert tool.input_schema == schema

    def test_pydantic_serialisation(self) -> None:
        tool = MCPToolDefinition(name="ping", description="Ping server")
        data = tool.model_dump()
        assert data["name"] == "ping"
        assert data["description"] == "Ping server"
        assert data["input_schema"] == {}

    def test_pydantic_deserialisation(self) -> None:
        tool = MCPToolDefinition.model_validate({"name": "call_api"})
        assert tool.name == "call_api"


# ---------------------------------------------------------------------------
# MCPServerConfig
# ---------------------------------------------------------------------------


class TestMCPServerConfig:
    def test_http_minimal(self) -> None:
        cfg = MCPServerConfig(
            server_name="erp",
            transport_type=MCPTransportType.STREAMABLE_HTTP,
            url="https://erp.example.com/mcp",
        )
        assert cfg.server_name == "erp"
        assert cfg.transport_type == MCPTransportType.STREAMABLE_HTTP
        assert cfg.url == "https://erp.example.com/mcp"
        assert cfg.gateway_url is None
        assert cfg.headers == {}
        assert cfg.enabled is False

    def test_http_with_gateway(self) -> None:
        cfg = MCPServerConfig(
            server_name="erp",
            transport_type=MCPTransportType.STREAMABLE_HTTP,
            url="https://erp.example.com/mcp",
            gateway_url="https://my-gateway.azure.com",
            headers={"Authorization": "Bearer token"},
        )
        assert cfg.gateway_url == "https://my-gateway.azure.com"
        assert cfg.headers["Authorization"] == "Bearer token"

    def test_websocket(self) -> None:
        cfg = MCPServerConfig(
            server_name="realtime",
            transport_type=MCPTransportType.WEBSOCKET,
            url="wss://realtime.example.com/mcp",
        )
        assert cfg.transport_type == MCPTransportType.WEBSOCKET
        assert cfg.url == "wss://realtime.example.com/mcp"

    def test_stdio(self) -> None:
        cfg = MCPServerConfig(
            server_name="local-fs",
            transport_type=MCPTransportType.STDIO,
            command="python",
            args=["fs_server.py"],
            env={"DEBUG": "1"},
        )
        assert cfg.transport_type == MCPTransportType.STDIO
        assert cfg.command == "python"
        assert cfg.args == ["fs_server.py"]
        assert cfg.env == {"DEBUG": "1"}

    def test_tags_and_enabled(self) -> None:
        cfg = MCPServerConfig(
            server_name="search",
            transport_type=MCPTransportType.STREAMABLE_HTTP,
            url="https://search.example.com/mcp",
            tags=["web", "research"],
            enabled=True,
        )
        assert cfg.tags == ["web", "research"]
        assert cfg.enabled is True

    def test_pydantic_serialisation(self) -> None:
        cfg = MCPServerConfig(
            server_name="crm",
            transport_type=MCPTransportType.WEBSOCKET,
            url="wss://crm.example.com/mcp",
        )
        data = cfg.model_dump()
        assert data["server_name"] == "crm"
        assert data["transport_type"] == "websocket"
        assert data["url"] == "wss://crm.example.com/mcp"

    def test_pydantic_deserialisation(self) -> None:
        cfg = MCPServerConfig.model_validate(
            {
                "server_name": "erp",
                "transport_type": "streamable_http",
                "url": "https://erp.example.com/mcp",
            }
        )
        assert cfg.transport_type == MCPTransportType.STREAMABLE_HTTP


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
        cfg = MCPServerConfig(
            server_name="erp",
            transport_type=MCPTransportType.STREAMABLE_HTTP,
            url="https://erp.example.com/mcp",
        )
        request = OrchestrationRequest(
            agent_ids=["ceo"],
            purpose=OrchestrationPurpose(purpose="Drive growth"),
            mcp_servers={"ceo": [cfg]},
        )
        assert "ceo" in request.mcp_servers
        assert request.mcp_servers["ceo"][0].server_name == "erp"

    def test_mcp_servers_multiple_agents(self) -> None:
        request = OrchestrationRequest(
            agent_ids=["ceo", "cmo"],
            purpose=OrchestrationPurpose(purpose="Drive strategic growth"),
            mcp_servers={
                "ceo": [
                    MCPServerConfig(
                        server_name="erp",
                        transport_type=MCPTransportType.STREAMABLE_HTTP,
                        url="https://erp.example.com/mcp",
                        gateway_url="https://my-foundry-gateway.azure.com",
                    ),
                ],
                "cmo": [
                    MCPServerConfig(
                        server_name="crm",
                        transport_type=MCPTransportType.WEBSOCKET,
                        url="wss://crm.example.com/mcp",
                    ),
                    MCPServerConfig(
                        server_name="analytics",
                        transport_type=MCPTransportType.STREAMABLE_HTTP,
                        url="https://analytics.example.com/mcp",
                    ),
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
                        transport_type=MCPTransportType.STREAMABLE_HTTP,
                        url="https://erp.example.com/mcp",
                    )
                ]
            },
        )
        data = request.model_dump(mode="json")
        assert "mcp_servers" in data
        assert data["mcp_servers"]["ceo"][0]["server_name"] == "erp"
        assert data["mcp_servers"]["ceo"][0]["transport_type"] == "streamable_http"

    def test_mcp_servers_with_stdio_config(self) -> None:
        request = OrchestrationRequest(
            agent_ids=["worker"],
            purpose=OrchestrationPurpose(purpose="Process files"),
            mcp_servers={
                "worker": [
                    MCPServerConfig(
                        server_name="filesystem",
                        transport_type=MCPTransportType.STDIO,
                        command="python",
                        args=["fs_server.py"],
                    )
                ]
            },
        )
        cfg = request.mcp_servers["worker"][0]
        assert cfg.transport_type == MCPTransportType.STDIO
        assert cfg.command == "python"

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
# SDK package-level imports
# ---------------------------------------------------------------------------


class TestSDKExports:
    def test_mcp_types_exported_from_sdk(self) -> None:
        import aos_client

        assert hasattr(aos_client, "MCPTransportType")
        assert hasattr(aos_client, "MCPToolDefinition")
        assert hasattr(aos_client, "MCPServerConfig")

    def test_mcp_server_config_in_all(self) -> None:
        import aos_client

        assert "MCPServerConfig" in aos_client.__all__
        assert "MCPTransportType" in aos_client.__all__
        assert "MCPToolDefinition" in aos_client.__all__
