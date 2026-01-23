"""
ML Pipeline Operations for AgentOperatingSystem (AOS)
Provides wrappers to trigger ML pipeline actions from agents or teams.
"""
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

# Import the refactored ML pipeline from FineTunedLLM
try:
    from azure_ml_lora import MLManager, LoRATrainer, LoRAPipeline, UnifiedMLManager
    ML_AVAILABLE = True
except ImportError:
    # Fallback for local dev if not installed as package
    try:
        import sys, os
        aos_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../FineTunedLLM'))
        if aos_root not in sys.path:
            sys.path.insert(0, aos_root)
        from azure_ml_lora import MLManager, LoRATrainer, LoRAPipeline, UnifiedMLManager
        ML_AVAILABLE = True
    except ImportError:
        logger.warning("Azure ML components not available")
        ML_AVAILABLE = False

# Example: Trigger LoRA training from an agent
async def trigger_lora_training(training_params: Dict[str, Any], adapters: list) -> str:
    """
    Trigger LoRA adapter training using the ML pipeline.
    Args:
        training_params: Dict with model_name, data_path, output_dir, etc.
        adapters: List of adapter config dicts
    Returns:
        str: Status message
    """
    if not ML_AVAILABLE:
        return "ML components not available"

    trainer = LoRATrainer(
        model_name=training_params["model_name"],
        data_path=training_params["data_path"],
        output_dir=training_params["output_dir"],
        adapters=adapters
    )
    trainer.train()
    return f"LoRA training complete. Adapters saved to {training_params['output_dir']}"

# Example: Run the full Azure ML pipeline
async def run_azure_ml_pipeline(subscription_id: str, resource_group: str, workspace_name: str) -> str:
    """
    Run the full Azure ML LoRA pipeline (provision compute, train, register).
    """
    if not ML_AVAILABLE:
        return "ML components not available"

    pipeline = LoRAPipeline(subscription_id, resource_group, workspace_name)
    pipeline.run()
    return "Azure ML LoRA pipeline executed."

# Example: Inference via UnifiedMLManager
async def aml_infer(agent_id: str, prompt: str) -> Any:
    """
    Perform inference using UnifiedMLManager endpoints.
    """
    if not ML_AVAILABLE:
        return {"error": "ML components not available"}

    manager = UnifiedMLManager()
    return await manager.aml_infer(agent_id, prompt)
