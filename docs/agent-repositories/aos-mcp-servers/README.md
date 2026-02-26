# aos-mcp-servers

Config-driven MCP (Model Context Protocol) server deployment Azure Function app for the Agent Operating System. Dynamically deploys and manages MCP servers based on registry configuration.

## Overview

MCPServers provides:

- **Config-Driven Deployment** — Define MCP servers in JSON, deploy automatically
- **MCP Server Registry** — Central registry of MCP server configurations
- **Dynamic Scaling** — MCP servers scale based on configuration
- **Tool & Resource Management** — Expose tools and resources via MCP protocol

## Quick Start

1. Define MCP server configuration in `example_mcp_server_registry.json`
2. Deploy the function app
3. MCP servers are automatically created and managed

## Local Development

```bash
pip install -r requirements.txt
func start
```

## Related Repositories

- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — Main function app
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — RealmOfAgents function app

## License

Apache License 2.0 — see [LICENSE](LICENSE)
