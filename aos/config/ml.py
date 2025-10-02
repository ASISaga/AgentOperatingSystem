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

    @classmethod
    def from_env(cls):
        return cls(
            enable_training=os.getenv("AOS_ENABLE_ML_TRAINING", "true").lower() == "true",
            model_storage_path=os.getenv("AOS_MODEL_STORAGE_PATH", "models"),
            training_data_path=os.getenv("AOS_TRAINING_DATA_PATH", "training_data"),
            max_training_jobs=int(os.getenv("AOS_MAX_TRAINING_JOBS", "5")),
            default_model_type=os.getenv("AOS_DEFAULT_MODEL_TYPE", "lora")
        )
