"""Azure AI Foundry Agent Service integration for the AOS Client SDK.

This module provides classes for interacting with the Azure AI Foundry
Agent Service, enabling multi-agent orchestration managed by Azure AI
Foundry.  The integration surfaces Foundry's agent lifecycle, conversation
threading, and run management through a Pythonic async API that is
consistent with the rest of the AOS Client SDK.

Typical usage::

    from aos_client.foundry import AIProjectClient, FoundryAgentService

    async with AIProjectClient(
        project_endpoint="https://<region>.api.azureml.ms/...",
    ) as project:
        service = FoundryAgentService(project_client=project)
        agent = await service.register_agent(
            agent_id="analyst-01",
            model="gpt-4o",
            name="Financial Analyst",
            instructions="You are a senior financial analyst.",
        )
        orch = await service.create_orchestration(
            agent_ids=[agent.agent_id],
            purpose="Quarterly review",
            context={"quarter": "Q1-2026"},
        )
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Azure AI Foundry REST API version used by this module
# ---------------------------------------------------------------------------
_DEFAULT_API_VERSION = "2024-12-01-preview"


# ===================================================================
# AzureAIAgent
# ===================================================================

class AzureAIAgent:
    """Represents an agent registered in the Azure AI Foundry Agent Service.

    :param agent_id: Unique identifier for the agent.
    :param model: Model deployment name (e.g. ``"gpt-4o"``).
    :param name: Human-readable agent name.
    :param instructions: System-level instructions for the agent.
    :param tools: Tool definitions attached to the agent.
    :param tool_resources: Resources required by the tools.
    :param metadata: Arbitrary metadata key/value pairs.
    :param created_at: Timestamp when the agent was created.
    """

    def __init__(
        self,
        agent_id: str,
        model: str,
        name: str = "",
        instructions: str = "",
        tools: Optional[List[dict]] = None,
        tool_resources: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.agent_id = agent_id
        self.model = model
        self.name = name
        self.instructions = instructions
        self.tools: List[dict] = tools or []
        self.tool_resources: Dict[str, Any] = tool_resources or {}
        self.metadata: Dict[str, Any] = metadata or {}
        self.created_at = created_at

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def update(
        self,
        name: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[dict]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update mutable fields on the agent in-place.

        :param name: New agent name, or ``None`` to keep existing.
        :param instructions: New instructions, or ``None`` to keep existing.
        :param tools: Replacement tool list, or ``None`` to keep existing.
        :param metadata: Replacement metadata dict, or ``None`` to keep existing.
        """
        if name is not None:
            self.name = name
        if instructions is not None:
            self.instructions = instructions
        if tools is not None:
            self.tools = tools
        if metadata is not None:
            self.metadata = metadata

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable dictionary representation.

        :returns: Dictionary with all agent fields.
        """
        return {
            "agent_id": self.agent_id,
            "model": self.model,
            "name": self.name,
            "instructions": self.instructions,
            "tools": self.tools,
            "tool_resources": self.tool_resources,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"AzureAIAgent(agent_id={self.agent_id!r}, model={self.model!r}, name={self.name!r})"


# ===================================================================
# FoundryRun
# ===================================================================

class FoundryRun:
    """Represents a single run of an agent on a conversation thread.

    :param run_id: Unique run identifier.
    :param thread_id: Thread this run belongs to.
    :param agent_id: Agent executing the run.
    :param status: Current run status (``queued``, ``in_progress``,
        ``completed``, ``failed``, ``cancelled``, etc.).
    :param created_at: Timestamp when the run was created.
    :param completed_at: Timestamp when the run finished, if applicable.
    """

    def __init__(
        self,
        run_id: str,
        thread_id: str,
        agent_id: str,
        status: str = "queued",
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> None:
        self.run_id = run_id
        self.thread_id = thread_id
        self.agent_id = agent_id
        self.status = status
        self.created_at = created_at
        self.completed_at = completed_at

    async def poll(self) -> None:
        """Poll the Foundry API and update :attr:`status` in-place.

        .. note::
            This is currently a local stub.  When connected to the live
            Foundry service the method will issue a GET against
            ``/threads/{thread_id}/runs/{run_id}``.
        """
        logger.debug("Polling run %s on thread %s", self.run_id, self.thread_id)
        # Stub: in a live environment this would call the Foundry REST API.

    async def cancel(self) -> None:
        """Request cancellation of the run.

        .. note::
            This is currently a local stub.
        """
        logger.info("Cancelling run %s on thread %s", self.run_id, self.thread_id)
        self.status = "cancelled"

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable dictionary representation.

        :returns: Dictionary with all run fields.
        """
        return {
            "run_id": self.run_id,
            "thread_id": self.thread_id,
            "agent_id": self.agent_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FoundryRun(run_id={self.run_id!r}, thread_id={self.thread_id!r}, "
            f"agent_id={self.agent_id!r}, status={self.status!r})"
        )


# ===================================================================
# FoundryThread
# ===================================================================

class FoundryThread:
    """Represents a conversation thread in the Foundry Agent Service.

    :param thread_id: Unique thread identifier.
    :param metadata: Arbitrary metadata key/value pairs.
    :param created_at: Timestamp when the thread was created.
    """

    def __init__(
        self,
        thread_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.thread_id = thread_id
        self.metadata: Dict[str, Any] = metadata or {}
        self.created_at = created_at
        self._messages: List[Dict[str, Any]] = []

    async def add_message(
        self,
        role: str,
        content: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Add a message to this thread.

        :param role: Message role (``"user"`` or ``"assistant"``).
        :param content: Text content of the message.
        :param attachments: Optional file or data attachments.
        :returns: Dictionary describing the created message.
        """
        message: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "thread_id": self.thread_id,
            "role": role,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if attachments:
            message["attachments"] = attachments
        self._messages.append(message)
        logger.debug("Added message %s to thread %s", message["id"], self.thread_id)
        return message

    async def list_messages(self) -> List[Dict[str, Any]]:
        """Return all messages in this thread.

        :returns: List of message dictionaries ordered by creation time.
        """
        return list(self._messages)

    async def create_run(
        self,
        agent_id: str,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
    ) -> FoundryRun:
        """Create a new run of an agent on this thread.

        :param agent_id: Identifier of the agent to run.
        :param instructions: Override instructions for this run.
        :param additional_instructions: Extra instructions appended to the
            agent's base instructions.
        :returns: A :class:`FoundryRun` tracking the execution.
        """
        run = FoundryRun(
            run_id=str(uuid.uuid4()),
            thread_id=self.thread_id,
            agent_id=agent_id,
            status="queued",
            created_at=datetime.now(timezone.utc),
        )
        logger.info(
            "Created run %s for agent %s on thread %s (instructions_override=%s)",
            run.run_id,
            agent_id,
            self.thread_id,
            instructions is not None,
        )
        return run

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable dictionary representation.

        :returns: Dictionary with all thread fields.
        """
        return {
            "thread_id": self.thread_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"FoundryThread(thread_id={self.thread_id!r})"


# ===================================================================
# AIProjectClient
# ===================================================================

class AIProjectClient:
    """Client for interacting with an Azure AI Foundry Project.

    Wraps the project connection and provides methods for agent, thread,
    and run lifecycle management via the Foundry Agent Service REST API.

    :param project_endpoint: Discovery URL of the AI Foundry project
        (e.g. ``"https://<region>.api.azureml.ms/..."``).
    :param credential: Azure credential for authentication.  When
        ``None``, anonymous access is assumed (suitable for local
        development or testing).
    :param api_version: Foundry REST API version string.
    """

    def __init__(
        self,
        project_endpoint: str,
        credential: Optional[Any] = None,
        api_version: str = _DEFAULT_API_VERSION,
    ) -> None:
        self.project_endpoint = project_endpoint.rstrip("/")
        self.credential = credential
        self.api_version = api_version
        self._session: Optional[Any] = None  # aiohttp.ClientSession placeholder
        # Local stores for stub / offline operation
        self._agents: Dict[str, AzureAIAgent] = {}
        self._threads: Dict[str, FoundryThread] = {}

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> AIProjectClient:
        try:
            import aiohttp  # type: ignore[import-untyped]

            self._session = aiohttp.ClientSession()
        except ImportError:
            logger.warning("aiohttp not installed — HTTP calls will not work")
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    # ------------------------------------------------------------------
    # Auth helpers
    # ------------------------------------------------------------------

    async def _auth_headers(self) -> Dict[str, str]:
        """Build authorization headers from the configured credential.

        :returns: Dictionary with ``Authorization`` header, or empty dict
            when no credential is available.
        """
        if self.credential is None:
            return {}
        try:
            token = self.credential.get_token("https://management.azure.com/.default")
            return {"Authorization": f"Bearer {token.token}"}
        except Exception as exc:
            logger.warning("Failed to obtain auth token: %s. Proceeding without authentication.", exc)
            return {}

    # ------------------------------------------------------------------
    # Low-level HTTP helpers (stubs that fall back to local state)
    # ------------------------------------------------------------------

    async def _get(self, url: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Issue an authenticated GET request.

        Falls back to an empty dict when no session is available so that
        the module remains testable without a live Azure connection.
        """
        if self._session is None:
            logger.debug("No HTTP session — returning empty response for GET %s", url)
            return {}
        headers = await self._auth_headers()
        async with self._session.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _post(self, url: str, json: Any) -> Dict[str, Any]:
        """Issue an authenticated POST request.

        Falls back to an empty dict when no session is available.
        """
        if self._session is None:
            logger.debug("No HTTP session — returning empty response for POST %s", url)
            return {}
        headers = await self._auth_headers()
        async with self._session.post(url, json=json, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _delete(self, url: str) -> None:
        """Issue an authenticated DELETE request.

        No-op when no session is available.
        """
        if self._session is None:
            logger.debug("No HTTP session — skipping DELETE %s", url)
            return
        headers = await self._auth_headers()
        async with self._session.delete(url, headers=headers) as resp:
            resp.raise_for_status()

    # ------------------------------------------------------------------
    # Agent lifecycle
    # ------------------------------------------------------------------

    async def create_agent(
        self,
        model: str,
        name: str = "",
        instructions: str = "",
        tools: Optional[List[dict]] = None,
        tool_resources: Optional[Dict[str, Any]] = None,
    ) -> AzureAIAgent:
        """Create a new agent in the Foundry Agent Service.

        :param model: Model deployment name (e.g. ``"gpt-4o"``).
        :param name: Human-readable agent name.
        :param instructions: System-level instructions for the agent.
        :param tools: Tool definitions to attach.
        :param tool_resources: Resources required by the tools.
        :returns: An :class:`AzureAIAgent` representing the created agent.
        """
        payload: Dict[str, Any] = {
            "model": model,
            "name": name,
            "instructions": instructions,
            "tools": tools or [],
            "tool_resources": tool_resources or {},
        }
        url = f"{self.project_endpoint}/assistants?api-version={self.api_version}"
        data = await self._post(url, json=payload)

        agent_id = data.get("id", str(uuid.uuid4()))
        agent = AzureAIAgent(
            agent_id=agent_id,
            model=model,
            name=name,
            instructions=instructions,
            tools=tools or [],
            tool_resources=tool_resources or {},
            metadata=data.get("metadata", {}),
            created_at=datetime.now(timezone.utc),
        )
        self._agents[agent.agent_id] = agent
        logger.info("Created agent %s (%s)", agent.agent_id, name)
        return agent

    async def list_agents(self) -> List[Dict[str, Any]]:
        """List agents registered in the Foundry project.

        :returns: List of agent info dictionaries.
        """
        url = f"{self.project_endpoint}/assistants?api-version={self.api_version}"
        data = await self._get(url)

        if data and "data" in data:
            return data["data"]

        # Fall back to local store
        return [agent.to_dict() for agent in self._agents.values()]

    async def get_agent(self, agent_id: str) -> AzureAIAgent:
        """Retrieve a single agent by its identifier.

        :param agent_id: The unique agent identifier.
        :returns: An :class:`AzureAIAgent` instance.
        :raises KeyError: If the agent is not found locally or remotely.
        """
        url = f"{self.project_endpoint}/assistants/{agent_id}?api-version={self.api_version}"
        data = await self._get(url)

        if data and "id" in data:
            agent = AzureAIAgent(
                agent_id=data["id"],
                model=data.get("model", ""),
                name=data.get("name", ""),
                instructions=data.get("instructions", ""),
                tools=data.get("tools", []),
                tool_resources=data.get("tool_resources", {}),
                metadata=data.get("metadata", {}),
            )
            self._agents[agent.agent_id] = agent
            return agent

        if agent_id in self._agents:
            return self._agents[agent_id]

        raise KeyError(f"Agent {agent_id!r} not found")

    async def delete_agent(self, agent_id: str) -> None:
        """Delete an agent from the Foundry Agent Service.

        :param agent_id: The unique agent identifier.
        """
        url = f"{self.project_endpoint}/assistants/{agent_id}?api-version={self.api_version}"
        await self._delete(url)
        self._agents.pop(agent_id, None)
        logger.info("Deleted agent %s", agent_id)

    # ------------------------------------------------------------------
    # Thread lifecycle
    # ------------------------------------------------------------------

    async def create_thread(self) -> FoundryThread:
        """Create a new conversation thread.

        :returns: A :class:`FoundryThread` instance.
        """
        url = f"{self.project_endpoint}/threads?api-version={self.api_version}"
        data = await self._post(url, json={})

        thread_id = data.get("id", str(uuid.uuid4()))
        thread = FoundryThread(
            thread_id=thread_id,
            metadata=data.get("metadata", {}),
            created_at=datetime.now(timezone.utc),
        )
        self._threads[thread.thread_id] = thread
        logger.info("Created thread %s", thread.thread_id)
        return thread

    async def get_thread(self, thread_id: str) -> FoundryThread:
        """Retrieve an existing conversation thread.

        :param thread_id: The unique thread identifier.
        :returns: A :class:`FoundryThread` instance.
        :raises KeyError: If the thread is not found locally or remotely.
        """
        url = f"{self.project_endpoint}/threads/{thread_id}?api-version={self.api_version}"
        data = await self._get(url)

        if data and "id" in data:
            thread = FoundryThread(
                thread_id=data["id"],
                metadata=data.get("metadata", {}),
            )
            self._threads[thread.thread_id] = thread
            return thread

        if thread_id in self._threads:
            return self._threads[thread_id]

        raise KeyError(f"Thread {thread_id!r} not found")

    async def delete_thread(self, thread_id: str) -> None:
        """Delete a conversation thread.

        :param thread_id: The unique thread identifier.
        """
        url = f"{self.project_endpoint}/threads/{thread_id}?api-version={self.api_version}"
        await self._delete(url)
        self._threads.pop(thread_id, None)
        logger.info("Deleted thread %s", thread_id)

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    async def health_check(self) -> Dict[str, Any]:
        """Check connectivity to the Foundry project endpoint.

        :returns: Dictionary with health status information.
        """
        url = f"{self.project_endpoint}/health"
        try:
            data = await self._get(url)
            return data if data else {"status": "ok", "source": "local"}
        except Exception as exc:
            logger.warning("Health check failed: %s", exc)
            return {"status": "degraded", "error": str(exc)}

    def __repr__(self) -> str:  # pragma: no cover
        return f"AIProjectClient(project_endpoint={self.project_endpoint!r})"


# ===================================================================
# FoundryAgentService
# ===================================================================

class FoundryAgentService:
    """High-level orchestration service for multi-agent collaboration via Foundry.

    This is the main integration point that AOS uses to manage
    orchestrations through the Azure AI Foundry Agent Service.  It
    coordinates agent registration, thread management, and turn-based
    execution across multiple agents.

    :param project_client: An :class:`AIProjectClient` connected to
        the target Foundry project.
    :param gateway_url: Optional AI Gateway URL for request routing.
    """

    def __init__(
        self,
        project_client: AIProjectClient,
        gateway_url: Optional[str] = None,
    ) -> None:
        self.project_client = project_client
        self.gateway_url = gateway_url
        # Local orchestration bookkeeping
        self._orchestrations: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Agent registration
    # ------------------------------------------------------------------

    async def register_agent(
        self,
        agent_id: str,
        model: str,
        name: str,
        instructions: str,
        tools: Optional[List[dict]] = None,
    ) -> AzureAIAgent:
        """Register an agent with the Foundry Agent Service.

        If an agent with the given *agent_id* already exists locally it
        is returned directly; otherwise a new agent is created via
        :meth:`AIProjectClient.create_agent`.

        :param agent_id: Desired agent identifier.
        :param model: Model deployment name (e.g. ``"gpt-4o"``).
        :param name: Human-readable agent name.
        :param instructions: System-level instructions.
        :param tools: Optional tool definitions.
        :returns: An :class:`AzureAIAgent` instance.
        """
        # Return existing agent when already registered
        if agent_id in self.project_client._agents:
            logger.debug("Agent %s already registered — returning existing", agent_id)
            return self.project_client._agents[agent_id]

        agent = await self.project_client.create_agent(
            model=model,
            name=name,
            instructions=instructions,
            tools=tools,
        )
        # Re-key under the caller-supplied agent_id when it differs
        if agent.agent_id != agent_id:
            self.project_client._agents.pop(agent.agent_id, None)
            agent.agent_id = agent_id
            self.project_client._agents[agent_id] = agent
        return agent

    # ------------------------------------------------------------------
    # Orchestration management
    # ------------------------------------------------------------------

    async def create_orchestration(
        self,
        agent_ids: List[str],
        purpose: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a multi-agent orchestration.

        :param agent_ids: List of agent identifiers to participate.
        :param purpose: Short description of the orchestration goal.
        :param context: Optional contextual data passed to agents.
        :returns: Dictionary with ``orchestration_id`` and ``thread_id``.
        """
        thread = await self.project_client.create_thread()
        orchestration_id = str(uuid.uuid4())

        record: Dict[str, Any] = {
            "orchestration_id": orchestration_id,
            "thread_id": thread.thread_id,
            "agent_ids": list(agent_ids),
            "purpose": purpose,
            "context": context or {},
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "turns": [],
        }
        self._orchestrations[orchestration_id] = record
        logger.info(
            "Created orchestration %s with agents %s on thread %s",
            orchestration_id,
            agent_ids,
            thread.thread_id,
        )
        return {"orchestration_id": orchestration_id, "thread_id": thread.thread_id}

    async def run_agent_turn(
        self,
        orchestration_id: str,
        agent_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """Execute a single agent turn within an orchestration.

        :param orchestration_id: Orchestration to run within.
        :param agent_id: Agent to execute this turn.
        :param message: User or system message for the turn.
        :returns: Dictionary with the agent's response.
        :raises KeyError: If the orchestration is not found.
        """
        record = self._orchestrations.get(orchestration_id)
        if record is None:
            raise KeyError(f"Orchestration {orchestration_id!r} not found")

        thread = await self.project_client.get_thread(record["thread_id"])
        await thread.add_message(role="user", content=message)
        run = await thread.create_run(agent_id=agent_id)

        turn_entry: Dict[str, Any] = {
            "agent_id": agent_id,
            "run_id": run.run_id,
            "message": message,
            "status": run.status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        record["turns"].append(turn_entry)
        logger.info(
            "Ran turn for agent %s in orchestration %s (run %s)",
            agent_id,
            orchestration_id,
            run.run_id,
        )
        return {
            "run_id": run.run_id,
            "agent_id": agent_id,
            "status": run.status,
            "thread_id": record["thread_id"],
        }

    async def get_orchestration_status(self, orchestration_id: str) -> Dict[str, Any]:
        """Return the current status of an orchestration.

        :param orchestration_id: Orchestration to query.
        :returns: Dictionary with orchestration status and history.
        :raises KeyError: If the orchestration is not found.
        """
        record = self._orchestrations.get(orchestration_id)
        if record is None:
            raise KeyError(f"Orchestration {orchestration_id!r} not found")
        return dict(record)

    async def stop_orchestration(self, orchestration_id: str) -> None:
        """Stop an active orchestration.

        :param orchestration_id: Orchestration to stop.
        :raises KeyError: If the orchestration is not found.
        """
        record = self._orchestrations.get(orchestration_id)
        if record is None:
            raise KeyError(f"Orchestration {orchestration_id!r} not found")
        record["status"] = "stopped"
        logger.info("Stopped orchestration %s", orchestration_id)

    async def list_registered_agents(self) -> List[Dict[str, Any]]:
        """List all agents currently registered with the project client.

        :returns: List of agent info dictionaries.
        """
        return await self.project_client.list_agents()

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FoundryAgentService(project_endpoint={self.project_client.project_endpoint!r}, "
            f"gateway_url={self.gateway_url!r})"
        )
