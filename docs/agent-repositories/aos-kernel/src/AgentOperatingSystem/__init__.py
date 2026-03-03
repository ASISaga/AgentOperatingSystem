"""AOS Kernel — Agent Operating System Kernel.

All orchestration is managed exclusively by the Foundry Agent Service.

Core components:

- :class:`AgentOperatingSystem` — the kernel entry point
- :class:`KernelConfig` — configuration from environment / Bicep
- :class:`FoundryAgentManager` — agent lifecycle management via Foundry
- :class:`FoundryOrchestrationEngine` — orchestration via Foundry threads/runs
- :class:`FoundryMessageBridge` — bidirectional PDA ↔ Foundry messaging
"""

__version__ = "4.0.0"

from AgentOperatingSystem.agent_operating_system import AgentOperatingSystem
from AgentOperatingSystem.config import KernelConfig
from AgentOperatingSystem.agents import FoundryAgentManager
from AgentOperatingSystem.orchestration import FoundryOrchestrationEngine
from AgentOperatingSystem.messaging import FoundryMessageBridge

__all__ = [
    "AgentOperatingSystem",
    "KernelConfig",
    "FoundryAgentManager",
    "FoundryOrchestrationEngine",
    "FoundryMessageBridge",
]
