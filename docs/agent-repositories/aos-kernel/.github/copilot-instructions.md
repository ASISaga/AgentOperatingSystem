# AOS Kernel — Copilot Instructions

This is the Agent Operating System kernel: orchestration, messaging, storage, auth, config,
monitoring, observability, reliability, governance, extensibility, MCP, and shared services.

## Key Patterns
- All I/O is async (asyncio)
- Use OpenTelemetry for tracing
- Follow PEP 8, 120-char line length
- Type hints on all public APIs
- Tests use pytest + pytest-asyncio with auto mode

## Architecture
See docs/architecture/ARCHITECTURE.md for the full system architecture.
The kernel depends on `purpose-driven-agent` for the agent base class.
ML/AI functionality is provided by the optional `aos-intelligence` package.
