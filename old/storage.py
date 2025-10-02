"""
AOS Storage Management

Provides unified storage abstraction for the Agent Operating System.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def read(self, key: str) -> Optional[Dict[str, Any]]:
        """Read data by key"""
        pass
    
    @abstractmethod
    async def write(self, key: str, data: Dict[str, Any]) -> bool:
        """Write data to key"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete data by key"""
        pass
    
    @abstractmethod
    async def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix"""
        pass


class FileStorageBackend(StorageBackend):
    """File-based storage backend"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for key"""
        return os.path.join(self.base_path, f"{key}.json")
    
    async def read(self, key: str) -> Optional[Dict[str, Any]]:
        """Read data from file"""
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    async def write(self, key: str, data: Dict[str, Any]) -> bool:
        """Write data to file"""
        file_path = self._get_file_path(key)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete file"""
        file_path = self._get_file_path(key)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False
    
    async def list_keys(self, prefix: str = "") -> List[str]:
        """List files with optional prefix"""
        keys = []
        
        try:
            for filename in os.listdir(self.base_path):
                if filename.endswith('.json'):
                    key = filename[:-5]  # Remove .json extension
                    if not prefix or key.startswith(prefix):
                        keys.append(key)
        except Exception:
            pass
        
        return keys


class StorageManager:
    """
    Unified storage manager for AOS.
    
    Provides high-level storage operations with backend abstraction.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("AOS.StorageManager")
        
        # Initialize storage backend based on configuration
        if config.storage_type == "file":
            self.backend = FileStorageBackend(config.base_path)
        else:
            # Default to file storage
            self.backend = FileStorageBackend(config.base_path)
        
        self.logger.info(f"Storage manager initialized with {config.storage_type} backend")
    
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
        
        return await self.backend.write(key, storage_data)
    
    async def load_agent_data(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent-specific data"""
        key = f"agents/{agent_id}"
        storage_data = await self.backend.read(key)
        
        if storage_data and "data" in storage_data:
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
        
        return await self.backend.write(key, storage_data)
    
    async def load_workflow_data(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow data"""
        key = f"workflows/{workflow_id}"
        storage_data = await self.backend.read(key)
        
        if storage_data and "data" in storage_data:
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
        
        return await self.backend.write(key, storage_data)
    
    async def load_system_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Load system configuration"""
        key = f"config/{config_name}"
        storage_data = await self.backend.read(key)
        
        if storage_data and "data" in storage_data:
            return storage_data["data"]
        
        return None
    
    async def list_agents(self) -> List[str]:
        """List all stored agents"""
        keys = await self.backend.list_keys("agents/")
        return [key.replace("agents/", "") for key in keys]
    
    async def list_workflows(self) -> List[str]:
        """List all stored workflows"""
        keys = await self.backend.list_keys("workflows/")
        return [key.replace("workflows/", "") for key in keys]
    
    async def delete_agent_data(self, agent_id: str) -> bool:
        """Delete agent data"""
        key = f"agents/{agent_id}"
        return await self.backend.delete(key)
    
    async def delete_workflow_data(self, workflow_id: str) -> bool:
        """Delete workflow data"""
        key = f"workflows/{workflow_id}"
        return await self.backend.delete(key)
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            agent_keys = await self.backend.list_keys("agents/")
            workflow_keys = await self.backend.list_keys("workflows/")
            config_keys = await self.backend.list_keys("config/")
            
            return {
                "total_agents": len(agent_keys),
                "total_workflows": len(workflow_keys),
                "total_configs": len(config_keys),
                "storage_type": self.config.storage_type,
                "base_path": getattr(self.config, 'base_path', 'N/A')
            }
        except Exception as e:
            self.logger.error(f"Error getting storage stats: {e}")
            return {"error": str(e)}