# AOS Deployment Guide

**Last Updated**: 2026-03-22

## Prerequisites

- Azure subscription with Contributor access
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) (`az`) >= 2.60.0
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd) (`azd`) >= 1.9.0
- [Azure AI Agents extension](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/sdk-overview) for `azd`
- Python >= 3.11
- Git with submodule support

---

## Step 1: Provision Infrastructure

AOS infrastructure is managed by `aos-infrastructure` (Bicep). This step provisions all Azure resources: AI Services, AI Foundry Hub & Project, AI Gateway (APIM), Service Bus, and Function Apps.

```bash
# Clone the infrastructure repository
git clone https://github.com/ASISaga/aos-infrastructure.git
cd aos-infrastructure

# Log in to Azure
az login
azd auth login

# Initialize the azd environment
azd env new aos-prod
azd env set AZURE_LOCATION eastus

# Provision all resources (~10 minutes)
azd provision
```

After provisioning, note the outputs:
- `AOS_DISPATCHER_URL` — base URL for the dispatcher
- `AZURE_AI_PROJECT_ID` — AI Foundry project resource ID
- `SERVICE_BUS_CONNECTION` — Service Bus connection string
- Per-app `AZURE_CLIENT_ID` values for each deployed agent

---

## Step 2: Register GitHub Secrets

For each deployed repository (dispatcher + 5 C-suite agents + realm-of-agents + mcp), configure the following GitHub secrets and variables:

| Type | Name | Value |
|------|------|-------|
| Secret | `AZURE_CLIENT_ID` | Per-app User-Assigned MI clientId (from Bicep output) |
| Secret | `AZURE_TENANT_ID` | Azure tenant ID |
| Secret | `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| Secret | `AZURE_AI_PROJECT_ID` | Azure AI Foundry project resource ID |
| Variable | `AZURE_ENV_NAME` | azd environment name (e.g. `aos-prod`) |
| Variable | `AZURE_LOCATION` | Primary Azure region (e.g. `eastus`) |

---

## Step 3: Deploy Platform Services

### Deploy aos-dispatcher (this meta-repo)

```bash
cd agent-operating-system   # this repository

# Set environment variables (Azure App Configuration or local .env)
export SERVICE_BUS_CONNECTION="<connection-string>"
export AZURE_AI_PROJECT_ID="<project-id>"

# Deploy via azd
azd deploy
```

The `deploy.yml` GitHub Actions workflow automates this on push to `main`.

### Deploy C-Suite Agents

Each agent is an independent Azure Functions app. Deploy using the agent's own repository:

```bash
# Example: deploy CEO agent
git clone https://github.com/ASISaga/ceo-agent.git
cd ceo-agent

# Initialize Foundry agent definition
azd ai agent init

# Deploy
azd deploy
```

The `deploy.yml` in each agent repo handles CI/CD automatically.

### Deploy Supporting Services

```bash
# Deploy realm-of-agents (agent catalog)
git clone https://github.com/ASISaga/realm-of-agents.git
cd realm-of-agents && azd deploy

# Deploy MCP servers
git clone https://github.com/ASISaga/mcp.git
cd mcp && azd deploy
```

---

## Step 4: Configure Proxy URLs

The dispatcher proxies some requests to `aos-mcp-servers` and `aos-realm-of-agents`. Set these in the dispatcher Function App's application settings:

| Setting | Value |
|---------|-------|
| `MCP_SERVERS_BASE_URL` | Base URL of the `mcp` function app |
| `REALM_OF_AGENTS_BASE_URL` | Base URL of the `realm-of-agents` function app |

If these variables are not set, the dispatcher returns stub responses (useful for local development).

---

## Step 5: Register a Client Application

Once deployed, register your client app to provision its Service Bus resources:

```bash
curl -X POST https://<dispatcher-url>/api/apps/register \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
           "app_name": "my-app",
           "workflows": ["strategic-review"]
         }'
```

---

## Local Development

### Run the Dispatcher Locally

```bash
# Install dependencies
pip install -e ".[dev]"

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Set required environment variables
export SERVICE_BUS_CONNECTION="Endpoint=sb://localhost..."
export AZURE_AI_PROJECT_ID="<project-id>"

# Start the function app
func start
```

The function app runs at `http://localhost:7071/api/`.

When `MCP_SERVERS_BASE_URL` and `REALM_OF_AGENTS_BASE_URL` are not set, stub responses are returned for MCP and agent catalog endpoints — no external dependencies needed for basic development.

### Run Tests

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
pylint function_app.py
```

---

## Environment Variables Reference

See [CONFIGURATION.md](CONFIGURATION.md) for the full list of required and optional environment variables.

---

## CI/CD Pipeline

GitHub Actions workflows (`.github/workflows/`):

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `ci.yml` | Push / PR to `main` | Validate meta-repo structure, verify all 15 submodules registered |
| `deploy.yml` | Push to `main` | Deploy the dispatcher function app to Azure using `azd` |

---

## Troubleshooting

### Orchestration stuck in `submitted` status

- Check that the `aos-orchestration-requests` Service Bus queue is receiving messages.
- Check that all C-suite agents are deployed and registered with Foundry.
- Review Application Insights logs for the dispatcher and agent function apps.

### 401 Unauthorized on API calls

- Verify the JWT token is being sent in the `Authorization: Bearer <token>` header.
- Check that the AI Gateway (APIM) policy is configured with the correct Entra tenant ID.
- Confirm that the client application's `AZURE_CLIENT_ID` matches the User-Assigned MI registered in Entra.

### MCP tools returning stub responses

- Set `MCP_SERVERS_BASE_URL` in the dispatcher function app's application settings.
- Verify that the `mcp` function app is deployed and healthy (`GET /api/health`).

### Service Bus connection errors

- Check `SERVICE_BUS_CONNECTION` is set correctly (full connection string or managed identity config).
- Confirm the Service Bus namespace exists and the queues/topics are provisioned.
- Verify the function app's managed identity has `Azure Service Bus Data Owner` RBAC on the namespace.

---

## References

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture overview
- [CONFIGURATION.md](CONFIGURATION.md) — Full environment variable reference
- [API-REFERENCE.md](API-REFERENCE.md) — Dispatcher API endpoints
