"""AgentOperatingSystem — the kernel entry point.

The :class:`AgentOperatingSystem` class is the top-level façade that wires
together all kernel subsystems:

* **FoundryAgentManager** — PurposeDrivenAgent ↔ Foundry registration.
* **FoundryOrchestrationEngine** — orchestration lifecycle via Foundry threads/runs.
* **FoundryMessageBridge** — bidirectional message passing.
* **KernelConfig** — configuration from environment / Bicep parameters.

All orchestration is managed exclusively by the Foundry Agent Service.
There is no legacy custom orchestration path.

Typical usage in an Azure Function::

    from AgentOperatingSystem import AgentOperatingSystem

    kernel = AgentOperatingSystem()
    await kernel.initialize()

    # Register an agent
    await kernel.register_agent(
        agent_id="ceo",
        purpose="Strategic leadership and executive decision-making",
        adapter_name="leadership",
    )

    # Create an orchestration
    orch = await kernel.create_orchestration(
        agent_ids=["ceo", "cfo"],
        purpose="Quarterly strategic review",
    )
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from AgentOperatingSystem.config import KernelConfig
from AgentOperatingSystem.agents import FoundryAgentManager
from AgentOperatingSystem.orchestration import FoundryOrchestrationEngine
from AgentOperatingSystem.messaging import FoundryMessageBridge

logger = logging.getLogger(__name__)


class AgentOperatingSystem:
    """The AOS Kernel — manages agent orchestrations via Foundry Agent Service.

    :param config: Kernel configuration.  When ``None``, configuration is
        loaded from environment variables.
    :param project_client: An optional ``AIProjectClient`` instance.  When
        ``None``, the kernel operates in local/stub mode suitable for
        testing and development.
    """

    def __init__(
        self,
        config: Optional[KernelConfig] = None,
        project_client: Any = None,
    ) -> None:
        self.config = config or KernelConfig.from_env()
        self._project_client = project_client
        self._foundry_service: Any = None
        self._initialized = False

        # Subsystems
        self.agent_manager = FoundryAgentManager(
            project_client=project_client,
            default_model=self.config.default_model,
        )
        self.orchestration_engine = FoundryOrchestrationEngine(
            foundry_service=None,  # set during initialize()
            agent_manager=self.agent_manager,
        )
        self.message_bridge = FoundryMessageBridge(
            agent_manager=self.agent_manager,
            orchestration_engine=self.orchestration_engine,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Initialize the kernel and establish Foundry connections.

        When a project client is not provided and a
        ``FOUNDRY_PROJECT_ENDPOINT`` is configured, the kernel attempts
        to create an ``AIProjectClient`` automatically.
        """
        if self._initialized:
            return

        # Try to create a FoundryAgentService if we have a project client
        if self._project_client is not None:
            try:
                from AgentOperatingSystem._foundry_internal import _create_foundry_service

                self._foundry_service = _create_foundry_service(
                    self._project_client,
                    self.config.ai_gateway_url,
                )
                self.orchestration_engine.foundry_service = self._foundry_service
            except Exception as exc:
                logger.warning("Failed to create FoundryAgentService: %s", exc)

        self._initialized = True
        logger.info(
            "AOS Kernel initialized (environment=%s, foundry=%s)",
            self.config.environment,
            "connected" if self._foundry_service else "local",
        )

    async def shutdown(self) -> None:
        """Gracefully shut down the kernel."""
        self._initialized = False
        logger.info("AOS Kernel shut down")

    # ------------------------------------------------------------------
    # Agent management (delegates to FoundryAgentManager)
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

        See :meth:`FoundryAgentManager.register_agent` for details.
        """
        return await self.agent_manager.register_agent(
            agent_id=agent_id,
            purpose=purpose,
            name=name,
            adapter_name=adapter_name,
            capabilities=capabilities,
            model=model,
            tools=tools,
        )

    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        await self.agent_manager.unregister_agent(agent_id)

    # ------------------------------------------------------------------
    # Orchestration (delegates to FoundryOrchestrationEngine)
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
        """Create a purpose-driven orchestration.

        See :meth:`FoundryOrchestrationEngine.create_orchestration` for details.
        """
        return await self.orchestration_engine.create_orchestration(
            agent_ids=agent_ids,
            purpose=purpose,
            purpose_scope=purpose_scope,
            context=context,
            workflow=workflow,
            mcp_servers=mcp_servers,
        )

    async def run_agent_turn(
        self,
        orchestration_id: str,
        agent_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """Execute a single agent turn."""
        return await self.orchestration_engine.run_agent_turn(
            orchestration_id=orchestration_id,
            agent_id=agent_id,
            message=message,
        )

    async def get_orchestration_status(self, orchestration_id: str) -> Dict[str, Any]:
        """Get orchestration status."""
        return await self.orchestration_engine.get_status(orchestration_id)

    async def stop_orchestration(self, orchestration_id: str) -> None:
        """Stop an orchestration."""
        await self.orchestration_engine.stop_orchestration(orchestration_id)

    async def cancel_orchestration(self, orchestration_id: str) -> None:
        """Cancel an orchestration."""
        await self.orchestration_engine.cancel_orchestration(orchestration_id)

    # ------------------------------------------------------------------
    # Messaging (delegates to FoundryMessageBridge)
    # ------------------------------------------------------------------

    async def send_message_to_agent(
        self,
        agent_id: str,
        message: str,
        orchestration_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a message to a PurposeDrivenAgent via the bridge."""
        return await self.message_bridge.deliver_to_agent(
            agent_id=agent_id,
            message=message,
            orchestration_id=orchestration_id,
        )

    async def send_message_to_foundry(
        self,
        agent_id: str,
        message: str,
        orchestration_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a PurposeDrivenAgent response to Foundry."""
        return await self.message_bridge.send_to_foundry(
            agent_id=agent_id,
            message=message,
            orchestration_id=orchestration_id,
        )

    async def broadcast_purpose_alignment(
        self,
        orchestration_id: str,
        purpose: str,
        purpose_scope: str = "",
    ) -> List[Dict[str, Any]]:
        """Broadcast purpose alignment to all agents in an orchestration."""
        return await self.message_bridge.broadcast_purpose_alignment(
            orchestration_id=orchestration_id,
            purpose=purpose,
            purpose_scope=purpose_scope,
        )

    # ------------------------------------------------------------------
    # Health / Status
    # ------------------------------------------------------------------

    async def health_check(self) -> Dict[str, Any]:
        """Return kernel health status."""
        return {
            "status": "healthy" if self._initialized else "not_initialized",
            "environment": self.config.environment,
            "foundry_connected": self._foundry_service is not None,
            "agents_registered": self.agent_manager.agent_count,
            "active_orchestrations": self.orchestration_engine.orchestration_count,
            "messages_bridged": self.message_bridge.message_count,
        }
