"""Kernel configuration — Pydantic models for AOS kernel settings.

All kernel components read their configuration from :class:`KernelConfig`.
Values are loaded from environment variables with sensible defaults for
local development.
"""

from __future__ import annotations

import os
from typing import Optional

from pydantic import BaseModel, Field


class KernelConfig(BaseModel):
    """Top-level configuration for the AOS kernel.

    Every setting has a default suitable for local development / testing.
    In production the values are injected via Azure Function App settings
    which are backed by Bicep parameters.

    :param foundry_project_endpoint: Discovery URL of the Azure AI Foundry
        project (e.g. ``"https://<region>.api.azureml.ms/..."``).
    :param ai_gateway_url: URL of the AI Gateway (APIM) for rate-limited
        model access.
    :param default_model: Default model deployment name.
    :param service_bus_namespace: Fully-qualified Service Bus namespace
        (e.g. ``"aos-sb-dev.servicebus.windows.net"``).
    :param orchestration_queue: Service Bus queue for orchestration requests.
    :param storage_table_uri: Azure Table Storage URI for cross-module state.
    :param key_vault_uri: Azure Key Vault URI for secrets.
    :param environment: Deployment environment (``dev``, ``staging``, ``prod``).
    """

    foundry_project_endpoint: str = Field(
        default_factory=lambda: os.environ.get("FOUNDRY_PROJECT_ENDPOINT", ""),
        description="Azure AI Foundry project discovery URL",
    )
    ai_gateway_url: str = Field(
        default_factory=lambda: os.environ.get("AI_GATEWAY_URL", ""),
        description="AI Gateway (APIM) URL",
    )
    default_model: str = Field(
        default_factory=lambda: os.environ.get("DEFAULT_MODEL", "gpt-4o"),
        description="Default model deployment name",
    )
    service_bus_namespace: str = Field(
        default_factory=lambda: os.environ.get(
            "ServiceBusConnection__fullyQualifiedNamespace", ""
        ),
        description="Service Bus fully-qualified namespace",
    )
    orchestration_queue: str = Field(
        default="aos-orchestration-requests",
        description="Service Bus queue for orchestration requests",
    )
    storage_table_uri: str = Field(
        default_factory=lambda: os.environ.get("AosStateStore__tableServiceUri", ""),
        description="Azure Table Storage URI for shared state",
    )
    key_vault_uri: str = Field(
        default_factory=lambda: os.environ.get("KEY_VAULT_URI", ""),
        description="Azure Key Vault URI",
    )
    environment: str = Field(
        default_factory=lambda: os.environ.get("ENVIRONMENT", "dev"),
        description="Deployment environment",
    )

    @classmethod
    def from_env(cls) -> "KernelConfig":
        """Create a :class:`KernelConfig` from environment variables.

        This is the preferred factory method in Azure Functions where all
        settings are injected as environment variables by the Bicep template.
        """
        return cls()
