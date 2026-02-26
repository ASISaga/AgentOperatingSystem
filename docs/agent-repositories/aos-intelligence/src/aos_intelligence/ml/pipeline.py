"""
AOS ML Pipeline Manager

Manages machine learning operations including training, inference, and model management.
All operations use Llama 3.3 70B as the base model for superior performance and capabilities.
Includes DPO (Direct Preference Optimization) support for cost-effective reinforcement learning.
Includes LoRAx integration for cost-effective multi-adapter inference.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..config import MLConfig
from .pipeline_ops import trigger_lora_training, run_azure_ml_pipeline, aml_infer


class MLPipelineManager:
    """
    Central manager for ML pipeline operations in AOS.

    Coordinates:
    - Model training and fine-tuning
    - Inference operations
    - Model deployment and versioning
    - Performance monitoring
    - LoRAx multi-adapter serving
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

        # LoRAx integration
        self.lorax_server = None
        if self.config.enable_lorax:
            self._initialize_lorax()

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

    async def train_dpo_adapter(
        self,
        agent_role: str,
        base_adapter_path: str,
        preference_data_path: str,
        output_dir: Optional[str] = None,
        config_override: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Train a DPO (Direct Preference Optimization) adapter for an agent.

        This applies reinforcement learning from human feedback using the cost-effective
        DPO approach, which reduces computational overhead by 30-50% compared to PPO.

        Args:
            agent_role: Agent role (e.g., "CEO", "CFO")
            base_adapter_path: Path to existing LoRA adapter to build upon
            preference_data_path: Path to preference data (JSONL format)
            output_dir: Optional output directory for DPO adapter
            config_override: Optional configuration overrides

        Returns:
            Training job ID
        """
        if not self.config.enable_training or not self.config.enable_dpo:
            raise RuntimeError("DPO training is disabled in configuration")

        # Check if we can start new training job
        active_jobs = sum(1 for job in self.training_jobs.values()
                         if job["status"] in ["running", "pending"])

        if active_jobs >= self.config.max_training_jobs:
            raise RuntimeError(f"Maximum training jobs ({self.config.max_training_jobs}) reached")

        # Create DPO training job
        job_id = f"dpo_job_{self.job_counter}"
        self.job_counter += 1

        if output_dir is None:
            output_dir = f"{self.config.model_storage_path}/{agent_role}_dpo_adapter"

        dpo_config = {
            "type": "dpo",
            "agent_role": agent_role,
            "base_adapter_path": base_adapter_path,
            "preference_data_path": preference_data_path,
            "output_dir": output_dir,
            "beta": config_override.get("beta", self.config.dpo_beta) if config_override else self.config.dpo_beta,
            "learning_rate": config_override.get("learning_rate", self.config.dpo_learning_rate) if config_override else self.config.dpo_learning_rate,
            "batch_size": config_override.get("batch_size", self.config.dpo_batch_size) if config_override else self.config.dpo_batch_size,
            "num_epochs": config_override.get("num_epochs", self.config.dpo_epochs) if config_override else self.config.dpo_epochs,
        }

        training_job = {
            "job_id": job_id,
            "config": dpo_config,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "model_path": None,
            "metrics": {}
        }

        self.training_jobs[job_id] = training_job

        # Start DPO training asynchronously
        import asyncio
        asyncio.create_task(self._execute_dpo_training(job_id))

        # Update adapter status
        adapter_key = f"{agent_role}_dpo"
        self.active_adapters[adapter_key] = {
            "job_id": job_id,
            "config": dpo_config,
            "status": "training",
            "type": "dpo"
        }

        self.logger.info(f"Started DPO training job: {job_id} for {agent_role}")
        return job_id

    async def _execute_dpo_training(self, job_id: str):
        """Execute a DPO training job"""
        job = self.training_jobs[job_id]

        try:
            job["status"] = "running"
            job["started_at"] = datetime.utcnow().isoformat()

            self.logger.info(f"Starting DPO training job: {job_id}")

            # Import DPO trainer
            try:
                from .dpo_trainer import DPOTrainer, DPOConfig, PreferenceDataCollector
            except ImportError as e:
                raise RuntimeError(f"DPO trainer not available: {e}")

            # Load preference data
            collector = PreferenceDataCollector()
            collector.load_preferences(job["config"]["preference_data_path"])
            preference_data = collector.get_preferences()

            if not preference_data:
                raise ValueError(f"No preference data loaded from {job['config']['preference_data_path']}")

            # Setup DPO configuration
            dpo_config = DPOConfig(
                base_model="meta-llama/Llama-3.3-70B-Instruct",
                lora_adapter_path=job["config"]["base_adapter_path"],
                beta=job["config"]["beta"],
                learning_rate=job["config"]["learning_rate"],
                batch_size=job["config"]["batch_size"],
                num_epochs=job["config"]["num_epochs"]
            )

            # Initialize trainer
            trainer = DPOTrainer(dpo_config)

            # Setup MLflow experiment name if enabled
            mlflow_experiment = None
            if self.config.enable_mlflow:
                mlflow_experiment = f"{self.config.mlflow_experiment_prefix}_{job['config']['agent_role']}"

            # Train
            result = trainer.train(
                preference_data=preference_data,
                output_dir=job["config"]["output_dir"],
                mlflow_experiment_name=mlflow_experiment
            )

            # Update job status
            job["status"] = "completed"
            job["completed_at"] = datetime.utcnow().isoformat()
            job["model_path"] = result["output_dir"]
            job["metrics"] = result["metrics"]

            # Register DPO adapter
            agent_role = job["config"]["agent_role"]
            adapter_key = f"{agent_role}_dpo"

            self.models[adapter_key] = {
                "job_id": job_id,
                "path": job["model_path"],
                "config": job["config"],
                "metrics": job["metrics"],
                "type": "dpo"
            }

            # Update adapter status
            if adapter_key in self.active_adapters:
                self.active_adapters[adapter_key]["status"] = "ready"
                self.active_adapters[adapter_key]["model_path"] = job["model_path"]

            self.logger.info(f"DPO training job completed: {job_id}, metrics: {job['metrics']}")

        except Exception as e:
            job["status"] = "failed"
            job["completed_at"] = datetime.utcnow().isoformat()
            job["error"] = str(e)

            # Update adapter status
            agent_role = job["config"].get("agent_role")
            if agent_role:
                adapter_key = f"{agent_role}_dpo"
                if adapter_key in self.active_adapters:
                    self.active_adapters[adapter_key]["status"] = "failed"

            self.logger.error(f"DPO training job failed: {job_id}, error: {e}")

    def collect_preference_data(
        self,
        agent_role: str,
        prompt: str,
        response_a: str,
        response_b: str,
        preference: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Collect preference data for DPO training.

        This method allows agents or human reviewers to provide pairwise preferences
        that will be used for DPO alignment training.

        Args:
            agent_role: Agent role this preference is for
            prompt: The input prompt
            response_a: First response option
            response_b: Second response option
            preference: Which response is preferred ('a' or 'b')
            metadata: Optional metadata (rater info, confidence, etc.)
        """
        try:
            from .dpo_trainer import PreferenceDataCollector
        except ImportError:
            self.logger.error("DPO trainer module not available")
            return

        # Get or create collector for this agent
        storage_path = f"{self.config.preference_data_path}/{agent_role}_preferences.jsonl"
        collector = PreferenceDataCollector(storage_path)

        # Load existing preferences
        try:
            collector.load_preferences()
        except (FileNotFoundError, IOError) as e:
            self.logger.debug(f"No existing preferences found: {e}")

        # Add new preference
        collector.add_human_preference(
            prompt=prompt,
            response_a=response_a,
            response_b=response_b,
            preference=preference,
            metadata={
                **(metadata or {}),
                "agent_role": agent_role
            }
        )

        # Save updated preferences
        collector.save_preferences()

        self.logger.info(f"Collected preference data for {agent_role}. Total: {len(collector.preferences)}")

    def get_dpo_status(self, agent_role: str) -> Dict[str, Any]:
        """
        Get DPO training status for an agent.

        Args:
            agent_role: Agent role

        Returns:
            DPO status information
        """
        adapter_key = f"{agent_role}_dpo"

        if adapter_key not in self.active_adapters:
            return {
                "status": "not_started",
                "agent_role": agent_role,
                "has_dpo_adapter": False
            }

        adapter_info = self.active_adapters[adapter_key]
        job_id = adapter_info.get("job_id")
        job_info = self.training_jobs.get(job_id, {}) if job_id else {}

        # Check preference data availability
        from pathlib import Path
        pref_path = Path(f"{self.config.preference_data_path}/{agent_role}_preferences.jsonl")
        has_preference_data = pref_path.exists()

        # Count preferences if file exists
        preference_count = 0
        if has_preference_data:
            try:
                with open(pref_path, 'r') as f:
                    preference_count = sum(1 for _ in f)
            except (IOError, PermissionError) as e:
                self.logger.warning(f"Could not count preferences in {pref_path}: {e}")

        return {
            "status": adapter_info.get("status", "unknown"),
            "agent_role": agent_role,
            "has_dpo_adapter": adapter_info.get("status") == "ready",
            "job_id": job_id,
            "model_path": adapter_info.get("model_path"),
            "has_preference_data": has_preference_data,
            "preference_count": preference_count,
            "config": adapter_info.get("config", {}),
            "metrics": job_info.get("metrics", {}),
            "created_at": job_info.get("created_at"),
            "completed_at": job_info.get("completed_at")
        }

    def _initialize_lorax(self):
        """Initialize LoRAx server for multi-adapter inference."""
        try:
            from .lorax_server import LoRAxServer, LoRAxConfig

            lorax_config = LoRAxConfig(
                base_model=self.config.lorax_base_model,
                host=self.config.lorax_host,
                port=self.config.lorax_port,
                adapter_cache_size=self.config.lorax_adapter_cache_size,
                max_concurrent_requests=self.config.lorax_max_concurrent_requests,
                max_batch_size=self.config.lorax_max_batch_size,
                gpu_memory_utilization=self.config.lorax_gpu_memory_utilization,
                adapter_base_path=self.config.model_storage_path
            )

            self.lorax_server = LoRAxServer(lorax_config)
            self.logger.info("LoRAx server initialized")

        except ImportError as e:
            self.logger.warning(f"LoRAx not available: {e}")
            self.lorax_server = None

    async def start_lorax_server(self) -> bool:
        """
        Start the LoRAx server for multi-adapter inference.

        Returns:
            True if server started successfully
        """
        if not self.config.enable_lorax:
            self.logger.warning("LoRAx is disabled in configuration")
            return False

        if self.lorax_server is None:
            self._initialize_lorax()

        if self.lorax_server is None:
            self.logger.error("Failed to initialize LoRAx server")
            return False

        return await self.lorax_server.start()

    async def stop_lorax_server(self) -> bool:
        """
        Stop the LoRAx server.

        Returns:
            True if server stopped successfully
        """
        if self.lorax_server is None:
            self.logger.warning("LoRAx server is not initialized")
            return True

        return await self.lorax_server.stop()

    def register_lorax_adapter(
        self,
        agent_role: str,
        adapter_path: str,
        adapter_id: Optional[str] = None,
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a LoRA adapter with LoRAx for multi-adapter serving.

        Args:
            agent_role: Agent role (e.g., "CEO", "CFO")
            adapter_path: Path to the adapter files
            adapter_id: Optional custom adapter ID (defaults to agent_role)
            version: Version string
            metadata: Optional metadata

        Returns:
            True if registration successful
        """
        if self.lorax_server is None:
            self.logger.error("LoRAx server is not initialized")
            return False

        adapter_id = adapter_id or agent_role

        try:
            self.lorax_server.registry.register_adapter(
                adapter_id=adapter_id,
                agent_role=agent_role,
                adapter_path=adapter_path,
                version=version,
                metadata=metadata
            )

            self.logger.info(f"Registered LoRAx adapter {adapter_id} for {agent_role}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register LoRAx adapter: {e}")
            return False

    async def lorax_inference(
        self,
        agent_role: str,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run inference using LoRAx for a specific agent role.

        This is the recommended method for multi-agent inference as it provides
        significant cost savings through adapter sharing.

        Args:
            agent_role: Agent role (e.g., "CEO", "CFO")
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional generation parameters

        Returns:
            Inference result
        """
        if self.lorax_server is None:
            self.logger.error("LoRAx server is not initialized")
            return {"error": "LoRAx server not available"}

        if not self.lorax_server.running:
            self.logger.error("LoRAx server is not running")
            return {"error": "LoRAx server not running"}

        try:
            result = await self.lorax_server.inference_for_agent(
                agent_role=agent_role,
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                **kwargs
            )

            return result

        except Exception as e:
            self.logger.error(f"LoRAx inference failed: {e}")
            return {"error": str(e)}

    async def lorax_batch_inference(
        self,
        requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process multiple inference requests using LoRAx batch processing.

        This is highly efficient for processing multiple agents concurrently.

        Args:
            requests: List of inference requests with agent_role and prompt

        Returns:
            List of inference results
        """
        if self.lorax_server is None:
            return [{"error": "LoRAx server not available"}] * len(requests)

        if not self.lorax_server.running:
            return [{"error": "LoRAx server not running"}] * len(requests)

        try:
            # Convert agent_role to adapter_id for each request
            lorax_requests = []
            for req in requests:
                adapter_info = self.lorax_server.registry.get_adapter_for_agent(
                    req["agent_role"]
                )
                if not adapter_info:
                    self.logger.warning(f"No adapter for agent {req['agent_role']}")
                    continue

                lorax_requests.append({
                    "adapter_id": adapter_info.adapter_id,
                    "prompt": req["prompt"],
                    "params": req.get("params", {})
                })

            results = await self.lorax_server.batch_inference(lorax_requests)
            return results

        except Exception as e:
            self.logger.error(f"LoRAx batch inference failed: {e}")
            return [{"error": str(e)}] * len(requests)

    def get_lorax_status(self) -> Dict[str, Any]:
        """
        Get LoRAx server status and metrics.

        Returns:
            Status dictionary with server info and metrics
        """
        if self.lorax_server is None:
            return {
                "enabled": self.config.enable_lorax,
                "initialized": False,
                "running": False,
                "message": "LoRAx server not initialized"
            }

        status = self.lorax_server.get_status()
        status["enabled"] = self.config.enable_lorax
        status["initialized"] = True

        return status

    def get_lorax_adapter_stats(self, agent_role: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific LoRAx adapter.

        Args:
            agent_role: Agent role

        Returns:
            Adapter statistics or None if not found
        """
        if self.lorax_server is None:
            return None

        adapter_info = self.lorax_server.registry.get_adapter_for_agent(agent_role)
        if not adapter_info:
            return None

        return self.lorax_server.get_adapter_stats(adapter_info.adapter_id)