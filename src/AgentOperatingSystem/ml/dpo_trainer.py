"""
DPO (Direct Preference Optimization) Trainer for AOS ML Pipeline

Implements cost-effective reinforcement learning using DPO as the industry standard
for low-cost alignment, eliminating the need for a separate Reward Model.

DPO treats the language model itself as the reward model, optimizing directly on
paired preference data (e.g., "Preferred" vs. "Rejected" responses).

Cost Benefit: Reduces computational overhead by approximately 30-50% compared to PPO
and is more stable during training.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("AOS.DPOTrainer")


@dataclass
class PreferenceData:
    """Represents a paired preference example for DPO training."""
    prompt: str
    chosen_response: str
    rejected_response: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DPOConfig:
    """Configuration for DPO training."""
    # Model configuration
    base_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    lora_adapter_path: Optional[str] = None  # Optional existing LoRA to build on
    
    # DPO-specific hyperparameters
    beta: float = 0.1  # Temperature parameter for DPO
    learning_rate: float = 5e-5
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    
    # LoRA configuration (applied on top of existing adapters)
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = None
    
    # Training infrastructure (Azure ML)
    compute_target: str = "Low-Priority-NC-Series"
    max_grad_norm: float = 1.0
    warmup_steps: int = 100
    logging_steps: int = 10
    save_steps: int = 500
    eval_steps: int = 100
    
    # Data configuration
    max_length: int = 2048
    max_prompt_length: int = 1024
    
    def __post_init__(self):
        if self.lora_target_modules is None:
            # Default LoRA target modules for Llama models
            self.lora_target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]


class DPOTrainer:
    """
    Direct Preference Optimization trainer for Llama-3.1-8B-Instruct.
    
    Implements the DPO algorithm which directly optimizes language models on
    preference data without requiring a separate reward model.
    
    Key Features:
    - Cost-effective: 30-50% reduction in computational overhead vs PPO
    - Stable training: More stable than traditional RLHF
    - Azure ML native: Integrates with Azure ML and AI Foundry
    - MLflow tracking: Built-in experiment tracking and metrics
    - LoRA-compatible: Works with existing LoRA adapters
    """
    
    def __init__(self, config: DPOConfig):
        """
        Initialize DPO trainer with configuration.
        
        Args:
            config: DPO training configuration
        """
        self.config = config
        self.logger = logging.getLogger("AOS.DPOTrainer")
        self.training_state = {
            "status": "initialized",
            "current_epoch": 0,
            "global_step": 0,
            "metrics": {}
        }
        
        # Try to import required libraries
        try:
            # Import TRL (Transformer Reinforcement Learning) library
            from trl import DPOTrainer as TRLDPOTrainer
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                TrainingArguments
            )
            from peft import LoraConfig, get_peft_model, PeftModel
            self.trl_available = True
            
            # Store class references for use in methods (enables lazy loading and optional dependencies)
            self.TRLDPOTrainer = TRLDPOTrainer
            self.AutoModelForCausalLM = AutoModelForCausalLM
            self.AutoTokenizer = AutoTokenizer
            self.TrainingArguments = TrainingArguments
            self.LoraConfig = LoraConfig
            self.get_peft_model = get_peft_model
            self.PeftModel = PeftModel
            
        except ImportError as e:
            self.logger.warning(f"TRL or transformers not available: {e}")
            self.trl_available = False
    
    def prepare_preference_dataset(
        self,
        preference_data: List[PreferenceData]
    ) -> Any:
        """
        Prepare preference dataset for DPO training.
        
        Converts preference data into the format required by TRL DPOTrainer.
        
        Args:
            preference_data: List of preference examples
            
        Returns:
            Formatted dataset for DPO training
        """
        if not self.trl_available:
            raise RuntimeError("TRL library not available")
        
        from datasets import Dataset
        
        # Convert to dataset format
        dataset_dict = {
            "prompt": [item.prompt for item in preference_data],
            "chosen": [item.chosen_response for item in preference_data],
            "rejected": [item.rejected_response for item in preference_data]
        }
        
        dataset = Dataset.from_dict(dataset_dict)
        
        self.logger.info(f"Prepared dataset with {len(dataset)} preference pairs")
        return dataset
    
    def load_base_model(self) -> Tuple[Any, Any]:
        """
        Load base model and tokenizer.
        
        If a LoRA adapter path is provided, loads the base model with the adapter
        as the starting point for DPO fine-tuning.
        
        Returns:
            Tuple of (model, tokenizer)
        """
        if not self.trl_available:
            raise RuntimeError("TRL library not available")
        
        self.logger.info(f"Loading base model: {self.config.base_model}")
        
        # Load tokenizer
        tokenizer = self.AutoTokenizer.from_pretrained(self.config.base_model)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load base model
        model = self.AutoModelForCausalLM.from_pretrained(
            self.config.base_model,
            device_map="auto",
            torch_dtype="auto"
        )
        
        # If existing LoRA adapter provided, load it
        if self.config.lora_adapter_path:
            self.logger.info(f"Loading existing LoRA adapter: {self.config.lora_adapter_path}")
            model = self.PeftModel.from_pretrained(
                model,
                self.config.lora_adapter_path
            )
            # Merge adapter to base model for DPO training
            model = model.merge_and_unload()
        
        return model, tokenizer
    
    def setup_lora_config(self) -> Any:
        """
        Setup LoRA configuration for DPO training.
        
        DPO training applies a new LoRA adapter on top of the base model
        (or merged base+adapter model).
        
        Returns:
            LoRA configuration
        """
        if not self.trl_available:
            raise RuntimeError("TRL library not available")
        
        lora_config = self.LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        self.logger.info(f"LoRA config: r={self.config.lora_r}, alpha={self.config.lora_alpha}")
        return lora_config
    
    def train(
        self,
        preference_data: List[PreferenceData],
        output_dir: str,
        mlflow_experiment_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Train model using DPO on preference data.
        
        Args:
            preference_data: List of preference examples (prompt, chosen, rejected)
            output_dir: Directory to save trained model and checkpoints
            mlflow_experiment_name: Optional MLflow experiment name for tracking
            
        Returns:
            Training results with metrics
        """
        if not self.trl_available:
            raise RuntimeError("TRL library not available. Install with: pip install trl transformers peft")
        
        self.logger.info("Starting DPO training")
        self.training_state["status"] = "preparing"
        
        # Setup MLflow tracking if requested
        if mlflow_experiment_name:
            try:
                import mlflow
                mlflow.set_experiment(mlflow_experiment_name)
                mlflow.start_run()
                mlflow.log_params({
                    "beta": self.config.beta,
                    "learning_rate": self.config.learning_rate,
                    "lora_r": self.config.lora_r,
                    "lora_alpha": self.config.lora_alpha,
                    "batch_size": self.config.batch_size
                })
                self.logger.info(f"MLflow tracking enabled: {mlflow_experiment_name}")
            except ImportError:
                self.logger.warning("MLflow not available, skipping experiment tracking")
        
        # Prepare dataset
        dataset = self.prepare_preference_dataset(preference_data)
        
        # Load model and tokenizer
        model, tokenizer = self.load_base_model()
        
        # Create reference model (frozen copy for DPO)
        # DPO requires a reference model to compute implicit rewards
        self.logger.info("Creating reference model")
        ref_model = self.AutoModelForCausalLM.from_pretrained(
            self.config.base_model,
            device_map="auto",
            torch_dtype="auto"
        )
        if self.config.lora_adapter_path:
            ref_model = self.PeftModel.from_pretrained(
                ref_model,
                self.config.lora_adapter_path
            )
            ref_model = ref_model.merge_and_unload()
        
        # Setup LoRA for the model to be trained
        lora_config = self.setup_lora_config()
        model = self.get_peft_model(model, lora_config)
        
        # Training arguments
        training_args = self.TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            max_grad_norm=self.config.max_grad_norm,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            save_total_limit=3,
            load_best_model_at_end=True,
            report_to=["mlflow"] if mlflow_experiment_name else [],
            remove_unused_columns=False
        )
        
        # Initialize DPO trainer
        self.logger.info("Initializing DPO trainer")
        dpo_trainer = self.TRLDPOTrainer(
            model=model,
            ref_model=ref_model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=tokenizer,
            beta=self.config.beta,
            max_length=self.config.max_length,
            max_prompt_length=self.config.max_prompt_length
        )
        
        # Train
        self.logger.info("Starting training loop")
        self.training_state["status"] = "training"
        
        train_result = dpo_trainer.train()
        
        # Save final model
        self.logger.info(f"Saving final model to {output_dir}")
        dpo_trainer.save_model(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        # Extract metrics
        metrics = {
            "train_loss": train_result.metrics.get("train_loss"),
            "train_runtime": train_result.metrics.get("train_runtime"),
            "train_samples_per_second": train_result.metrics.get("train_samples_per_second"),
            "total_steps": train_result.global_step,
            "epochs_completed": self.config.num_epochs
        }
        
        # Log to MLflow
        if mlflow_experiment_name:
            try:
                import mlflow
                mlflow.log_metrics(metrics)
                mlflow.log_artifact(output_dir)
                mlflow.end_run()
            except Exception as e:
                self.logger.warning(f"MLflow logging failed: {e}")
        
        self.training_state["status"] = "completed"
        self.training_state["metrics"] = metrics
        
        self.logger.info(f"Training completed. Metrics: {metrics}")
        return {
            "status": "success",
            "output_dir": output_dir,
            "metrics": metrics,
            "training_state": self.training_state
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current training status and metrics."""
        return self.training_state.copy()


class PreferenceDataCollector:
    """
    Utility for collecting and managing preference data for DPO training.
    
    Supports multiple collection strategies:
    1. Human feedback (explicit preferences)
    2. Teacher model ranking (e.g., Llama 4 as judge)
    3. Automated heuristics (e.g., length, coherence scores)
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize preference data collector.
        
        Args:
            storage_path: Optional path to store collected preferences
        """
        self.storage_path = storage_path
        self.preferences: List[PreferenceData] = []
        self.logger = logging.getLogger("AOS.PreferenceDataCollector")
    
    def add_human_preference(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        preference: str,  # 'a' or 'b'
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a human-labeled preference pair.
        
        Args:
            prompt: The input prompt
            response_a: First response option
            response_b: Second response option
            preference: Which response is preferred ('a' or 'b')
            metadata: Optional metadata (rater info, confidence, etc.)
        """
        if preference.lower() == 'a':
            chosen, rejected = response_a, response_b
        elif preference.lower() == 'b':
            chosen, rejected = response_b, response_a
        else:
            raise ValueError("Preference must be 'a' or 'b'")
        
        pref_data = PreferenceData(
            prompt=prompt,
            chosen_response=chosen,
            rejected_response=rejected,
            metadata={
                **(metadata or {}),
                "source": "human",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        self.preferences.append(pref_data)
        self.logger.info(f"Added human preference. Total: {len(self.preferences)}")
    
    async def add_teacher_model_preference(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        teacher_model: str = "llama-4",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Use a teacher model (e.g., Llama 4) to rank responses.
        
        Note: This functionality requires integration with the ML pipeline
        for teacher model inference. It is not yet implemented.
        
        Args:
            prompt: The input prompt
            response_a: First response option
            response_b: Second response option
            teacher_model: Name/ID of teacher model to use for ranking
            metadata: Optional metadata
            
        Raises:
            NotImplementedError: This feature is not yet implemented
        """
        raise NotImplementedError(
            "Teacher model ranking is not yet implemented. "
            "This requires integration with the ML pipeline to call the teacher model. "
            "Use add_human_preference() or add_heuristic_preference() instead."
        )
    
    # Heuristic thresholds for response quality
    MIN_RESPONSE_LENGTH = 50
    MAX_RESPONSE_LENGTH = 2000
    
    def add_heuristic_preference(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        heuristic: str = "length",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Use automated heuristics to determine preference.
        
        Useful for bootstrapping or augmenting human preferences.
        
        Args:
            prompt: The input prompt
            response_a: First response option
            response_b: Second response option
            heuristic: Heuristic to use ('length', 'coherence', etc.)
            metadata: Optional metadata
        """
        if heuristic == "length":
            # Prefer longer, more detailed responses (within reasonable bounds)
            len_a, len_b = len(response_a), len(response_b)
            if self.MIN_RESPONSE_LENGTH < len_a < self.MAX_RESPONSE_LENGTH and len_a > len_b:
                preference = 'a'
            elif self.MIN_RESPONSE_LENGTH < len_b < self.MAX_RESPONSE_LENGTH and len_b > len_a:
                preference = 'b'
            else:
                # Skip if heuristic is inconclusive
                return
        else:
            raise ValueError(f"Unknown heuristic: {heuristic}")
        
        self.add_human_preference(
            prompt, response_a, response_b, preference,
            metadata={
                **(metadata or {}),
                "source": "heuristic",
                "heuristic_type": heuristic
            }
        )
    
    def get_preferences(self) -> List[PreferenceData]:
        """Get all collected preferences."""
        return self.preferences.copy()
    
    def save_preferences(self, path: Optional[str] = None) -> str:
        """
        Save preferences to disk in JSONL format.
        
        Args:
            path: Optional path to save to (overrides storage_path)
            
        Returns:
            Path where preferences were saved
        """
        import json
        
        save_path = path or self.storage_path
        if not save_path:
            raise ValueError("No storage path specified")
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w') as f:
            for pref in self.preferences:
                json.dump({
                    "prompt": pref.prompt,
                    "chosen": pref.chosen_response,
                    "rejected": pref.rejected_response,
                    "metadata": pref.metadata
                }, f)
                f.write('\n')
        
        self.logger.info(f"Saved {len(self.preferences)} preferences to {save_path}")
        return str(save_path)
    
    def load_preferences(self, path: Optional[str] = None) -> int:
        """
        Load preferences from disk.
        
        Args:
            path: Optional path to load from (overrides storage_path)
            
        Returns:
            Number of preferences loaded
        """
        import json
        
        load_path = path or self.storage_path
        if not load_path:
            raise ValueError("No storage path specified")
        
        load_path = Path(load_path)
        if not load_path.exists():
            self.logger.warning(f"Preference file not found: {load_path}")
            return 0
        
        loaded_count = 0
        with open(load_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                pref = PreferenceData(
                    prompt=data["prompt"],
                    chosen_response=data["chosen"],
                    rejected_response=data["rejected"],
                    metadata=data.get("metadata")
                )
                self.preferences.append(pref)
                loaded_count += 1
        
        self.logger.info(f"Loaded {loaded_count} preferences from {load_path}")
        return loaded_count
