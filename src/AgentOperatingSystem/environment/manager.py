"""
AOS Environment Manager

Unified environment variable and configuration management for AOS.
"""

import os
import logging
from typing import Any, Optional, Dict, List


class EnvironmentError(Exception):
    """Environment configuration errors"""
    pass


class EnvironmentManager:
    """
    Unified environment manager for AOS.

    Provides centralized access to environment variables and configuration
    with validation, fallbacks, and type conversion.
    """

    def __init__(self):
        self.logger = logging.getLogger("AOS.EnvironmentManager")
        self._cache = {}

    def get(self, key: str, default: Any = None, required: bool = False,
            env_type: type = str) -> Any:
        """
        Get environment variable with type conversion and validation.

        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether the variable is required
            env_type: Type to convert to (str, int, bool, float)

        Returns:
            Environment variable value

        Raises:
            EnvironmentError: If required variable is missing or conversion fails
        """
        # Check cache first
        cache_key = f"{key}_{env_type.__name__}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        value = os.environ.get(key, default)

        if required and value is None:
            raise EnvironmentError(f"Required environment variable '{key}' is not set")

        if value is None:
            return None

        # Convert type
        try:
            if env_type == bool:
                converted_value = str(value).lower() in ('true', '1', 'yes', 'on')
            elif env_type == int:
                converted_value = int(value)
            elif env_type == float:
                converted_value = float(value)
            else:
                converted_value = str(value)

            # Cache the result
            self._cache[cache_key] = converted_value
            return converted_value

        except (ValueError, TypeError) as e:
            raise EnvironmentError(f"Failed to convert '{key}' to {env_type.__name__}: {e}")

    def require_any(self, keys: List[str], error_message: str = None) -> str:
        """
        Require at least one of the specified environment variables.

        Args:
            keys: List of environment variable names
            error_message: Custom error message

        Returns:
            First found environment variable value

        Raises:
            EnvironmentError: If none of the variables are set
        """
        for key in keys:
            value = os.environ.get(key)
            if value:
                self.logger.debug(f"Found environment variable: {key}")
                return value

        error_msg = error_message or f"At least one of these environment variables is required: {', '.join(keys)}"
        raise EnvironmentError(error_msg)

    def get_azure_connection_string(self, service: str = "storage") -> str:
        """
        Get Azure connection string with fallback patterns.

        Args:
            service: Azure service name (storage, tables, queues, servicebus)

        Returns:
            Connection string
        """
        patterns = {
            "storage": [
                "AzureWebJobsStorage",
                "AZURE_STORAGE_CONNECTION_STRING",
                "STORAGE_CONNECTION_STRING"
            ],
            "tables": [
                "AZURE_TABLES_CONNECTION_STRING",
                "AzureWebJobsStorage",
                "AZURE_STORAGE_CONNECTION_STRING"
            ],
            "queues": [
                "AZURE_QUEUES_CONNECTION_STRING",
                "AzureWebJobsStorage",
                "AZURE_STORAGE_CONNECTION_STRING"
            ],
            "servicebus": [
                "AZURE_SERVICE_BUS_CONNECTION_STRING",
                "SERVICE_BUS_CONNECTION_STRING"
            ],
            "cosmos": [
                "AZURE_COSMOS_CONNECTION_STRING",
                "COSMOS_CONNECTION_STRING"
            ]
        }

        keys = patterns.get(service, [f"AZURE_{service.upper()}_CONNECTION_STRING"])
        return self.require_any(keys, f"Missing Azure {service} connection string")

    def get_ml_config(self) -> Dict[str, Any]:
        """Get Azure ML configuration"""
        return {
            "subscription_id": self.get("AZURE_ML_SUBSCRIPTION_ID"),
            "resource_group": self.get("AZURE_ML_RESOURCE_GROUP"),
            "workspace_name": self.get("AZURE_ML_WORKSPACE_NAME"),
            "tenant_id": self.get("AZURE_TENANT_ID"),
            "client_id": self.get("AZURE_CLIENT_ID"),
            "client_secret": self.get("AZURE_CLIENT_SECRET"),
            "endpoint": self.get("AZURE_ML_ENDPOINT"),
            "key": self.get("AZURE_ML_KEY")
        }

    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration"""
        return {
            "api_key": self.get("OPENAI_API_KEY"),
            "azure_endpoint": self.get("AZURE_OPENAI_ENDPOINT"),
            "azure_key": self.get("AZURE_OPENAI_KEY"),
            "api_version": self.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            "model": self.get("AZURE_OPENAI_MODEL", "gpt-4"),
            "deployment": self.get("AZURE_OPENAI_DEPLOYMENT")
        }

    def get_database_config(self, db_type: str = "default") -> Dict[str, Any]:
        """Get database configuration"""
        if db_type == "postgresql":
            return {
                "host": self.get("POSTGRES_HOST", "localhost"),
                "port": self.get("POSTGRES_PORT", 5432, env_type=int),
                "database": self.get("POSTGRES_DB"),
                "username": self.get("POSTGRES_USER"),
                "password": self.get("POSTGRES_PASSWORD"),
                "connection_string": self.get("POSTGRES_CONNECTION_STRING")
            }
        elif db_type == "mongodb":
            return {
                "host": self.get("MONGODB_HOST", "localhost"),
                "port": self.get("MONGODB_PORT", 27017, env_type=int),
                "database": self.get("MONGODB_DB"),
                "username": self.get("MONGODB_USER"),
                "password": self.get("MONGODB_PASSWORD"),
                "connection_string": self.get("MONGODB_CONNECTION_STRING")
            }
        else:
            # Default to environment-based configuration
            return {
                "connection_string": self.get("DATABASE_CONNECTION_STRING"),
                "type": self.get("DATABASE_TYPE", "sqlite"),
                "host": self.get("DATABASE_HOST"),
                "port": self.get("DATABASE_PORT", env_type=int),
                "name": self.get("DATABASE_NAME"),
                "username": self.get("DATABASE_USER"),
                "password": self.get("DATABASE_PASSWORD")
            }

    def get_auth_config(self) -> Dict[str, Any]:
        """Get authentication configuration"""
        return {
            "jwt_secret": self.get("JWT_SECRET"),
            "jwt_algorithm": self.get("JWT_ALGORITHM", "HS256"),
            "jwt_expiration": self.get("JWT_EXPIRATION_HOURS", 24, env_type=int),
            "azure_b2c_tenant": self.get("B2C_TENANT"),
            "azure_b2c_policy": self.get("B2C_POLICY"),
            "azure_b2c_client_id": self.get("B2C_CLIENT_ID"),
            "azure_b2c_client_secret": self.get("B2C_CLIENT_SECRET"),
            "linkedin_client_id": self.get("LINKEDIN_CLIENT_ID"),
            "linkedin_client_secret": self.get("LINKEDIN_CLIENT_SECRET"),
            "linkedin_redirect_uri": self.get("LINKEDIN_REDIRECT_URI")
        }

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "level": self.get("LOG_LEVEL", "INFO"),
            "format": self.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            "file": self.get("LOG_FILE"),
            "max_bytes": self.get("LOG_MAX_BYTES", 10485760, env_type=int),  # 10MB
            "backup_count": self.get("LOG_BACKUP_COUNT", 3, env_type=int)
        }

    def validate_required_vars(self, required_vars: List[str]) -> List[str]:
        """
        Validate that required environment variables are set.

        Args:
            required_vars: List of required environment variable names

        Returns:
            List of missing variables
        """
        missing = []
        for var in required_vars:
            if not os.environ.get(var):
                missing.append(var)

        if missing:
            self.logger.warning(f"Missing required environment variables: {missing}")

        return missing

    def get_all_aos_vars(self) -> Dict[str, str]:
        """Get all AOS-related environment variables"""
        aos_vars = {}

        for key, value in os.environ.items():
            if key.startswith(('AOS_', 'AZURE_', 'OPENAI_', 'B2C_', 'LINKEDIN_')):
                # Don't expose sensitive values in logs
                if any(sensitive in key.lower() for sensitive in ['secret', 'key', 'password', 'token']):
                    aos_vars[key] = "***"
                else:
                    aos_vars[key] = value

        return aos_vars

    def set_defaults(self, defaults: Dict[str, str]):
        """
        Set default environment variables if not already set.

        Args:
            defaults: Dictionary of default values
        """
        for key, value in defaults.items():
            if key not in os.environ:
                os.environ[key] = value
                self.logger.debug(f"Set default environment variable: {key}")

    def get_ml_config(self) -> Dict[str, Any]:
        """
        Get Azure ML configuration.
        Enhanced from old environment.py functionality.
        """
        return {
            "subscription_id": self.get("AZURESUBSCRIPTION_ID"),
            "resource_group": self.get("AZURERESOURCEGROUP"),
            "workspace": self.get("AZUREML_WORKSPACE"),
            "pipeline_name": self.get("PIPELINEENDPOINT_NAME"),
            "ml_url": self.get("MLENDPOINT_URL"),
            "ml_key": self.get("MLENDPOINT_KEY")
        }

    def get_agent_endpoints(self) -> Dict[str, Dict[str, str]]:
        """
        Get agent endpoint configurations.
        Enhanced from old environment.py functionality.
        """
        return {
            "cmo": {
                "scoring_uri": self.get("AML_CMO_SCORING_URI", ""),
                "key": self.get("AML_CMO_KEY", "")
            },
            "cfo": {
                "scoring_uri": self.get("AML_CFO_SCORING_URI", ""),
                "key": self.get("AML_CFO_KEY", "")
            },
            "cto": {
                "scoring_uri": self.get("AML_CTO_SCORING_URI", ""),
                "key": self.get("AML_CTO_KEY", "")
            },
            "ceo": {
                "scoring_uri": self.get("AML_CEO_SCORING_URI", ""),
                "key": self.get("AML_CEO_KEY", "")
            },
            "coo": {
                "scoring_uri": self.get("AML_COO_SCORING_URI", ""),
                "key": self.get("AML_COO_KEY", "")
            },
            "chro": {
                "scoring_uri": self.get("AML_CHRO_SCORING_URI", ""),
                "key": self.get("AML_CHRO_KEY", "")
            }
        }

    def get_list(self, key: str, separator: str = ",", default: List[str] = None) -> List[str]:
        """
        Get environment variable as a list.
        Enhanced from old environment.py functionality.
        """
        value = self.get(key)
        if value is None:
            return default or []
        return [item.strip() for item in value.split(separator) if item.strip()]

    def get_json(self, key: str, default: Any = None) -> Any:
        """
        Get environment variable as JSON.
        Enhanced from old environment.py functionality.
        """
        import json
        value = self.get(key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON from {key}: {e}")
            return default

    def get_env_vars_by_prefix(self, prefix: str) -> Dict[str, str]:
        """
        Get environment variables with a specific prefix.
        Enhanced from old environment.py functionality.
        """
        return {k: v for k, v in os.environ.items() if k.startswith(prefix)}

    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate environment configuration comprehensively.
        Enhanced from old environment.py functionality.
        """
        issues = []
        warnings = []

        # Check Azure Storage connection
        try:
            self.get_azure_connection_string("storage")
        except EnvironmentError:
            issues.append("Missing Azure Storage connection string")

        # Check ML configuration
        ml_config = self.get_ml_config()
        missing_ml = [k for k, v in ml_config.items() if not v]
        if missing_ml:
            warnings.append(f"Missing ML configuration: {', '.join(missing_ml)}")

        # Check agent endpoints
        agent_endpoints = self.get_agent_endpoints()
        configured_agents = [
            agent for agent, config in agent_endpoints.items()
            if config["scoring_uri"] and config["key"]
        ]

        if not configured_agents:
            warnings.append("No agent endpoints configured")

        # Check authentication configuration
        auth_config = self.get_auth_config()
        missing_auth = []
        if not auth_config.get("jwt_secret"):
            missing_auth.append("JWT_SECRET")
        if not all([auth_config.get("azure_b2c_tenant"), auth_config.get("azure_b2c_client_id")]):
            missing_auth.append("Azure B2C configuration incomplete")

        if missing_auth:
            warnings.append(f"Authentication configuration issues: {', '.join(missing_auth)}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "configured_agents": configured_agents,
            "ml_configured": all(ml_config.values()),
            "storage_configured": len([i for i in issues if "storage" in i.lower()]) == 0,
            "auth_configured": len(missing_auth) == 0
        }

    def clear_cache(self):
        """Clear the environment variable cache"""
        self._cache.clear()
        self.logger.debug("Environment variable cache cleared")


# Global instance
env_manager = EnvironmentManager()