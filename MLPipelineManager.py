"""
MLPipelineManager for AgentOperatingSystem (AOS)
Centralized management of the ML pipeline for all agents.
"""
from typing import Any, Dict, List
from .ml_pipeline_ops import trigger_lora_training, run_azure_ml_pipeline, aml_infer

class MLPipelineManager:
    """
    Central manager for ML pipeline operations in AOS.
    Coordinates training, deployment, monitoring, and adapter management for all agents.
    """
    def __init__(self):
        self.active_adapters: Dict[str, Dict[str, Any]] = {}  # adapter_name -> config

    async def train_adapter(self, agent_role: str, training_params: Dict[str, Any], adapter_config: Dict[str, Any]) -> str:
        """
        Train a LoRA adapter for a specific agent role.
        """
        adapter_config = dict(adapter_config)
        adapter_config["adapter_name"] = agent_role
        result = await trigger_lora_training(training_params, [adapter_config])
        self.active_adapters[agent_role] = adapter_config
        return result

    async def run_pipeline(self, subscription_id: str, resource_group: str, workspace_name: str) -> str:
        """
        Run the full Azure ML pipeline (provision, train, register).
        """
        return await run_azure_ml_pipeline(subscription_id, resource_group, workspace_name)

    async def infer(self, agent_role: str, prompt: str) -> Any:
        """
        Perform inference for a specific agent role using its adapter.
        """
        return await aml_infer(agent_role, prompt)

    def list_adapters(self) -> List[str]:
        """
        List all registered/active adapters.
        """
        return list(self.active_adapters.keys())

    def get_adapter_config(self, agent_role: str) -> Dict[str, Any]:
        """
        Get the config for a specific adapter.
        """
        return self.active_adapters.get(agent_role, {})
