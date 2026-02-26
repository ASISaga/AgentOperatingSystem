"""
ContextMCPServer - Lightweight standalone stub for context preservation.

This is a self-contained implementation of the ContextMCPServer interface used
by PurposeDrivenAgent. In the full AgentOperatingSystem runtime, this is backed
by Azure Storage; here it provides an in-process store suitable for development,
testing, and standalone deployments.

Swap the implementation for a remote-backed version by subclassing
ContextMCPServer and overriding the storage methods.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime


class ContextMCPServer:
    """
    Lightweight MCP (Model Context Protocol) context server.

    Provides persistent context storage for perpetual agents, enabling state
    preservation across events, restarts, and the entire lifetime of an agent.

    Key features:
    - In-process key/value context store
    - Event history tracking (configurable limit)
    - Structured memory management
    - Async-compatible interface
    - One dedicated instance per agent

    Example::

        context_server = ContextMCPServer(agent_id="ceo")
        await context_server.initialize()
        await context_server.set_context("current_strategy", "expand_market")
        strategy = await context_server.get_context("current_strategy")
    """

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialise a ContextMCPServer for a specific agent.

        Args:
            agent_id: Unique identifier for the agent using this context server.
            config: Optional configuration dict.  Recognised keys:

                - ``max_history_size`` (int, default 1000): maximum events kept.
                - ``max_memory_size`` (int, default 500): maximum memory items kept.
        """
        self.agent_id = agent_id
        self.config: Dict[str, Any] = config or {}
        self.logger = logging.getLogger(f"purpose_driven_agent.ContextMCPServer.{agent_id}")

        # Primary context store
        self.context: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }

        # Event history
        self.event_history: List[Dict[str, Any]] = []
        self.max_history_size: int = self.config.get("max_history_size", 1000)

        # Semantic memory
        self.memory: List[Dict[str, Any]] = []
        self.max_memory_size: int = self.config.get("max_memory_size", 500)

        # Statistics
        self.stats: Dict[str, int] = {
            "total_context_reads": 0,
            "total_context_writes": 0,
            "total_events_stored": 0,
            "total_memory_items": 0,
        }

        self.is_initialized: bool = False
        self.is_connected: bool = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> bool:
        """
        Initialise the context server.

        Returns:
            ``True`` if initialisation was successful.
        """
        try:
            self.is_initialized = True
            self.is_connected = True
            self.logger.info(f"ContextMCPServer initialised for agent '{self.agent_id}'")
            return True
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.logger.error(f"ContextMCPServer initialisation failed: {exc}")
            return False

    # ------------------------------------------------------------------
    # Context store
    # ------------------------------------------------------------------

    async def set_context(self, key: str, value: Any) -> bool:
        """
        Store a value in the context under *key*.

        Args:
            key: Context key.
            value: Serialisable value.

        Returns:
            ``True`` on success.
        """
        try:
            self.context[key] = value
            self.stats["total_context_writes"] += 1
            return True
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Failed to set context '{key}': {exc}")
            return False

    async def get_context(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the context store.

        Args:
            key: Context key.

        Returns:
            Stored value, or ``None`` if not found.
        """
        self.stats["total_context_reads"] += 1
        return self.context.get(key)

    async def get_all_context(self) -> Dict[str, Any]:
        """
        Return a shallow copy of the entire context store.

        Returns:
            Dictionary of all context key/value pairs.
        """
        self.stats["total_context_reads"] += 1
        return dict(self.context)

    async def delete_context(self, key: str) -> bool:
        """
        Delete an entry from the context store.

        Args:
            key: Key to delete.

        Returns:
            ``True`` if the key existed and was removed.
        """
        if key in self.context:
            del self.context[key]
            return True
        return False

    async def clear_context(self) -> bool:
        """
        Clear all context entries.

        Returns:
            ``True`` on success.
        """
        self.context.clear()
        return True

    # ------------------------------------------------------------------
    # Event history
    # ------------------------------------------------------------------

    async def add_event(self, event: Dict[str, Any]) -> bool:
        """
        Append an event to the history log.

        Args:
            event: Event payload.

        Returns:
            ``True`` on success.
        """
        enriched = {
            **event,
            "stored_at": datetime.utcnow().isoformat(),
        }
        self.event_history.append(enriched)
        self.stats["total_events_stored"] += 1

        # Trim history to configured limit
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size :]

        return True

    async def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Return the most recent events from history.

        Args:
            limit: Maximum number of events to return.

        Returns:
            List of recent events (newest last).
        """
        return self.event_history[-limit:]

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    async def add_memory(self, memory_item: Dict[str, Any]) -> bool:
        """
        Add an item to semantic memory.

        Args:
            memory_item: Memory payload.

        Returns:
            ``True`` on success.
        """
        enriched = {
            **memory_item,
            "added_at": datetime.utcnow().isoformat(),
        }
        self.memory.append(enriched)
        self.stats["total_memory_items"] += 1

        # Trim memory to configured limit
        if len(self.memory) > self.max_memory_size:
            self.memory = self.memory[-self.max_memory_size :]

        return True

    async def get_memory(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Return the most recent memory items.

        Args:
            limit: Maximum number of items to return.

        Returns:
            List of memory items (newest last).
        """
        return self.memory[-limit:]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    async def get_stats(self) -> Dict[str, Any]:
        """
        Return usage statistics.

        Returns:
            Statistics dictionary.
        """
        return {
            **self.stats,
            "context_items": len(self.context),
            "event_history_size": len(self.event_history),
            "memory_size": len(self.memory),
            "is_initialized": self.is_initialized,
            "is_connected": self.is_connected,
        }
