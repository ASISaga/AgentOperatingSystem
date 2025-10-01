"""
AOS ML Module

Machine learning pipeline management for AOS.
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

__all__ = [
    "MLPipelineManager"
]

if SELF_LEARNING_AVAILABLE:
    __all__.extend([
        "SelfLearningSystem", "LearningEpisode", "LearningPattern", "AdaptationPlan",
        "LearningPhase", "LearningFocus", "FeedbackType"
    ])