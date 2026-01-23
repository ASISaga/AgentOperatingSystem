"""
AOS ML Module

Machine learning pipeline management for AOS.
Includes DPO (Direct Preference Optimization) for cost-effective reinforcement learning.
All ML operations use Llama 3.3 70B as the base model for superior performance.
Includes Azure Foundry Agent Service integration with Llama 3.3 70B and LoRA adapters.
"""

from .pipeline import MLPipelineManager

try:
    SELF_LEARNING_AVAILABLE = True
except ImportError:
    SELF_LEARNING_AVAILABLE = False

try:
    DPO_AVAILABLE = True
except ImportError:
    DPO_AVAILABLE = False

try:
    LORAX_AVAILABLE = True
except ImportError:
    LORAX_AVAILABLE = False

try:
    FOUNDRY_AGENT_SERVICE_AVAILABLE = True
except ImportError:
    FOUNDRY_AGENT_SERVICE_AVAILABLE = False

__all__ = [
    "MLPipelineManager"
]

if SELF_LEARNING_AVAILABLE:
    __all__.extend([
        "SelfLearningSystem", "LearningEpisode", "LearningPattern", "AdaptationPlan",
        "LearningPhase", "LearningFocus", "FeedbackType"
    ])

if DPO_AVAILABLE:
    __all__.extend([
        "DPOTrainer", "DPOConfig", "PreferenceData", "PreferenceDataCollector"
    ])

if LORAX_AVAILABLE:
    __all__.extend([
        "LoRAxServer", "LoRAxConfig", "LoRAxAdapterRegistry", "AdapterInfo"
    ])

if FOUNDRY_AGENT_SERVICE_AVAILABLE:
    __all__.extend([
        "FoundryAgentServiceClient", "FoundryAgentServiceConfig",
        "FoundryResponse", "ThreadInfo"
    ])
