"""
AOS Configuration Management

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
            monitoring_config=MonitoringConfig.from_env()
        )
    
    @classmethod
    def from_file(cls, config_path: str):
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Convert nested dicts to dataclass instances
        if 'message_bus_config' in config_data:
            config_data['message_bus_config'] = MessageBusConfig(**config_data['message_bus_config'])
        if 'decision_config' in config_data:
            config_data['decision_config'] = DecisionConfig(**config_data['decision_config'])
        if 'orchestration_config' in config_data:
            config_data['orchestration_config'] = OrchestrationConfig(**config_data['orchestration_config'])
        if 'storage_config' in config_data:
            config_data['storage_config'] = StorageConfig(**config_data['storage_config'])
        if 'monitoring_config' in config_data:
            config_data['monitoring_config'] = MonitoringConfig(**config_data['monitoring_config'])
        
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
            "custom_config": self.custom_config
        }
    
    def save_to_file(self, config_path: str):
        """Save configuration to JSON file"""
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# Default configuration instance
default_config = AOSConfig.from_env()

# Legacy configurations for backward compatibility
# These will be moved to proper configuration management

# Azure OpenAI Configuration (for fine-tuning)
azure_openai_model = "gpt-4-turbo-2024-04-09"  # GPT-4.1 equivalent
azure_openai_endpoint = ""  # Set your Azure OpenAI endpoint
azure_openai_key = ""  # Set your Azure OpenAI key
azure_openai_api_version = "2024-02-01"

# Amazon Bedrock Configuration (for Claude Sonnet 4)
aws_region = "us-east-1"  # Or your preferred region
aws_access_key_id = ""  # Set your AWS access key
aws_secret_access_key = ""  # Set your AWS secret key
bedrock_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"  # Claude Sonnet 4

# Legacy model for backward compatibility
model = azure_openai_model