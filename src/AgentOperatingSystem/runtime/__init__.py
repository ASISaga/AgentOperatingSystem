"""
AOS Runtime Infrastructure

This module provides the infrastructure-level runtime support for agents,
including Foundry Agent Service integration with Llama 3.3 70B and LoRA adapters.

The runtime infrastructure is transparent to PurposeDrivenAgent, which remains
pure Microsoft Agent Framework code.
"""

from .agent_runtime_provider import AgentRuntimeProvider, RuntimeConfig

__all__ = [
    "AgentRuntimeProvider",
    "RuntimeConfig",
]
