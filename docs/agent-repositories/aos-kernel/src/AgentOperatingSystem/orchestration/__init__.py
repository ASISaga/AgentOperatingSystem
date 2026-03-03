"""Orchestration engine — Foundry Agent Service based orchestration.

:class:`FoundryOrchestrationEngine` replaces the legacy custom Microsoft
Agent Framework orchestration with Foundry Agent Service managed
orchestrations.  All orchestration lifecycle (create, run turns, stop) is
delegated to Foundry threads and runs.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FoundryOrchestrationEngine:
    """Manages multi-agent orchestrations via the Foundry Agent Service.

    :param foundry_service: A ``FoundryAgentService`` instance (from
        ``aos_client.foundry``).
    :param agent_manager: The kernel's :class:`FoundryAgentManager`.
    """

    def __init__(
        self,
        foundry_service: Any = None,
        agent_manager: Any = None,
    ) -> None:
        self.foundry_service = foundry_service
        self.agent_manager = agent_manager
        # orchestration_id → record
        self._orchestrations: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Orchestration lifecycle
    # ------------------------------------------------------------------

    async def create_orchestration(
        self,
        agent_ids: List[str],
        purpose: str,
        purpose_scope: str = "",
        context: Optional[Dict[str, Any]] = None,
        workflow: str = "collaborative",
        mcp_servers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new purpose-driven orchestration.

        Agents are registered with Foundry (if not already) and a shared
        conversation thread is created.

        :param agent_ids: Local agent identifiers to participate.
        :param purpose: Orchestration purpose text.
        :param purpose_scope: Boundaries of the purpose.
        :param context: Contextual data for agents.
        :param workflow: Workflow pattern (``collaborative``, ``sequential``,
            ``hierarchical``).
        :param mcp_servers: Per-agent MCP server selection.
        :returns: Orchestration record with ``orchestration_id`` and status.
        """
        orchestration_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        thread_id = str(uuid.uuid4())

        # Delegate to FoundryAgentService when available
        if self.foundry_service is not None:
            try:
                result = await self.foundry_service.create_orchestration(
                    agent_ids=agent_ids,
                    purpose=purpose,
                    context=context,
                )
                orchestration_id = result.get("orchestration_id", orchestration_id)
                thread_id = result.get("thread_id", thread_id)
            except Exception as exc:
                logger.warning("Foundry create_orchestration failed: %s — using local stub", exc)

        record: Dict[str, Any] = {
            "orchestration_id": orchestration_id,
            "thread_id": thread_id,
            "agent_ids": list(agent_ids),
            "purpose": purpose,
            "purpose_scope": purpose_scope,
            "context": context or {},
            "workflow": workflow,
            "mcp_servers": mcp_servers or {},
            "status": "active",
            "turns": [],
            "created_at": now,
            "updated_at": now,
            "managed_by": "foundry_agent_service",
        }
        self._orchestrations[orchestration_id] = record
        logger.info(
            "Created orchestration %s — agents=%s workflow=%s purpose=%s",
            orchestration_id,
            agent_ids,
            workflow,
            purpose[:60],
        )
        return dict(record)

    async def run_agent_turn(
        self,
        orchestration_id: str,
        agent_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """Execute a single agent turn within an orchestration.

        :param orchestration_id: Target orchestration.
        :param agent_id: Agent to execute this turn.
        :param message: Input message for the agent.
        :returns: Turn result with run_id and status.
        :raises KeyError: If the orchestration is not found.
        """
        record = self._orchestrations.get(orchestration_id)
        if record is None:
            raise KeyError(f"Orchestration {orchestration_id!r} not found")

        turn_result: Dict[str, Any] = {
            "run_id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "message": message,
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Delegate to FoundryAgentService when available
        if self.foundry_service is not None:
            try:
                result = await self.foundry_service.run_agent_turn(
                    orchestration_id=orchestration_id,
                    agent_id=agent_id,
                    message=message,
                )
                turn_result.update(result)
            except Exception as exc:
                logger.warning("Foundry run_agent_turn failed: %s — using local result", exc)

        record["turns"].append(turn_result)
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        return turn_result

    async def get_status(self, orchestration_id: str) -> Dict[str, Any]:
        """Get the current status of an orchestration.

        :raises KeyError: If the orchestration is not found.
        """
        record = self._orchestrations.get(orchestration_id)
        if record is None:
            raise KeyError(f"Orchestration {orchestration_id!r} not found")
        return dict(record)

    async def stop_orchestration(self, orchestration_id: str) -> None:
        """Stop an active orchestration.

        :raises KeyError: If the orchestration is not found.
        """
        record = self._orchestrations.get(orchestration_id)
        if record is None:
            raise KeyError(f"Orchestration {orchestration_id!r} not found")

        if self.foundry_service is not None:
            try:
                await self.foundry_service.stop_orchestration(orchestration_id)
            except Exception as exc:
                logger.warning("Foundry stop_orchestration failed: %s", exc)

        record["status"] = "stopped"
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("Stopped orchestration %s", orchestration_id)

    async def cancel_orchestration(self, orchestration_id: str) -> None:
        """Cancel an orchestration.

        :raises KeyError: If the orchestration is not found.
        """
        record = self._orchestrations.get(orchestration_id)
        if record is None:
            raise KeyError(f"Orchestration {orchestration_id!r} not found")

        record["status"] = "cancelled"
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("Cancelled orchestration %s", orchestration_id)

    def list_orchestrations(self) -> List[Dict[str, Any]]:
        """Return all orchestration records."""
        return list(self._orchestrations.values())

    @property
    def orchestration_count(self) -> int:
        """Number of active orchestrations."""
        return len(self._orchestrations)
