from dataclasses import dataclass, field
from typing import Dict, Any
import os
import json
from .messagebus import MessageBusConfig
from .decision import DecisionConfig
from .orchestration import OrchestrationConfig
from .storage import StorageConfig
from .monitoring import MonitoringConfig
from .ml import MLConfig
from .auth import AuthConfig
from .learning import LearningConfig

@dataclass
class AOSConfig:
    """Master configuration for Agent Operating System"""
    environment: str = "development"
    debug: bool = False
    message_bus_config: MessageBusConfig = field(default_factory=MessageBusConfig)
    decision_config: DecisionConfig = field(default_factory=DecisionConfig)
    orchestration_config: OrchestrationConfig = field(default_factory=OrchestrationConfig)
    storage_config: StorageConfig = field(default_factory=StorageConfig)
    monitoring_config: MonitoringConfig = field(default_factory=MonitoringConfig)
    ml_config: MLConfig = field(default_factory=MLConfig)
    auth_config: AuthConfig = field(default_factory=AuthConfig)
    learning_config: LearningConfig = field(default_factory=LearningConfig)
    custom_config: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls):
        return cls(
            environment=os.getenv("AOS_ENVIRONMENT", "development"),
            debug=os.getenv("AOS_DEBUG", "false").lower() == "true",
            message_bus_config=MessageBusConfig.from_env(),
            decision_config=DecisionConfig.from_env(),
            orchestration_config=OrchestrationConfig.from_env(),
            storage_config=StorageConfig.from_env(),
            monitoring_config=MonitoringConfig.from_env(),
            ml_config=MLConfig.from_env(),
            auth_config=AuthConfig.from_env(),
            learning_config=LearningConfig.from_env()
        )

    @classmethod
    def from_file(cls, config_path: str):
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        config_classes = {
            'message_bus_config': MessageBusConfig,
            'decision_config': DecisionConfig,
            'orchestration_config': OrchestrationConfig,
            'storage_config': StorageConfig,
            'monitoring_config': MonitoringConfig,
            'ml_config': MLConfig,
            'auth_config': AuthConfig,
            'learning_config': LearningConfig
        }
        for key, config_class in config_classes.items():
            if key in config_data:
                config_data[key] = config_class(**config_data[key])
        return cls(**config_data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment": self.environment,
            "debug": self.debug,
            "message_bus_config": self.message_bus_config.__dict__,
            "decision_config": self.decision_config.__dict__,
            "orchestration_config": self.orchestration_config.__dict__,
            "storage_config": self.storage_config.__dict__,
            "monitoring_config": self.monitoring_config.__dict__,
            "ml_config": self.ml_config.__dict__,
            "auth_config": self.auth_config.__dict__,
            "learning_config": self.learning_config.__dict__,
            "custom_config": self.custom_config
        }

    def save_to_file(self, config_path: str):
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

# Default configuration instance
default_config = AOSConfig.from_env()
