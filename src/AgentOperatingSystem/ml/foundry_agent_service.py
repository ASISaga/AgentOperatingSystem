"""
Azure Foundry Agent Service Integration for AOS

Provides native support for Microsoft Azure Foundry Agent Service with Llama 3.3 70B
as the core reasoning engine. Enables high-level features such as:
- Stateful Threads: Maintain conversation context across sessions
- Entra Agent ID: Secure agent identity management
- Foundry Tools: Access to Azure AI Foundry tools and capabilities

This integration allows AOS to leverage Llama 3.3 70B fine-tuned weights through
the Agent Service's enterprise-grade infrastructure.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

logger = logging.getLogger("AOS.FoundryAgentService")


@dataclass
class FoundryAgentServiceConfig:
    """Configuration for Azure Foundry Agent Service."""

    # Service endpoint configuration
    endpoint_url: str = ""
    api_key: str = ""

    # Agent configuration
    agent_id: str = ""
    model: str = "llama-3.3-70b"  # Llama 3.3 70B as core reasoning engine

    # Feature flags
    enable_stateful_threads: bool = True
    enable_entra_agent_id: bool = True
    enable_foundry_tools: bool = True

    # Performance settings
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0

    # Advanced settings
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9

    @classmethod
    def from_env(cls) -> 'FoundryAgentServiceConfig':
        """Create configuration from environment variables."""
        return cls(
            endpoint_url=os.getenv("FOUNDRY_AGENT_SERVICE_ENDPOINT", ""),
            api_key=os.getenv("FOUNDRY_AGENT_SERVICE_API_KEY", ""),
            agent_id=os.getenv("FOUNDRY_AGENT_ID", ""),
            model=os.getenv("FOUNDRY_MODEL", "llama-3.3-70b"),
            enable_stateful_threads=os.getenv("FOUNDRY_ENABLE_STATEFUL_THREADS", "true").lower() == "true",
            enable_entra_agent_id=os.getenv("FOUNDRY_ENABLE_ENTRA_AGENT_ID", "true").lower() == "true",
            enable_foundry_tools=os.getenv("FOUNDRY_ENABLE_FOUNDRY_TOOLS", "true").lower() == "true",
            timeout=int(os.getenv("FOUNDRY_TIMEOUT", "60")),
            max_retries=int(os.getenv("FOUNDRY_MAX_RETRIES", "3")),
            temperature=float(os.getenv("FOUNDRY_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("FOUNDRY_MAX_TOKENS", "4096")),
            top_p=float(os.getenv("FOUNDRY_TOP_P", "0.9")),
        )


@dataclass
class ThreadInfo:
    """Information about a stateful thread."""
    thread_id: str
    agent_id: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_accessed: Optional[str] = None
    message_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FoundryResponse:
    """Response from Foundry Agent Service."""
    content: str
    thread_id: Optional[str] = None
    agent_id: Optional[str] = None
    model: str = "llama-3.3-70b"
    tools_used: List[str] = field(default_factory=list)
    usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


class FoundryAgentServiceClient:
    """
    Client for interacting with Azure Foundry Agent Service.

    Provides a high-level interface for:
    - Creating and managing stateful threads
    - Sending messages and receiving responses
    - Managing agent identity through Entra ID
    - Utilizing Foundry Tools for enhanced capabilities
    - Working with fine-tuned Llama 3.3 70B models

    Example:
        config = FoundryAgentServiceConfig.from_env()
        client = FoundryAgentServiceClient(config)
        await client.initialize()

        response = await client.send_message(
            message="Analyze the quarterly revenue trends",
            thread_id="thread-123",
            domain="financial_analysis"
        )
    """

    def __init__(self, config: Optional[FoundryAgentServiceConfig] = None):
        """
        Initialize Foundry Agent Service client.

        Args:
            config: Service configuration. If None, loads from environment.
        """
        self.config = config or FoundryAgentServiceConfig.from_env()
        self.logger = logging.getLogger("AOS.FoundryAgentService")

        # Thread management
        self.active_threads: Dict[str, ThreadInfo] = {}

        # Metrics tracking
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0,
            "average_latency": 0.0
        }

        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the Foundry Agent Service client."""
        if self._initialized:
            return

        # Validate configuration
        if not self.config.endpoint_url:
            raise ValueError("Foundry Agent Service endpoint URL not configured")

        if not self.config.api_key:
            raise ValueError("Foundry Agent Service API key not configured")

        if not self.config.agent_id:
            self.logger.warning("Agent ID not configured - some features may be limited")

        self.logger.info(
            f"Foundry Agent Service initialized - Model: {self.config.model}, "
            f"Stateful Threads: {self.config.enable_stateful_threads}, "
            f"Entra Agent ID: {self.config.enable_entra_agent_id}, "
            f"Foundry Tools: {self.config.enable_foundry_tools}"
        )

        self._initialized = True

    async def send_message(
        self,
        message: str,
        thread_id: Optional[str] = None,
        domain: str = "general",
        system_prompt: Optional[str] = None,
        tools: Optional[List[str]] = None,
        **kwargs
    ) -> FoundryResponse:
        """
        Send a message to the Foundry Agent Service.

        Args:
            message: User message to send
            thread_id: Optional thread ID for stateful conversations
            domain: Domain context for the agent
            system_prompt: Optional system prompt override
            tools: Optional list of Foundry Tools to enable
            **kwargs: Additional parameters

        Returns:
            FoundryResponse containing the agent's response
        """
        if not self._initialized:
            await self.initialize()

        start_time = datetime.utcnow()

        try:
            # Prepare request payload
            payload = self._prepare_request_payload(
                message=message,
                thread_id=thread_id,
                domain=domain,
                system_prompt=system_prompt,
                tools=tools,
                **kwargs
            )

            # Send request to Foundry Agent Service
            # Note: This is a reference implementation
            # In production, use actual Azure SDK or HTTP client
            result = await self._call_foundry_service(payload)

            # Update metrics
            latency = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(success=True, latency=latency, tokens=result.get("usage", {}).get("total_tokens", 0))

            # Create response
            response = FoundryResponse(
                content=result.get("content", ""),
                thread_id=result.get("thread_id"),
                agent_id=result.get("agent_id"),
                model=result.get("model", self.config.model),
                tools_used=result.get("tools_used", []),
                usage=result.get("usage", {}),
                metadata=result.get("metadata", {}),
                success=True
            )

            # Update thread info if using stateful threads
            if thread_id and self.config.enable_stateful_threads:
                self._update_thread_info(thread_id, response)

            return response

        except Exception as e:
            self.logger.error(f"Failed to send message to Foundry Agent Service: {e}")
            latency = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(success=False, latency=latency)

            return FoundryResponse(
                content="",
                success=False,
                error=str(e)
            )

    def _prepare_request_payload(
        self,
        message: str,
        thread_id: Optional[str],
        domain: str,
        system_prompt: Optional[str],
        tools: Optional[List[str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare request payload for Foundry Agent Service."""

        # Build messages array
        messages = []

        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": f"You are a specialized AI agent for the {domain} domain, powered by Llama 3.3 70B."
            })

        # Add user message
        messages.append({"role": "user", "content": message})

        # Build payload
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
        }

        # Add agent ID if using Entra Agent ID
        if self.config.enable_entra_agent_id and self.config.agent_id:
            payload["agent_id"] = self.config.agent_id

        # Add thread ID if using stateful threads
        if thread_id and self.config.enable_stateful_threads:
            payload["thread_id"] = thread_id

        # Add tools if using Foundry Tools
        if self.config.enable_foundry_tools and tools:
            payload["tools"] = tools

        return payload

    async def _call_foundry_service(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the Foundry Agent Service endpoint.

        Note: This is a reference implementation.
        In production, implement actual HTTP client logic or use Azure SDK.
        """

        # This would be replaced with actual HTTP request
        # For now, return a simulated response
        self.logger.info(f"Calling Foundry Agent Service with payload: {payload}")

        # Simulated response structure
        return {
            "content": f"Response from Llama 3.3 70B via Foundry Agent Service",
            "thread_id": payload.get("thread_id"),
            "agent_id": payload.get("agent_id"),
            "model": payload.get("model", "llama-3.3-70b"),
            "tools_used": payload.get("tools", []),
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            },
            "metadata": {
                "stateful_threads_enabled": self.config.enable_stateful_threads,
                "entra_agent_id_enabled": self.config.enable_entra_agent_id,
                "foundry_tools_enabled": self.config.enable_foundry_tools
            }
        }

    def _update_thread_info(self, thread_id: str, response: FoundryResponse) -> None:
        """Update information about a stateful thread."""

        if thread_id not in self.active_threads:
            self.active_threads[thread_id] = ThreadInfo(
                thread_id=thread_id,
                agent_id=response.agent_id or self.config.agent_id
            )

        thread = self.active_threads[thread_id]
        thread.last_accessed = datetime.utcnow().isoformat()
        thread.message_count += 1

    def _update_metrics(self, success: bool, latency: float, tokens: int = 0) -> None:
        """Update client metrics."""

        self.metrics["total_requests"] += 1

        if success:
            self.metrics["successful_requests"] += 1
            self.metrics["total_tokens_used"] += tokens
        else:
            self.metrics["failed_requests"] += 1

        # Update average latency
        total = self.metrics["total_requests"]
        current_avg = self.metrics["average_latency"]
        self.metrics["average_latency"] = ((current_avg * (total - 1)) + latency) / total

    async def create_thread(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new stateful thread.

        Args:
            metadata: Optional metadata for the thread

        Returns:
            Thread ID
        """

        if not self.config.enable_stateful_threads:
            raise ValueError("Stateful threads not enabled")

        # Generate thread ID
        thread_id = f"thread-{datetime.utcnow().timestamp()}"

        # Create thread info
        self.active_threads[thread_id] = ThreadInfo(
            thread_id=thread_id,
            agent_id=self.config.agent_id,
            metadata=metadata or {}
        )

        self.logger.info(f"Created stateful thread: {thread_id}")
        return thread_id

    async def get_thread_info(self, thread_id: str) -> Optional[ThreadInfo]:
        """Get information about a stateful thread."""
        return self.active_threads.get(thread_id)

    async def delete_thread(self, thread_id: str) -> bool:
        """Delete a stateful thread."""

        if thread_id in self.active_threads:
            del self.active_threads[thread_id]
            self.logger.info(f"Deleted stateful thread: {thread_id}")
            return True

        return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics."""
        return self.metrics.copy()

    async def health_check(self) -> bool:
        """Check if the Foundry Agent Service is healthy."""

        try:
            # Send a simple health check message
            response = await self.send_message("health check", domain="system")
            return response.success
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
