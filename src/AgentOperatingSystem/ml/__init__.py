"""
AOS ML Module

Machine learning pipeline management for AOS.
Includes DPO (Direct Preference Optimization) for cost-effective reinforcement learning.
"""

from .pipeline import MLPipelineManager

try:
    from .self_learning_system import (
        SelfLearningSystem, LearningEpisode, LearningPattern, AdaptationPlan,
        LearningPhase, LearningFocus, FeedbackType
    )
    SELF_LEARNING_AVAILABLE = True
except ImportError:
    SELF_LEARNING_AVAILABLE = False

try:
    from .dpo_trainer import (
        DPOTrainer, DPOConfig, PreferenceData, PreferenceDataCollector
    )
    DPO_AVAILABLE = True
except ImportError:
    DPO_AVAILABLE = False

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