"""
AOS Core Configuration Management

Centralized configuration for the Agent Operating System.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class MessageBusConfig:
    """Configuration for AOS message bus"""
    max_queue_size: int = 10000
    message_timeout_seconds: int = 30
    enable_persistence: bool = True
    connection_string: Optional[str] = None
    
    @classmethod
    def from_env(cls):
        return cls(
            max_queue_size=int(os.getenv("AOS_MESSAGE_QUEUE_SIZE", "10000")),
            message_timeout_seconds=int(os.getenv("AOS_MESSAGE_TIMEOUT", "30")),
            enable_persistence=os.getenv("AOS_MESSAGE_PERSISTENCE", "true").lower() == "true",
            connection_string=os.getenv("AOS_MESSAGE_BUS_CONNECTION_STRING")
        )


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


@dataclass
class OrchestrationConfig:
    """Configuration for AOS orchestration engine"""
    max_concurrent_workflows: int = 100
    workflow_timeout_seconds: int = 3600
    enable_workflow_persistence: bool = True
    retry_max_attempts: int = 3
    retry_delay_seconds: int = 5
    
    @classmethod
    def from_env(cls):
        return cls(
            max_concurrent_workflows=int(os.getenv("AOS_MAX_WORKFLOWS", "100")),
            workflow_timeout_seconds=int(os.getenv("AOS_WORKFLOW_TIMEOUT", "3600")),
            enable_workflow_persistence=os.getenv("AOS_WORKFLOW_PERSISTENCE", "true").lower() == "true",
            retry_max_attempts=int(os.getenv("AOS_RETRY_MAX_ATTEMPTS", "3")),
            retry_delay_seconds=int(os.getenv("AOS_RETRY_DELAY", "5"))
        )


@dataclass
class StorageConfig:
    """Configuration for AOS storage"""
    storage_type: str = "file"  # file, azure_blob, s3
    base_path: str = "data"
    connection_string: Optional[str] = None
    container_name: str = "aos-storage"
    enable_encryption: bool = True
    
    @classmethod
    def from_env(cls):
        return cls(
            storage_type=os.getenv("AOS_STORAGE_TYPE", "file"),
            base_path=os.getenv("AOS_STORAGE_PATH", "data"),
            connection_string=os.getenv("AOS_STORAGE_CONNECTION_STRING"),
            container_name=os.getenv("AOS_STORAGE_CONTAINER", "aos-storage"),
            enable_encryption=os.getenv("AOS_ENABLE_ENCRYPTION", "true").lower() == "true"
        )


@dataclass
class MonitoringConfig:
    """Configuration for AOS monitoring"""
    enable_metrics: bool = True
    metrics_interval_seconds: int = 60
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_telemetry: bool = True
    telemetry_endpoint: Optional[str] = None
    
    @classmethod
    def from_env(cls):
        return cls(
            enable_metrics=os.getenv("AOS_ENABLE_METRICS", "true").lower() == "true",
            metrics_interval_seconds=int(os.getenv("AOS_METRICS_INTERVAL", "60")),
            enable_logging=os.getenv("AOS_ENABLE_LOGGING", "true").lower() == "true",
            log_level=os.getenv("AOS_LOG_LEVEL", "INFO"),
            enable_telemetry=os.getenv("AOS_ENABLE_TELEMETRY", "true").lower() == "true",
            telemetry_endpoint=os.getenv("AOS_TELEMETRY_ENDPOINT")
        )


@dataclass 
class MLConfig:
    """Configuration for AOS ML pipeline"""
    enable_training: bool = True
    model_storage_path: str = "models"
    training_data_path: str = "training_data"
    max_training_jobs: int = 5
    default_model_type: str = "lora"
    
    @classmethod
    def from_env(cls):
        return cls(
            enable_training=os.getenv("AOS_ENABLE_ML_TRAINING", "true").lower() == "true",
            model_storage_path=os.getenv("AOS_MODEL_STORAGE_PATH", "models"),
            training_data_path=os.getenv("AOS_TRAINING_DATA_PATH", "training_data"),
            max_training_jobs=int(os.getenv("AOS_MAX_TRAINING_JOBS", "5")),
            default_model_type=os.getenv("AOS_DEFAULT_MODEL_TYPE", "lora")
        )


@dataclass
class AuthConfig:
    """Configuration for AOS authentication"""
    enable_auth: bool = True
    auth_provider: str = "azure_b2c"  # azure_b2c, oauth, jwt
    auth_endpoint: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    
    @classmethod
    def from_env(cls):
        return cls(
            enable_auth=os.getenv("AOS_ENABLE_AUTH", "true").lower() == "true",
            auth_provider=os.getenv("AOS_AUTH_PROVIDER", "azure_b2c"),
            auth_endpoint=os.getenv("AOS_AUTH_ENDPOINT"),
            client_id=os.getenv("AOS_AUTH_CLIENT_ID"),
            client_secret=os.getenv("AOS_AUTH_CLIENT_SECRET")
        )


@dataclass
class LearningConfig:
    """Configuration for AOS learning system"""
    # Knowledge management
    knowledge_base_path: str = "knowledge"
    enable_knowledge_management: bool = True
    
    # RAG configuration
    enable_rag: bool = True
    vector_db_host: str = "localhost"
    vector_db_port: int = 8000
    top_k_snippets: int = 5
    min_similarity: float = 0.7
    
    # Interaction learning
    enable_interaction_learning: bool = True
    learning_window_days: int = 30
    min_interactions_for_pattern: int = 10
    feedback_weight: float = 0.7
    
    # Learning pipeline
    enable_learning_pipeline: bool = True
    learning_cycle_hours: int = 24
    knowledge_update_threshold: float = 0.8
    cross_domain_sharing: bool = True
    auto_optimization: bool = True
    auto_start: bool = True
    
    # Sub-configurations
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


@dataclass
class AOSConfig:
    """Master configuration for Agent Operating System"""
    environment: str = "development"
    debug: bool = False
    
    # Component configurations
    message_bus_config: MessageBusConfig = field(default_factory=MessageBusConfig)
    decision_config: DecisionConfig = field(default_factory=DecisionConfig)
    orchestration_config: OrchestrationConfig = field(default_factory=OrchestrationConfig)
    storage_config: StorageConfig = field(default_factory=StorageConfig)
    monitoring_config: MonitoringConfig = field(default_factory=MonitoringConfig)
    ml_config: MLConfig = field(default_factory=MLConfig)
    auth_config: AuthConfig = field(default_factory=AuthConfig)
    learning_config: LearningConfig = field(default_factory=LearningConfig)
    
    # Additional configuration
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
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
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Convert nested dicts to dataclass instances
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
        """Convert configuration to dictionary"""
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
        """Save configuration to JSON file"""
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# Default configuration instance
default_config = AOSConfig.from_env()