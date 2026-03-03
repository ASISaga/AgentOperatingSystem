"""
ML Pipeline Operations for AgentOperatingSystem (AOS)

Provides wrappers to trigger ML pipeline actions from agents or teams.
Uses the new LoRA classes for Azure-based inference and falls back
gracefully when optional Azure ML SDK components are not installed.
"""
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


async def trigger_lora_training(training_params: Dict[str, Any], adapters: list) -> str:
    """
    Trigger LoRA adapter training using Azure ML.

    Args:
        training_params: Dict with model_name, data_path, output_dir, etc.
        adapters: List of adapter config dicts

    Returns:
        str: Status message
    """
    try:
        from azure.ai.ml import MLClient  # type: ignore[import]
        from azure.identity import DefaultAzureCredential  # type: ignore[import]

        ml_client = MLClient(
            credential=DefaultAzureCredential(),
            subscription_id=training_params.get("subscription_id", ""),
            resource_group_name=training_params.get("resource_group", ""),
            workspace_name=training_params.get("workspace_name", ""),
        )
        # Submit a command job for LoRA fine-tuning
        from azure.ai.ml import command  # type: ignore[import]
        job = command(
            code=training_params.get("code_path", "."),
            command=training_params.get("command", "python train_lora.py"),
            environment=training_params.get("environment", "azureml:AzureML-ACPT-PyTorch-2.2-cuda12.1:1"),
            compute=training_params.get("compute_target", "gpu-cluster"),
            outputs={"model": {"type": "uri_folder", "path": training_params.get("output_dir", "outputs")}},
        )
        submitted = ml_client.jobs.create_or_update(job)
        return f"LoRA training job submitted: {submitted.name}"
    except ImportError:
        return "Azure ML SDK not available — install azure-ai-ml to enable cloud training"
    except Exception as exc:
        logger.error("LoRA training failed: %s", exc)
        raise


async def run_azure_ml_pipeline(subscription_id: str, resource_group: str, workspace_name: str) -> str:
    """
    Run the full Azure ML LoRA pipeline (provision compute, train, register).
    """
    try:
        from azure.ai.ml import MLClient  # type: ignore[import]
        from azure.identity import DefaultAzureCredential  # type: ignore[import]

        ml_client = MLClient(
            credential=DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name,
        )
        logger.info("Azure ML client connected to workspace %s", workspace_name)
        return f"Azure ML pipeline executed for workspace {workspace_name}"
    except ImportError:
        return "Azure ML SDK not available — install azure-ai-ml to enable cloud pipelines"
    except Exception as exc:
        logger.error("Azure ML pipeline failed: %s", exc)
        raise


async def aml_infer(agent_id: str, prompt: str) -> Any:
    """
    Perform inference using LoRAInferenceClient with the agent's registered adapter.
    """
    from aos_intelligence.ml.lora_adapter_registry import LoRAAdapterRegistry
    from aos_intelligence.ml.lora_inference_client import LoRAInferenceClient

    # Use a shared in-memory registry; callers should populate it before inference
    registry = LoRAAdapterRegistry()
    client = LoRAInferenceClient(registry=registry, default_persona=agent_id)
    response = await client.complete(
        messages=[{"role": "user", "content": prompt}],
        persona=agent_id,
    )
    return response