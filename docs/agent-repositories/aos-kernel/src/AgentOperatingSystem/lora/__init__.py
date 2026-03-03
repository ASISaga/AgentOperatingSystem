"""LoRA Management layer — Multi-LoRA adapter lifecycle for AOS Kernel.

This package provides three high-level components for managing persona-specific
LoRA adapters that are injected into the Llama-3.3-70B-Instruct base model at
inference time:

- :class:`LoRAAdapterRegistry` — registers fine-tuned adapter artefacts as
  MLflow Model Assets in the Azure AI Foundry Model Registry, tagged with
  ``persona_type`` and ``base_model_version`` for lineage tracking.

- :class:`LoRAInferenceClient` — abstracts the Azure AI Model Inference API,
  resolving the correct adapter ID from the Registry and forwarding it via
  ``extra_body`` on every request so the endpoint loads only the requested
  adapter without disturbing the resident base weights.

- :class:`LoRAOrchestrationRouter` — maps orchestration steps to the
  appropriate adapter, providing the Foundry Agent Service with the information
  it needs to select which LoRA personality to activate.
"""

from AgentOperatingSystem.lora.registry import LoRAAdapterRegistry
from AgentOperatingSystem.lora.inference_client import LoRAInferenceClient
from AgentOperatingSystem.lora.orchestration_router import LoRAOrchestrationRouter

__all__ = [
    "LoRAAdapterRegistry",
    "LoRAInferenceClient",
    "LoRAOrchestrationRouter",
]
