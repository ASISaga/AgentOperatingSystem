"""AOS Kernel — Agent Operating System Kernel.

All orchestration is managed exclusively by the Foundry Agent Service.

Core components:

- :class:`AgentOperatingSystem` — the kernel entry point
- :class:`KernelConfig` — configuration from environment / Bicep
- :class:`FoundryAgentManager` — agent lifecycle management via Foundry
- :class:`FoundryOrchestrationEngine` — orchestration via Foundry threads/runs
- :class:`FoundryMessageBridge` — bidirectional PDA ↔ Foundry messaging

Multi-LoRA components:

- :class:`LoRAAdapterRegistry` — adapter registration in Foundry Model Registry
- :class:`LoRAInferenceClient` — high-level inference client with adapter routing
- :class:`LoRAOrchestrationRouter` — maps orchestration steps to LoRA adapters
"""

__version__ = "5.0.0"

from AgentOperatingSystem.agent_operating_system import AgentOperatingSystem
from AgentOperatingSystem.config import KernelConfig
from AgentOperatingSystem.agents import FoundryAgentManager
from AgentOperatingSystem.orchestration import FoundryOrchestrationEngine
from AgentOperatingSystem.messaging import FoundryMessageBridge
from AgentOperatingSystem.lora import LoRAAdapterRegistry, LoRAInferenceClient, LoRAOrchestrationRouter

__all__ = [
    "AgentOperatingSystem",
    "KernelConfig",
    "FoundryAgentManager",
    "FoundryOrchestrationEngine",
    "FoundryMessageBridge",
    "LoRAAdapterRegistry",
    "LoRAInferenceClient",
    "LoRAOrchestrationRouter",
]
