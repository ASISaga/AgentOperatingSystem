"""
AOS Storage Manager

Unified storage manager for AOS.
Provides high-level storage operations with backend abstraction.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..config.storage import StorageConfig
from .file_backend import FileStorageBackend


class StorageManager:
    """
    Unified storage manager for AOS.

    Provides high-level storage operations with backend abstraction.
    """

    def __init__(self, config: StorageConfig):
        self.config = config
        self.logger = logging.getLogger("AOS.StorageManager")

        # Initialize storage backend based on configuration
        self.backend = self._create_backend()

        self.logger.info(f"Storage manager initialized with {config.storage_type} backend")

    def _create_backend(self):
        """Create storage backend based on configuration"""
        if self.config.storage_type == "file":
            return FileStorageBackend(self.config.base_path)
        elif self.config.storage_type == "azure":
            from .azure_backend import AzureStorageBackend
            return AzureStorageBackend(getattr(self.config, 'connection_string', None))
        elif self.config.storage_type == "azure_blob":
            # Legacy support - use azure backend
            from .azure_backend import AzureStorageBackend
            return AzureStorageBackend(getattr(self.config, 'connection_string', None))
        elif self.config.storage_type == "s3":
            # TODO: Implement S3 storage backend
            self.logger.warning("S3 Storage not implemented, falling back to file storage")
            return FileStorageBackend(self.config.base_path)
        else:
            # Default to file storage
            self.logger.warning(f"Unknown storage type {self.config.storage_type}, using file storage")
            return FileStorageBackend(self.config.base_path)

    async def store_agent_data(self, agent_id: str, data: Dict[str, Any]) -> bool:
        """Store agent-specific data"""
        key = f"agents/{agent_id}"

        # Add metadata
        storage_data = {
            "agent_id": agent_id,
            "data": data,
            "stored_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }

        success = await self.backend.write(key, storage_data)
        if success:
            self.logger.debug(f"Stored data for agent {agent_id}")
        else:
            self.logger.error(f"Failed to store data for agent {agent_id}")

        return success

    async def load_agent_data(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent-specific data"""
        key = f"agents/{agent_id}"
        storage_data = await self.backend.read(key)

        if storage_data and "data" in storage_data:
            self.logger.debug(f"Loaded data for agent {agent_id}")
            return storage_data["data"]

        return None

    async def store_workflow_data(self, workflow_id: str, workflow_data: Dict[str, Any]) -> bool:
        """Store workflow data"""
        key = f"workflows/{workflow_id}"

        storage_data = {
            "workflow_id": workflow_id,
            "data": workflow_data,
            "stored_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }

        success = await self.backend.write(key, storage_data)
        if success:
            self.logger.debug(f"Stored workflow data for {workflow_id}")
        else:
            self.logger.error(f"Failed to store workflow data for {workflow_id}")

        return success

    async def load_workflow_data(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow data"""
        key = f"workflows/{workflow_id}"
        storage_data = await self.backend.read(key)

        if storage_data and "data" in storage_data:
            self.logger.debug(f"Loaded workflow data for {workflow_id}")
            return storage_data["data"]

        return None

    async def store_system_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Store system configuration"""
        key = f"config/{config_name}"

        storage_data = {
            "config_name": config_name,
            "data": config_data,
            "stored_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }

        success = await self.backend.write(key, storage_data)
        if success:
            self.logger.debug(f"Stored system config {config_name}")
        else:
            self.logger.error(f"Failed to store system config {config_name}")

        return success

    async def load_system_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Load system configuration"""
        key = f"config/{config_name}"
        storage_data = await self.backend.read(key)

        if storage_data and "data" in storage_data:
            self.logger.debug(f"Loaded system config {config_name}")
            return storage_data["data"]

        return None

    async def store_decision_history(self, decision_id: str, decision_data: Dict[str, Any]) -> bool:
        """Store decision history"""
        key = f"decisions/{decision_id}"

        storage_data = {
            "decision_id": decision_id,
            "data": decision_data,
            "stored_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }

        return await self.backend.write(key, storage_data)

    async def store_message_history(self, message_id: str, message_data: Dict[str, Any]) -> bool:
        """Store message history"""
        key = f"messages/{message_id}"

        storage_data = {
            "message_id": message_id,
            "data": message_data,
            "stored_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }

        return await self.backend.write(key, storage_data)

    async def list_agents(self) -> List[str]:
        """List all stored agents"""
        keys = await self.backend.list_keys("agents/")
        return [key.replace("agents/", "") for key in keys]

    async def list_workflows(self) -> List[str]:
        """List all stored workflows"""
        keys = await self.backend.list_keys("workflows/")
        return [key.replace("workflows/", "") for key in keys]

    async def list_configs(self) -> List[str]:
        """List all stored configurations"""
        keys = await self.backend.list_keys("config/")
        return [key.replace("config/", "") for key in keys]

    async def delete_agent_data(self, agent_id: str) -> bool:
        """Delete agent data"""
        key = f"agents/{agent_id}"
        success = await self.backend.delete(key)
        if success:
            self.logger.info(f"Deleted data for agent {agent_id}")
        return success

    async def delete_workflow_data(self, workflow_id: str) -> bool:
        """Delete workflow data"""
        key = f"workflows/{workflow_id}"
        success = await self.backend.delete(key)
        if success:
            self.logger.info(f"Deleted workflow data for {workflow_id}")
        return success

    async def exists(self, key: str) -> bool:
        """Check if key exists in storage"""
        return await self.backend.exists(key)

    async def write_json(self, key: str, data: Dict[str, Any]) -> bool:
        """Write JSON data to storage"""
        return await self.backend.write(key, data)

    async def read_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Read JSON data from storage"""
        return await self.backend.read(key)

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            agent_keys = await self.backend.list_keys("agents/")
            workflow_keys = await self.backend.list_keys("workflows/")
            config_keys = await self.backend.list_keys("config/")
            decision_keys = await self.backend.list_keys("decisions/")
            message_keys = await self.backend.list_keys("messages/")

            stats = {
                "total_agents": len(agent_keys),
                "total_workflows": len(workflow_keys),
                "total_configs": len(config_keys),
                "total_decisions": len(decision_keys),
                "total_messages": len(message_keys),
                "storage_type": self.config.storage_type,
                "base_path": getattr(self.config, 'base_path', ''),
                "encryption_enabled": getattr(self.config, 'enable_encryption', False)
            }

            # Add Azure-specific health status if using Azure backend
            if hasattr(self.backend, 'get_health_status'):
                stats["azure_health"] = self.backend.get_health_status()

            return stats
        except Exception as e:
            self.logger.error(f"Error getting storage stats: {e}")
            return {"error": str(e)}

    # === Azure-specific operations (when using Azure backend) ===

    async def store_table_entity(self, table_name: str, entity: Dict[str, Any]) -> bool:
        """Store entity in Azure Tables (Azure backend only)"""
        if hasattr(self.backend, 'store_table_entity'):
            return await self.backend.store_table_entity(table_name, entity)
        else:
            self.logger.warning("Table entity storage not supported by current backend")
            return False

    async def get_table_entity(self, table_name: str, partition_key: str, row_key: str) -> Optional[Dict[str, Any]]:
        """Get entity from Azure Tables (Azure backend only)"""
        if hasattr(self.backend, 'get_table_entity'):
            return await self.backend.get_table_entity(table_name, partition_key, row_key)
        else:
            self.logger.warning("Table entity retrieval not supported by current backend")
            return None

    async def query_table_entities(self, table_name: str, filter_query: str = None, select: List[str] = None) -> List[Dict[str, Any]]:
        """Query entities from Azure Tables (Azure backend only)"""
        if hasattr(self.backend, 'query_table_entities'):
            return await self.backend.query_table_entities(table_name, filter_query, select)
        else:
            self.logger.warning("Table entity querying not supported by current backend")
            return []

    async def send_queue_message(self, queue_name: str, message: str) -> bool:
        """Send message to queue (Azure backend only)"""
        if hasattr(self.backend, 'send_queue_message'):
            return await self.backend.send_queue_message(queue_name, message)
        else:
            self.logger.warning("Queue messaging not supported by current backend")
            return False

    async def receive_queue_messages(self, queue_name: str, max_messages: int = 1) -> List[Dict[str, Any]]:
        """Receive messages from queue (Azure backend only)"""
        if hasattr(self.backend, 'receive_queue_messages'):
            return await self.backend.receive_queue_messages(queue_name, max_messages)
        else:
            self.logger.warning("Queue message receiving not supported by current backend")
            return []