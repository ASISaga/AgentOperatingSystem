"""
Azure Storage Backend for AOS

Implements Azure-based storage operations for the AOS StorageManager.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

try:
    from azure.data.tables import TableClient, TableServiceClient
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobServiceClient
    from azure.storage.queue import QueueClient, QueueServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class AzureStorageBackend:
    """
    Azure Storage backend implementation for AOS StorageManager.

    Supports:
    - Blob Storage for file operations
    - Table Storage for structured data
    - Queue Storage for message operations
    """

    def __init__(self, connection_string: str = None):
        self.logger = logging.getLogger("AOS.AzureStorageBackend")

        if not AZURE_AVAILABLE:
            raise ImportError("Azure Storage SDK not available. Install with: pip install azure-storage-blob azure-data-tables azure-storage-queue")

        # Configuration
        self.connection_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")

        if not self.connection_string and not self.storage_account:
            raise ValueError("Azure Storage connection string or account name required")

        # Initialize clients
        self._initialize_clients()

        self.logger.info("Azure Storage backend initialized")

    def _initialize_clients(self):
        """Initialize Azure storage clients"""
        try:
            # Handle development/test mode with invalid connection strings
            if self.connection_string in ['test', 'mock', 'development']:
                self.logger.warning("Using mock connection string - Azure operations will be mocked")
                self.blob_client = None
                self.table_client = None
                self.queue_client = None
                return

            if self.connection_string:
                # Use connection string
                self.blob_client = BlobServiceClient.from_connection_string(self.connection_string)
                self.table_client = TableServiceClient.from_connection_string(self.connection_string)
                self.queue_client = QueueServiceClient.from_connection_string(self.connection_string)
            else:
                # Use managed identity
                credential = DefaultAzureCredential()
                blob_url = f"https://{self.storage_account}.blob.core.windows.net"
                table_url = f"https://{self.storage_account}.table.core.windows.net"
                queue_url = f"https://{self.storage_account}.queue.core.windows.net"

                self.blob_client = BlobServiceClient(account_url=blob_url, credential=credential)
                self.table_client = TableServiceClient(endpoint=table_url, credential=credential)
                self.queue_client = QueueServiceClient(account_url=queue_url, credential=credential)

            self.logger.debug("Azure storage clients initialized")

        except Exception as error:
            self.logger.error("Failed to initialize Azure storage clients: %s", str(error))
            # In development, continue with None clients rather than failing
            if self.connection_string and self.connection_string not in ['test', 'mock', 'development']:
                raise
            else:
                self.logger.warning("Continuing with mock clients for development")
                self.blob_client = None
                self.table_client = None
                self.queue_client = None

    def _check_clients_available(self) -> bool:
        """Check if Azure clients are available (not in mock mode)"""
        return self.blob_client is not None and self.table_client is not None and self.queue_client is not None

    # === File Backend Interface ===

    async def write(self, key: str, data: Dict[str, Any]) -> bool:
        """Write data to Azure Blob Storage"""
        if not self._check_clients_available():
            self.logger.warning("Mock write operation for key: %s", key)
            return True

        try:
            container_name = "aos-data"
            blob_name = f"{key}.json"

            # Ensure container exists
            await self._ensure_container(container_name)

            # Upload data as JSON
            blob_client = self.blob_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )

            json_data = json.dumps(data, indent=2)
            blob_client.upload_blob(json_data, overwrite=True)

            self.logger.debug("Wrote data to blob: %s", key)
            return True

        except Exception as error:
            self.logger.error("Failed to write data for key '%s': %s", key, str(error))
            return False

    async def read(self, key: str) -> Optional[Dict[str, Any]]:
        """Read data from Azure Blob Storage"""
        if not self._check_clients_available():
            self.logger.warning("Mock read operation for key: %s", key)
            return {"mock": True, "key": key}

        try:
            container_name = "aos-data"
            blob_name = f"{key}.json"

            blob_client = self.blob_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )

            if not blob_client.exists():
                return None

            blob_data = blob_client.download_blob()
            content = blob_data.readall().decode('utf-8')

            data = json.loads(content)
            self.logger.debug("Read data from blob: %s", key)
            return data

        except Exception as error:
            self.logger.error("Failed to read data for key '%s': %s", key, str(error))
            return None

    async def delete(self, key: str) -> bool:
        """Delete data from Azure Blob Storage"""
        try:
            container_name = "aos-data"
            blob_name = f"{key}.json"

            blob_client = self.blob_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )

            if blob_client.exists():
                blob_client.delete_blob()
                self.logger.debug("Deleted blob: %s", key)

            return True

        except Exception as error:
            self.logger.error("Failed to delete data for key '%s': %s", key, str(error))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Azure Blob Storage"""
        try:
            container_name = "aos-data"
            blob_name = f"{key}.json"

            blob_client = self.blob_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )

            return blob_client.exists()

        except Exception as error:
            self.logger.error("Failed to check existence for key '%s': %s", key, str(error))
            return False

    async def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with given prefix from Azure Blob Storage"""
        try:
            container_name = "aos-data"

            # Ensure container exists
            await self._ensure_container(container_name)

            container_client = self.blob_client.get_container_client(container_name)
            blobs = container_client.list_blobs(name_starts_with=prefix)

            keys = []
            for blob in blobs:
                # Remove .json extension and return key
                key = blob.name
                if key.endswith('.json'):
                    key = key[:-5]
                keys.append(key)

            return keys

        except Exception as error:
            self.logger.error("Failed to list keys with prefix '%s': %s", prefix, str(error))
            return []

    # === Extended Azure-specific Operations ===

    async def store_table_entity(self, table_name: str, entity: Dict[str, Any]) -> bool:
        """Store entity in Azure Tables"""
        try:
            # Ensure table exists
            table_client = await self._get_table_client(table_name)

            # Upsert entity
            table_client.upsert_entity(entity=entity)

            self.logger.debug("Stored entity in table '%s': %s", table_name, entity.get('RowKey', 'unknown'))
            return True

        except Exception as error:
            self.logger.error("Failed to store entity in table '%s': %s", table_name, str(error))
            return False

    async def get_table_entity(self, table_name: str, partition_key: str, row_key: str) -> Optional[Dict[str, Any]]:
        """Get entity from Azure Tables"""
        try:
            table_client = await self._get_table_client(table_name)

            entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)

            self.logger.debug("Retrieved entity from table '%s': %s", table_name, row_key)
            return dict(entity)

        except Exception as error:
            self.logger.error("Failed to get entity from table '%s': %s", table_name, str(error))
            return None

    async def query_table_entities(self, table_name: str, filter_query: str = None, select: List[str] = None) -> List[Dict[str, Any]]:
        """Query entities from Azure Tables"""
        try:
            table_client = await self._get_table_client(table_name)

            entities = []
            entity_list = table_client.query_entities(query_filter=filter_query, select=select)

            for entity in entity_list:
                entities.append(dict(entity))

            self.logger.debug("Queried %s entities from table '%s'", len(entities), table_name)
            return entities

        except Exception as error:
            self.logger.error("Failed to query entities from table '%s': %s", table_name, str(error))
            return []

    async def send_queue_message(self, queue_name: str, message: str) -> bool:
        """Send message to Azure Storage Queue"""
        try:
            queue_client = await self._get_queue_client(queue_name)

            queue_client.send_message(message)

            self.logger.debug("Sent message to queue '%s'", queue_name)
            return True

        except Exception as error:
            self.logger.error("Failed to send message to queue '%s': %s", queue_name, str(error))
            return False

    async def receive_queue_messages(self, queue_name: str, max_messages: int = 1) -> List[Dict[str, Any]]:
        """Receive messages from Azure Storage Queue"""
        try:
            queue_client = await self._get_queue_client(queue_name)

            messages = queue_client.receive_messages(max_messages=max_messages)

            message_list = []
            for message in messages:
                message_list.append({
                    "id": message.id,
                    "content": message.content,
                    "dequeue_count": message.dequeue_count,
                    "insertion_time": message.insertion_time.isoformat() if message.insertion_time else None
                })

            self.logger.debug("Received %s messages from queue '%s'", len(message_list), queue_name)
            return message_list

        except Exception as error:
            self.logger.error("Failed to receive messages from queue '%s': %s", queue_name, str(error))
            return []

    # === Helper Methods ===

    async def _ensure_container(self, container_name: str):
        """Ensure blob container exists"""
        try:
            container_client = self.blob_client.get_container_client(container_name)
            if not container_client.exists():
                container_client.create_container()
                self.logger.debug("Created container: %s", container_name)
        except Exception as error:
            # Container might already exist
            self.logger.debug("Container '%s' handling: %s", container_name, str(error))

    async def _get_table_client(self, table_name: str) -> TableClient:
        """Get table client, creating table if needed"""
        try:
            table_client = self.table_client.create_table_if_not_exists(table_name)
            return table_client
        except Exception:
            # Table might already exist, try to get it
            return self.table_client.get_table_client(table_name)

    async def _get_queue_client(self, queue_name: str) -> QueueClient:
        """Get queue client, creating queue if needed"""
        try:
            queue_client = self.queue_client.create_queue(queue_name)
            return queue_client
        except Exception:
            # Queue might already exist, try to get it
            return self.queue_client.get_queue_client(queue_name)

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of Azure storage services"""
        status = {
            "backend_type": "azure",
            "blob_storage": False,
            "table_storage": False,
            "queue_storage": False,
            "connection_method": "connection_string" if self.connection_string else "managed_identity"
        }

        try:
            # Test blob storage
            list(self.blob_client.list_containers())
            status["blob_storage"] = True
        except Exception as error:
            self.logger.debug("Blob storage health check failed: %s", str(error))

        try:
            # Test table storage
            list(self.table_client.list_tables())
            status["table_storage"] = True
        except Exception as error:
            self.logger.debug("Table storage health check failed: %s", str(error))

        try:
            # Test queue storage
            list(self.queue_client.list_queues())
            status["queue_storage"] = True
        except Exception as error:
            self.logger.debug("Queue storage health check failed: %s", str(error))

        return status
