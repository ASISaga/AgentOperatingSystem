"""
Generic Service Interfaces for Agent Operating System

This module provides clean, generic service interfaces that enable:
- Separation of concerns between interface and implementation
- Better testability through dependency injection
- Flexibility to swap implementations
- Future-proofing against infrastructure changes

These interfaces define contracts for core infrastructure services that
any agent-based system needs: storage, messaging, workflow, and authentication.

Usage:
    from AgentOperatingSystem.service_interfaces import IStorageService, IMessagingService
    
    # Define your implementation
    class MyStorageService(IStorageService):
        async def save(self, container: str, key: str, data: Any) -> bool:
            # Your implementation
            ...
    
    # Or use provided AOS implementations
    from AgentOperatingSystem.service_interfaces import AOSStorageService
    storage = AOSStorageService(storage_manager)
"""

from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod


class IStorageService(Protocol):
    """
    Storage Service Interface
    
    Generic abstraction for data storage operations. Implementations
    can use Azure Blob Storage, AWS S3, local filesystem, or any other
    storage backend.
    
    Example:
        storage = get_storage_service()
        await storage.save("users", "user_123", user_data)
        data = await storage.load("users", "user_123")
    """
    
    async def save(self, container: str, key: str, data: Any) -> bool:
        """
        Save data to storage.
        
        Args:
            container: Storage container/bucket name
            key: Unique key for the data
            data: Data to save (will be serialized as needed)
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    async def load(self, container: str, key: str) -> Optional[Any]:
        """
        Load data from storage.
        
        Args:
            container: Storage container/bucket name
            key: Unique key for the data
            
        Returns:
            Loaded data or None if not found
        """
        ...
    
    async def delete(self, container: str, key: str) -> bool:
        """
        Delete data from storage.
        
        Args:
            container: Storage container/bucket name
            key: Unique key for the data
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    async def list_keys(self, container: str, prefix: str = "") -> List[str]:
        """
        List keys in container.
        
        Args:
            container: Storage container/bucket name
            prefix: Optional prefix to filter keys
            
        Returns:
            List of keys matching the criteria
        """
        ...
    
    async def exists(self, container: str, key: str) -> bool:
        """
        Check if key exists.
        
        Args:
            container: Storage container/bucket name
            key: Unique key to check
            
        Returns:
            True if exists, False otherwise
        """
        ...


class IMessagingService(Protocol):
    """
    Messaging Service Interface
    
    Generic abstraction for message-based communication. Supports both
    pub/sub patterns and direct messaging. Implementations can use
    Azure Service Bus, RabbitMQ, Kafka, or any other messaging system.
    
    Example:
        messaging = get_messaging_service()
        await messaging.publish("events", {"type": "user_created", "id": "123"})
        response = await messaging.send_request("agent_xyz", {"action": "analyze"})
    """
    
    async def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """
        Publish message to topic.
        
        Args:
            topic: Topic name
            message: Message payload
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    async def subscribe(self, topic: str, handler: callable) -> bool:
        """
        Subscribe to topic with handler.
        
        Args:
            topic: Topic name
            handler: Async function to handle messages
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    async def send_direct(self, agent_id: str, message: Dict[str, Any]) -> Any:
        """
        Send direct message to agent.
        
        Args:
            agent_id: Target agent ID
            message: Message payload
            
        Returns:
            Message acknowledgment or None
        """
        ...
    
    async def send_request(self, agent_id: str, request: Dict[str, Any], timeout: int = 30) -> Any:
        """
        Send request and wait for response.
        
        Args:
            agent_id: Target agent ID
            request: Request payload
            timeout: Timeout in seconds
            
        Returns:
            Response from agent or None
        """
        ...


class IWorkflowService(Protocol):
    """
    Workflow Service Interface
    
    Generic abstraction for workflow orchestration. Enables execution,
    monitoring, and management of multi-step workflows.
    
    Example:
        workflow = get_workflow_service()
        result = await workflow.execute_workflow("onboarding", context)
        status = await workflow.get_workflow_status("onboarding")
    """
    
    async def execute_workflow(self, workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_id: Workflow identifier
            context: Execution context and parameters
            
        Returns:
            Workflow execution result
        """
        ...
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow execution status.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Status information
        """
        ...
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel running workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all workflows.
        
        Returns:
            List of workflow definitions
        """
        ...


class IAuthService(Protocol):
    """
    Authentication Service Interface
    
    Generic abstraction for authentication and authorization.
    Supports multiple authentication providers and authorization models.
    
    Example:
        auth = get_auth_service()
        user = await auth.authenticate({"token": jwt_token})
        authorized = await auth.authorize("user_123", "resource_xyz", "read")
    """
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Authenticate user/agent.
        
        Args:
            credentials: Authentication credentials (token, username/password, etc.)
            
        Returns:
            Principal information if authenticated, None otherwise
        """
        ...
    
    async def authorize(self, principal: str, resource: str, action: str) -> bool:
        """
        Check authorization.
        
        Args:
            principal: User/agent identifier
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            True if authorized, False otherwise
        """
        ...
    
    async def get_principal(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get principal from token.
        
        Args:
            token: Authentication token
            
        Returns:
            Principal information or None
        """
        ...


# Note: Concrete implementations (AOSStorageService, AOSMessagingService, etc.)
# should be provided by the AOS implementation based on the actual infrastructure
# components available (StorageManager, ServiceBusManager, etc.)
