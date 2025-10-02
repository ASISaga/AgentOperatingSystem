"""
PerpetualAgent for AgentOperatingSystem (AOS)
Now supports ML pipeline operations via ml_pipeline_ops.
"""
from typing import Any, Dict
from .ml_pipeline_ops import trigger_lora_training, run_azure_ml_pipeline, aml_infer

class PerpetualAgent:
    def __init__(self, tools=None, system_message=None, adapter_name=None):
        self.tools = tools or []
        self.system_message = system_message or ""
        self.adapter_name = adapter_name  # e.g., 'ceo', 'cfo', 'coo', etc.

    async def act(self, action: str, params: Dict[str, Any]) -> Any:
        """
        Perform an action. Supports ML pipeline operations.
        """
        # Always inject this agent's adapter_name if not explicitly set in params
        if self.adapter_name and action in ("trigger_lora_training", "aml_infer"):
            if action == "trigger_lora_training":
                for adapter in params.get("adapters", []):
                    if "adapter_name" not in adapter:
                        adapter["adapter_name"] = self.adapter_name
            elif action == "aml_infer":
                params.setdefault("agent_id", self.adapter_name)

        if action == "trigger_lora_training":
            return await trigger_lora_training(params["training_params"], params["adapters"])
        elif action == "run_azure_ml_pipeline":
            return await run_azure_ml_pipeline(
                params["subscription_id"],
                params["resource_group"],
                params["workspace_name"]
            )
        elif action == "aml_infer":
            return await aml_infer(params["agent_id"], params["prompt"])
        else:
            raise ValueError(f"Unknown action: {action}")

    # ...existing code for perpetual operation, error handling, etc...
