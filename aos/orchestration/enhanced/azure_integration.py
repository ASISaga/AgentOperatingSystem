"""
Azure Integration for AOS

Enhanced Azure service integration system from SelfLearningAgent.
Provides comprehensive Azure Functions, Storage, and Service connectivity.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
import json
import os
from enum import Enum

try:
    from azure.functions import HttpRequest, HttpResponse
    from azure.storage.blob import BlobServiceClient
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class AzureServiceType(Enum):
    """Different Azure services that can be integrated"""
    FUNCTIONS = "functions"
    STORAGE = "storage"
    KEYVAULT = "keyvault"
    COSMOSDB = "cosmosdb"
    SERVICEBUS = "servicebus"
    EVENTHUB = "eventhub"


class AzureIntegration:
    """
    Azure integration system that provides seamless connectivity
    between AOS and Azure services.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.AzureIntegration")
        
        # Azure clients
        self.blob_client: Optional[BlobServiceClient] = None
        self.keyvault_client: Optional[SecretClient] = None
        self.credential = None
        
        # Configuration
        self.azure_config = {
            "storage_account": os.getenv("AZURE_STORAGE_ACCOUNT"),
            "storage_key": os.getenv("AZURE_STORAGE_KEY"),
            "keyvault_url": os.getenv("AZURE_KEYVAULT_URL"),
            "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID"),
            "resource_group": os.getenv("AZURE_RESOURCE_GROUP")
        }
        
        # Service status
        self.service_status: Dict[str, Dict[str, Any]] = {}
        self.last_health_check = None
        
        # Initialize if Azure SDK is available
        if AZURE_AVAILABLE:
            asyncio.create_task(self._initialize_azure_services())
        else:
            self.logger.warning("Azure SDK not available. Azure integration disabled.")
    
    async def _initialize_azure_services(self) -> None:
        """Initialize Azure service clients"""
        try:
            # Initialize credential
            self.credential = DefaultAzureCredential()
            
            # Initialize Blob Storage client
            if self.azure_config["storage_account"]:
                storage_url = f"https://{self.azure_config['storage_account']}.blob.core.windows.net"
                self.blob_client = BlobServiceClient(
                    account_url=storage_url,
                    credential=self.credential
                )
                self.service_status[AzureServiceType.STORAGE.value] = {
                    "status": "initialized",
                    "last_check": datetime.utcnow().isoformat()
                }
            
            # Initialize Key Vault client
            if self.azure_config["keyvault_url"]:
                self.keyvault_client = SecretClient(
                    vault_url=self.azure_config["keyvault_url"],
                    credential=self.credential
                )
                self.service_status[AzureServiceType.KEYVAULT.value] = {
                    "status": "initialized",
                    "last_check": datetime.utcnow().isoformat()
                }
            
            self.logger.info("Azure services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure services: {e}")
            for service in self.service_status:
                self.service_status[service]["status"] = "failed"
                self.service_status[service]["error"] = str(e)
    
    async def handle_function_request(self, req: 'HttpRequest') -> 'HttpResponse':
        """
        Handle incoming Azure Function requests and route to AOS.
        
        This method serves as the entry point for Azure Functions
        integrating with the AOS system.
        """
        if not AZURE_AVAILABLE:
            return self._create_error_response("Azure SDK not available", 500)
        
        try:
            # Parse request
            request_data = await self._parse_function_request(req)
            
            # Route to appropriate AOS handler
            aos_response = await self._route_to_aos(request_data)
            
            # Convert AOS response to Azure Function response
            return self._create_function_response(aos_response)
            
        except Exception as e:
            self.logger.error(f"Azure Function request failed: {e}")
            return self._create_error_response(str(e), 500)
    
    async def _parse_function_request(self, req: 'HttpRequest') -> Dict[str, Any]:
        """Parse Azure Function HTTP request into AOS format"""
        
        # Get request body
        try:
            body = req.get_json()
        except ValueError:
            body = {}
        
        # Get query parameters
        params = dict(req.params)
        
        # Get headers
        headers = dict(req.headers)
        
        # Extract common AOS parameters
        request_data = {
            "type": "azure_function_request",
            "method": req.method,
            "url": req.url,
            "headers": headers,
            "params": params,
            "body": body,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Extract AOS-specific parameters from body or params
        if body:
            request_data.update({
                "domain": body.get("domain", params.get("domain", "general")),
                "agent_id": body.get("agent_id", params.get("agent_id")),
                "content": body.get("content", body.get("message", "")),
                "conversation_id": body.get("conversation_id", params.get("conversation_id"))
            })
        
        return request_data
    
    async def _route_to_aos(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route parsed request to appropriate AOS component"""
        
        # This would integrate with the UnifiedOrchestrator
        # For now, return a placeholder response
        
        return {
            "success": True,
            "message": "Request processed by AOS Azure Integration",
            "request_id": request_data.get("conversation_id", "unknown"),
            "domain": request_data.get("domain", "general"),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "azure_integration"
        }
    
    def _create_function_response(self, aos_response: Dict[str, Any]) -> 'HttpResponse':
        """Convert AOS response to Azure Function HTTP response"""
        
        if not AZURE_AVAILABLE:
            return None
        
        from azure.functions import HttpResponse
        
        status_code = 200 if aos_response.get("success", True) else 500
        
        return HttpResponse(
            json.dumps(aos_response, indent=2),
            status_code=status_code,
            headers={
                "Content-Type": "application/json",
                "X-AOS-Processed": "true",
                "X-AOS-Timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def _create_error_response(self, error_msg: str, status_code: int) -> Union['HttpResponse', Dict[str, Any]]:
        """Create error response for Azure Function or fallback dict"""
        
        error_data = {
            "success": False,
            "error": error_msg,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "azure_integration"
        }
        
        if AZURE_AVAILABLE:
            from azure.functions import HttpResponse
            return HttpResponse(
                json.dumps(error_data, indent=2),
                status_code=status_code,
                headers={"Content-Type": "application/json"}
            )
        else:
            return error_data
    
    async def store_data(self, container_name: str, blob_name: str, data: Any) -> Dict[str, Any]:
        """Store data in Azure Blob Storage"""
        
        if not self.blob_client:
            return {"success": False, "error": "Blob storage client not initialized"}
        
        try:
            # Convert data to JSON if it's not a string
            if not isinstance(data, str):
                data = json.dumps(data, indent=2)
            
            # Upload to blob storage
            blob_client = self.blob_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_client.upload_blob(data, overwrite=True)
            
            self.logger.info(f"Successfully stored data in {container_name}/{blob_name}")
            
            return {
                "success": True,
                "container": container_name,
                "blob_name": blob_name,
                "size": len(data),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store data in Azure Storage: {e}")
            return {"success": False, "error": str(e)}
    
    async def retrieve_data(self, container_name: str, blob_name: str) -> Dict[str, Any]:
        """Retrieve data from Azure Blob Storage"""
        
        if not self.blob_client:
            return {"success": False, "error": "Blob storage client not initialized"}
        
        try:
            blob_client = self.blob_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_data = blob_client.download_blob()
            content = blob_data.readall().decode('utf-8')
            
            # Try to parse as JSON
            try:
                parsed_content = json.loads(content)
            except json.JSONDecodeError:
                parsed_content = content
            
            self.logger.info(f"Successfully retrieved data from {container_name}/{blob_name}")
            
            return {
                "success": True,
                "container": container_name,
                "blob_name": blob_name,
                "data": parsed_content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve data from Azure Storage: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve secret from Azure Key Vault"""
        
        if not self.keyvault_client:
            return {"success": False, "error": "Key Vault client not initialized"}
        
        try:
            secret = self.keyvault_client.get_secret(secret_name)
            
            self.logger.info(f"Successfully retrieved secret {secret_name}")
            
            return {
                "success": True,
                "secret_name": secret_name,
                "value": secret.value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_secret(self, secret_name: str, secret_value: str) -> Dict[str, Any]:
        """Store secret in Azure Key Vault"""
        
        if not self.keyvault_client:
            return {"success": False, "error": "Key Vault client not initialized"}
        
        try:
            self.keyvault_client.set_secret(secret_name, secret_value)
            
            self.logger.info(f"Successfully stored secret {secret_name}")
            
            return {
                "success": True,
                "secret_name": secret_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store secret {secret_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_containers(self) -> Dict[str, Any]:
        """List all containers in the storage account"""
        
        if not self.blob_client:
            return {"success": False, "error": "Blob storage client not initialized"}
        
        try:
            containers = []
            container_list = self.blob_client.list_containers()
            
            for container in container_list:
                containers.append({
                    "name": container.name,
                    "last_modified": container.last_modified.isoformat() if container.last_modified else None,
                    "metadata": container.metadata
                })
            
            return {
                "success": True,
                "containers": containers,
                "count": len(containers),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list containers: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_blobs(self, container_name: str) -> Dict[str, Any]:
        """List all blobs in a container"""
        
        if not self.blob_client:
            return {"success": False, "error": "Blob storage client not initialized"}
        
        try:
            container_client = self.blob_client.get_container_client(container_name)
            blobs = []
            blob_list = container_client.list_blobs()
            
            for blob in blob_list:
                blobs.append({
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                    "content_type": blob.content_settings.content_type if blob.content_settings else None
                })
            
            return {
                "success": True,
                "container": container_name,
                "blobs": blobs,
                "count": len(blobs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list blobs in {container_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all Azure services"""
        
        health_results = {}
        overall_health = True
        
        # Check Blob Storage
        if self.blob_client:
            try:
                # Try to list containers as a health check
                await self.list_containers()
                health_results[AzureServiceType.STORAGE.value] = {
                    "status": "healthy",
                    "last_check": datetime.utcnow().isoformat()
                }
            except Exception as e:
                health_results[AzureServiceType.STORAGE.value] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                overall_health = False
        else:
            health_results[AzureServiceType.STORAGE.value] = {
                "status": "not_configured",
                "last_check": datetime.utcnow().isoformat()
            }
        
        # Check Key Vault
        if self.keyvault_client:
            try:
                # Try to list secret properties as a health check
                secret_list = list(self.keyvault_client.list_properties_of_secrets())
                health_results[AzureServiceType.KEYVAULT.value] = {
                    "status": "healthy",
                    "secret_count": len(secret_list),
                    "last_check": datetime.utcnow().isoformat()
                }
            except Exception as e:
                health_results[AzureServiceType.KEYVAULT.value] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                overall_health = False
        else:
            health_results[AzureServiceType.KEYVAULT.value] = {
                "status": "not_configured",
                "last_check": datetime.utcnow().isoformat()
            }
        
        # Update service status
        self.service_status.update(health_results)
        self.last_health_check = datetime.utcnow()
        
        return {
            "overall_health": "healthy" if overall_health else "degraded",
            "services": health_results,
            "azure_sdk_available": AZURE_AVAILABLE,
            "configuration": {
                "storage_configured": bool(self.azure_config["storage_account"]),
                "keyvault_configured": bool(self.azure_config["keyvault_url"]),
                "subscription_configured": bool(self.azure_config["subscription_id"])
            },
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def get_azure_status(self) -> Dict[str, Any]:
        """Get comprehensive Azure integration status"""
        
        # Perform health check if it's been more than 5 minutes
        if (not self.last_health_check or 
            datetime.utcnow() - self.last_health_check > timedelta(minutes=5)):
            await self.health_check()
        
        return {
            "azure_sdk_available": AZURE_AVAILABLE,
            "services_initialized": len(self.service_status),
            "service_status": self.service_status,
            "configuration": self.azure_config,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "integration_version": "1.0.0"
        }
    
    def create_function_handler(self, orchestrator: Optional[Any] = None) -> Callable:
        """
        Create an Azure Function handler that integrates with AOS orchestrator.
        
        Args:
            orchestrator: AOS UnifiedOrchestrator instance
            
        Returns:
            Function handler for Azure Functions
        """
        
        async def function_handler(req: 'HttpRequest') -> 'HttpResponse':
            """Azure Function entry point"""
            
            try:
                # Parse request
                request_data = await self._parse_function_request(req)
                
                # Route to orchestrator if available
                if orchestrator:
                    aos_response = await orchestrator.orchestrate_request(request_data)
                else:
                    aos_response = await self._route_to_aos(request_data)
                
                return self._create_function_response(aos_response)
                
            except Exception as e:
                self.logger.error(f"Function handler error: {e}")
                return self._create_error_response(str(e), 500)
        
        return function_handler