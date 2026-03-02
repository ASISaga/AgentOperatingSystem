"""
Azure Foundry Agent Service Integration for AOS

Provides native support for Microsoft Azure AI Foundry with Llama 3.3 70B
as the core reasoning engine, built on ``azure-ai-projects`` v2. Enables:

- **Agent lifecycle management**: create, retrieve, and list versioned agents
  in Azure AI Foundry via :class:`~azure.ai.projects.AIProjectClient`.
- **Stateful threads**: maintain conversation context across sessions using the
  OpenAI-compatible threads/runs API exposed by ``get_openai_client()``.
- **Entra ID authentication**: uses :class:`~azure.identity.DefaultAzureCredential`
  — no API keys required.
- **AOS integration**: accepts AOS orchestration context so that agent
  invocations can be correlated with purpose-driven orchestrations.

Usage::

    config = FoundryAgentServiceConfig.from_env()
    client = FoundryAgentServiceClient(config)
    await client.initialize()

    thread_id = await client.create_thread()
    response = await client.send_message(
        message="Analyze the quarterly revenue trends",
        thread_id=thread_id,
        domain="financial_analysis",
    )
"""

import logging
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("AOS.FoundryAgentService")


@dataclass
class FoundryAgentServiceConfig:
    """Configuration for Azure Foundry Agent Service."""

    # Foundry project endpoint:
    #   https://<ai-services>.services.ai.azure.com/api/projects/<project>
    endpoint_url: str = ""

    # Agent configuration
    agent_name: str = ""  # Foundry agent name (used as the persistent identifier)
    model: str = "llama-3.3-70b"  # Llama 3.3 70B as core reasoning engine

    # Feature flags
    enable_stateful_threads: bool = True
    enable_foundry_tools: bool = True

    # Performance settings
    timeout: int = 60
    max_retries: int = 3

    # Sampling settings forwarded to the model
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9

    # AOS integration — optional orchestration correlation
    aos_orchestration_id: str = ""

    @classmethod
    def from_env(cls) -> "FoundryAgentServiceConfig":
        """Create configuration from environment variables."""
        return cls(
            endpoint_url=os.getenv("FOUNDRY_ENDPOINT", ""),
            agent_name=os.getenv("FOUNDRY_AGENT_NAME", ""),
            model=os.getenv("FOUNDRY_MODEL", "llama-3.3-70b"),
            enable_stateful_threads=os.getenv("FOUNDRY_ENABLE_STATEFUL_THREADS", "true").lower() == "true",
            enable_foundry_tools=os.getenv("FOUNDRY_ENABLE_FOUNDRY_TOOLS", "true").lower() == "true",
            timeout=int(os.getenv("FOUNDRY_TIMEOUT", "60")),
            max_retries=int(os.getenv("FOUNDRY_MAX_RETRIES", "3")),
            temperature=float(os.getenv("FOUNDRY_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("FOUNDRY_MAX_TOKENS", "4096")),
            top_p=float(os.getenv("FOUNDRY_TOP_P", "0.9")),
            aos_orchestration_id=os.getenv("AOS_ORCHESTRATION_ID", ""),
        )


@dataclass
class ThreadInfo:
    """Information about a stateful thread."""
    thread_id: str
    agent_name: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_accessed: Optional[str] = None
    message_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FoundryResponse:
    """Response from Foundry Agent Service."""
    content: str
    thread_id: Optional[str] = None
    agent_name: Optional[str] = None
    model: str = "llama-3.3-70b"
    tools_used: List[str] = field(default_factory=list)
    usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


class FoundryAgentServiceClient:
    """
    AOS client for Azure AI Foundry Agent Service built on ``azure-ai-projects`` v2.

    Responsibilities
    ----------------
    * **Agent management** — create/retrieve versioned :class:`PromptAgentDefinition`
      agents via ``AIProjectClient.agents``.
    * **Stateful conversations** — create OpenAI threads and run the agent within
      those threads via ``AIProjectClient.get_openai_client()``.
    * **AOS integration** — attaches AOS orchestration metadata to every request so
      that Foundry runs can be correlated with purpose-driven orchestrations.

    Authentication
    --------------
    Uses :class:`~azure.identity.DefaultAzureCredential` — no API keys needed.
    Ensure the running identity (managed identity, service principal, or developer
    login) has the *Azure AI User* role on the Foundry project.

    Example::

        config = FoundryAgentServiceConfig.from_env()
        client = FoundryAgentServiceClient(config)
        await client.initialize()

        thread_id = await client.create_thread()
        response = await client.send_message(
            "Summarise this quarter's KPIs",
            thread_id=thread_id,
            domain="analytics",
        )
        print(response.content)
    """

    def __init__(self, config: Optional[FoundryAgentServiceConfig] = None):
        """
        Initialise the client.

        Args:
            config: Service configuration. If ``None``, loads from environment.
        """
        self.config = config or FoundryAgentServiceConfig.from_env()
        self.logger = logging.getLogger("AOS.FoundryAgentService")

        # Lazily created SDK clients
        self._project_client: Any = None  # AIProjectClient
        self._openai_client: Any = None   # openai.OpenAI (via get_openai_client)

        # Thread management — in-process cache of thread metadata
        self.active_threads: Dict[str, ThreadInfo] = {}

        # Metrics tracking
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0,
            "average_latency": 0.0,
        }

        self._initialized = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """
        Initialise the Azure AI Foundry connection.

        Creates the :class:`~azure.ai.projects.AIProjectClient` using
        :class:`~azure.identity.DefaultAzureCredential` and optionally
        verifies that the configured agent exists in the project.
        """
        if self._initialized:
            return

        if not self.config.endpoint_url:
            raise ValueError(
                "Foundry endpoint not configured. "
                "Set FOUNDRY_ENDPOINT to your AI Foundry project URL."
            )

        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential
        except ImportError as exc:
            raise ImportError(
                "azure-ai-projects and azure-identity are required. "
                "Install with: pip install 'azure-ai-projects>=2.0.0b4' azure-identity"
            ) from exc

        self._project_client = AIProjectClient(
            endpoint=self.config.endpoint_url,
            credential=DefaultAzureCredential(),
        )

        # Pre-warm the OpenAI-compatible client used for threads/runs
        self._openai_client = self._project_client.get_openai_client()

        self.logger.info(
            "Foundry Agent Service initialised — endpoint: %s, model: %s, "
            "stateful threads: %s, foundry tools: %s",
            self.config.endpoint_url,
            self.config.model,
            self.config.enable_stateful_threads,
            self.config.enable_foundry_tools,
        )

        self._initialized = True

    def close(self) -> None:
        """Close the underlying Azure SDK client and release resources."""
        if self._project_client is not None:
            self._project_client.close()
            self._project_client = None
            self._openai_client = None
            self._initialized = False

    # ------------------------------------------------------------------
    # Agent management (AIProjectClient.agents)
    # ------------------------------------------------------------------

    def create_or_update_agent(
        self,
        *,
        agent_name: Optional[str] = None,
        instructions: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Create or update an agent version in Azure AI Foundry.

        Uses :meth:`~azure.ai.projects.operations.AgentsOperations.create_version`
        with a :class:`~azure.ai.projects.models.PromptAgentDefinition` so that
        the agent is backed by the configured model deployment.

        Args:
            agent_name: Foundry agent name; defaults to ``config.agent_name``.
            instructions: System-level instructions for the agent.
            description: Human-readable description stored in Foundry.
            metadata: Up to 16 key-value string pairs attached to the version.

        Returns:
            :class:`~azure.ai.projects.models.AgentVersionDetails`
        """
        if not self._initialized:
            raise RuntimeError("Client not initialised — call initialize() first.")

        from azure.ai.projects.models import PromptAgentDefinition

        name = agent_name or self.config.agent_name
        if not name:
            raise ValueError("agent_name must be provided or set in config.")

        default_instructions = (
            f"You are an AOS-managed AI agent powered by {self.config.model}. "
            "Assist the user with their requests accurately and concisely."
        )
        definition = PromptAgentDefinition(
            model=self.config.model,
            instructions=instructions or default_instructions,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
        )

        version_details = self._project_client.agents.create_version(
            agent_name=name,
            definition=definition,
            description=description or f"AOS agent — {name}",
            metadata=metadata or {},
        )

        self.logger.info(
            "Created/updated Foundry agent '%s' (version %s)",
            name,
            version_details.version,
        )
        return version_details

    def get_agent(self, agent_name: Optional[str] = None) -> Any:
        """
        Retrieve agent details from Azure AI Foundry.

        Args:
            agent_name: Agent name; defaults to ``config.agent_name``.

        Returns:
            :class:`~azure.ai.projects.models.AgentDetails`
        """
        if not self._initialized:
            raise RuntimeError("Client not initialised — call initialize() first.")

        name = agent_name or self.config.agent_name
        if not name:
            raise ValueError("agent_name must be provided or set in config.")

        return self._project_client.agents.get(agent_name=name)

    def list_agents(self, limit: int = 20) -> List[Any]:
        """
        List agents registered in the Azure AI Foundry project.

        Args:
            limit: Maximum number of agents to return (1–100).

        Returns:
            List of :class:`~azure.ai.projects.models.AgentDetails` objects.
        """
        if not self._initialized:
            raise RuntimeError("Client not initialised — call initialize() first.")

        return list(self._project_client.agents.list(limit=limit))

    # ------------------------------------------------------------------
    # Stateful threads and message sending (OpenAI-compatible API)
    # ------------------------------------------------------------------

    async def create_thread(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new stateful thread via the OpenAI-compatible API.

        Args:
            metadata: Optional metadata stored alongside the thread locally.

        Returns:
            The thread ID to use in subsequent :meth:`send_message` calls.
        """
        if not self._initialized:
            await self.initialize()

        if not self.config.enable_stateful_threads:
            raise ValueError("Stateful threads are disabled (enable_stateful_threads=False).")

        thread = self._openai_client.beta.threads.create()
        thread_id: str = thread.id

        self.active_threads[thread_id] = ThreadInfo(
            thread_id=thread_id,
            agent_name=self.config.agent_name,
            metadata=metadata or {},
        )

        self.logger.info("Created stateful thread: %s", thread_id)
        return thread_id

    async def send_message(
        self,
        message: str,
        thread_id: Optional[str] = None,
        domain: str = "general",
        system_prompt: Optional[str] = None,
        tools: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> FoundryResponse:
        """
        Send a message and obtain a response from the Foundry agent.

        When *thread_id* is provided (and stateful threads are enabled) the
        conversation history is preserved across calls. Otherwise a single-turn
        chat completion is performed via ``client.chat.completions.create``.

        Args:
            message: User message to send.
            thread_id: Thread ID for a stateful conversation.
            domain: Domain hint embedded in the default system prompt.
            system_prompt: Overrides the auto-generated system prompt.
            tools: Reserved for future tool-binding extensions.
            **kwargs: ``temperature``, ``max_tokens``, and ``top_p`` overrides.

        Returns:
            :class:`FoundryResponse` with the agent's reply.
        """
        if not self._initialized:
            await self.initialize()

        start_time = datetime.utcnow()

        try:
            if thread_id and self.config.enable_stateful_threads:
                result = self._run_thread(
                    thread_id=thread_id,
                    message=message,
                    domain=domain,
                    system_prompt=system_prompt,
                    **kwargs,
                )
            else:
                result = self._chat_completion(
                    message=message,
                    domain=domain,
                    system_prompt=system_prompt,
                    **kwargs,
                )

            latency = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(success=True, latency=latency, tokens=result.get("usage", {}).get("total_tokens", 0))

            response = FoundryResponse(
                content=result.get("content", ""),
                thread_id=result.get("thread_id"),
                agent_name=result.get("agent_name", self.config.agent_name),
                model=result.get("model", self.config.model),
                tools_used=result.get("tools_used", []),
                usage=result.get("usage", {}),
                metadata={
                    **result.get("metadata", {}),
                    "aos_orchestration_id": self.config.aos_orchestration_id,
                },
                success=True,
            )

            if thread_id and self.config.enable_stateful_threads:
                self._update_thread_info(thread_id, response)

            return response

        except Exception as exc:
            self.logger.error("Failed to send message to Foundry Agent Service: %s", exc)
            latency = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(success=False, latency=latency)
            return FoundryResponse(content="", success=False, error=str(exc))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_thread(
        self,
        *,
        thread_id: str,
        message: str,
        domain: str,
        system_prompt: Optional[str],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Add a message to a thread and wait for the run to complete."""

        # Add user message to thread
        self._openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message,
        )

        # Build run parameters
        run_kwargs: Dict[str, Any] = {}
        if system_prompt:
            run_kwargs["additional_instructions"] = system_prompt
        elif domain != "general":
            run_kwargs["additional_instructions"] = (
                f"You are assisting with tasks in the {domain} domain."
            )

        # Add AOS orchestration context via metadata
        if self.config.aos_orchestration_id:
            run_kwargs["metadata"] = {"aos_orchestration_id": self.config.aos_orchestration_id}

        # Sampling overrides
        temperature = kwargs.get("temperature", self.config.temperature)
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        top_p = kwargs.get("top_p", self.config.top_p)
        if temperature != self.config.temperature:
            run_kwargs["temperature"] = temperature
        if max_tokens != self.config.max_tokens:
            run_kwargs["max_completion_tokens"] = max_tokens
        if top_p != self.config.top_p:
            run_kwargs["top_p"] = top_p

        # Create and poll the run until completion
        run = self._openai_client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=self.config.agent_name,
            **run_kwargs,
        )

        # Retrieve the last assistant message
        messages = self._openai_client.beta.threads.messages.list(
            thread_id=thread_id, order="desc", limit=1
        )
        content = ""
        for msg in messages:
            if msg.role == "assistant":
                for block in msg.content:
                    if hasattr(block, "text"):
                        content = block.text.value
                        break
            break

        usage_obj = getattr(run, "usage", None)
        usage = (
            {
                "prompt_tokens": usage_obj.prompt_tokens,
                "completion_tokens": usage_obj.completion_tokens,
                "total_tokens": usage_obj.total_tokens,
            }
            if usage_obj is not None
            else {}
        )

        return {
            "content": content,
            "thread_id": thread_id,
            "agent_name": self.config.agent_name,
            "model": self.config.model,
            "tools_used": [],
            "usage": usage,
            "metadata": {"run_id": run.id, "run_status": run.status},
        }

    def _chat_completion(
        self,
        *,
        message: str,
        domain: str,
        system_prompt: Optional[str],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Single-turn chat completion (no persistent thread)."""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": (
                    f"You are an AOS-managed AI agent for the {domain} domain, "
                    f"powered by {self.config.model}."
                ),
            })
        messages.append({"role": "user", "content": message})

        completion = self._openai_client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            top_p=kwargs.get("top_p", self.config.top_p),
        )

        content = completion.choices[0].message.content or ""
        usage_obj = getattr(completion, "usage", None)
        usage = (
            {
                "prompt_tokens": usage_obj.prompt_tokens,
                "completion_tokens": usage_obj.completion_tokens,
                "total_tokens": usage_obj.total_tokens,
            }
            if usage_obj is not None
            else {}
        )

        return {
            "content": content,
            "thread_id": None,
            "agent_name": self.config.agent_name,
            "model": self.config.model,
            "tools_used": [],
            "usage": usage,
            "metadata": {},
        }

    def _update_thread_info(self, thread_id: str, response: FoundryResponse) -> None:
        """Update in-process thread metadata cache."""
        if thread_id not in self.active_threads:
            self.active_threads[thread_id] = ThreadInfo(
                thread_id=thread_id,
                agent_name=response.agent_name or self.config.agent_name,
            )
        thread = self.active_threads[thread_id]
        thread.last_accessed = datetime.utcnow().isoformat()
        thread.message_count += 1

    def _update_metrics(self, success: bool, latency: float, tokens: int = 0) -> None:
        """Update running metrics."""
        self.metrics["total_requests"] += 1
        if success:
            self.metrics["successful_requests"] += 1
            self.metrics["total_tokens_used"] += tokens
        else:
            self.metrics["failed_requests"] += 1
        total = self.metrics["total_requests"]
        current_avg = self.metrics["average_latency"]
        self.metrics["average_latency"] = ((current_avg * (total - 1)) + latency) / total

    # ------------------------------------------------------------------
    # Thread accessors
    # ------------------------------------------------------------------

    async def get_thread_info(self, thread_id: str) -> Optional[ThreadInfo]:
        """Return cached metadata for a thread, or ``None`` if unknown."""
        return self.active_threads.get(thread_id)

    async def delete_thread(self, thread_id: str) -> bool:
        """
        Delete a stateful thread via the OpenAI-compatible API and remove it
        from the local cache.

        Returns:
            ``True`` if the thread existed and was deleted, ``False`` otherwise.
        """
        if not self._initialized:
            await self.initialize()

        if thread_id not in self.active_threads:
            return False

        try:
            self._openai_client.beta.threads.delete(thread_id)
        except Exception as exc:
            self.logger.warning("Could not delete remote thread %s: %s", thread_id, exc)

        del self.active_threads[thread_id]
        self.logger.info("Deleted stateful thread: %s", thread_id)
        return True

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_metrics(self) -> Dict[str, Any]:
        """Return a copy of the current metrics snapshot."""
        return self.metrics.copy()

    async def health_check(self) -> bool:
        """
        Verify connectivity by listing agents in the project.

        Returns:
            ``True`` if the Foundry project endpoint is reachable.
        """
        try:
            if not self._initialized:
                await self.initialize()
            self.list_agents(limit=1)
            return True
        except Exception as exc:
            self.logger.error("Foundry health check failed: %s", exc)
            return False
