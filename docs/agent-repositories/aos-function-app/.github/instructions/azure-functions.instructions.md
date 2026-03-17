# Azure Functions Instructions

## Function App Development

- Use Azure Functions Core Tools for local development
- Follow the trigger-binding pattern for new functions
- Test with local Service Bus emulator when possible

## Deployment

- Deploy through the aos-deployment orchestrator
- Use staging slots for zero-downtime deployments
- Verify health endpoints after deployment

## Configuration

- Use `local.settings.json` for local development
- Azure Application Settings for production
- Never commit secrets — use Azure Key Vault references
