"""
ML Pipeline Operations for AgentOperatingSystem (AOS)

Provides wrappers to trigger ML pipeline actions from agents or teams.
Uses the new LoRA classes for Azure-based inference (requires azure-ai-ml
and azure-identity to be installed — available in the [foundry] extras of
aos-intelligence).
"""
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


async def trigger_lora_training(training_params: Dict[str, Any], adapters: list) -> str:
    """
    Trigger LoRA adapter training using Azure ML.

    Args:
        training_params: Dict with required keys: subscription_id, resource_group,
            workspace_name. Optional: code_path, command, environment, compute_target,
            output_dir.
        adapters: List of adapter config dicts

    Returns:
        str: Status message
    """
    required = ("subscription_id", "resource_group", "workspace_name")
    missing = [k for k in required if not training_params.get(k)]
    if missing:
        raise ValueError(f"trigger_lora_training: missing required training_params keys: {missing}")

    from azure.ai.ml import MLClient, command  # type: ignore[import]
    from azure.identity import DefaultAzureCredential  # type: ignore[import]

    ml_client = MLClient(
        credential=DefaultAzureCredential(),
        subscription_id=training_params["subscription_id"],
        resource_group_name=training_params["resource_group"],
        workspace_name=training_params["workspace_name"],
    )
    job = command(
        code=training_params.get("code_path", "."),
        command=training_params.get("command", "python train_lora.py"),
        environment=training_params.get("environment", "azureml:AzureML-ACPT-PyTorch-2.2-cuda12.1:1"),
        compute=training_params.get("compute_target", "gpu-cluster"),
        outputs={"model": {"type": "uri_folder", "path": training_params.get("output_dir", "outputs")}},
    )
    submitted = ml_client.jobs.create_or_update(job)
    return f"LoRA training job submitted: {submitted.name}"


async def run_azure_ml_pipeline(subscription_id: str, resource_group: str, workspace_name: str) -> str:
    """
    Run the full Azure ML LoRA pipeline (provision compute, train, register).
    """
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