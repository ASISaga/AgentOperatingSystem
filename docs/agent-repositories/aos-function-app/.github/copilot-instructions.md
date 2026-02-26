# AOS Function App — Copilot Instructions

Main Azure Functions host for AOS. Exposes kernel services via
Service Bus triggers and HTTP endpoints.

## Key Patterns
- function_app.py is the entry point
- Uses Azure Service Bus for messaging
- HTTP endpoints for health/status
- Depends on aos-kernel[azure]
