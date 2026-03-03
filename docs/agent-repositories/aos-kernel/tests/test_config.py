"""Tests for AOS Kernel configuration."""

import os
import pytest

from AgentOperatingSystem.config import KernelConfig


class TestKernelConfig:
    """KernelConfig unit tests."""

    def test_defaults(self):
        config = KernelConfig()
        assert config.default_model == "gpt-4o"
        assert config.orchestration_queue == "aos-orchestration-requests"
        assert config.environment == "dev"

    def test_custom_values(self):
        config = KernelConfig(
            foundry_project_endpoint="https://example.com/project",
            ai_gateway_url="https://gw.example.com",
            default_model="gpt-35-turbo",
            environment="prod",
        )
        assert config.foundry_project_endpoint == "https://example.com/project"
        assert config.ai_gateway_url == "https://gw.example.com"
        assert config.default_model == "gpt-35-turbo"
        assert config.environment == "prod"

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://foundry.test")
        monkeypatch.setenv("AI_GATEWAY_URL", "https://gateway.test")
        monkeypatch.setenv("DEFAULT_MODEL", "gpt-4")
        monkeypatch.setenv("ENVIRONMENT", "staging")

        config = KernelConfig.from_env()
        assert config.foundry_project_endpoint == "https://foundry.test"
        assert config.ai_gateway_url == "https://gateway.test"
        assert config.default_model == "gpt-4"
        assert config.environment == "staging"

    def test_from_env_defaults(self, monkeypatch):
        # Clear any env vars that might be set
        for var in ["FOUNDRY_PROJECT_ENDPOINT", "AI_GATEWAY_URL", "DEFAULT_MODEL", "ENVIRONMENT"]:
            monkeypatch.delenv(var, raising=False)
        config = KernelConfig.from_env()
        assert config.foundry_project_endpoint == ""
        assert config.ai_gateway_url == ""
        assert config.default_model == "gpt-4o"
        assert config.environment == "dev"

    def test_service_bus_config(self):
        config = KernelConfig(
            service_bus_namespace="aos-sb-dev.servicebus.windows.net",
            orchestration_queue="custom-queue",
        )
        assert config.service_bus_namespace == "aos-sb-dev.servicebus.windows.net"
        assert config.orchestration_queue == "custom-queue"

    def test_storage_and_keyvault(self):
        config = KernelConfig(
            storage_table_uri="https://aosstorage.table.core.windows.net/",
            key_vault_uri="https://aos-kv.vault.azure.net/",
        )
        assert config.storage_table_uri == "https://aosstorage.table.core.windows.net/"
        assert config.key_vault_uri == "https://aos-kv.vault.azure.net/"
