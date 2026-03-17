from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class StorageConfig:
    """Configuration for AOS storage"""
    storage_type: str = "file"  # file, azure_blob, s3
    base_path: str = "data"
    connection_string: Optional[str] = None
    container_name: str = "aos-storage"
    enable_encryption: bool = True

    @classmethod
    def from_env(cls):
        return cls(
            storage_type=os.getenv("AOS_STORAGE_TYPE", "file"),
            base_path=os.getenv("AOS_STORAGE_PATH", "data"),
            connection_string=os.getenv("AOS_STORAGE_CONNECTION_STRING"),
            container_name=os.getenv("AOS_STORAGE_CONTAINER", "aos-storage"),
            enable_encryption=os.getenv("AOS_ENABLE_ENCRYPTION", "true").lower() == "true"
        )
