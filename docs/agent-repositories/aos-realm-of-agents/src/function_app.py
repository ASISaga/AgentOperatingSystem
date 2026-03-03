"""RealmOfAgents Azure Function app entry point.

Provides the agent catalog API for the Agent Operating System.  Client
applications (via ``aos-client-sdk``) query this function app to browse
available agents and their capabilities.

Agents are defined in a JSON registry (``example_agent_registry.json``)
and registered with the Foundry Agent Service on startup.  The Foundry
Agent Service is the internal orchestration backbone for all agents.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import azure.functions as func

from agent_config_schema import AgentRegistry, AgentRegistryEntry

logger = logging.getLogger(__name__)
app = func.FunctionApp()

# ── Foundry Agent Manager (optional — works in stub mode without Azure SDK) ──

try:
    from AgentOperatingSystem.agents import FoundryAgentManager as _FoundryAgentManager

    _agent_manager: Optional[Any] = _FoundryAgentManager()
except ImportError:  # pragma: no cover
    _agent_manager = None

# ── Registry Loading ─────────────────────────────────────────────────────────

_registry: Optional[AgentRegistry] = None
_foundry_registered: bool = False


def _load_registry() -> AgentRegistry:
    """Load the agent registry from the JSON configuration file."""
    global _registry  # noqa: PLW0603
    if _registry is not None:
        return _registry

    registry_path = os.environ.get(
        "AGENT_REGISTRY_PATH",
        str(Path(__file__).parent / "example_agent_registry.json"),
    )
    logger.info("Loading agent registry from %s", registry_path)

    with open(registry_path, encoding="utf-8") as fh:
        data = json.load(fh)

    _registry = AgentRegistry(**data)
    logger.info(
        "Loaded %d agents (%d enabled)",
        len(_registry.agents),
        len(_registry.get_enabled_agents()),
    )
    return _registry


async def _ensure_foundry_registration(registry: AgentRegistry) -> None:
    """Register enabled agents with the Foundry Agent Service.

    Each agent is registered via :class:`FoundryAgentManager` so the Foundry
    Agent Service manages its lifecycle and orchestration.  When called on
    subsequent requests the registration is skipped (idempotent).
    """
    global _foundry_registered  # noqa: PLW0603
    if _foundry_registered:
        return

    foundry_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "")
    for entry in registry.get_enabled_agents():
        if _agent_manager is not None:
            await _agent_manager.register_agent(
                agent_id=entry.agent_id,
                purpose=entry.purpose,
                name=entry.agent_id,
                adapter_name=entry.adapter_name,
                capabilities=entry.capabilities,
            )
        else:
            logger.info(
                "Registering agent '%s' (%s) with Foundry Agent Service at %s",
                entry.agent_id,
                entry.agent_type,
                foundry_endpoint or "<not configured>",
            )
    _foundry_registered = True


# ── HTTP Endpoints ───────────────────────────────────────────────────────────


@app.function_name("list_agents")
@app.route(route="realm/agents", methods=["GET"])
async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
    """List all enabled agents in the catalog.

    All agents are registered with the Foundry Agent Service on first access.

    Query parameters:
        agent_type: Optional filter by agent class name.
    """
    registry = _load_registry()
    await _ensure_foundry_registration(registry)
    agent_type = req.params.get("agent_type")

    if agent_type:
        agents = registry.filter_by_type(agent_type)
    else:
        agents = registry.get_enabled_agents()

    payload = {"agents": [a.model_dump() for a in agents]}
    return func.HttpResponse(
        json.dumps(payload), mimetype="application/json"
    )


@app.function_name("get_agent")
@app.route(route="realm/agents/{agent_id}", methods=["GET"])
async def get_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Get a single agent descriptor by ID."""
    agent_id = req.route_params.get("agent_id", "")
    registry = _load_registry()
    await _ensure_foundry_registration(registry)
    entry = registry.get_agent(agent_id)

    if entry is None or not entry.enabled:
        return func.HttpResponse(
            json.dumps({"error": f"Agent '{agent_id}' not found"}),
            status_code=404,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps(entry.model_dump()), mimetype="application/json"
    )


@app.function_name("get_config")
@app.route(route="realm/config", methods=["GET"])
async def get_config(req: func.HttpRequest) -> func.HttpResponse:
    """Return the full registry configuration (admin endpoint)."""
    registry = _load_registry()
    return func.HttpResponse(
        json.dumps(registry.model_dump()), mimetype="application/json"
    )


@app.function_name("health")
@app.route(route="health", methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    try:
        registry = _load_registry()
        status: Dict[str, Any] = {
            "app": "aos-realm-of-agents",
            "status": "healthy",
            "agents_registered": len(registry.agents),
            "agents_enabled": len(registry.get_enabled_agents()),
        }
        return func.HttpResponse(
            json.dumps(status), mimetype="application/json"
        )
    except Exception as exc:
        return func.HttpResponse(
            json.dumps({"app": "aos-realm-of-agents", "status": "unhealthy", "error": str(exc)}),
            status_code=503,
            mimetype="application/json",
        )
