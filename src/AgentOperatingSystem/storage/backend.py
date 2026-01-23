"""
AOS Storage Backend Interfaces

Abstract interfaces for different storage backends.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StorageBackend(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    async def read(self, key: str) -> Optional[Dict[str, Any]]:
        """Read data by key"""

    @abstractmethod
    async def write(self, key: str, data: Dict[str, Any]) -> bool:
        """Write data to key"""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete data by key"""

    @abstractmethod
    async def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix"""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
