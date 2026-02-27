"""Code deployment mechanism for AOS client applications.

Provides utilities for deploying client applications to Azure Functions,
including packaging, configuration, and deployment orchestration.

Usage::

    from aos_client.deployment import AOSDeployer

    deployer = AOSDeployer(
        app_name="business-infinity",
        resource_group="rg-business-infinity",
    )
    result = await deployer.deploy()
    print(result.url)
"""

from __future__ import annotations

import logging
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""

    app_name: str
    url: Optional[str] = None
    resource_group: Optional[str] = None
    status: str = "unknown"
    details: Dict[str, Any] = field(default_factory=dict)


class AOSDeployer:
    """Deploys AOS client applications to Azure Functions.

    Handles packaging and deployment of client applications, including
    creating the necessary Azure Functions configuration files.

    Args:
        app_name: Azure Functions app name.
        resource_group: Azure resource group name.
        subscription_id: Azure subscription ID.
        location: Azure region (e.g. ``"eastus2"``).
        project_path: Path to the project root.  Defaults to current directory.
    """

    def __init__(
        self,
        app_name: str,
        resource_group: Optional[str] = None,
        subscription_id: Optional[str] = None,
        location: str = "eastus2",
        project_path: Optional[str] = None,
    ) -> None:
        self.app_name = app_name
        self.resource_group = resource_group or f"rg-{app_name}"
        self.subscription_id = subscription_id
        self.location = location
        self.project_path = Path(project_path) if project_path else Path.cwd()

    def ensure_host_json(self) -> Path:
        """Ensure ``host.json`` exists in the project root.

        Creates a default Azure Functions host configuration if missing.

        Returns:
            Path to the host.json file.
        """
        host_json = self.project_path / "host.json"
        if not host_json.exists():
            import json

            config = {
                "version": "2.0",
                "logging": {
                    "applicationInsights": {
                        "samplingSettings": {"isEnabled": True, "excludedTypes": "Request"}
                    }
                },
                "extensionBundle": {
                    "id": "Microsoft.Azure.Functions.ExtensionBundle",
                    "version": "[4.*, 5.0.0)",
                },
                "extensions": {
                    "serviceBus": {
                        "prefetchCount": 10,
                        "autoCompleteMessages": True,
                    }
                },
            }
            host_json.write_text(json.dumps(config, indent=2) + "\n")
            logger.info("Created host.json at %s", host_json)
        return host_json

    def ensure_local_settings(
        self,
        aos_endpoint: Optional[str] = None,
        service_bus_connection: Optional[str] = None,
    ) -> Path:
        """Ensure ``local.settings.json`` exists for local development.

        Args:
            aos_endpoint: AOS endpoint URL.
            service_bus_connection: Service Bus connection string.

        Returns:
            Path to the local.settings.json file.
        """
        settings_path = self.project_path / "local.settings.json"
        if not settings_path.exists():
            import json

            settings = {
                "IsEncrypted": False,
                "Values": {
                    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
                    "FUNCTIONS_WORKER_RUNTIME": "python",
                    "AOS_ENDPOINT": aos_endpoint or "http://localhost:7071",
                    "SERVICE_BUS_CONNECTION": service_bus_connection or "",
                },
            }
            settings_path.write_text(json.dumps(settings, indent=2) + "\n")
            logger.info("Created local.settings.json at %s", settings_path)
        return settings_path

    def get_required_files(self) -> List[str]:
        """List files required for Azure Functions deployment.

        Returns:
            List of expected file paths relative to project root.
        """
        return [
            "host.json",
            "requirements.txt",
        ]

    def generate_requirements_txt(self) -> Path:
        """Generate ``requirements.txt`` from the project's dependencies.

        Returns:
            Path to the generated requirements.txt.
        """
        requirements_path = self.project_path / "requirements.txt"
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                check=True,
            )
            requirements_path.write_text(result.stdout)
            logger.info("Generated requirements.txt at %s", requirements_path)
        except subprocess.CalledProcessError as exc:
            logger.warning("Failed to generate requirements.txt: %s", exc)
        return requirements_path

    async def deploy(self, slot: Optional[str] = None) -> DeploymentResult:
        """Deploy the application to Azure Functions.

        Uses the Azure CLI (``az functionapp``) to deploy the application.
        Ensures required configuration files exist before deployment.

        Args:
            slot: Optional deployment slot (e.g. ``"staging"``).

        Returns:
            :class:`DeploymentResult` with deployment details.
        """
        import tempfile
        import zipfile

        # Ensure configuration files exist
        self.ensure_host_json()

        # Create a zip archive for deployment
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            zip_path = tmp.name

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.project_path.rglob("*"):
                if file_path.is_file() and "__pycache__" not in str(file_path):
                    arcname = file_path.relative_to(self.project_path)
                    zf.write(file_path, arcname)

        cmd = [
            "az",
            "functionapp",
            "deployment",
            "source",
            "config-zip",
            "--resource-group",
            self.resource_group,
            "--name",
            self.app_name,
            "--src",
            zip_path,
        ]

        if slot:
            cmd.extend(["--slot", slot])

        if self.subscription_id:
            cmd.extend(["--subscription", self.subscription_id])

        logger.info("Deploying %s to Azure Functions...", self.app_name)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json

            details = json.loads(result.stdout) if result.stdout.strip() else {}

            return DeploymentResult(
                app_name=self.app_name,
                url=f"https://{self.app_name}.azurewebsites.net",
                resource_group=self.resource_group,
                status="succeeded",
                details=details,
            )
        except FileNotFoundError:
            logger.error("Azure CLI not found. Install with: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash")
            return DeploymentResult(
                app_name=self.app_name,
                status="failed",
                details={"error": "Azure CLI (az) not found"},
            )
        except subprocess.CalledProcessError as exc:
            logger.error("Deployment failed: %s", exc.stderr)
            return DeploymentResult(
                app_name=self.app_name,
                resource_group=self.resource_group,
                status="failed",
                details={"error": exc.stderr},
            )
        finally:
            Path(zip_path).unlink(missing_ok=True)
