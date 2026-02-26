"""
IMLService - Abstract ML service interface for LoRA training and inference.

PurposeDrivenAgent uses this interface for all ML pipeline operations so that
the core agent logic remains decoupled from a specific ML backend (Azure ML,
local, mock, etc.).

Implement :class:`IMLService` and pass it to the agent's ``act()`` method or
configure it via the ``config`` dict under the ``"ml_service"`` key to plug in
your own training / inference backend.

Example - mock service for tests::

    from purpose_driven_agent.ml_interface import IMLService

    class MockMLService(IMLService):
        async def trigger_lora_training(self, training_params, adapters):
            return "training-run-mock-001"

        async def run_pipeline(self, subscription_id, resource_group, workspace_name):
            return "pipeline-mock-001"

        async def infer(self, agent_id, prompt):
            return {"text": f"Mock response for {agent_id}: {prompt}"}

Example - Azure ML backend::

    from purpose_driven_agent.ml_interface import IMLService
    from azure_ml_lora import LoRATrainer, UnifiedMLManager

    class AzureMLService(IMLService):
        async def trigger_lora_training(self, training_params, adapters):
            trainer = LoRATrainer(
                model_name=training_params["model_name"],
                data_path=training_params["data_path"],
                output_dir=training_params["output_dir"],
                adapters=adapters,
            )
            trainer.train()
            return f"Training complete, adapters saved to {training_params['output_dir']}"

        async def run_pipeline(self, subscription_id, resource_group, workspace_name):
            mgr = UnifiedMLManager(subscription_id, resource_group, workspace_name)
            return await mgr.run_pipeline()

        async def infer(self, agent_id, prompt):
            mgr = UnifiedMLManager(...)
            return await mgr.infer(agent_id, prompt)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IMLService(ABC):
    """
    Abstract interface for ML pipeline operations used by PurposeDrivenAgent.

    Implementors supply the actual compute backend (Azure ML, local, mock…).
    The default no-op implementation raises :class:`NotImplementedError` for
    all methods, making missing implementations obvious at call time.
    """

    @abstractmethod
    async def trigger_lora_training(
        self,
        training_params: Dict[str, Any],
        adapters: List[Dict[str, Any]],
    ) -> str:
        """
        Trigger LoRA adapter training.

        Args:
            training_params: Dictionary with at minimum:

                - ``model_name`` (str): base model identifier.
                - ``data_path`` (str): path to training data.
                - ``output_dir`` (str): where to write trained adapters.

            adapters: List of adapter config dicts, each containing at minimum:

                - ``adapter_name`` (str): logical adapter identifier.

        Returns:
            Human-readable status / run-ID string.
        """

    @abstractmethod
    async def run_pipeline(
        self,
        subscription_id: str,
        resource_group: str,
        workspace_name: str,
    ) -> str:
        """
        Execute the full Azure ML pipeline.

        Args:
            subscription_id: Azure subscription ID.
            resource_group: Azure resource group name.
            workspace_name: Azure ML workspace name.

        Returns:
            Pipeline run ID or status string.
        """

    @abstractmethod
    async def infer(self, agent_id: str, prompt: str) -> Dict[str, Any]:
        """
        Run inference for the given agent / adapter.

        Args:
            agent_id: Agent (adapter) identifier used to select the LoRA adapter.
            prompt: Input prompt.

        Returns:
            Inference result dict; at minimum ``{"text": str}``.
        """


class NoOpMLService(IMLService):
    """
    No-operation implementation of :class:`IMLService`.

    Raises :class:`NotImplementedError` for every method, which surfaces
    clearly when ML operations are attempted without a real backend.
    Useful as a placeholder when an agent does not require ML operations.
    """

    async def trigger_lora_training(
        self,
        training_params: Dict[str, Any],
        adapters: List[Dict[str, Any]],
    ) -> str:
        raise NotImplementedError(
            "ML backend not configured. Provide an IMLService implementation."
        )

    async def run_pipeline(
        self,
        subscription_id: str,
        resource_group: str,
        workspace_name: str,
    ) -> str:
        raise NotImplementedError(
            "ML backend not configured. Provide an IMLService implementation."
        )

    async def infer(self, agent_id: str, prompt: str) -> Dict[str, Any]:
        raise NotImplementedError(
            "ML backend not configured. Provide an IMLService implementation."
        )
