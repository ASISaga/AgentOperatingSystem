# aos-mcp-servers

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/aos-mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/aos-mcp-servers/actions)

**Config-driven MCP server deployment for the Agent Operating System.**

Deploy and manage Model Context Protocol (MCP) servers via configuration
(JSON registry) — no code changes needed.

## Structure

```
aos-mcp-servers
├── function_app.py                     # Azure Functions entry point
├── mcp_server_schema.py                # MCP server configuration schema
├── example_mcp_server_registry.json    # Example server registry
├── host.json                           # Azure Functions host config
├── requirements.txt                    # Python dependencies
└── tests/                              # Tests
```

## Related Packages

| Package | Description |
|---|---|
| [`aos-kernel`](https://github.com/ASISaga/aos-kernel) | AOS kernel runtime |

## License

[MIT License](LICENSE)
