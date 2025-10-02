"""
File Storage Backend

File-based storage implementation for AOS.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from .backend import StorageBackend


class FileStorageBackend(StorageBackend):
    """File-based storage backend"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.logger = logging.getLogger("AOS.FileStorage")
        os.makedirs(base_path, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for key"""
        # Ensure safe file path
        safe_key = key.replace("/", "_").replace("\\", "_")
        return os.path.join(self.base_path, f"{safe_key}.json")
    
    async def read(self, key: str) -> Optional[Dict[str, Any]]:
        """Read data from file"""
        file_path = self._get_file_path(key)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    async def write(self, key: str, data: Dict[str, Any]) -> bool:
        """Write data to file"""
        file_path = self._get_file_path(key)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete file"""
        file_path = self._get_file_path(key)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if file exists"""
        file_path = self._get_file_path(key)
        return os.path.exists(file_path)
    
    async def list_keys(self, prefix: str = "") -> List[str]:
        """List files with optional prefix"""
        keys = []
        
        try:
            for filename in os.listdir(self.base_path):
                if filename.endswith('.json'):
                    key = filename[:-5]  # Remove .json extension
                    # Convert back from safe filename
                    original_key = key.replace("_", "/")
                    
                    if not prefix or original_key.startswith(prefix):
                        keys.append(original_key)
        except Exception as e:
            self.logger.error(f"Error listing keys: {e}")
        
        return keys