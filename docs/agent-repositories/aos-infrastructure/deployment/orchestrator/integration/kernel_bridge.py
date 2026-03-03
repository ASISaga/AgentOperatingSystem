"""Integration layer — bridges aos-infrastructure with the AOS Kernel.

``KernelBridge`` derives the ``KernelConfig``-compatible environment
variable set from the infrastructure deployment outputs, enabling kernel
instances to be automatically configured after a Bicep deployment.

This bridge does **not** depend on ``aos-kernel`` at import time.  It
uses only the deployment output JSON that ``az deployment group show``
returns after a successful Bicep run.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any, Optional


# Mapping from Bicep output names to AOS Kernel environment variable names.
# Keys: exact output names from main-modular.bicep
# Values: env var names consumed by KernelConfig (aos-kernel)
_OUTPUT_TO_ENV_MAP: dict[str, str] = {
    "aiServicesEndpoint": "AZURE_AI_SERVICES_ENDPOINT",
    "aiProjectDiscoveryUrl": "FOUNDRY_PROJECT_ENDPOINT",
    "aiGatewayUrl": "AI_GATEWAY_URL",
    "keyVaultName": "KEY_VAULT_NAME",
    "serviceBusNamespace": "SERVICE_BUS_NAMESPACE",
    "appInsightsName": "APPLICATIONINSIGHTS_NAME",
    "logAnalyticsWorkspaceId": "LOG_ANALYTICS_WORKSPACE_ID",
    "storageAccountName": "AOS_STORAGE_ACCOUNT",
    "aiHubName": "AZURE_ML_HUB_NAME",
    "aiProjectName": "AZURE_ML_PROJECT_NAME",
    "loraInferenceScoringUri": "LORA_INFERENCE_SCORING_URI",
    "modelRegistryName": "LORA_MODEL_REGISTRY_NAME",
    "resourceGroupName": "AZURE_RESOURCE_GROUP",
}

# Environment variable prefixes used by KernelConfig
_KERNEL_REQUIRED_VARS: set[str] = {
    "AZURE_AI_SERVICES_ENDPOINT",
    "FOUNDRY_PROJECT_ENDPOINT",
    "KEY_VAULT_NAME",
    "SERVICE_BUS_NAMESPACE",
    "AOS_STORAGE_ACCOUNT",
}


class KernelBridge:
    """Derives AOS Kernel environment configuration from deployment outputs.

    After a successful Bicep deployment, the outputs from
    ``az deployment group show`` contain all the resource names and
    endpoints that the kernel needs.  This bridge translates them into a
    ``dict[str, str]`` that can be written to ``.env``, Azure App
    Settings, or passed directly to a kernel process.

    Usage
    -----
    ::

        from orchestrator.integration.kernel_bridge import KernelBridge

        bridge = KernelBridge("rg-aos-dev", "main-deploy-dev")
        env_vars = bridge.extract_kernel_env()
        # env_vars = {"AZURE_AI_SERVICES_ENDPOINT": "https://...", ...}
    """

    def __init__(
        self,
        resource_group: str,
        deployment_name: str = "",
        subscription_id: str = "",
    ) -> None:
        self.resource_group = resource_group
        self.deployment_name = deployment_name
        self.subscription_id = subscription_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_kernel_env(self) -> dict[str, str]:
        """Return a KernelConfig-compatible env-var dict from deployment outputs.

        Fetches the most recent successful deployment outputs from Azure and
        translates known Bicep output names to kernel environment variable
        names via :data:`_OUTPUT_TO_ENV_MAP`.

        Returns an empty dict if the deployment cannot be found or outputs
        are unavailable.
        """
        outputs = self._get_deployment_outputs()
        if not outputs:
            return {}
        return self._translate_outputs(outputs)

    def validate_kernel_config(self, env_vars: dict[str, str]) -> dict[str, list[str]]:
        """Validate that all required kernel env vars are present.

        Parameters
        ----------
        env_vars:
            The dict returned by :meth:`extract_kernel_env`.

        Returns
        -------
        dict[str, list[str]]
            Keys: ``"present"`` and ``"missing"``.
        """
        present = [k for k in _KERNEL_REQUIRED_VARS if k in env_vars]
        missing = [k for k in _KERNEL_REQUIRED_VARS if k not in env_vars]
        if missing:
            print(f"  ⚠️  Kernel config missing: {', '.join(missing)}", file=sys.stderr)
        else:
            print("  ✅ All required kernel env vars are present")
        return {"present": present, "missing": missing}

    def write_env_file(self, env_vars: dict[str, str], path: str = ".env") -> bool:
        """Write the env vars to a ``.env`` file for local kernel development.

        Parameters
        ----------
        env_vars:
            The dict returned by :meth:`extract_kernel_env`.
        path:
            File path to write.  Defaults to ``.env`` in the current directory.
        """
        from pathlib import Path
        try:
            lines = [f"{k}={v}" for k, v in sorted(env_vars.items())]
            Path(path).write_text("\n".join(lines) + "\n")
            print(f"  ✅ Kernel env written to '{path}' ({len(lines)} vars)")
            return True
        except OSError as exc:
            print(f"  ❌ Failed to write env file: {exc}", file=sys.stderr)
            return False

    def sync_function_app_settings(
        self,
        app_name: str,
        env_vars: Optional[dict[str, str]] = None,
    ) -> bool:
        """Push kernel env vars to an Azure Function App's application settings.

        Parameters
        ----------
        app_name:
            Azure Function App name.
        env_vars:
            Env vars to push.  If ``None``, fetches them automatically.
        """
        if env_vars is None:
            env_vars = self.extract_kernel_env()
        if not env_vars:
            print("  ⚠️  No env vars to sync", file=sys.stderr)
            return False

        setting_args = [f"{k}={v}" for k, v in env_vars.items()]
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
        print(f"  {icon} Kernel settings synced to '{app_name}': "
              f"{'ok' if ok else result.stderr.strip()}")
        return ok

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_deployment_outputs(self) -> dict[str, Any] | None:
        """Fetch deployment outputs from Azure."""
        cmd = [
            "az", "deployment", "group", "show",
            "--resource-group", self.resource_group,
            "--query", "properties.outputs",
            "--output", "json",
        ]
        if self.deployment_name:
            cmd += ["--name", self.deployment_name]
        else:
            # Fall back to the most recently created deployment
            list_result = subprocess.run(  # noqa: S603
                [
                    "az", "deployment", "group", "list",
                    "--resource-group", self.resource_group,
                    "--query", "[?properties.provisioningState=='Succeeded'] | [0].name",
                    "--output", "tsv",
                ],
                capture_output=True, text=True,
            )
            if list_result.returncode != 0 or not list_result.stdout.strip():
                return None
            cmd += ["--name", list_result.stdout.strip()]

        result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
        if result.returncode != 0:
            print(
                f"  ⚠️  Could not fetch deployment outputs: {result.stderr.strip()}",
                file=sys.stderr,
            )
            return None
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _translate_outputs(outputs: dict[str, Any]) -> dict[str, str]:
        """Translate Bicep output objects to env var strings."""
        env_vars: dict[str, str] = {}
        for bicep_key, env_key in _OUTPUT_TO_ENV_MAP.items():
            output = outputs.get(bicep_key, {})
            value = output.get("value")
            if value is not None:
                env_vars[env_key] = str(value)
        return env_vars
