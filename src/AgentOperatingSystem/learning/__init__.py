"""
AOS Learning Module

Provides self-learning capabilities for all agents in the Agent Operating System.
Includes knowledge management, RAG (Retrieval-Augmented Generation),
interaction learning, and continuous improvement features.
"""

from .domain_expert import DomainExpert
from .interaction_learner import InteractionLearner
from .knowledge_manager import KnowledgeManager
from .learning_pipeline import LearningPipeline
from .rag_engine import RAGEngine

# Self-learning agent implementations (moved from agents module)
from .self_learning_agents import SelfLearningAgent, SelfLearningStatefulAgent
from .self_learning_mixin import SelfLearningMixin

__all__ = [
    "KnowledgeManager",
    "RAGEngine",
    "InteractionLearner",
    "SelfLearningMixin",
    "DomainExpert",
    "LearningPipeline",
    "SelfLearningAgent",
    "SelfLearningStatefulAgent",
]
