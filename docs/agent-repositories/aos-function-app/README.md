# aos-function-app

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/aos-function-app/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/aos-function-app/actions)

**Main Azure Functions host for the Agent Operating System.**

Exposes AOS kernel services via Azure Service Bus triggers and HTTP endpoints.

## Structure

```
aos-function-app
├── function_app.py       # Main Azure Functions entry point
├── host.json             # Azure Functions host configuration
├── requirements.txt      # Python dependencies
└── tests/                # Function tests
```

## Related Packages

| Package | Description |
|---|---|
| [`aos-kernel`](https://github.com/ASISaga/aos-kernel) | AOS kernel runtime (required) |
| [`aos-intelligence`](https://github.com/ASISaga/aos-intelligence) | ML/AI services (optional) |

## License

[MIT License](LICENSE)
