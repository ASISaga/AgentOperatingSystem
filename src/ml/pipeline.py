"""
AOS ML Pipeline Manager

Manages machine learning operations including training, inference, and model management.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..config.ml import MLConfig
from .pipeline_ops import trigger_lora_training, run_azure_ml_pipeline, aml_infer


class MLPipelineManager:
    """
    Central manager for ML pipeline operations in AOS.
    
    Coordinates:
    - Model training and fine-tuning
    - Inference operations
    - Model deployment and versioning
    - Performance monitoring
    """
    
    def __init__(self, config: MLConfig):
        self.config = config
        self.logger = logging.getLogger("AOS.MLPipelineManager")
        
        # Model registry
        self.models = {}
        self.active_adapters = {}
        
        # Training jobs
        self.training_jobs = {}
        self.job_counter = 0
        
        # Inference cache
        self.inference_cache = {}
    
    async def train_model(self, model_config: Dict[str, Any]) -> str:
        """
        Train a new model or fine-tune an existing one.
        
        Args:
            model_config: Configuration for training
            
        Returns:
            Training job ID
        """
        if not self.config.enable_training:
            raise RuntimeError("ML training is disabled in configuration")
        
        # Check if we can start new training job
        active_jobs = sum(1 for job in self.training_jobs.values() 
                         if job["status"] in ["running", "pending"])
        
        if active_jobs >= self.config.max_training_jobs:
            raise RuntimeError(f"Maximum training jobs ({self.config.max_training_jobs}) reached")
        
        # Create training job
        job_id = f"training_job_{self.job_counter}"
        self.job_counter += 1
        
        training_job = {
            "job_id": job_id,
            "config": model_config,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "model_path": None,
            "metrics": {}
        }
        
        self.training_jobs[job_id] = training_job
        
        # Start training asynchronously
        import asyncio
        asyncio.create_task(self._execute_training(job_id))
        
        self.logger.info(f"Started training job: {job_id}")
        return job_id
    
    async def train_lora_adapter(self, agent_role: str, training_params: Dict[str, Any]) -> str:
        """
        Train a LoRA adapter for a specific agent role.
        
        Args:
            agent_role: Role of the agent (e.g., "CEO", "CFO")
            training_params: Parameters for LoRA training
            
        Returns:
            Training job ID
        """
        adapter_config = {
            "type": "lora",
            "agent_role": agent_role,
            "base_model": training_params.get("base_model", "default"),
            "training_data": training_params.get("training_data"),
            "hyperparameters": training_params.get("hyperparameters", {}),
            "adapter_name": f"{agent_role}_adapter"
        }
        
        job_id = await self.train_model(adapter_config)
        
        # Register adapter
        self.active_adapters[agent_role] = {
            "job_id": job_id,
            "config": adapter_config,
            "status": "training"
        }
        
        return job_id
    
    async def get_inference(self, model_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get inference from a trained model.
        
        Args:
            model_name: Name of the model to use
            input_data: Input data for inference
            
        Returns:
            Inference results
        """
        try:
            # Check cache first
            cache_key = f"{model_name}_{hash(str(input_data))}"
            if cache_key in self.inference_cache:
                self.logger.debug(f"Returning cached inference for {model_name}")
                return self.inference_cache[cache_key]
            
            # Perform inference
            self.logger.debug(f"Running inference with {model_name}")
            
            # Placeholder for actual inference logic
            result = {
                "model": model_name,
                "input": input_data,
                "output": {"prediction": "sample_output", "confidence": 0.85},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache result
            self.inference_cache[cache_key] = result
            
            # Limit cache size
            if len(self.inference_cache) > 1000:
                # Remove oldest entries
                oldest_keys = list(self.inference_cache.keys())[:100]
                for key in oldest_keys:
                    del self.inference_cache[key]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during inference: {e}")
            return {"error": str(e)}
    
    async def get_agent_inference(self, agent_role: str, prompt: str) -> Dict[str, Any]:
        """
        Get inference for a specific agent role using its adapter.
        
        Args:
            agent_role: Agent role (e.g., "CEO", "CFO")
            prompt: Input prompt
            
        Returns:
            Inference results
        """
        if agent_role not in self.active_adapters:
            return {"error": f"No adapter found for agent role: {agent_role}"}
        
        adapter_info = self.active_adapters[agent_role]
        if adapter_info["status"] != "ready":
            return {"error": f"Adapter for {agent_role} is not ready (status: {adapter_info['status']})"}
        
        model_name = adapter_info["config"]["adapter_name"]
        input_data = {"prompt": prompt, "role": agent_role}
        
        return await self.get_inference(model_name, input_data)
    
    def get_training_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a training job"""
        return self.training_jobs.get(job_id)
    
    def list_models(self) -> List[str]:
        """List all available models"""
        return list(self.models.keys())
    
    def list_adapters(self) -> List[str]:
        """List all active adapters"""
        return list(self.active_adapters.keys())
    
    def get_adapter_config(self, agent_role: str) -> Dict[str, Any]:
        """Get configuration for a specific adapter"""
        adapter_info = self.active_adapters.get(agent_role, {})
        return adapter_info.get("config", {})
    
    async def run_azure_ml_pipeline_full(self, subscription_id: str, resource_group: str, workspace_name: str) -> str:
        """
        Run the full Azure ML pipeline (provision, train, register).
        Enhanced from old MLPipelineManager functionality.
        """
        try:
            result = await run_azure_ml_pipeline(subscription_id, resource_group, workspace_name)
            self.logger.info(f"Azure ML pipeline executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Azure ML pipeline failed: {e}")
            raise
    
    async def infer_with_adapter(self, agent_role: str, prompt: str) -> Any:
        """
        Perform inference for a specific agent role using its adapter.
        Enhanced from old MLPipelineManager functionality.
        """
        try:
            # Check if adapter exists and is ready
            if agent_role not in self.active_adapters:
                return {"error": f"No adapter found for agent role: {agent_role}"}
            
            adapter_info = self.active_adapters[agent_role]
            if adapter_info.get("status") != "ready":
                return {"error": f"Adapter for {agent_role} is not ready. Status: {adapter_info.get('status', 'unknown')}"}
            
            # Use the pipeline ops for inference
            result = await aml_infer(agent_role, prompt)
            
            self.logger.debug(f"Inference completed for {agent_role}")
            return result
            
        except Exception as e:
            self.logger.error(f"Inference failed for {agent_role}: {e}")
            return {"error": str(e)}
    
    async def train_adapter_with_pipeline_ops(self, agent_role: str, training_params: Dict[str, Any], adapter_config: Dict[str, Any]) -> str:
        """
        Train a LoRA adapter for a specific agent role using pipeline operations.
        Enhanced from old MLPipelineManager functionality.
        """
        try:
            # Prepare adapter config
            adapter_config = dict(adapter_config)
            adapter_config["adapter_name"] = agent_role
            
            # Use pipeline ops for training
            result = await trigger_lora_training(training_params, [adapter_config])
            
            # Register the adapter
            self.active_adapters[agent_role] = {
                "config": adapter_config,
                "status": "ready",
                "training_params": training_params,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"LoRA adapter training completed for {agent_role}")
            return result
            
        except Exception as e:
            self.logger.error(f"Adapter training failed for {agent_role}: {e}")
            # Update adapter status
            if agent_role in self.active_adapters:
                self.active_adapters[agent_role]["status"] = "failed"
            raise

    def get_ml_status(self) -> Dict[str, Any]:
        """Get comprehensive ML pipeline status"""
        active_training_jobs = sum(1 for job in self.training_jobs.values() 
                                  if job["status"] in ["running", "pending"])
        
        return {
            "training_enabled": self.config.enable_training,
            "total_models": len(self.models),
            "total_adapters": len(self.active_adapters),
            "total_training_jobs": len(self.training_jobs),
            "active_training_jobs": active_training_jobs,
            "inference_cache_size": len(self.inference_cache),
            "adapter_status": {role: info.get("status", "unknown") for role, info in self.active_adapters.items()},
            "config": {
                "max_training_jobs": self.config.max_training_jobs,
                "model_storage_path": self.config.model_storage_path,
                "default_model_type": self.config.default_model_type
            }
        }
    
    async def _execute_training(self, job_id: str):
        """Execute a training job"""
        job = self.training_jobs[job_id]
        
        try:
            job["status"] = "running"
            job["started_at"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"Starting training job: {job_id}")
            
            # Placeholder for actual training logic
            # This would integrate with Azure ML, local training, etc.
            import asyncio
            await asyncio.sleep(2)  # Simulate training time
            
            # Update job status
            job["status"] = "completed"
            job["completed_at"] = datetime.utcnow().isoformat()
            job["model_path"] = f"{self.config.model_storage_path}/{job_id}_model"
            job["metrics"] = {"accuracy": 0.95, "loss": 0.05}
            
            # Register model
            model_name = job["config"].get("adapter_name", job_id)
            self.models[model_name] = {
                "job_id": job_id,
                "path": job["model_path"],
                "config": job["config"],
                "metrics": job["metrics"]
            }
            
            # Update adapter status if this was an adapter training job
            agent_role = job["config"].get("agent_role")
            if agent_role and agent_role in self.active_adapters:
                self.active_adapters[agent_role]["status"] = "ready"
            
            self.logger.info(f"Training job completed: {job_id}")
            
        except Exception as e:
            job["status"] = "failed"
            job["completed_at"] = datetime.utcnow().isoformat()
            job["error"] = str(e)
            
            # Update adapter status
            agent_role = job["config"].get("agent_role")
            if agent_role and agent_role in self.active_adapters:
                self.active_adapters[agent_role]["status"] = "failed"
            
            self.logger.error(f"Training job failed: {job_id}, error: {e}")