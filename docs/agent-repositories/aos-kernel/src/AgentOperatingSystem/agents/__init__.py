"""Agent management — Foundry Agent Service registration for PurposeDrivenAgents.

:class:`FoundryAgentManager` bridges PurposeDrivenAgent instances (which run
as Microsoft Agent Framework code inside Azure Functions) with the Foundry
Agent Service.  It handles:

* Registering each PurposeDrivenAgent as an ``AzureAIAgent`` in Foundry.
* Maintaining a bidirectional mapping between local agent IDs and Foundry
  agent IDs.
* Purpose alignment when orchestration context changes.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FoundryAgentManager:
    """Manages PurposeDrivenAgent ↔ Foundry Agent Service lifecycle.

    :param project_client: An ``AIProjectClient`` connected to the target
        Foundry project (from ``aos_client.foundry``).
    :param default_model: Default model deployment name for new agents.
    """

    def __init__(
        self,
        project_client: Any = None,
        default_model: str = "gpt-4o",
    ) -> None:
        self.project_client = project_client
        self.default_model = default_model
        # local_agent_id → foundry registration record
        self._registered: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    async def register_agent(
        self,
        agent_id: str,
        purpose: str,
        name: str = "",
        adapter_name: str = "",
        capabilities: Optional[List[str]] = None,
        model: Optional[str] = None,
        tools: Optional[List[dict]] = None,
    ) -> Dict[str, Any]:
        """Register a PurposeDrivenAgent with the Foundry Agent Service.

        If the agent is already registered the existing record is returned.

        :param agent_id: Local agent identifier.
        :param purpose: Agent's perpetual purpose (used as instructions).
        :param name: Human-readable name (defaults to *agent_id*).
        :param adapter_name: LoRA adapter name for domain specialisation.
        :param capabilities: List of declared capabilities.
        :param model: Model deployment name (overrides default).
        :param tools: Tool definitions to attach.
        :returns: Registration record dictionary.
        """
        if agent_id in self._registered:
            logger.debug("Agent %s already registered — returning existing record", agent_id)
            return self._registered[agent_id]

        foundry_agent_id = str(uuid.uuid4())
        model_name = model or self.default_model
        instructions = purpose
        if adapter_name:
            instructions = f"[Adapter: {adapter_name}] {purpose}"

        # Create agent in Foundry if project client is available
        if self.project_client is not None:
            try:
                foundry_agent = await self.project_client.create_agent(
                    model=model_name,
                    name=name or agent_id,
                    instructions=instructions,
                    tools=tools,
                )
                foundry_agent_id = foundry_agent.agent_id
            except Exception as exc:
                logger.warning(
                    "Failed to create Foundry agent for %s: %s — using local stub",
                    agent_id,
                    exc,
                )

        record: Dict[str, Any] = {
            "agent_id": agent_id,
            "foundry_agent_id": foundry_agent_id,
            "name": name or agent_id,
            "purpose": purpose,
            "adapter_name": adapter_name,
            "capabilities": capabilities or [],
            "model": model_name,
            "tools": tools or [],
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "managed_by": "foundry_agent_service",
        }
        self._registered[agent_id] = record
        logger.info(
            "Registered agent %s → Foundry agent %s (model=%s)",
            agent_id,
            foundry_agent_id,
            model_name,
        )
        return record

    async def unregister_agent(self, agent_id: str) -> None:
        """Remove an agent registration.

        :param agent_id: Local agent identifier.
        :raises KeyError: If the agent is not registered.
        """
        record = self._registered.pop(agent_id, None)
        if record is None:
            raise KeyError(f"Agent {agent_id!r} is not registered")

        if self.project_client is not None:
            try:
                await self.project_client.delete_agent(record["foundry_agent_id"])
            except Exception as exc:
                logger.warning("Failed to delete Foundry agent %s: %s", record["foundry_agent_id"], exc)
        logger.info("Unregistered agent %s", agent_id)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_registration(self, agent_id: str) -> Dict[str, Any]:
        """Return the registration record for *agent_id*.

        :raises KeyError: If the agent is not registered.
        """
        if agent_id not in self._registered:
            raise KeyError(f"Agent {agent_id!r} is not registered")
        return dict(self._registered[agent_id])

    def get_foundry_agent_id(self, agent_id: str) -> str:
        """Return the Foundry agent ID for *agent_id*.

        :raises KeyError: If the agent is not registered.
        """
        return self.get_registration(agent_id)["foundry_agent_id"]

    def list_registered_agents(self) -> List[Dict[str, Any]]:
        """Return registration records for all registered agents."""
        return list(self._registered.values())

    @property
    def agent_count(self) -> int:
        """Number of currently registered agents."""
        return len(self._registered)
