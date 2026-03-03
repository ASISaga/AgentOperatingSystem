"""Integration layer — bridges aos-infrastructure with the AOS Client SDK.

``SDKBridge`` connects the infrastructure orchestrator with the
``AOSDeployer`` from ``aos-client-sdk``, enabling a single end-to-end
lifecycle that covers both Azure infrastructure provisioning (Bicep) and
Function App code deployment (SDK).

The bridge is designed so that the infrastructure orchestrator has **no
hard dependency** on ``aos-client-sdk`` at import time.  The SDK is
imported lazily so that the orchestrator remains a standalone CLI tool
even when the SDK is not installed.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


# AOS application module names — mirrors the canonical list in main-modular.bicep
_DEFAULT_APP_NAMES: list[str] = [
    "purpose-driven-agent",
    "leadership-agent",
    "cmo-agent",
    "aos-kernel",
    "aos-intelligence",
    "aos-realm-of-agents",
    "aos-mcp-servers",
    "aos-client-sdk",
    "business-infinity",
    "aos-dispatcher",
]


@dataclass
class AppDeploymentStatus:
    """Deployment status for a single AOS Function App."""

    app_name: str
    status: str = "unknown"   # "succeeded" | "failed" | "skipped" | "unknown"
    url: Optional[str] = None
    error: Optional[str] = None
    details: dict[str, Any] = field(default_factory=dict)


class SDKBridge:
    """Bridges the infrastructure orchestrator with the AOS Client SDK.

    Responsibilities
    ----------------
    - Invoke ``aos_client.deployment.AOSDeployer`` to deploy individual
      Function Apps after infrastructure provisioning.
    - Report consolidated deployment status across all app modules.
    - Provide ``get_aos_endpoint()`` for discovering the dispatcher URL
      from an existing deployment.

    Availability
    ------------
    If ``aos-client-sdk`` is not installed the bridge degrades gracefully:
    ``is_sdk_available()`` returns ``False`` and deployment calls are
    skipped with a warning.
    """

    def __init__(
        self,
        resource_group: str,
        environment: str,
        subscription_id: str = "",
        location: str = "eastus",
        app_names: Optional[list[str]] = None,
    ) -> None:
        self.resource_group = resource_group
        self.environment = environment
        self.subscription_id = subscription_id
        self.location = location
        self.app_names = app_names or _DEFAULT_APP_NAMES

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def is_sdk_available() -> bool:
        """Return ``True`` if ``aos-client-sdk`` is importable."""
        try:
            import importlib
            importlib.import_module("aos_client.deployment")
            return True
        except ImportError:
            return False

    def deploy_function_apps(
        self,
        app_names: Optional[list[str]] = None,
        project_paths: Optional[dict[str, str]] = None,
    ) -> list[AppDeploymentStatus]:
        """Deploy one or more AOS Function Apps using the SDK's ``AOSDeployer``.

        Parameters
        ----------
        app_names:
            Override the default list of apps to deploy.
        project_paths:
            Optional mapping of ``app_name → project_path`` for each app.
            Defaults to current working directory for each app.

        Returns
        -------
        list[AppDeploymentStatus]
            One entry per app with status, URL, and error details.
        """
        targets = app_names or self.app_names
        project_paths = project_paths or {}
        results: list[AppDeploymentStatus] = []

        if not self.is_sdk_available():
            logger.warning(
                "aos-client-sdk is not installed; skipping Function App deployment. "
                "Install with: pip install aos-client-sdk"
            )
            for name in targets:
                results.append(AppDeploymentStatus(
                    app_name=name,
                    status="skipped",
                    error="aos-client-sdk not available",
                ))
            return results

        import asyncio
        from aos_client.deployment import AOSDeployer  # type: ignore[import]

        for app_name in targets:
            deployer = AOSDeployer(
                app_name=app_name,
                resource_group=self.resource_group,
                subscription_id=self.subscription_id or None,
                location=self.location,
                project_path=project_paths.get(app_name),
            )
            try:
                result = asyncio.run(deployer.deploy())
                results.append(AppDeploymentStatus(
                    app_name=app_name,
                    status=result.status,
                    url=result.url,
                    error=result.details.get("error"),
                    details=result.details,
                ))
                icon = "✅" if result.status == "succeeded" else "❌"
                print(f"  {icon} {app_name}: {result.status} — {result.url or 'no URL'}")
            except Exception as exc:  # noqa: BLE001
                logger.error("Deployment failed for %s: %s", app_name, exc)
                results.append(AppDeploymentStatus(
                    app_name=app_name,
                    status="failed",
                    error=str(exc),
                ))

        return results

    def get_aos_endpoint(self) -> Optional[str]:
        """Discover the AOS dispatcher endpoint from the live resource group.

        Queries the ``aos-dispatcher`` Function App hostname.
        """
        result = subprocess.run(  # noqa: S603
            [
                "az", "functionapp", "show",
                "--resource-group", self.resource_group,
                "--name", f"func-aos-dispatcher-{self.environment}",
                "--query", "defaultHostName",
                "--output", "tsv",
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        hostname = result.stdout.strip()
        return f"https://{hostname}"

    def get_function_app_status(self, app_name: str) -> AppDeploymentStatus:
        """Retrieve the current deployment status of a Function App from Azure."""
        result = subprocess.run(  # noqa: S603
            [
                "az", "functionapp", "show",
                "--resource-group", self.resource_group,
                "--name", app_name,
                "--query", "{state:state, url:defaultHostName}",
                "--output", "json",
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            return AppDeploymentStatus(
                app_name=app_name,
                status="unknown",
                error=result.stderr.strip(),
            )
        try:
            data = json.loads(result.stdout)
            state = data.get("state", "unknown")
            hostname = data.get("url")
            return AppDeploymentStatus(
                app_name=app_name,
                status="running" if state == "Running" else state.lower(),
                url=f"https://{hostname}" if hostname else None,
            )
        except json.JSONDecodeError:
            return AppDeploymentStatus(app_name=app_name, status="unknown")

    def sync_app_settings(
        self,
        app_name: str,
        settings: dict[str, str],
    ) -> bool:
        """Push application settings (environment variables) to a Function App.

        Parameters
        ----------
        app_name:
            Azure Function App name.
        settings:
            Key→value pairs to set.  Existing settings are preserved.
        """
        if not settings:
            return True
        setting_args = [f"{k}={v}" for k, v in settings.items()]
        result = subprocess.run(  # noqa: S603
            [
                "az", "functionapp", "config", "appsettings", "set",
                "--resource-group", self.resource_group,
                "--name", app_name,
                "--settings", *setting_args,
                "--output", "json",
            ],
            capture_output=True, text=True,
        )
        ok = result.returncode == 0
        icon = "✅" if ok else "❌"
        print(f"  {icon} App settings for '{app_name}': {'updated' if ok else result.stderr.strip()}")
        return ok
