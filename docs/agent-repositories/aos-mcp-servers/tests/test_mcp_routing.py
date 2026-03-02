"""
Tests for the MCP transport connection classes in aos_mcp_servers.routing.

MCPTransportType and MCPToolDefinition are defined in the SDK (aos_client.mcp)
and imported here via aos_mcp_servers.routing.  The transport connection
classes (MCPStdioTool, MCPStreamableHTTPTool, MCPWebsocketTool) are defined
in aos_mcp_servers.routing and tested here.
"""

import pytest

from aos_mcp_servers.routing import (
    MCPStdioTool,
    MCPStreamableHTTPTool,
    MCPWebsocketTool,
)
from aos_client.mcp import (
    MCPToolDefinition,
    MCPTransportType,
)


# ---------------------------------------------------------------------------
# MCPTransportType
# ---------------------------------------------------------------------------


class TestMCPTransportType:
    def test_enum_values(self) -> None:
        assert MCPTransportType.STDIO == "stdio"
        assert MCPTransportType.STREAMABLE_HTTP == "streamable_http"
        assert MCPTransportType.WEBSOCKET == "websocket"

    def test_all_three_variants_exist(self) -> None:
        variants = {MCPTransportType.STDIO, MCPTransportType.STREAMABLE_HTTP, MCPTransportType.WEBSOCKET}
        assert len(variants) == 3

    def test_is_string_enum(self) -> None:
        assert isinstance(MCPTransportType.STDIO, str)


# ---------------------------------------------------------------------------
# MCPToolDefinition
# ---------------------------------------------------------------------------


class TestMCPToolDefinition:
    def test_required_name_only(self) -> None:
        tool = MCPToolDefinition(name="read_file")
        assert tool.name == "read_file"
        assert tool.description == ""
        assert tool.input_schema == {}

    def test_all_fields(self) -> None:
        schema = {"type": "object", "properties": {"query": {"type": "string"}}}
        tool = MCPToolDefinition(
            name="search",
            description="Web search",
            input_schema=schema,
        )
        assert tool.name == "search"
        assert tool.description == "Web search"
        assert tool.input_schema == schema

    def test_independent_default_schemas(self) -> None:
        """Default input_schema dicts are independent instances."""
        t1 = MCPToolDefinition(name="a")
        t2 = MCPToolDefinition(name="b")
        t1.input_schema["key"] = "val"
        assert "key" not in t2.input_schema


# ---------------------------------------------------------------------------
# MCPStdioTool
# ---------------------------------------------------------------------------


class TestMCPStdioTool:
    def test_construction_defaults(self) -> None:
        server = MCPStdioTool(command="python")
        assert server.command == "python"
        assert server.args == []
        assert server.env == {}
        assert server.transport_type == MCPTransportType.STDIO

    def test_construction_full(self) -> None:
        server = MCPStdioTool(
            command="python",
            args=["server.py", "--port", "8080"],
            env={"DEBUG": "1"},
            tools=[MCPToolDefinition(name="read_file")],
        )
        assert server.args == ["server.py", "--port", "8080"]
        assert server.env == {"DEBUG": "1"}

    @pytest.mark.asyncio
    async def test_list_tools_returns_configured_tools(self) -> None:
        tools = [MCPToolDefinition(name="read_file"), MCPToolDefinition(name="write_file")]
        server = MCPStdioTool(command="python", tools=tools)
        discovered = await server.list_tools()
        assert len(discovered) == 2
        assert discovered[0].name == "read_file"
        assert discovered[1].name == "write_file"

    @pytest.mark.asyncio
    async def test_list_tools_returns_copy(self) -> None:
        """Mutating the returned list does not change the server's internal list."""
        server = MCPStdioTool(command="python", tools=[MCPToolDefinition(name="ping")])
        result = await server.list_tools()
        result.clear()
        assert len(await server.list_tools()) == 1

    @pytest.mark.asyncio
    async def test_list_tools_empty_by_default(self) -> None:
        server = MCPStdioTool(command="python")
        assert await server.list_tools() == []

    @pytest.mark.asyncio
    async def test_call_tool_known(self) -> None:
        server = MCPStdioTool(
            command="python",
            tools=[MCPToolDefinition(name="read_file")],
        )
        result = await server.call_tool("read_file", {"path": "/tmp/test.txt"})
        assert result["transport"] == MCPTransportType.STDIO
        assert result["tool"] == "read_file"
        assert result["params"] == {"path": "/tmp/test.txt"}

    @pytest.mark.asyncio
    async def test_call_tool_unknown_raises_value_error(self) -> None:
        server = MCPStdioTool(
            command="python",
            tools=[MCPToolDefinition(name="read_file")],
        )
        with pytest.raises(ValueError, match="not available"):
            await server.call_tool("write_file", {})

    @pytest.mark.asyncio
    async def test_call_tool_no_restriction_when_no_tools(self) -> None:
        """A server with no pre-configured tools accepts any tool name."""
        server = MCPStdioTool(command="python")
        result = await server.call_tool("anything", {})
        assert result["tool"] == "anything"


# ---------------------------------------------------------------------------
# MCPStreamableHTTPTool
# ---------------------------------------------------------------------------


class TestMCPStreamableHTTPTool:
    def test_construction_defaults(self) -> None:
        server = MCPStreamableHTTPTool(url="https://api.example.com/mcp")
        assert server.url == "https://api.example.com/mcp"
        assert server.headers == {}
        assert server.gateway_url is None
        assert server.transport_type == MCPTransportType.STREAMABLE_HTTP

    def test_effective_url_without_gateway(self) -> None:
        server = MCPStreamableHTTPTool(url="https://api.example.com/mcp")
        assert server.effective_url == "https://api.example.com/mcp"

    def test_effective_url_with_gateway(self) -> None:
        server = MCPStreamableHTTPTool(
            url="https://api.example.com/mcp",
            gateway_url="https://gateway.azure.com",
        )
        assert server.effective_url == "https://gateway.azure.com"

    def test_custom_headers_stored(self) -> None:
        server = MCPStreamableHTTPTool(
            url="https://api.example.com/mcp",
            headers={"Authorization": "Bearer token"},
        )
        assert server.headers["Authorization"] == "Bearer token"

    @pytest.mark.asyncio
    async def test_list_tools(self) -> None:
        tools = [MCPToolDefinition(name="search_web", description="Web search")]
        server = MCPStreamableHTTPTool(url="https://api.example.com/mcp", tools=tools)
        discovered = await server.list_tools()
        assert len(discovered) == 1
        assert discovered[0].name == "search_web"

    @pytest.mark.asyncio
    async def test_call_tool_uses_effective_url(self) -> None:
        server = MCPStreamableHTTPTool(
            url="https://api.example.com/mcp",
            gateway_url="https://gateway.azure.com",
            tools=[MCPToolDefinition(name="search_web")],
        )
        result = await server.call_tool("search_web", {"q": "test"})
        assert result["url"] == "https://gateway.azure.com"
        assert result["transport"] == MCPTransportType.STREAMABLE_HTTP

    @pytest.mark.asyncio
    async def test_call_tool_direct_url_without_gateway(self) -> None:
        server = MCPStreamableHTTPTool(
            url="https://api.example.com/mcp",
            tools=[MCPToolDefinition(name="search_web")],
        )
        result = await server.call_tool("search_web", {"q": "test"})
        assert result["url"] == "https://api.example.com/mcp"

    @pytest.mark.asyncio
    async def test_call_tool_unknown_raises_value_error(self) -> None:
        server = MCPStreamableHTTPTool(
            url="https://api.example.com/mcp",
            tools=[MCPToolDefinition(name="search_web")],
        )
        with pytest.raises(ValueError, match="not available"):
            await server.call_tool("create_issue", {})


# ---------------------------------------------------------------------------
# MCPWebsocketTool
# ---------------------------------------------------------------------------


class TestMCPWebsocketTool:
    def test_construction(self) -> None:
        server = MCPWebsocketTool(url="wss://realtime.example.com/mcp")
        assert server.url == "wss://realtime.example.com/mcp"
        assert server.transport_type == MCPTransportType.WEBSOCKET

    @pytest.mark.asyncio
    async def test_list_tools(self) -> None:
        tools = [MCPToolDefinition(name="stream_events")]
        server = MCPWebsocketTool(url="wss://realtime.example.com/mcp", tools=tools)
        discovered = await server.list_tools()
        assert len(discovered) == 1
        assert discovered[0].name == "stream_events"

    @pytest.mark.asyncio
    async def test_call_tool_success(self) -> None:
        server = MCPWebsocketTool(
            url="wss://realtime.example.com/mcp",
            tools=[MCPToolDefinition(name="subscribe")],
        )
        result = await server.call_tool("subscribe", {"channel": "events"})
        assert result["transport"] == MCPTransportType.WEBSOCKET
        assert result["url"] == "wss://realtime.example.com/mcp"
        assert result["tool"] == "subscribe"

    @pytest.mark.asyncio
    async def test_call_tool_unknown_raises_value_error(self) -> None:
        server = MCPWebsocketTool(
            url="wss://realtime.example.com/mcp",
            tools=[MCPToolDefinition(name="subscribe")],
        )
        with pytest.raises(ValueError, match="not available"):
            await server.call_tool("publish", {})


# ---------------------------------------------------------------------------
# Package-level imports
# ---------------------------------------------------------------------------


class TestPackageExports:
    def test_imports_from_package_init(self) -> None:
        from aos_mcp_servers import (  # noqa: F401
            MCPStdioTool,
            MCPStreamableHTTPTool,
            MCPToolDefinition,
            MCPTransportType,
            MCPWebsocketTool,
        )
