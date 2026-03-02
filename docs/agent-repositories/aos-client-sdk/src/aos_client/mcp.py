"""
MCP (Model Context Protocol) client-facing types for the AOS Client SDK.

This module defines the **only** MCP concept exposed to client applications.
All MCP transport implementation details (transport types, URLs, gateway
configuration, subprocess commands, etc.) are **internal** to the Agent
Operating System and are never surfaced here.

:class:`MCPServerConfig` lets a client application declare two things per
registered MCP server:

1. **Which pre-registered server** to connect an agent to (``server_name``).
2. **Client-managed secrets** for that server (``secrets``), such as API keys
   or access tokens that AOS should inject at runtime.

MCP servers are registered and configured in AOS (``aos-mcp-servers``).
The client does not know — and must not need to know — how they are
connected.

Usage (client side — e.g. *business-infinity*)::

    from aos_client import MCPServerConfig, OrchestrationRequest

    request = OrchestrationRequest(
        agent_ids=["ceo", "cmo"],
        purpose=OrchestrationPurpose(purpose="Drive strategic growth"),
        mcp_servers={
            "ceo": [
                MCPServerConfig(
                    server_name="erp",
                    secrets={"api_key": "secret-erp-key"},
                ),
            ],
            "cmo": [
                MCPServerConfig(server_name="crm"),
                MCPServerConfig(server_name="analytics"),
            ],
        },
    )
"""

from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# MCPServerConfig
# ---------------------------------------------------------------------------


class MCPServerConfig(BaseModel):
    """
    Per-agent MCP server selection for use in
    :class:`~aos_client.models.OrchestrationRequest`.

    Client applications declare which pre-registered MCP servers each
    participating agent should use.  AOS looks up the server in its internal
    registry, applies the client-supplied secrets, and connects the agent at
    orchestration start.

    Transport details (protocol, URLs, gateway configuration, etc.) are
    managed entirely by AOS and are **not** part of this model.

    Attributes:
        server_name: Name of a pre-registered MCP server in the AOS registry.
            AOS will look this up and configure the agent's connection.
        secrets: Client-managed secrets to inject for this server at runtime
            (e.g. ``{"api_key": "...", "api_secret": "..."``}).  These are
            merged with any AOS-managed credentials before the connection is
            established.  Treat values as sensitive — do not log them.
    """

    server_name: str = Field(
        ...,
        description="Name of a pre-registered MCP server in the AOS registry",
    )
    secrets: Dict[str, str] = Field(
        default_factory=dict,
        description="Client-managed secrets for this server (e.g. API keys). "
                    "Merged with AOS-managed credentials at runtime.",
    )
