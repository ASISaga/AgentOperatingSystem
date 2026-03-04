"""
PurposeDrivenAgent - Standalone fundamental building block.

This module provides the complete, standalone implementation of PurposeDrivenAgent —
the core abstraction of the Agent Operating System (AOS).

PurposeDrivenAgent works against a perpetual, assigned purpose rather than
short-term tasks.  It is the fundamental building block that makes AOS an
operating system of Purpose-Driven, Perpetual Agents.

Architecture components
-----------------------
- **LoRA Adapters**: Provide domain-specific knowledge (language, vocabulary,
  concepts, and agent persona) to specialise the agent via the ``adapter_name``
  parameter.
- **Core Purposes**: Incorporated into the primary LLM context to guide all
  agent decisions and behaviours.
- **MCP Integration**: :class:`ContextMCPServer` provides context management,
  domain-specific tools, and access to external software systems.

PurposeDrivenAgent inherits from ``agent_framework.Agent`` (Microsoft Agent
Framework) when the package is available, establishing it as the foundational
AOS building block on top of the agent-framework runtime.
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Protocol

from purpose_driven_agent.context_server import ContextMCPServer
from purpose_driven_agent.ml_interface import IMLService, NoOpMLService
from aos_mcp_servers.routing import MCPToolDefinition, MCPTransportType


# ---------------------------------------------------------------------------
# A2A Agent Tool — represents a PurposeDrivenAgent exposed as an AgentTool
# ---------------------------------------------------------------------------


@dataclass
class A2AAgentTool:
    """Represents a PurposeDrivenAgent as an Agent-to-Agent (A2A) tool.

    This is the data structure returned by :meth:`PurposeDrivenAgent.as_tool`.
    It mirrors the ``azure.ai.projects.models.AgentTool`` shape so that the
    AOS kernel or a coordinator agent can register specialist agents as callable
    tools in the Foundry Agent Service.

    Attributes:
        name: Tool name — the agent's role (e.g. ``"CTO"``).
        description: Tool description — pulled from the agent's purpose
            (mission statement) to guide the LLM's routing logic.
        connection_id: The A2A connection string for the Azure AI Project.
        agent_id: The local agent identifier.
        foundry_agent_id: The Foundry-assigned agent ID (set after registration).
        metadata: Additional metadata about the agent tool.
    """

    name: str
    description: str
    connection_id: str
    agent_id: str
    foundry_agent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_foundry_tool_definition(self, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Return a Foundry-compatible tool definition dict.

        This can be passed to ``AIProjectClient.create_agent(tools=[...])``
        to register this agent as a callable tool.

        Args:
            thread_id: Optional thread ID to inject so
                the specialist agent inherits the orchestration context.

        Returns:
            Dictionary compatible with the Foundry Agent Service tool schema.
        """
        definition: Dict[str, Any] = {
            "type": "agent",
            "agent": {
                "name": self.name,
                "description": self.description,
                "connection_id": self.connection_id,
                "agent_id": self.agent_id,
            },
        }
        if self.foundry_agent_id:
            definition["agent"]["foundry_agent_id"] = self.foundry_agent_id
        if thread_id:
            definition["agent"]["thread_id"] = thread_id
        if self.metadata:
            definition["agent"]["metadata"] = self.metadata
        return definition

# ---------------------------------------------------------------------------
# Optional agent_framework integration
# ---------------------------------------------------------------------------

try:
    from agent_framework import Agent as _AgentFrameworkBase  # type: ignore[import]

    _AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:  # pragma: no cover
    # Stub base class when agent_framework package is not installed.
    # Install via:  pip install agent-framework>=1.0.0rc1
    class _AgentFrameworkBase:  # type: ignore[no-redef]  # pylint: disable=too-few-public-methods
        """Stub for agent_framework.Agent when the package is not available."""

    _AGENT_FRAMEWORK_AVAILABLE = False


# ---------------------------------------------------------------------------
# MCPServerProtocol
# ---------------------------------------------------------------------------


class MCPServerProtocol(Protocol):
    """
    Structural protocol for MCP servers registered with :class:`PurposeDrivenAgent`.

    Any object that provides ``call_tool`` and ``list_tools`` async methods
    satisfies this protocol and can be registered via
    :meth:`PurposeDrivenAgent.register_mcp_server`.

    The three concrete transport classes — :class:`~aos_mcp_servers.routing.MCPStdioTool`,
    :class:`~aos_mcp_servers.routing.MCPStreamableHTTPTool`, and
    :class:`~aos_mcp_servers.routing.MCPWebsocketTool` — all satisfy this
    protocol.  They are defined in the ``aos-mcp-servers`` package.

    The :class:`~aos_client.mcp.MCPServerConfig` Pydantic model (from
    ``aos-client-sdk``) describes these servers declaratively for use in
    :class:`~aos_client.models.OrchestrationRequest`, letting clients select
    which MCP servers each agent should connect to.
    """

    async def list_tools(self) -> List[MCPToolDefinition]:
        """
        Return the :class:`MCPToolDefinition` objects available on this server.

        Called by :meth:`~PurposeDrivenAgent.discover_mcp_tools` to build the
        tool-name → server-name routing index.

        Returns:
            List of :class:`~purpose_driven_agent.mcp_routing.MCPToolDefinition` objects.
        """
        ...  # pragma: no cover

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Invoke *tool_name* with *params* and return the result."""
        ...  # pragma: no cover


# ---------------------------------------------------------------------------
# PurposeDrivenAgent (abstract)
# ---------------------------------------------------------------------------


class PurposeDrivenAgent(_AgentFrameworkBase, ABC):
    """
    Purpose-Driven Perpetual Agent — the fundamental building block of AOS.

    This is an **abstract base class** (ABC).  You *cannot* instantiate it
    directly.  Create a concrete subclass (e.g. :class:`GenericPurposeDrivenAgent`,
    ``LeadershipAgent``, ``CMOAgent``) that implements :meth:`get_agent_type`.

    Unlike task-based agents that execute and terminate, a PurposeDrivenAgent
    works continuously against an assigned, long-term purpose.

    Key characteristics
    -------------------
    - **Persistent**: remains registered and active indefinitely.
    - **Event-driven**: awakens in response to events.
    - **Stateful**: maintains context across all interactions via MCP.
    - **Resource-efficient**: sleeps when idle, awakens on events.
    - **Purpose-driven**: works toward a defined, long-term purpose.
    - **Context-aware**: uses :class:`ContextMCPServer` for state preservation.
    - **Autonomous**: makes decisions aligned with its purpose.
    - **Adapter-mapped**: purpose mapped to a LoRA adapter for domain expertise.

    Example::

        # PurposeDrivenAgent is abstract — this raises TypeError:
        # agent = PurposeDrivenAgent(...)  # ❌

        # Use the generic concrete subclass instead:
        from purpose_driven_agent import GenericPurposeDrivenAgent

        agent = GenericPurposeDrivenAgent(
            agent_id="assistant",
            purpose="General assistance and task execution",
            adapter_name="general",
        )
        await agent.initialize()
        await agent.start()
    """

    def __init__(
        self,
        agent_id: str,
        purpose: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        agent_type: Optional[str] = None,
        purpose_scope: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        system_message: Optional[str] = None,
        adapter_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        aos: Optional[Any] = None,
        ml_service: Optional[IMLService] = None,
    ) -> None:
        """
        Initialise a Purpose-Driven Agent.

        Purposes are perpetual — there are no success criteria.  The agent
        works toward its purpose indefinitely, guided by its purpose scope.

        Args:
            agent_id: Unique identifier for this agent.
            purpose: The long-term, perpetual purpose this agent works
                toward (added to LLM context).
            name: Human-readable agent name (defaults to *agent_id*).
            role: Agent role/type (defaults to ``"agent"``).
            agent_type: Type label (defaults to ``"purpose_driven"``).
            purpose_scope: Scope/boundaries of the purpose.
            tools: Tools available to the agent (via MCP).
            system_message: System message for the agent.
            adapter_name: Name for the LoRA adapter providing domain knowledge
                and persona (e.g. ``"ceo"``, ``"cfo"``).
            config: Optional configuration dictionary.  Recognised sub-keys:

                - ``"context_server"`` (dict): forwarded to
                  :class:`ContextMCPServer`.

            aos: Optional reference to an AgentOperatingSystem instance for
                querying available personas.
            ml_service: Optional :class:`IMLService` implementation.  Defaults
                to :class:`NoOpMLService` which raises ``NotImplementedError``
                if ML operations are attempted.
        """
        # Initialise agent_framework.Agent base class when available.
        if _AGENT_FRAMEWORK_AVAILABLE:
            try:
                super().__init__(
                    client=None,
                    name=name or agent_id,
                    instructions=system_message or purpose,
                )
            except TypeError:
                # Agent signature may vary across rc versions; fall back silently.
                pass

        # ---- Core identity ------------------------------------------------
        self.agent_id = agent_id
        self.name = name or agent_id
        self.role = role or "agent"
        self.agent_type = agent_type or "purpose_driven"
        self.config: Dict[str, Any] = config or {}
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }
        self.state = "initialized"

        # ---- Logging -------------------------------------------------------
        self.logger = logging.getLogger(f"purpose_driven_agent.{agent_id}")

        # ---- Perpetual operation state ------------------------------------
        self.tools: List[Any] = tools or []
        self.system_message: str = system_message or ""
        self.adapter_name: Optional[str] = adapter_name
        self.is_running: bool = False
        self.sleep_mode: bool = True
        self.event_subscriptions: Dict[str, List[Callable]] = {}
        self.wake_count: int = 0
        self.total_events_processed: int = 0

        # Context is preserved via ContextMCPServer (one instance per agent)
        self.mcp_context_server: Optional[ContextMCPServer] = None

        # Dynamic MCP server registry: name -> {server, tags, enabled}
        # Only enabled servers contribute tools to the LLM context window.
        self.mcp_servers: Dict[str, Dict[str, Any]] = {}

        # Tool-name → server-name index built by discover_mcp_tools().
        # Enables tool-name-based routing: the agent routes to the correct
        # server without the caller needing to know the server's location.
        self._tool_index: Dict[str, str] = {}

        # ---- Purpose attributes --------------------------------------------
        self.purpose: str = purpose
        self.purpose_scope: str = purpose_scope or "General purpose operation"

        self.purpose_metrics: Dict[str, int] = {
            "purpose_aligned_actions": 0,
            "purpose_evaluations": 0,
            "decisions_made": 0,
            "goals_achieved": 0,
        }
        self.active_goals: List[Dict[str, Any]] = []
        self.completed_goals: List[Dict[str, Any]] = []

        # ---- Optional AOS / ML references ---------------------------------
        self.aos = aos
        self.ml_service: IMLService = ml_service or NoOpMLService()

        # ---- Foundry Agent Service registration ----------------------------
        self.foundry_agent_id: Optional[str] = None

        self.logger.info(
            "PurposeDrivenAgent '%s' created | purpose='%s' | adapter='%s'",
            self.agent_id,
            self.purpose,
            self.adapter_name,
        )

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def get_agent_type(self) -> List[str]:
        """
        Return the personas/skills that compose this agent.

        Concrete subclasses must select personas from those available in
        the AgentOperatingSystem registry.  Each persona corresponds to a
        LoRA adapter that provides domain-specific knowledge.

        Implementation pattern::

            def get_agent_type(self) -> List[str]:
                available = self.get_available_personas()
                if "leadership" in available:
                    return ["leadership"]
                return ["leadership"]  # fall back to default

        Returns:
            Non-empty list of persona name strings.
        """

    # ------------------------------------------------------------------
    # Foundry Agent Service registration
    # ------------------------------------------------------------------

    async def register_with_foundry(
        self,
        project_client: Any,
        model: str = "gpt-4o",
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Register this agent with the Azure AI Foundry Agent Service.

        Creates a corresponding agent in the Foundry project so that
        multi-agent orchestrations can be managed by the Foundry Agent
        Service while this :class:`PurposeDrivenAgent` continues to run
        as Python code inside an Azure Function.

        Args:
            project_client: An :class:`~aos_client.foundry.AIProjectClient`
                instance connected to the target AI Foundry project.
            model: Model deployment name (default ``"gpt-4o"``).
            tools: Optional tool definitions to register with the Foundry agent.

        Returns:
            The Foundry-assigned agent ID.
        """
        agent = await project_client.create_agent(
            model=model,
            name=self.name,
            instructions=self.purpose,
            tools=tools or [],
            tool_resources={},
        )
        self.foundry_agent_id = agent.agent_id
        self.logger.info(
            "Registered with Foundry Agent Service: foundry_id='%s'",
            self.foundry_agent_id,
        )
        return self.foundry_agent_id

    # ------------------------------------------------------------------
    # A2A (Agent-to-Agent) Tool Factory
    # ------------------------------------------------------------------

    def get_a2a_connection_id(self) -> str:
        """Resolve the A2A connection ID for this agent based on its role.

        The connection ID uniquely identifies the Agent-to-Agent endpoint
        provisioned in the Azure AI Project.  It is read from the
        environment variable ``A2A_CONNECTION_ID_{ROLE}`` (upper-cased
        role name), falling back to ``A2A_CONNECTION_ID_DEFAULT``, and
        finally to a deterministic placeholder built from the role name.

        Returns:
            Connection ID string for this agent's A2A endpoint.
        """
        role_key = self.role.upper().replace(" ", "_").replace("-", "_")
        # Try role-specific env var first
        connection_id = os.environ.get(f"A2A_CONNECTION_ID_{role_key}")
        if connection_id:
            return connection_id
        # Fall back to default connection
        connection_id = os.environ.get("A2A_CONNECTION_ID_DEFAULT")
        if connection_id:
            return connection_id
        # Deterministic placeholder for local/test mode
        return f"a2a-connection-{self.role.lower().replace(' ', '-')}"

    def as_tool(self, thread_id: Optional[str] = None) -> A2AAgentTool:
        """Return this agent as an A2A tool for enrollment in another agent.

        The returned :class:`A2AAgentTool` can be registered with a
        coordinator agent (e.g. the CEO) so that the LLM can dynamically
        discover, consult, and delegate to this specialist.

        The tool's *description* is pulled from the agent's :attr:`purpose`
        (its mission statement) so the LLM's routing logic can determine
        when to invoke this specialist.

        When *thread_id* is provided the specialist inherits the full
        orchestration context from that thread, enabling contextual continuity
        across the Agent-to-Agent handshake.

        Args:
            thread_id: Optional thread ID for context injection.

        Returns:
            :class:`A2AAgentTool` instance representing this agent.
        """
        tool = A2AAgentTool(
            name=self.role,
            description=self.purpose,
            connection_id=self.get_a2a_connection_id(),
            agent_id=self.agent_id,
            foundry_agent_id=self.foundry_agent_id,
            metadata={
                "adapter_name": self.adapter_name or "",
                "agent_type": self.agent_type,
            },
        )
        if thread_id:
            tool.metadata["thread_id"] = thread_id
        return tool

    # ------------------------------------------------------------------
    # AOS persona helpers
    # ------------------------------------------------------------------

    def get_available_personas(self) -> List[str]:
        """
        Query the AgentOperatingSystem for available LoRA adapter personas.

        Returns:
            List of persona name strings.  Falls back to a built-in default
            set when no AOS instance is provided.
        """
        if self.aos:
            return self.aos.get_available_personas()
        self.logger.warning(
            "AgentOperatingSystem not provided — using built-in default personas"
        )
        return [
            "generic",
            "leadership",
            "marketing",
            "finance",
            "operations",
            "technology",
            "hr",
            "legal",
        ]

    def validate_personas(self, personas: List[str]) -> bool:
        """
        Validate that the requested personas are available.

        Args:
            personas: List of persona names to validate.

        Returns:
            ``True`` if all personas are available (or if AOS is not wired up,
            in which case any personas are accepted).
        """
        if self.aos:
            return self.aos.validate_personas(personas)
        return True

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> bool:
        """
        Initialise agent resources and the MCP context server.

        Sets up the dedicated :class:`ContextMCPServer` for context
        preservation, loads previously saved state, configures event
        listeners, and stores the purpose in the MCP context so it is
        available to the primary LLM context.

        Returns:
            ``True`` if initialisation was successful.
        """
        try:
            self.logger.info("Initialising perpetual agent '%s'", self.agent_id)

            await self._setup_mcp_context_server()
            await self._load_context_from_mcp()
            await self._setup_event_listeners()

            self.logger.info("Perpetual agent '%s' base init complete", self.agent_id)

            # Purpose-specific setup
            await self._load_purpose_context()

            if self.mcp_context_server:
                await self.mcp_context_server.set_context("purpose", self.purpose)
                await self.mcp_context_server.set_context("purpose_scope", self.purpose_scope)

            self.logger.info(
                "PurposeDrivenAgent '%s' initialised — purpose in LLM context, "
                "adapter '%s' provides domain expertise",
                self.agent_id,
                self.adapter_name,
            )
            return True

        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.logger.error(
                "Failed to initialise agent '%s': %s", self.agent_id, exc
            )
            return False

    async def start(self) -> bool:
        """
        Start perpetual operation — the agent runs indefinitely.

        Creates a background task running :meth:`_perpetual_loop`.

        Returns:
            ``True`` when the background task has been scheduled.
        """
        try:
            self.logger.info("Starting perpetual agent '%s'", self.agent_id)
            self.is_running = True
            asyncio.create_task(self._perpetual_loop())
            self.logger.info(
                "Perpetual agent '%s' is now running indefinitely", self.agent_id
            )
            return True
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.logger.error(
                "Failed to start perpetual agent '%s': %s", self.agent_id, exc
            )
            return False

    async def stop(self) -> bool:
        """
        Stop perpetual operations gracefully.

        Saves purpose-specific state to the MCP context server before
        setting :attr:`is_running` to ``False``.

        Returns:
            ``True`` if stopped successfully.
        """
        try:
            self.logger.info("Stopping perpetual agent '%s'", self.agent_id)

            if self.mcp_context_server:
                await self.mcp_context_server.set_context("active_goals", self.active_goals)
                await self.mcp_context_server.set_context(
                    "completed_goals", self.completed_goals
                )
                await self.mcp_context_server.set_context(
                    "purpose_metrics", self.purpose_metrics
                )

            await self._save_context_to_mcp()
            self.is_running = False
            self.logger.info("Perpetual agent '%s' stopped gracefully", self.agent_id)
            return True

        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.logger.error(
                "Error stopping perpetual agent '%s': %s", self.agent_id, exc
            )
            return False

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incoming message by delegating to :meth:`handle_event`.

        Args:
            message: Message payload.

        Returns:
            Response dictionary.
        """
        return await self.handle_event(message)

    async def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an event with purpose-driven processing.

        This is the core of the perpetual model: the agent awakens,
        evaluates purpose alignment, dispatches to subscribed handlers,
        saves context via MCP, then returns to sleep.

        Args:
            event: Event payload dict.  The ``"type"`` key is used for
                handler dispatch; the ``"data"`` key is forwarded to handlers.

        Returns:
            Response dictionary with at minimum:

            - ``"status"`` — ``"success"`` or ``"error"``.
            - ``"processed_by"`` — agent ID.
            - ``"purpose_alignment"`` — alignment evaluation result.
            - ``"purpose"`` — this agent's purpose string.
        """
        try:
            alignment = await self.evaluate_purpose_alignment(event)
            if alignment["aligned"]:
                self.purpose_metrics["purpose_aligned_actions"] += 1

            await self._awaken()
            await self.select_mcp_servers_for_event(event)

            event_type = event.get("type")
            self.logger.info(
                "Agent '%s' processing event type '%s'", self.agent_id, event_type
            )

            result: Dict[str, Any] = {
                "status": "success",
                "processed_by": self.agent_id,
            }

            if event_type and event_type in self.event_subscriptions:
                handler_results = []
                for handler in self.event_subscriptions[event_type]:
                    try:
                        handler_results.append(await handler(event.get("data", {})))
                    except Exception as exc:  # pylint: disable=broad-exception-caught
                        self.logger.error("Handler error for '%s': %s", event_type, exc)
                        handler_results.append({"error": str(exc)})
                result["handler_results"] = handler_results

            await self._save_context_to_mcp()
            self.total_events_processed += 1

            result["purpose_alignment"] = alignment
            result["purpose"] = self.purpose

            await self._sleep()
            return result

        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.logger.error("Error handling event: %s", exc)
            return {"status": "error", "error": str(exc)}

    async def subscribe_to_event(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], Any],
    ) -> bool:
        """
        Subscribe a handler callable to an event type.

        When the event occurs, the agent awakens and executes the handler.

        Args:
            event_type: Event type string to subscribe to.
            handler: Async callable invoked with ``event["data"]`` when the
                event is received.

        Returns:
            ``True`` if subscription was successful.
        """
        try:
            self.event_subscriptions.setdefault(event_type, []).append(handler)
            self.logger.info(
                "Agent '%s' subscribed to event '%s' (%d handlers total)",
                self.agent_id,
                event_type,
                len(self.event_subscriptions[event_type]),
            )
            return True
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.logger.error("Failed to subscribe to event '%s': %s", event_type, exc)
            return False

    # ------------------------------------------------------------------
    # Actions / ML pipeline
    # ------------------------------------------------------------------

    async def act(self, action: str, params: Dict[str, Any]) -> Any:
        """
        Perform a named action, including ML pipeline operations.

        Automatically injects :attr:`adapter_name` into LoRA training and
        inference params when not explicitly set.

        Args:
            action: One of ``"trigger_lora_training"``,
                ``"run_azure_ml_pipeline"``, or ``"aml_infer"``.
            params: Action-specific parameter dictionary.

        Returns:
            Action-specific result.

        Raises:
            ValueError: For unknown *action* names.
        """
        # Inject adapter_name automatically
        if self.adapter_name:
            if action == "trigger_lora_training":
                for adapter in params.get("adapters", []):
                    adapter.setdefault("adapter_name", self.adapter_name)
            elif action == "aml_infer":
                params.setdefault("agent_id", self.adapter_name)

        if action == "trigger_lora_training":
            return await self.ml_service.trigger_lora_training(
                params["training_params"], params["adapters"]
            )
        if action == "run_azure_ml_pipeline":
            return await self.ml_service.run_pipeline(
                params["subscription_id"],
                params["resource_group"],
                params["workspace_name"],
            )
        if action == "aml_infer":
            return await self.ml_service.infer(params["agent_id"], params["prompt"])
        raise ValueError(f"Unknown action: '{action}'")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task dictionary.

        Expects ``task["action"]`` and optional ``task["params"]``.

        Args:
            task: Task dict with ``"action"`` and ``"params"`` keys.

        Returns:
            Result dictionary with ``"status"`` and ``"result"`` or ``"error"``.
        """
        try:
            action = task.get("action")
            params: Dict[str, Any] = task.get("params", {})
            if action:
                result = await self.act(action, params)
                return {"status": "success", "result": result}
            return {"status": "error", "error": "No action specified"}
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return {"status": "error", "error": str(exc)}

    # ------------------------------------------------------------------
    # Purpose operations
    # ------------------------------------------------------------------

    async def evaluate_purpose_alignment(
        self, action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate whether an action aligns with the agent's purpose.

        In production, this would use LLM reasoning or a rules engine.
        This implementation returns a placeholder alignment score of 0.85.

        Args:
            action: Action payload (``"type"`` key used for logging).

        Returns:
            Dict with keys: ``"action"``, ``"aligned"``, ``"alignment_score"``,
            ``"reasoning"``, ``"timestamp"``.
        """
        self.purpose_metrics["purpose_evaluations"] += 1
        evaluation = {
            "action": action.get("type", "unknown"),
            "aligned": True,
            "alignment_score": 0.85,
            "reasoning": f"Action aligns with purpose: {self.purpose}",
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logger.debug(
            "Purpose alignment: aligned=%s score=%.2f",
            evaluation["aligned"],
            evaluation["alignment_score"],
        )
        return evaluation

    async def align_purpose_to_orchestration(
        self,
        orchestration_purpose: str,
        orchestration_scope: str = "",
    ) -> Dict[str, Any]:
        """
        Align this agent's working purpose to an orchestration's overarching purpose.

        When an agent participates in a purpose-driven orchestration, it creates
        an aligned purpose that combines the orchestration's overarching goal with
        its own domain-specific knowledge, skill, and persona (provided by the
        LoRA adapter).

        The agent's *original* purpose is preserved and used to inform how it
        contributes to the orchestration purpose.  The ``aligned_purpose`` is
        stored in MCP context so that subsequent event handling, decision-making,
        and goal tracking operate under the aligned purpose for the duration of
        the orchestration.

        Purposes are perpetual — there are no success criteria to merge.

        Args:
            orchestration_purpose: The overarching purpose of the orchestration.
            orchestration_scope: Scope/boundaries of the orchestration purpose.

        Returns:
            Dict with keys: ``"agent_id"``, ``"original_purpose"``,
            ``"aligned_purpose"``, ``"orchestration_purpose"``,
            ``"alignment_strategy"``, ``"timestamp"``.
        """
        original_purpose = self.purpose

        # Build an aligned purpose that merges orchestration goal with agent
        # domain expertise (adapter_name provides the agent's persona).
        domain = self.adapter_name or "general"
        aligned_purpose = (
            f"Contribute {domain} expertise toward: {orchestration_purpose}. "
            f"Agent domain purpose: {original_purpose}"
        )

        # Merge scopes
        merged_scope = orchestration_scope or self.purpose_scope
        if orchestration_scope and self.purpose_scope:
            merged_scope = f"{orchestration_scope} | Agent scope: {self.purpose_scope}"

        # Apply the alignment
        self.purpose = aligned_purpose
        self.purpose_scope = merged_scope

        # Persist to MCP context
        if self.mcp_context_server:
            await self.mcp_context_server.set_context("purpose", self.purpose)
            await self.mcp_context_server.set_context("purpose_scope", self.purpose_scope)
            await self.mcp_context_server.set_context("original_purpose", original_purpose)
            await self.mcp_context_server.set_context(
                "orchestration_purpose", orchestration_purpose
            )

        alignment_result = {
            "agent_id": self.agent_id,
            "original_purpose": original_purpose,
            "aligned_purpose": aligned_purpose,
            "orchestration_purpose": orchestration_purpose,
            "alignment_strategy": (
                f"Merged orchestration purpose with {domain} domain expertise"
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.logger.info(
            "Agent '%s' aligned purpose to orchestration: %s",
            self.agent_id,
            orchestration_purpose,
        )
        return alignment_result

    async def restore_original_purpose(self) -> bool:
        """
        Restore the agent's original purpose after an orchestration completes.

        Retrieves the ``original_purpose`` stored during
        :meth:`align_purpose_to_orchestration` and reapplies it.

        Returns:
            ``True`` if the original purpose was restored, ``False`` if no
            original purpose was stored (agent was not aligned).
        """
        if self.mcp_context_server:
            original = await self.mcp_context_server.get_context("original_purpose")
            if original:
                self.purpose = original
                await self.mcp_context_server.set_context("purpose", self.purpose)
                await self.mcp_context_server.set_context("orchestration_purpose", None)
                self.logger.info(
                    "Agent '%s' restored original purpose: %s",
                    self.agent_id,
                    self.purpose,
                )
                return True
        return False

    # ------------------------------------------------------------------
    # Dynamic MCP server registration and routing
    # ------------------------------------------------------------------

    def register_mcp_server(
        self,
        name: str,
        server: MCPServerProtocol,
        tags: Optional[List[str]] = None,
        enabled: bool = False,
    ) -> None:
        """
        Register an external MCP server with this agent.

        Registered servers are disabled by default to avoid consuming LLM
        context window with tools that may not be needed for every event.
        Call :meth:`enable_mcp_server` explicitly, or use
        :meth:`select_mcp_servers_for_event` to activate servers dynamically.

        Args:
            name: Unique name identifying this MCP server.
            server: MCP server instance.  Must expose ``call_tool(tool_name,
                params)`` as an async callable for use with
                :meth:`route_mcp_request`.
            tags: Capability tags used for dynamic server selection
                (e.g. ``["file_system", "search"]``).  During
                :meth:`select_mcp_servers_for_event` a server is enabled when
                its tags overlap with the event's ``"tags"`` list or when an
                event ``"type"`` matches one of its tags.
            enabled: Whether the server starts in an enabled state.  Defaults
                to ``False`` so newly registered servers do not immediately
                expand the context window.
        """
        self.mcp_servers[name] = {
            "server": server,
            "tags": list(tags or []),
            "enabled": enabled,
        }
        self.logger.info(
            "Registered MCP server '%s' | tags=%s | enabled=%s",
            name,
            tags,
            enabled,
        )

    async def enable_mcp_server(self, name: str) -> bool:
        """
        Enable a registered MCP server so its tools enter the LLM context.

        Args:
            name: Name of the registered server to enable.

        Returns:
            ``True`` if the server was found and enabled, ``False`` if no
            server with *name* is registered.
        """
        if name not in self.mcp_servers:
            self.logger.warning("Cannot enable unknown MCP server '%s'", name)
            return False
        self.mcp_servers[name]["enabled"] = True
        self.logger.info("Enabled MCP server '%s'", name)
        return True

    async def disable_mcp_server(self, name: str) -> bool:
        """
        Disable a registered MCP server, removing its tools from the LLM context.

        Args:
            name: Name of the registered server to disable.

        Returns:
            ``True`` if the server was found and disabled, ``False`` if no
            server with *name* is registered.
        """
        if name not in self.mcp_servers:
            self.logger.warning("Cannot disable unknown MCP server '%s'", name)
            return False
        self.mcp_servers[name]["enabled"] = False
        self.logger.info("Disabled MCP server '%s'", name)
        return True

    def get_active_mcp_servers(self) -> Dict[str, MCPServerProtocol]:
        """
        Return only the currently enabled MCP server instances.

        Use this to expose tools to the LLM — pass the result to the LLM
        tool-calling layer so only relevant tools occupy the context window.

        Returns:
            Dict mapping server name to server instance for every enabled server.
        """
        return {
            name: entry["server"]
            for name, entry in self.mcp_servers.items()
            if entry["enabled"]
        }

    async def route_mcp_request(
        self,
        server_name: str,
        tool_name: str,
        params: Dict[str, Any],
    ) -> Any:
        """
        Route a tool call to a specific named MCP server.

        Raises:
            ValueError: If *server_name* is not registered.
            RuntimeError: If the target server is currently disabled.

        Args:
            server_name: Name of the target MCP server.
            tool_name: Tool to invoke on that server.
            params: Tool parameters.

        Returns:
            Result returned by ``server.call_tool(tool_name, params)``.
        """
        entry = self.mcp_servers.get(server_name)
        if entry is None:
            raise ValueError(f"MCP server '{server_name}' is not registered")
        if not entry["enabled"]:
            raise RuntimeError(
                f"MCP server '{server_name}' is disabled; enable it before routing requests"
            )
        self.logger.debug(
            "Routing tool '%s' to MCP server '%s'", tool_name, server_name
        )
        return await entry["server"].call_tool(tool_name, params)

    async def select_mcp_servers_for_event(
        self, event: Dict[str, Any]
    ) -> List[str]:
        """
        Dynamically enable only the MCP servers relevant to *event*.

        Compares the event's ``"tags"`` list and ``"type"`` string against each
        server's registered tags.  A server is enabled when:

        - the event carries no ``"tags"`` (no filter → all servers enabled), or
        - the server's tags and the event's tags share at least one element, or
        - the event's ``"type"`` appears in the server's tags.

        All non-matching servers are disabled.  This keeps the LLM context
        window focused on the tools relevant to the current event.

        Args:
            event: Event payload dict.  Recognised keys:
                ``"tags"`` (list of str) and ``"type"`` (str).

        Returns:
            List of server names that were activated.
        """
        event_tags: set = set(event.get("tags", []))
        event_type: str = event.get("type", "")
        activated: List[str] = []

        for name, entry in self.mcp_servers.items():
            server_tags: set = set(entry["tags"])
            if (
                not event_tags  # no filter: enable all registered servers
                or bool(event_tags & server_tags)  # tag overlap
                or (event_type and event_type in server_tags)  # type matches a tag
            ):
                entry["enabled"] = True
                activated.append(name)
            else:
                entry["enabled"] = False

        if self.mcp_servers:
            self.logger.info(
                "Dynamic MCP selection for event type '%s': activated=%s",
                event_type,
                activated,
            )
        return activated

    async def discover_mcp_tools(self) -> Dict[str, str]:
        """
        Discover tools across all enabled MCP servers and rebuild the tool index.

        Calls ``list_tools()`` on every **enabled** server (mirroring
        ``ListToolsAsync()`` in the Microsoft Agent Framework) and constructs
        an internal ``tool_name → server_name`` lookup dictionary.

        After this call, :meth:`invoke_tool` can route any discovered tool to
        the correct server automatically, without the caller needing to know
        the server's physical location.

        When two enabled servers expose a tool with the same name, the **last
        server iterated** wins.  A warning is logged so operators can detect
        and resolve the collision by renaming the tool or disabling the
        unwanted server.

        Returns:
            A copy of the rebuilt ``tool_name → server_name`` index.
        """
        self._tool_index = {}
        for name, entry in self.mcp_servers.items():
            if not entry["enabled"]:
                continue
            try:
                tools: List[MCPToolDefinition] = await entry["server"].list_tools()
                for tool in tools:
                    if tool.name in self._tool_index:
                        self.logger.warning(
                            "Tool '%s' already registered by server '%s'; "
                            "server '%s' will override it in the index",
                            tool.name,
                            self._tool_index[tool.name],
                            name,
                        )
                    self._tool_index[tool.name] = name
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self.logger.error(
                    "Failed to list tools from MCP server '%s': %s", name, exc
                )

        self.logger.info(
            "Discovered %d tools across %d active MCP servers",
            len(self._tool_index),
            sum(1 for e in self.mcp_servers.values() if e["enabled"]),
        )
        return dict(self._tool_index)

    async def invoke_tool(
        self, tool_name: str, params: Dict[str, Any]
    ) -> Any:
        """
        Invoke a tool by name, routing to the correct MCP server automatically.

        Uses the tool index built by :meth:`discover_mcp_tools` to determine
        which server exposes *tool_name*, then delegates to
        :meth:`route_mcp_request`.  The caller does not need to know the
        server's transport type or physical location.

        Args:
            tool_name: Name of the tool to invoke.
            params: Tool input parameters.

        Returns:
            Result from the server's ``call_tool`` implementation.

        Raises:
            KeyError: If *tool_name* is not in the tool index.  Call
                :meth:`discover_mcp_tools` first to populate the index.
        """
        server_name = self._tool_index.get(tool_name)
        if server_name is None:
            raise KeyError(
                f"Tool '{tool_name}' not found in tool index. "
                "Call discover_mcp_tools() to populate the index."
            )
        self.logger.debug(
            "invoke_tool: routing '%s' → server '%s'", tool_name, server_name
        )
        return await self.route_mcp_request(server_name, tool_name, params)

    async def make_purpose_driven_decision(
        self, decision_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make a decision guided by the agent's purpose.

        Evaluates each option in ``decision_context["options"]`` for purpose
        alignment and returns the best-scoring option.

        Args:
            decision_context: Dict with an ``"options"`` list of candidate
                action dicts.

        Returns:
            Decision dict with keys: ``"decision_id"``, ``"context"``,
            ``"selected_option"``, ``"reasoning"``, ``"alignment_score"``,
            ``"timestamp"``.
        """
        self.purpose_metrics["decisions_made"] += 1
        options = decision_context.get("options", [])
        evaluated_options = []
        for option in options:
            evaluation = await self.evaluate_purpose_alignment(option)
            evaluated_options.append({"option": option, "evaluation": evaluation})

        best = (
            max(evaluated_options, key=lambda x: x["evaluation"]["alignment_score"])
            if evaluated_options
            else None
        )

        decision: Dict[str, Any] = {
            "decision_id": f"decision_{self.purpose_metrics['decisions_made']}",
            "context": decision_context,
            "selected_option": best["option"] if best else None,
            "reasoning": f"Selected option most aligned with purpose: {self.purpose}",
            "alignment_score": best["evaluation"]["alignment_score"] if best else 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if self.mcp_context_server:
            await self.mcp_context_server.add_memory({"type": "decision", "decision": decision})

        self.logger.info("Made purpose-driven decision: %s", decision["decision_id"])
        return decision

    async def add_goal(
        self,
        goal_description: str,
        success_criteria: Optional[List[str]] = None,
        deadline: Optional[str] = None,
    ) -> str:
        """
        Add an active goal aligned with the agent's purpose.

        Args:
            goal_description: Human-readable description of the goal.
            success_criteria: Criteria for goal completion.
            deadline: Optional ISO-8601 deadline string.

        Returns:
            Assigned goal ID string.
        """
        goal_id = f"goal_{len(self.active_goals) + len(self.completed_goals) + 1}"
        goal: Dict[str, Any] = {
            "goal_id": goal_id,
            "description": goal_description,
            "success_criteria": success_criteria or [],
            "deadline": deadline,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "progress": 0.0,
        }
        self.active_goals.append(goal)
        if self.mcp_context_server:
            await self.mcp_context_server.set_context(f"goal_{goal_id}", goal)
        self.logger.info("Added goal '%s': %s", goal_id, goal_description)
        return goal_id

    async def update_goal_progress(
        self,
        goal_id: str,
        progress: float,
        notes: Optional[str] = None,
    ) -> bool:
        """
        Update progress on an active goal.

        When *progress* reaches 1.0, the goal is moved to
        :attr:`completed_goals`.

        Args:
            goal_id: Goal ID returned by :meth:`add_goal`.
            progress: Fractional progress (0.0 – 1.0).
            notes: Optional progress notes.

        Returns:
            ``True`` if the goal was found and updated.
        """
        for goal in self.active_goals:
            if goal["goal_id"] == goal_id:
                goal["progress"] = progress
                goal["last_updated"] = datetime.utcnow().isoformat()
                if notes:
                    goal.setdefault("notes", []).append(
                        {"timestamp": datetime.utcnow().isoformat(), "note": notes}
                    )
                if progress >= 1.0:
                    goal["status"] = "completed"
                    goal["completed_at"] = datetime.utcnow().isoformat()
                    self.active_goals.remove(goal)
                    self.completed_goals.append(goal)
                    self.purpose_metrics["goals_achieved"] += 1
                    self.logger.info("Goal completed: %s", goal_id)
                if self.mcp_context_server:
                    await self.mcp_context_server.set_context(f"goal_{goal_id}", goal)
                return True
        return False

    # ------------------------------------------------------------------
    # Status / state queries
    # ------------------------------------------------------------------

    async def get_purpose_status(self) -> Dict[str, Any]:
        """
        Return a summary of the agent's purpose-driven operation.

        Returns:
            Dictionary with purpose, metrics, goal counts, and runtime state.
        """
        return {
            "agent_id": self.agent_id,
            "purpose": self.purpose,
            "purpose_scope": self.purpose_scope,
            "metrics": self.purpose_metrics,
            "active_goals": len(self.active_goals),
            "completed_goals": len(self.completed_goals),
            "is_running": self.is_running,
            "total_events_processed": self.total_events_processed,
        }

    async def get_state(self) -> Dict[str, Any]:
        """
        Return the current perpetual operation state.

        Returns:
            Dictionary with adapter name, run state, sleep state, wake/event
            counts, event subscriptions, and MCP context status.
        """
        return {
            "agent_id": self.agent_id,
            "adapter_name": self.adapter_name,
            "is_running": self.is_running,
            "sleep_mode": self.sleep_mode,
            "wake_count": self.wake_count,
            "total_events_processed": self.total_events_processed,
            "subscriptions": list(self.event_subscriptions.keys()),
            "mcp_context_preserved": self.mcp_context_server is not None,
            "registered_mcp_servers": list(self.mcp_servers.keys()),
            "active_mcp_servers": [
                name for name, entry in self.mcp_servers.items() if entry["enabled"]
            ],
            "discovered_tools": list(self._tool_index.keys()),
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a lightweight health check.

        Returns:
            Dict with ``"agent_id"``, ``"state"``, ``"healthy"``, and
            ``"timestamp"``.
        """
        return {
            "agent_id": self.agent_id,
            "state": self.state,
            "healthy": self.state in ("initialized", "running"),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return agent metadata (ID, name, role, state, creation info).

        Returns:
            Metadata dictionary.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "state": self.state,
            "metadata": self.metadata,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _perpetual_loop(self) -> None:
        """Main perpetual loop — runs indefinitely until :attr:`is_running` is False."""
        self.logger.info("Agent '%s' entered perpetual loop", self.agent_id)
        while self.is_running:
            try:
                if self.wake_count % 100 == 0:
                    self.logger.debug(
                        "Agent '%s' heartbeat — processed %d events, awoken %d times",
                        self.agent_id,
                        self.total_events_processed,
                        self.wake_count,
                    )
                await asyncio.sleep(1)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self.logger.error("Error in perpetual loop: %s", exc)
                await asyncio.sleep(5)
        self.logger.info("Agent '%s' exited perpetual loop", self.agent_id)

    async def _awaken(self) -> None:
        """Transition the agent from sleep mode to active."""
        if self.sleep_mode:
            self.sleep_mode = False
            self.wake_count += 1
            self.logger.debug(
                "Agent '%s' awakened (count: %d)", self.agent_id, self.wake_count
            )

    async def _sleep(self) -> None:
        """Transition the agent back to sleep mode."""
        if not self.sleep_mode:
            self.sleep_mode = True
            self.logger.debug("Agent '%s' sleeping", self.agent_id)

    async def _setup_mcp_context_server(self) -> None:
        """Create and initialise the dedicated :class:`ContextMCPServer`."""
        try:
            self.mcp_context_server = ContextMCPServer(
                agent_id=self.agent_id,
                config=self.config.get("context_server", {}),
            )
            await self.mcp_context_server.initialize()
            self.logger.info(
                "ContextMCPServer initialised for agent '%s'", self.agent_id
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.logger.error("Failed to initialise ContextMCPServer: %s", exc)
            raise

    async def _setup_event_listeners(self) -> None:
        """Set up event-listening infrastructure (no-op in standalone mode)."""
        self.logger.debug("Event listeners set up for agent '%s'", self.agent_id)

    async def _load_context_from_mcp(self) -> None:
        """Load previously saved context from the MCP context server."""
        if self.mcp_context_server:
            context = await self.mcp_context_server.get_all_context()
            self.logger.debug(
                "Loaded %d context items from ContextMCPServer", len(context)
            )

    async def _save_context_to_mcp(self) -> None:
        """Persist current operation state to the MCP context server."""
        if self.mcp_context_server:
            await self.mcp_context_server.set_context("wake_count", self.wake_count)
            await self.mcp_context_server.set_context(
                "total_events_processed", self.total_events_processed
            )
            await self.mcp_context_server.set_context(
                "last_active", datetime.utcnow().isoformat()
            )
            self.logger.debug("Saved context to ContextMCPServer")

    async def _load_purpose_context(self) -> None:
        """Restore purpose-specific state (goals, metrics) from MCP."""
        if self.mcp_context_server:
            active = await self.mcp_context_server.get_context("active_goals")
            if active:
                self.active_goals = active
            completed = await self.mcp_context_server.get_context("completed_goals")
            if completed:
                self.completed_goals = completed
            metrics = await self.mcp_context_server.get_context("purpose_metrics")
            if metrics:
                self.purpose_metrics.update(metrics)
        self.logger.debug("Loaded purpose context for '%s'", self.agent_id)


# ---------------------------------------------------------------------------
# GenericPurposeDrivenAgent (concrete)
# ---------------------------------------------------------------------------


class GenericPurposeDrivenAgent(PurposeDrivenAgent):
    """
    Concrete general-purpose implementation of :class:`PurposeDrivenAgent`.

    Use this when you need a basic purpose-driven agent without specialised
    functionality.  For domain-specific use cases prefer purpose-built
    subclasses such as ``LeadershipAgent`` or ``CMOAgent``.

    Example::

        from purpose_driven_agent import GenericPurposeDrivenAgent

        agent = GenericPurposeDrivenAgent(
            agent_id="assistant",
            purpose="General assistance and task execution",
            adapter_name="general",
        )
        await agent.initialize()
        await agent.start()
    """

    def get_agent_type(self) -> List[str]:
        """
        Return ``["generic"]``, selecting the generic LoRA adapter persona.

        Queries the AOS registry and falls back to ``["generic"]`` if the
        persona is unavailable.

        Returns:
            ``["generic"]``
        """
        available = self.get_available_personas()
        if "generic" not in available:
            self.logger.warning(
                "'generic' persona not in AOS registry, using default"
            )
        return ["generic"]
