from dataclasses import dataclass
import os

@dataclass
class MLConfig:
    """Configuration for AOS ML pipeline"""
    enable_training: bool = True
    model_storage_path: str = "models"
    training_data_path: str = "training_data"
    max_training_jobs: int = 5
    default_model_type: str = "lora"
    
    # DPO (Direct Preference Optimization) configuration
    enable_dpo: bool = True
    dpo_beta: float = 0.1  # Temperature parameter for DPO
    dpo_learning_rate: float = 5e-5
    dpo_batch_size: int = 4
    dpo_epochs: int = 3
    preference_data_path: str = "preference_data"
    
    # MLflow tracking for DPO
    enable_mlflow: bool = True
    mlflow_tracking_uri: str = ""
    mlflow_experiment_prefix: str = "aos_dpo"
    
    # LoRAx (LoRA eXchange) configuration
    enable_lorax: bool = True
    lorax_base_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    lorax_host: str = "0.0.0.0"
    lorax_port: int = 8080
    lorax_adapter_cache_size: int = 100
    lorax_max_concurrent_requests: int = 128
    lorax_max_batch_size: int = 32
    lorax_gpu_memory_utilization: float = 0.9

    @classmethod
    def from_env(cls):
        return cls(
            enable_training=os.getenv("AOS_ENABLE_ML_TRAINING", "true").lower() == "true",
            model_storage_path=os.getenv("AOS_MODEL_STORAGE_PATH", "models"),
            training_data_path=os.getenv("AOS_TRAINING_DATA_PATH", "training_data"),
            max_training_jobs=int(os.getenv("AOS_MAX_TRAINING_JOBS", "5")),
            default_model_type=os.getenv("AOS_DEFAULT_MODEL_TYPE", "lora"),
            # DPO configuration
            enable_dpo=os.getenv("AOS_ENABLE_DPO", "true").lower() == "true",
            dpo_beta=float(os.getenv("AOS_DPO_BETA", "0.1")),
            dpo_learning_rate=float(os.getenv("AOS_DPO_LEARNING_RATE", "5e-5")),
            dpo_batch_size=int(os.getenv("AOS_DPO_BATCH_SIZE", "4")),
            dpo_epochs=int(os.getenv("AOS_DPO_EPOCHS", "3")),
            preference_data_path=os.getenv("AOS_PREFERENCE_DATA_PATH", "preference_data"),
            # MLflow configuration
            enable_mlflow=os.getenv("AOS_ENABLE_MLFLOW", "true").lower() == "true",
            mlflow_tracking_uri=os.getenv("AOS_MLFLOW_TRACKING_URI", ""),
            mlflow_experiment_prefix=os.getenv("AOS_MLFLOW_EXPERIMENT_PREFIX", "aos_dpo"),
            # LoRAx configuration
            enable_lorax=os.getenv("AOS_ENABLE_LORAX", "true").lower() == "true",
            lorax_base_model=os.getenv("AOS_LORAX_BASE_MODEL", "meta-llama/Llama-3.1-8B-Instruct"),
            lorax_host=os.getenv("AOS_LORAX_HOST", "0.0.0.0"),
            lorax_port=int(os.getenv("AOS_LORAX_PORT", "8080")),
            lorax_adapter_cache_size=int(os.getenv("AOS_LORAX_ADAPTER_CACHE_SIZE", "100")),
            lorax_max_concurrent_requests=int(os.getenv("AOS_LORAX_MAX_CONCURRENT_REQUESTS", "128")),
            lorax_max_batch_size=int(os.getenv("AOS_LORAX_MAX_BATCH_SIZE", "32")),
            lorax_gpu_memory_utilization=float(os.getenv("AOS_LORAX_GPU_MEMORY_UTILIZATION", "0.9")),
        )
