"""
Service Interfaces - Clean contracts for AOS services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class IStorageService(ABC):
    """Interface for storage operations."""
    
    @abstractmethod
    async def save(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Save data to storage."""
        pass
    
    @abstractmethod
    async def load(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Load data from storage."""
        pass
    
    @abstractmethod
    async def query(self, collection: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query data with filters."""
        pass
    
    @abstractmethod
    async def delete(self, collection: str, key: str) -> bool:
        """Delete data from storage."""
        pass

class IMessagingService(ABC):
    """Interface for messaging operations."""
    
    @abstractmethod
    async def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish message to topic."""
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str, handler: callable) -> bool:
        """Subscribe to topic with handler."""
        pass
    
    @abstractmethod
    async def send_to_agent(self, agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message directly to agent."""
        pass

class IWorkflowService(ABC):
    """Interface for workflow orchestration."""
    
    @abstractmethod
    async def execute_workflow(
        self,
        workflow_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow."""
        pass
    
    @abstractmethod
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status."""
        pass

class IAuthService(ABC):
    """Interface for authentication and authorization."""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate user/agent."""
        pass
    
    @abstractmethod
    async def authorize(self, user_id: str, resource: str, action: str) -> bool:
        """Check authorization."""
        pass
