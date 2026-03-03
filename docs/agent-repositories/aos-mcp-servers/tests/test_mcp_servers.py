"""Tests for MCPServers function app."""
import json
from pathlib import Path

import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from mcp_server_schema import MCPServerRegistry, MCPServerRegistryEntry, MCPToolEntry


class TestMCPToolEntry:
    """MCPToolEntry model tests."""

    def test_create_minimal(self):
        tool = MCPToolEntry(name="read_file")
        assert tool.name == "read_file"
        assert tool.description == ""
        assert tool.input_schema == {}

    def test_create_full(self):
        schema = {"type": "object", "properties": {"path": {"type": "string"}}}
        tool = MCPToolEntry(name="read_file", description="Read a file", input_schema=schema)
        assert tool.description == "Read a file"
        assert tool.input_schema == schema

    def test_independent_default_schemas(self):
        t1 = MCPToolEntry(name="a")
        t2 = MCPToolEntry(name="b")
        t1.input_schema["key"] = "val"
        assert "key" not in t2.input_schema


class TestMCPServerRegistryEntry:
    """MCPServerRegistryEntry model tests."""

    def test_create_stdio_server(self):
        entry = MCPServerRegistryEntry(
            server_id="context-server",
            server_type="stdio",
            command="python",
        )
        assert entry.server_id == "context-server"
        assert entry.server_type == "stdio"
        assert entry.command == "python"
        assert entry.enabled is True
        assert entry.tools == []

    def test_create_http_server(self):
        entry = MCPServerRegistryEntry(
            server_id="knowledge-server",
            server_type="streamable_http",
            url="https://api.example.com/mcp",
            gateway_url="https://gateway.azure.com",
            tools=[MCPToolEntry(name="search", description="Search")],
        )
        assert entry.url == "https://api.example.com/mcp"
        assert entry.gateway_url == "https://gateway.azure.com"
        assert len(entry.tools) == 1

    def test_create_websocket_server(self):
        entry = MCPServerRegistryEntry(
            server_id="realtime-server",
            server_type="websocket",
            url="wss://realtime.example.com/mcp",
        )
        assert entry.server_type == "websocket"

    def test_disabled_server(self):
        entry = MCPServerRegistryEntry(
            server_id="disabled-server",
            server_type="stdio",
            command="python",
            enabled=False,
        )
        assert entry.enabled is False


class TestMCPServerRegistry:
    """MCPServerRegistry model tests."""

    def test_load_example_registry(self):
        registry_path = (
            Path(__file__).resolve().parent.parent / "src" / "example_mcp_server_registry.json"
        )
        with open(registry_path, encoding="utf-8") as fh:
            data = json.load(fh)
        registry = MCPServerRegistry(**data)
        assert len(registry.mcp_servers) == 3

    def test_get_enabled_servers(self):
        registry = MCPServerRegistry(
            mcp_servers=[
                MCPServerRegistryEntry(server_id="s1", server_type="stdio", command="python", enabled=True),
                MCPServerRegistryEntry(server_id="s2", server_type="stdio", command="python", enabled=False),
            ]
        )
        enabled = registry.get_enabled_servers()
        assert len(enabled) == 1
        assert enabled[0].server_id == "s1"

    def test_get_server_by_id(self):
        registry = MCPServerRegistry(
            mcp_servers=[
                MCPServerRegistryEntry(server_id="context-server", server_type="stdio", command="python"),
            ]
        )
        server = registry.get_server("context-server")
        assert server is not None
        assert server.server_id == "context-server"

    def test_get_server_not_found(self):
        registry = MCPServerRegistry(mcp_servers=[])
        assert registry.get_server("nonexistent") is None

    def test_example_registry_has_enabled_servers(self):
        registry_path = (
            Path(__file__).resolve().parent.parent / "src" / "example_mcp_server_registry.json"
        )
        with open(registry_path, encoding="utf-8") as fh:
            data = json.load(fh)
        registry = MCPServerRegistry(**data)
        enabled = registry.get_enabled_servers()
        assert len(enabled) >= 1
        server_ids = {s.server_id for s in enabled}
        assert "context-server" in server_ids
        assert "knowledge-server" in server_ids

    def test_example_registry_server_types(self):
        registry_path = (
            Path(__file__).resolve().parent.parent / "src" / "example_mcp_server_registry.json"
        )
        with open(registry_path, encoding="utf-8") as fh:
            data = json.load(fh)
        registry = MCPServerRegistry(**data)
        server_types = {s.server_type for s in registry.mcp_servers}
        assert "stdio" in server_types
        assert "streamable_http" in server_types
