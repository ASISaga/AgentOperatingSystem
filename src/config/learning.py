from dataclasses import dataclass, field
from typing import Dict, Any
import os

@dataclass
class LearningConfig:
    """Configuration for AOS learning system"""
    knowledge_base_path: str = "knowledge"
    enable_knowledge_management: bool = True
    enable_rag: bool = True
    vector_db_host: str = "localhost"
    vector_db_port: int = 8000
    top_k_snippets: int = 5
    min_similarity: float = 0.7
    enable_interaction_learning: bool = True
    learning_window_days: int = 30
    min_interactions_for_pattern: int = 10
    feedback_weight: float = 0.7
    enable_learning_pipeline: bool = True
    learning_cycle_hours: int = 24
    knowledge_update_threshold: float = 0.8
    cross_domain_sharing: bool = True
    auto_optimization: bool = True
    auto_start: bool = True
    knowledge: Dict[str, Any] = field(default_factory=dict)
    rag: Dict[str, Any] = field(default_factory=lambda: {
        "vector_db_host": "localhost",
        "vector_db_port": 8000,
        "top_k_snippets": 5,
        "min_similarity": 0.7
    })
    interaction: Dict[str, Any] = field(default_factory=lambda: {
        "learning_window_days": 30,
        "min_interactions_for_pattern": 10,
        "feedback_weight": 0.7
    })
    pipeline: Dict[str, Any] = field(default_factory=lambda: {
        "learning_cycle_hours": 24,
        "knowledge_update_threshold": 0.8,
        "cross_domain_sharing": True,
        "auto_optimization": True,
        "auto_start": True
    })

    @classmethod
    def from_env(cls):
        return cls(
            knowledge_base_path=os.getenv("AOS_KNOWLEDGE_BASE_PATH", "knowledge"),
            enable_knowledge_management=os.getenv("AOS_ENABLE_KNOWLEDGE", "true").lower() == "true",
            enable_rag=os.getenv("AOS_ENABLE_RAG", "true").lower() == "true",
            vector_db_host=os.getenv("AOS_VECTOR_DB_HOST", "localhost"),
            vector_db_port=int(os.getenv("AOS_VECTOR_DB_PORT", "8000")),
            top_k_snippets=int(os.getenv("AOS_TOP_K_SNIPPETS", "5")),
            min_similarity=float(os.getenv("AOS_MIN_SIMILARITY", "0.7")),
            enable_interaction_learning=os.getenv("AOS_ENABLE_INTERACTION_LEARNING", "true").lower() == "true",
            learning_window_days=int(os.getenv("AOS_LEARNING_WINDOW_DAYS", "30")),
            enable_learning_pipeline=os.getenv("AOS_ENABLE_LEARNING_PIPELINE", "true").lower() == "true",
            learning_cycle_hours=int(os.getenv("AOS_LEARNING_CYCLE_HOURS", "24")),
            cross_domain_sharing=os.getenv("AOS_CROSS_DOMAIN_SHARING", "true").lower() == "true",
            auto_optimization=os.getenv("AOS_AUTO_OPTIMIZATION", "true").lower() == "true"
        )
