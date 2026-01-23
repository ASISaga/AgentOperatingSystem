"""
File Storage Backend

File-based storage implementation for AOS.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

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
            with open(file_path, 'r', encoding='utf-8') as file_obj:
                return json.load(file_obj)
        except Exception as error:
            self.logger.error("Error reading file %s: %s", file_path, str(error))
            return None

    async def write(self, key: str, data: Dict[str, Any]) -> bool:
        """Write data to file"""
        file_path = self._get_file_path(key)

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as file_obj:
                json.dump(data, file_obj, indent=2, default=str, ensure_ascii=False)
            return True
        except Exception as error:
            self.logger.error("Error writing file %s: %s", file_path, str(error))
            return False

    async def delete(self, key: str) -> bool:
        """Delete file"""
        file_path = self._get_file_path(key)

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as error:
            self.logger.error("Error deleting file %s: %s", file_path, str(error))
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
        except Exception as error:
            self.logger.error("Error listing keys: %s", str(error))

        return keys
