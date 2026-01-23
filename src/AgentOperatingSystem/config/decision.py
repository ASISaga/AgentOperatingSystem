import os
from dataclasses import dataclass


@dataclass
class DecisionConfig:
    """Configuration for AOS decision engine"""
    principles_path: str = "configs/principles.json"
    decision_tree_path: str = "configs/decision_tree.json"
    adapters_path: str = "configs/adapters.json"
    enable_ml_scoring: bool = True
    default_scoring_method: str = "weighted"

    @classmethod
    def from_env(cls):
        return cls(
            principles_path=os.getenv("AOS_PRINCIPLES_PATH", "configs/principles.json"),
            decision_tree_path=os.getenv("AOS_DECISION_TREE_PATH", "configs/decision_tree.json"),
            adapters_path=os.getenv("AOS_ADAPTERS_PATH", "configs/adapters.json"),
            enable_ml_scoring=os.getenv("AOS_ENABLE_ML_SCORING", "true").lower() == "true",
            default_scoring_method=os.getenv("AOS_SCORING_METHOD", "weighted")
        )
