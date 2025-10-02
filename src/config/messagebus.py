from dataclasses import dataclass, field
from typing import Optional
import os

@dataclass
class MessageBusConfig:
    """Configuration for AOS message bus"""
    max_queue_size: int = 10000
    message_timeout_seconds: int = 30
    enable_persistence: bool = True
    connection_string: Optional[str] = None

    @classmethod
    def from_env(cls):
        return cls(
            max_queue_size=int(os.getenv("AOS_MESSAGE_QUEUE_SIZE", "10000")),
            message_timeout_seconds=int(os.getenv("AOS_MESSAGE_TIMEOUT", "30")),
            enable_persistence=os.getenv("AOS_MESSAGE_PERSISTENCE", "true").lower() == "true",
            connection_string=os.getenv("AOS_MESSAGE_BUS_CONNECTION_STRING")
        )
