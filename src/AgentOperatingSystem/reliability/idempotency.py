"""
Idempotency framework for AgentOperatingSystem

Deterministic handlers keyed by message IDs and business keys to ensure
operations can be safely retried without side effects.
"""

from typing import Dict, Any, Optional, Callable, TypeVar, Generic
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import hashlib
import json


T = TypeVar('T')


class IdempotencyKey(BaseModel):
    """
    Idempotency key combining message ID and business key.
    """
    message_id: str
    business_key: Optional[str] = None
    
    def to_hash(self) -> str:
        """Generate deterministic hash for the key"""
        key_str = f"{self.message_id}:{self.business_key or ''}"
        return hashlib.sha256(key_str.encode()).hexdigest()


class IdempotencyRecord(BaseModel):
    """
    Record of an idempotent operation execution.
    """
    key_hash: str
    result: Any
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def is_expired(self) -> bool:
        """Check if this record has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class IdempotencyHandler(Generic[T]):
    """
    Handler for idempotent operations.
    
    Ensures that operations with the same idempotency key are only executed once,
    with subsequent calls returning the cached result.
    """
    
    def __init__(self, ttl_seconds: int = 86400):  # 24 hours default
        """
        Initialize idempotency handler.
        
        Args:
            ttl_seconds: Time-to-live for idempotency records in seconds
        """
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, IdempotencyRecord] = {}
    
    def execute(
        self,
        key: IdempotencyKey,
        operation: Callable[[], T]
    ) -> T:
        """
        Execute operation idempotently.
        
        Args:
            key: Idempotency key for this operation
            operation: Function to execute if not already executed
            
        Returns:
            Result of the operation (cached or fresh)
        """
        key_hash = key.to_hash()
        
        # Check if we have a cached result
        if key_hash in self._cache:
            record = self._cache[key_hash]
            if not record.is_expired():
                return record.result
            else:
                # Remove expired record
                del self._cache[key_hash]
        
        # Execute operation
        result = operation()
        
        # Store result
        expires_at = datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
        self._cache[key_hash] = IdempotencyRecord(
            key_hash=key_hash,
            result=result,
            expires_at=expires_at
        )
        
        return result
    
    async def execute_async(
        self,
        key: IdempotencyKey,
        operation: Callable[[], T]
    ) -> T:
        """
        Execute async operation idempotently.
        
        Args:
            key: Idempotency key for this operation
            operation: Async function to execute if not already executed
            
        Returns:
            Result of the operation (cached or fresh)
        """
        key_hash = key.to_hash()
        
        # Check if we have a cached result
        if key_hash in self._cache:
            record = self._cache[key_hash]
            if not record.is_expired():
                return record.result
            else:
                # Remove expired record
                del self._cache[key_hash]
        
        # Execute operation
        result = await operation()
        
        # Store result
        expires_at = datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
        self._cache[key_hash] = IdempotencyRecord(
            key_hash=key_hash,
            result=result,
            expires_at=expires_at
        )
        
        return result
    
    def cleanup_expired(self) -> int:
        """
        Remove expired records from cache.
        
        Returns:
            Number of records removed
        """
        expired_keys = [
            key for key, record in self._cache.items()
            if record.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)
    
    def clear(self):
        """Clear all cached records"""
        self._cache.clear()
    
    def get_record(self, key: IdempotencyKey) -> Optional[IdempotencyRecord]:
        """Get cached record for a key if it exists and is not expired"""
        key_hash = key.to_hash()
        if key_hash in self._cache:
            record = self._cache[key_hash]
            if not record.is_expired():
                return record
        return None
