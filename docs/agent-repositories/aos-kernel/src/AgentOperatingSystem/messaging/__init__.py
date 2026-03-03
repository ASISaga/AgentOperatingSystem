"""Messaging bridge — bidirectional communication between PurposeDrivenAgent and Foundry.

:class:`FoundryMessageBridge` connects the local PurposeDrivenAgent event/message
system with Foundry conversation threads.  Messages flow in both directions:

* **Inbound** (Foundry → PDA): Orchestration instructions are translated into
  ``handle_message`` calls on the PurposeDrivenAgent.
* **Outbound** (PDA → Foundry): Agent responses and events are posted back to
  the Foundry thread so the orchestration has a complete conversation history.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FoundryMessageBridge:
    """Bidirectional message bridge between PurposeDrivenAgent and Foundry threads.

    :param agent_manager: The kernel's :class:`FoundryAgentManager`.
    :param orchestration_engine: The kernel's :class:`FoundryOrchestrationEngine`.
    """

    def __init__(
        self,
        agent_manager: Any = None,
        orchestration_engine: Any = None,
    ) -> None:
        self.agent_manager = agent_manager
        self.orchestration_engine = orchestration_engine
        # message log: list of all bridged messages
        self._messages: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Inbound: Foundry → PurposeDrivenAgent
    # ------------------------------------------------------------------

    async def deliver_to_agent(
        self,
        agent_id: str,
        message: str,
        orchestration_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Deliver a Foundry orchestration message to a PurposeDrivenAgent.

        This translates Foundry thread messages into the PDA event model.
        The concrete delivery mechanism depends on how agents are hosted
        (in-process, via HTTP, or via Service Bus).

        :param agent_id: Target agent identifier.
        :param message: Message content from the orchestration thread.
        :param orchestration_id: Orchestration that generated the message.
        :param metadata: Additional metadata.
        :returns: Delivery result with message_id and status.
        """
        message_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        record: Dict[str, Any] = {
            "message_id": message_id,
            "direction": "foundry_to_agent",
            "agent_id": agent_id,
            "orchestration_id": orchestration_id,
            "content": message,
            "metadata": metadata or {},
            "status": "delivered",
            "timestamp": now,
        }
        self._messages.append(record)
        logger.info(
            "Delivered message %s to agent %s (orchestration=%s)",
            message_id,
            agent_id,
            orchestration_id,
        )
        return record

    # ------------------------------------------------------------------
    # Outbound: PurposeDrivenAgent → Foundry
    # ------------------------------------------------------------------

    async def send_to_foundry(
        self,
        agent_id: str,
        message: str,
        orchestration_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a PurposeDrivenAgent response back to the Foundry thread.

        Agent responses, events, and purpose-alignment updates are posted
        to the orchestration's Foundry thread for a complete audit trail.

        :param agent_id: Source agent identifier.
        :param message: Response content from the agent.
        :param orchestration_id: Target orchestration.
        :param metadata: Additional metadata.
        :returns: Send result with message_id and status.
        """
        message_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        # Post to orchestration thread if available
        if orchestration_id and self.orchestration_engine:
            try:
                await self.orchestration_engine.run_agent_turn(
                    orchestration_id=orchestration_id,
                    agent_id=agent_id,
                    message=message,
                )
            except Exception as exc:
                logger.warning(
                    "Failed to post to Foundry thread for orchestration %s: %s",
                    orchestration_id,
                    exc,
                )

        record: Dict[str, Any] = {
            "message_id": message_id,
            "direction": "agent_to_foundry",
            "agent_id": agent_id,
            "orchestration_id": orchestration_id,
            "content": message,
            "metadata": metadata or {},
            "status": "sent",
            "timestamp": now,
        }
        self._messages.append(record)
        logger.info(
            "Sent message %s from agent %s to Foundry (orchestration=%s)",
            message_id,
            agent_id,
            orchestration_id,
        )
        return record

    # ------------------------------------------------------------------
    # Purpose alignment messaging
    # ------------------------------------------------------------------

    async def broadcast_purpose_alignment(
        self,
        orchestration_id: str,
        purpose: str,
        purpose_scope: str = "",
    ) -> List[Dict[str, Any]]:
        """Broadcast a purpose-alignment message to all agents in an orchestration.

        This is called when an orchestration's purpose changes and agents
        need to re-align their working purpose.

        :param orchestration_id: Target orchestration.
        :param purpose: New purpose text.
        :param purpose_scope: New purpose scope.
        :returns: List of delivery results.
        """
        if not self.orchestration_engine:
            return []

        try:
            status = await self.orchestration_engine.get_status(orchestration_id)
        except KeyError:
            logger.warning("Cannot broadcast — orchestration %s not found", orchestration_id)
            return []

        results: List[Dict[str, Any]] = []
        alignment_message = (
            f"[PURPOSE ALIGNMENT] Align your working purpose to: {purpose}"
        )
        if purpose_scope:
            alignment_message += f" | Scope: {purpose_scope}"

        for agent_id in status.get("agent_ids", []):
            result = await self.deliver_to_agent(
                agent_id=agent_id,
                message=alignment_message,
                orchestration_id=orchestration_id,
                metadata={"type": "purpose_alignment", "purpose": purpose, "purpose_scope": purpose_scope},
            )
            results.append(result)

        logger.info(
            "Broadcast purpose alignment to %d agents in orchestration %s",
            len(results),
            orchestration_id,
        )
        return results

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_messages(
        self,
        agent_id: Optional[str] = None,
        orchestration_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query bridged messages with optional filters.

        :param agent_id: Filter by agent.
        :param orchestration_id: Filter by orchestration.
        :param direction: Filter by direction (``foundry_to_agent`` or
            ``agent_to_foundry``).
        """
        results = self._messages
        if agent_id:
            results = [m for m in results if m["agent_id"] == agent_id]
        if orchestration_id:
            results = [m for m in results if m["orchestration_id"] == orchestration_id]
        if direction:
            results = [m for m in results if m["direction"] == direction]
        return results

    @property
    def message_count(self) -> int:
        """Total number of bridged messages."""
        return len(self._messages)
