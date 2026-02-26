# aos-realm-of-agents

Config-driven agent deployment Azure Function app for the Agent Operating System. Dynamically deploys and manages agents based on registry configuration.

## Overview

RealmOfAgents provides:

- **Config-Driven Deployment** — Define agents in JSON, deploy automatically
- **Agent Registry** — Central registry of agent configurations
- **Dynamic Scaling** — Agents scale based on configuration
- **Migration Support** — Path from custom deployment to Microsoft Foundry Agent Service

## Quick Start

1. Define agent configuration in `example_agent_registry.json`
2. Deploy the function app
3. Agents are automatically created and managed

## Local Development

```bash
pip install -r requirements.txt
func start
```

## Related Repositories

- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — Main function app
- [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) — MCPServers function app

## License

Apache License 2.0 — see [LICENSE](LICENSE)
