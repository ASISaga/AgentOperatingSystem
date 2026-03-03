"""
aos_intelligence — Public API.

Machine learning pipelines, LoRA/LoRAx, DPO training, self-learning,
knowledge management, and RAG for the Agent Operating System (AOS).
"""

from aos_intelligence.config import MLConfig
from aos_intelligence.ml.lora_adapter_registry import LoRAAdapterRegistry, BASE_MODEL_ID
from aos_intelligence.ml.lora_inference_client import LoRAInferenceClient
from aos_intelligence.ml.lora_orchestration_router import LoRAOrchestrationRouter

__all__ = [
    "MLConfig",
    "LoRAAdapterRegistry",
    "LoRAInferenceClient",
    "LoRAOrchestrationRouter",
    "BASE_MODEL_ID",
]

__version__ = "2.0.0"
