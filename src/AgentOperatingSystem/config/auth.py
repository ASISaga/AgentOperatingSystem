import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthConfig:
    """Configuration for AOS authentication"""
    enable_auth: bool = True
    auth_provider: str = "azure_b2c"  # azure_b2c, oauth, jwt
    auth_endpoint: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    @classmethod
    def from_env(cls):
        return cls(
            enable_auth=os.getenv("AOS_ENABLE_AUTH", "true").lower() == "true",
            auth_provider=os.getenv("AOS_AUTH_PROVIDER", "azure_b2c"),
            auth_endpoint=os.getenv("AOS_AUTH_ENDPOINT"),
            client_id=os.getenv("AOS_AUTH_CLIENT_ID"),
            client_secret=os.getenv("AOS_AUTH_CLIENT_SECRET")
        )
