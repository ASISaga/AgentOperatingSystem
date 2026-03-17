# MCPServers Instructions

## Overview

MCPServers is a config-driven MCP (Model Context Protocol) server deployment
Azure Function app. MCP servers are defined in JSON registry files and
automatically deployed and managed.

## MCP Server Configuration

- Define MCP servers in `example_mcp_server_registry.json`
- Each entry specifies: server type, tools, resources, and runtime config
- The function app reads the registry on startup and creates server instances

## Development

- Use Azure Functions Core Tools for local development
- Test MCP server configurations with the validation schema
- Run `func start` to test locally

## Deployment

- Deploy through the aos-deployment orchestrator
- MCP server registry is read at function app startup
- Configuration changes require function app restart

## MCP Protocol

- MCP servers expose tools and resources to agents
- Tools are callable functions that agents can invoke
- Resources are data sources that agents can read
- See the [MCP specification](https://modelcontextprotocol.io/) for protocol details
