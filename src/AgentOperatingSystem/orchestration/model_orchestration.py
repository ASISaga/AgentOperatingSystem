"""
Model Orchestration for AOS

Enhanced model orchestration system integrated from SelfLearningAgent.
Provides comprehensive model management, Azure ML integration, and semantic kernel support.
"""

import asyncio
import logging
import os
import json
import requests
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

# Optional Azure ML imports
try:
    from azure.ai.ml import MLClient
    from azure.ai.ml.dsl import pipeline
    from azure.identity import DefaultAzureCredential
    from azure.ai.ml.entities import CommandComponent, Job
    AZURE_ML_AVAILABLE = True
except ImportError:
    AZURE_ML_AVAILABLE = False

# Optional Agent Framework imports
try:
    from agent_framework import ChatAgent, WorkflowBuilder
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False


class ModelType(Enum):
    """Different model types supported by the orchestrator"""
    VLLM = "vllm"
    AZURE_ML = "azure_ml"
    OPENAI = "openai"
    AGENT_FRAMEWORK = "agent_framework"
    LOCAL_MODEL = "local_model"


class ModelOrchestrator:
    """
    Model orchestration system that manages multiple AI models,
    endpoints, and inference strategies for AOS agents.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None, config_dir: Optional[str] = None):
        self.logger = logger or logging.getLogger("AOS.ModelOrchestrator")
        
        # Model configurations
        self.model_configs: Dict[str, Dict[str, Any]] = {}
        self.active_models: Dict[str, Any] = {}
        self.model_health: Dict[str, Dict[str, Any]] = {}
        
        # Azure ML configuration
        self.azure_ml_client: Optional[MLClient] = None
        self.azure_ml_config = {
            "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID"),
            "resource_group": os.getenv("AZURE_RESOURCE_GROUP"),
            "workspace": os.getenv("AZURE_ML_WORKSPACE"),
            "endpoint_url": os.getenv("MLENDPOINTURL"),
            "endpoint_key": os.getenv("MLENDPOINTKEY")
        }
        
        # vLLM configuration
        self.vllm_config = {
            "server_url": None,
            "api_key": os.getenv("VLLM_API_KEY"),
            "timeout": 30
        }
        
        # Semantic Kernel is now Agent Framework
        self.agent_framework_client: Optional['ChatAgent'] = None
        
        # Performance tracking
        self.request_metrics: Dict[str, Dict[str, Any]] = {}
        self.model_usage: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.max_concurrent_requests = 5
        self.default_timeout = 60
        self.retry_attempts = 3
        
        # Store config_dir for deferred initialization
        self._config_dir = config_dir
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the orchestrator asynchronously"""
        if self._initialized:
            return
            
        # Load configuration if provided
        if self._config_dir:
            await self._load_configuration(self._config_dir)
        
        # Initialize services
        await self._initialize_services()
        self._initialized = True
    
    async def _initialize_services(self) -> None:
        """Initialize available model services"""
        
        try:
            # Initialize Azure ML if available
            if AZURE_ML_AVAILABLE and self.azure_ml_config["subscription_id"]:
                await self._initialize_azure_ml()
            
            # Initialize Agent Framework if available (replaces Semantic Kernel)
            if AGENT_FRAMEWORK_AVAILABLE:
                await self._initialize_agent_framework()
            
            # Perform initial health check
            await self._perform_health_check()
            
            self.logger.info("Model orchestrator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize model orchestrator: {e}")
    
    async def _load_configuration(self, config_dir: str) -> None:
        """Load model orchestrator configuration"""
        
        try:
            config_path = Path(config_dir) / "orchestrator_config.json"
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Update vLLM configuration
                if "vllm_server_url" in config:
                    self.vllm_config["server_url"] = config["vllm_server_url"]
                
                # Update model configurations
                if "models" in config:
                    self.model_configs.update(config["models"])
                
                # Update orchestrator settings
                if "orchestrator" in config:
                    orch_config = config["orchestrator"]
                    self.max_concurrent_requests = orch_config.get("max_concurrent_requests", self.max_concurrent_requests)
                    self.default_timeout = orch_config.get("default_timeout", self.default_timeout)
                    self.retry_attempts = orch_config.get("retry_attempts", self.retry_attempts)
                
                self.logger.info("Loaded orchestrator configuration")
            else:
                self.logger.info("No orchestrator config found, using defaults")
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
    
    async def _initialize_azure_ml(self) -> None:
        """Initialize Azure ML client"""
        
        try:
            credential = DefaultAzureCredential()
            
            self.azure_ml_client = MLClient(
                credential=credential,
                subscription_id=self.azure_ml_config["subscription_id"],
                resource_group_name=self.azure_ml_config["resource_group"],
                workspace_name=self.azure_ml_config["workspace"]
            )
            
            self.logger.info("Azure ML client initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure ML: {e}")
            self.azure_ml_client = None
    
    async def _initialize_agent_framework(self) -> None:
        """Initialize Agent Framework"""
        
        try:
            # Create a generic chat agent for model orchestration
            # Note: In production, use a real chat client instead of Mock
            from unittest.mock import Mock
            mock_chat_client = Mock()
            
            self.agent_framework_client = ChatAgent(
                chat_client=mock_chat_client,
                instructions="You are a model orchestration agent responsible for managing AI model requests.",
                name="ModelOrchestrator"
            )
            self.logger.info("Agent Framework initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Agent Framework: {e}")
            self.agent_framework_client = None
    
    async def process_model_request(self, model_type: ModelType, domain: str, 
                                  user_input: str, conversation_id: str,
                                  **kwargs) -> Dict[str, Any]:
        """Process a request using specified model type"""
        
        start_time = datetime.utcnow()
        
        try:
            # Route to appropriate model handler
            if model_type == ModelType.VLLM:
                result = await self._handle_vllm_request(domain, user_input, conversation_id, **kwargs)
            elif model_type == ModelType.AZURE_ML:
                result = await self._handle_azure_ml_request(domain, user_input, conversation_id, **kwargs)
            elif model_type == ModelType.AGENT_FRAMEWORK:
                result = await self._handle_agent_framework_request(domain, user_input, conversation_id, **kwargs)
            elif model_type == ModelType.OPENAI:
                result = await self._handle_openai_request(domain, user_input, conversation_id, **kwargs)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Record successful request
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            await self._record_model_success(model_type.value, execution_time)
            
            return {
                **result,
                "model_type": model_type.value,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            await self._record_model_failure(model_type.value, str(e), execution_time)
            
            return {
                "conversationId": conversation_id,
                "domain": domain,
                "model_type": model_type.value,
                "error": str(e),
                "success": False,
                "execution_time": execution_time,
                "source": "model_orchestrator"
            }
    
    async def _handle_vllm_request(self, domain: str, user_input: str, 
                                  conversation_id: str, **kwargs) -> Dict[str, Any]:
        """Handle vLLM model request"""
        
        if not self.vllm_config["server_url"]:
            raise ValueError("vLLM server URL not configured")
        
        try:
            # Prepare prompt
            mentor_mode = kwargs.get("mentor_mode", False)
            prompt = f"Domain: {domain}\\nUser Input: {user_input}\\nMentor Mode: {mentor_mode}"
            
            # Call vLLM endpoint
            result = await self._call_vllm(prompt)
            
            return {
                "conversationId": conversation_id,
                "domain": domain,
                "reply": result.get("response", "No response generated"),
                "success": True,
                "source": "vllm",
                "model_details": result.get("model_info", {})
            }
            
        except Exception as e:
            self.logger.error(f"vLLM request failed: {e}")
            raise
    
    async def _handle_azure_ml_request(self, domain: str, user_input: str, 
                                     conversation_id: str, **kwargs) -> Dict[str, Any]:
        """Handle Azure ML endpoint request"""
        
        if not self.azure_ml_config["endpoint_url"]:
            raise ValueError("Azure ML endpoint URL not configured")
        
        try:
            # Prepare request payload
            payload = {
                "instances": [{
                    "domain": domain,
                    "user_input": user_input,
                    "conversation_id": conversation_id,
                    **kwargs
                }]
            }
            
            # Call Azure ML endpoint
            result = await self._call_azure_ml_endpoint(payload)
            
            return {
                "conversationId": conversation_id,
                "domain": domain,
                "reply": result.get("response", "No response generated"),
                "success": True,
                "source": "azure_ml",
                "predictions": result.get("predictions", [])
            }
            
        except Exception as e:
            self.logger.error(f"Azure ML request failed: {e}")
            raise
    
    async def _handle_agent_framework_request(self, domain: str, user_input: str, 
                                            conversation_id: str, **kwargs) -> Dict[str, Any]:
        """Handle Agent Framework request"""
        
        if not self.agent_framework_client:
            raise ValueError("Agent Framework not initialized")
        
        try:
            # Use Agent Framework for processing
            # Format input for the agent
            formatted_input = f"Domain: {domain}\nRequest: {user_input}"
            
            # Process through Agent Framework
            # Note: This is a simplified implementation
            # In practice, you would use the agent's complete() method or similar
            response = f"Processed by Agent Framework - Domain: {domain}, Input: {user_input}"
            
            return {
                "conversationId": conversation_id,
                "domain": domain,
                "reply": response,
                "success": True,
                "source": "agent_framework"
            }
            
        except Exception as e:
            self.logger.error(f"Agent Framework request failed: {e}")
            raise
    
    async def _handle_openai_request(self, domain: str, user_input: str, 
                                   conversation_id: str, **kwargs) -> Dict[str, Any]:
        """Handle OpenAI API request"""
        
        # This would integrate with OpenAI API
        # Placeholder implementation
        try:
            response = f"OpenAI processing not yet implemented - Domain: {domain}, Input: {user_input}"
            
            return {
                "conversationId": conversation_id,
                "domain": domain,
                "reply": response,
                "success": True,
                "source": "openai",
                "note": "OpenAI integration requires implementation"
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI request failed: {e}")
            raise
    
    async def _call_vllm(self, prompt: str) -> Dict[str, Any]:
        """Call vLLM server endpoint"""
        
        try:
            url = f"{self.vllm_config['server_url']}/generate"
            
            payload = {
                "prompt": prompt,
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            headers = {"Content-Type": "application/json"}
            if self.vllm_config["api_key"]:
                headers["Authorization"] = f"Bearer {self.vllm_config['api_key']}"
            
            # Use aiohttp for async request (simplified with requests for now)
            response = requests.post(
                url, 
                json=payload, 
                headers=headers, 
                timeout=self.vllm_config["timeout"]
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "response": result.get("text", ""),
                "model_info": result.get("model", {}),
                "usage": result.get("usage", {})
            }
            
        except requests.RequestException as e:
            self.logger.error(f"vLLM API request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"vLLM processing failed: {e}")
            raise
    
    async def _call_azure_ml_endpoint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call Azure ML model endpoint"""
        
        try:
            url = self.azure_ml_config["endpoint_url"]
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.azure_ml_config['endpoint_key']}"
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.default_timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "response": result.get("output", ""),
                "predictions": result.get("predictions", []),
                "model_info": result.get("model", {})
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Azure ML endpoint request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Azure ML processing failed: {e}")
            raise
    
    async def select_optimal_model(self, domain: str, complexity: str = "medium", 
                                 latency_requirement: str = "standard") -> ModelType:
        """Select optimal model based on domain and requirements"""
        
        # Simple model selection logic (can be enhanced with ML)
        model_preferences = {
            "leadership": [ModelType.AGENT_FRAMEWORK, ModelType.VLLM, ModelType.AZURE_ML],
            "sales": [ModelType.AZURE_ML, ModelType.VLLM, ModelType.OPENAI],
            "erp": [ModelType.AZURE_ML, ModelType.VLLM],
            "general": [ModelType.VLLM, ModelType.OPENAI, ModelType.AZURE_ML]
        }
        
        # Get domain preferences
        preferred_models = model_preferences.get(domain.lower(), model_preferences["general"])
        
        # Filter by availability and health
        available_models = []
        for model_type in preferred_models:
            if await self._is_model_available(model_type):
                available_models.append(model_type)
        
        # Return first available model or default
        return available_models[0] if available_models else ModelType.VLLM
    
    async def _is_model_available(self, model_type: ModelType) -> bool:
        """Check if a model type is available and healthy"""
        
        if model_type == ModelType.VLLM:
            return bool(self.vllm_config["server_url"])
        elif model_type == ModelType.AZURE_ML:
            return bool(self.azure_ml_config["endpoint_url"])
        elif model_type == ModelType.AGENT_FRAMEWORK:
            return self.agent_framework_client is not None
        elif model_type == ModelType.OPENAI:
            return bool(os.getenv("OPENAI_API_KEY"))
        
        return False
    
    async def batch_process_requests(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple model requests in batch"""
        
        results = []
        
        # Limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        async def process_single_request(request):
            async with semaphore:
                model_type = ModelType(request.get("model_type", "vllm"))
                return await self.process_model_request(
                    model_type=model_type,
                    domain=request.get("domain", "general"),
                    user_input=request.get("user_input", ""),
                    conversation_id=request.get("conversation_id", "batch"),
                    **request.get("kwargs", {})
                )
        
        # Execute all requests
        tasks = [process_single_request(req) for req in requests]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                results.append({
                    "success": False,
                    "error": str(result),
                    "request_index": i,
                    "original_request": requests[i]
                })
            else:
                results.append(result)
        
        return {
            "total_requests": len(requests),
            "successful_requests": len([r for r in results if r.get("success")]),
            "failed_requests": len([r for r in results if not r.get("success")]),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform health check on all configured models"""
        
        health_results = {}
        
        # Check vLLM
        if self.vllm_config["server_url"]:
            try:
                # Simple health check request
                result = await self._call_vllm("Health check")
                health_results[ModelType.VLLM.value] = {
                    "status": "healthy",
                    "response_time": 0,  # Would measure actual response time
                    "last_check": datetime.utcnow().isoformat()
                }
            except Exception as e:
                health_results[ModelType.VLLM.value] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
        
        # Check Azure ML
        if self.azure_ml_config["endpoint_url"]:
            health_results[ModelType.AZURE_ML.value] = {
                "status": "configured",
                "last_check": datetime.utcnow().isoformat(),
                "note": "Health check requires actual endpoint test"
            }
        
        # Check Agent Framework
        if self.agent_framework_client:
            health_results[ModelType.AGENT_FRAMEWORK.value] = {
                "status": "initialized",
                "last_check": datetime.utcnow().isoformat()
            }
        
        self.model_health.update(health_results)
        return health_results
    
    async def _record_model_success(self, model_type: str, execution_time: float) -> None:
        """Record successful model request metrics"""
        
        if model_type not in self.request_metrics:
            self.request_metrics[model_type] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0
            }
        
        metrics = self.request_metrics[model_type]
        metrics["total_requests"] += 1
        metrics["successful_requests"] += 1
        
        # Update average response time
        if metrics["total_requests"] == 1:
            metrics["average_response_time"] = execution_time
        else:
            metrics["average_response_time"] = (
                (metrics["average_response_time"] * (metrics["total_requests"] - 1) + execution_time)
                / metrics["total_requests"]
            )
    
    async def _record_model_failure(self, model_type: str, error: str, execution_time: float) -> None:
        """Record failed model request metrics"""
        
        if model_type not in self.request_metrics:
            self.request_metrics[model_type] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0
            }
        
        metrics = self.request_metrics[model_type]
        metrics["total_requests"] += 1
        metrics["failed_requests"] += 1
    
    def get_service_availability(self) -> Dict[str, Any]:
        """Get service availability status"""
        return {
            "azure_ml": AZURE_ML_AVAILABLE,
            "agent_framework": AGENT_FRAMEWORK_AVAILABLE,
            "vllm_configured": bool(self.vllm_config["server_url"]),
            "azure_ml_configured": bool(self.azure_ml_config["endpoint_url"])
        }
    
    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive model orchestrator status"""
        
        return {
            "configured_models": len(self.model_configs),
            "active_models": len(self.active_models),
            "model_health": self.model_health,
            "request_metrics": self.request_metrics,
            "service_availability": {
                "azure_ml": AZURE_ML_AVAILABLE,
                "agent_framework": AGENT_FRAMEWORK_AVAILABLE,
                "vllm_configured": bool(self.vllm_config["server_url"]),
                "azure_ml_configured": bool(self.azure_ml_config["endpoint_url"])
            },
            "configuration": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "default_timeout": self.default_timeout,
                "retry_attempts": self.retry_attempts
            },
            "timestamp": datetime.utcnow().isoformat()
        }