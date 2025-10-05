"""
PerpetualAgent for AgentOperatingSystem (AOS)
Now supports ML pipeline operations via ML pipeline components.
"""
from typing import Any, Dict
from ..ml.pipeline_ops import trigger_lora_training, run_azure_ml_pipeline, aml_infer
from .base import BaseAgent

class PerpetualAgent(BaseAgent):
    """
    A perpetual agent that can perform continuous operations and ML pipeline tasks.
    """
    
    def __init__(self, tools=None, system_message=None, adapter_name=None):
        super().__init__(
            agent_id=f"perpetual_{adapter_name}" if adapter_name else "perpetual_agent",
            agent_type="perpetual"
        )
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

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with perpetual operation capabilities.
        """
        try:
            action = task.get("action")
            params = task.get("params", {})
            
            if action:
                result = await self.act(action, params)
                return {"status": "success", "result": result}
            else:
                return {"status": "error", "error": "No action specified"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}