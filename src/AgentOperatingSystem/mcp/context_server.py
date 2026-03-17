"""
ContextMCPServer - Infrastructure for Agent Context Preservation

The ContextMCPServer is a common infrastructure component provided by the
AgentOperatingSystem for preserving agent context across events and restarts.

Each perpetual agent (and by extension, each PurposeDrivenAgent) uses a
dedicated ContextMCPServer instance for persistent state management.

This server will eventually be moved to a dedicated repository.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class ContextMCPServer:
    """
    Context MCP Server for preserving agent state.

    This server provides persistent context storage for perpetual agents,
    enabling state preservation across events, restarts, and the entire
    lifetime of an agent.

    Key features:
    - Persistent context storage (key-value store)
    - Event history tracking
    - Memory management (configurable limits)
    - Async operations for non-blocking persistence
    - Dedicated instance per agent

    Example:
        >>> context_server = ContextMCPServer(agent_id="ceo")
        >>> await context_server.initialize()
        >>> await context_server.set_context("current_strategy", "expand_market")
        >>> strategy = await context_server.get_context("current_strategy")
    """

    def __init__(self, agent_id: str, config: Dict[str, Any] = None):
        """
        Initialize a ContextMCPServer for a specific agent.

        Args:
            agent_id: Unique identifier for the agent using this context server
            config: Optional configuration (storage backend, limits, etc.)
        """
        self.agent_id = agent_id
        self.config = config or {}
        self.logger = logging.getLogger(f"AOS.ContextMCPServer.{agent_id}")

        # Context storage
        self.context: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

        # Event history
        self.event_history: List[Dict[str, Any]] = []
        self.max_history_size = self.config.get("max_history_size", 1000)

        # Memory management
        self.memory: List[Dict[str, Any]] = []
        self.max_memory_size = self.config.get("max_memory_size", 500)

        # Statistics
        self.stats = {
            "total_context_reads": 0,
            "total_context_writes": 0,
            "total_events_stored": 0,
            "total_memory_items": 0
        }

        # Status
        self.is_initialized = False
        self.is_connected = False

    async def initialize(self) -> bool:
        """
        Initialize the context server.

        Sets up storage backend, loads any existing context, and
        prepares for operation.

        Returns:
            True if initialization successful
        """
        try:
            self.logger.info(f"Initializing ContextMCPServer for agent {self.agent_id}")

            # Load existing context if available
            await self._load_from_storage()

            self.is_initialized = True
            self.is_connected = True

            self.logger.info(f"ContextMCPServer initialized for agent {self.agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize ContextMCPServer: {e}")
            return False

    async def shutdown(self) -> bool:
        """
        Gracefully shutdown the context server.

        Saves all context to storage and releases resources.

        Returns:
            True if shutdown successful
        """
        try:
            self.logger.info(f"Shutting down ContextMCPServer for agent {self.agent_id}")

            # Save context to storage
            await self._save_to_storage()

            self.is_connected = False

            self.logger.info(f"ContextMCPServer shut down for agent {self.agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error shutting down ContextMCPServer: {e}")
            return False

    async def set_context(self, key: str, value: Any) -> bool:
        """
        Set a context value.

        Args:
            key: Context key
            value: Context value (must be JSON-serializable)

        Returns:
            True if successful
        """
        try:
            self.context[key] = value
            self.stats["total_context_writes"] += 1

            # Auto-save on write (could be optimized with batching)
            await self._save_to_storage()

            self.logger.debug(f"Set context: {key}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting context {key}: {e}")
            return False

    async def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a context value.

        Args:
            key: Context key
            default: Default value if key not found

        Returns:
            Context value or default
        """
        self.stats["total_context_reads"] += 1
        value = self.context.get(key, default)
        self.logger.debug(f"Get context: {key} -> {value}")
        return value

    async def update_context(self, updates: Dict[str, Any]) -> bool:
        """
        Update multiple context values at once.

        Args:
            updates: Dictionary of key-value pairs to update

        Returns:
            True if successful
        """
        try:
            self.context.update(updates)
            self.stats["total_context_writes"] += len(updates)

            await self._save_to_storage()

            self.logger.debug(f"Updated context with {len(updates)} items")
            return True

        except Exception as e:
            self.logger.error(f"Error updating context: {e}")
            return False

    async def get_all_context(self) -> Dict[str, Any]:
        """
        Get all context values.

        Returns:
            Complete context dictionary
        """
        self.stats["total_context_reads"] += 1
        return self.context.copy()

    async def store_event(self, event: Dict[str, Any]) -> bool:
        """
        Store an event in history.

        Args:
            event: Event data to store

        Returns:
            True if successful
        """
        try:
            event_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "event": event
            }

            self.event_history.append(event_record)
            self.stats["total_events_stored"] += 1

            # Trim history if needed
            if len(self.event_history) > self.max_history_size:
                self.event_history = self.event_history[-self.max_history_size:]

            await self._save_to_storage()

            self.logger.debug(f"Stored event in history")
            return True

        except Exception as e:
            self.logger.error(f"Error storing event: {e}")
            return False

    async def get_event_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get event history.

        Args:
            limit: Maximum number of events to return (most recent)

        Returns:
            List of event records
        """
        if limit:
            return self.event_history[-limit:]
        return self.event_history.copy()

    async def add_memory(self, memory_item: Dict[str, Any]) -> bool:
        """
        Add an item to agent memory.

        Args:
            memory_item: Memory data to store

        Returns:
            True if successful
        """
        try:
            memory_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "item": memory_item
            }

            self.memory.append(memory_record)
            self.stats["total_memory_items"] += 1

            # Trim memory if needed
            if len(self.memory) > self.max_memory_size:
                self.memory = self.memory[-self.max_memory_size:]

            await self._save_to_storage()

            self.logger.debug(f"Added memory item")
            return True

        except Exception as e:
            self.logger.error(f"Error adding memory: {e}")
            return False

    async def get_memory(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get agent memory.

        Args:
            limit: Maximum number of memory items to return (most recent)

        Returns:
            List of memory records
        """
        if limit:
            return self.memory[-limit:]
        return self.memory.copy()

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get context server statistics.

        Returns:
            Statistics dictionary
        """
        return {
            **self.stats,
            "current_context_size": len(self.context),
            "current_history_size": len(self.event_history),
            "current_memory_size": len(self.memory),
            "is_connected": self.is_connected
        }

    async def clear_context(self, keys: List[str] = None) -> bool:
        """
        Clear context (all or specific keys).

        Args:
            keys: Specific keys to clear, or None to clear all

        Returns:
            True if successful
        """
        try:
            if keys:
                for key in keys:
                    self.context.pop(key, None)
            else:
                self.context.clear()

            await self._save_to_storage()

            self.logger.info(f"Cleared context")
            return True

        except Exception as e:
            self.logger.error(f"Error clearing context: {e}")
            return False

    async def _load_from_storage(self) -> None:
        """
        Load context from persistent storage.

        In production, this would load from a database or file system.
        For now, this is a placeholder.
        """
        # Placeholder for storage backend integration
        # Would integrate with Azure Blob Storage, Cosmos DB, etc.
        self.logger.debug(f"Loaded context from storage (placeholder)")

    async def _save_to_storage(self) -> None:
        """
        Save context to persistent storage.

        In production, this would save to a database or file system.
        For now, this is a placeholder.
        """
        # Placeholder for storage backend integration
        # Would integrate with Azure Blob Storage, Cosmos DB, etc.
        self.logger.debug(f"Saved context to storage (placeholder)")

    def __repr__(self) -> str:
        return f"ContextMCPServer(agent_id='{self.agent_id}', connected={self.is_connected})"
