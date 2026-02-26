# aos-realm-of-agents

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/aos-realm-of-agents/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/aos-realm-of-agents/actions)

**Config-driven agent deployment for the Agent Operating System.**

Deploy and manage AOS agents via configuration (JSON registry) — no code changes
needed. Supports Microsoft Foundry Agent Service integration.

## Structure

```
aos-realm-of-agents
├── function_app.py                # Azure Functions entry point
├── agent_config_schema.py         # Agent configuration schema
├── example_agent_registry.json    # Example agent registry
├── host.json                      # Azure Functions host config
├── requirements.txt               # Python dependencies
└── docs/
    └── MIGRATION_TO_FOUNDRY.md    # Foundry migration guide
```

## Related Packages

| Package | Description |
|---|---|
| [`aos-kernel`](https://github.com/ASISaga/aos-kernel) | AOS kernel runtime |
| [`purpose-driven-agent`](https://github.com/ASISaga/purpose-driven-agent) | Agent building block |

## License

[MIT License](LICENSE)
