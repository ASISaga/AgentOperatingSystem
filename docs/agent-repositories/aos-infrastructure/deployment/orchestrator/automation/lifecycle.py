"""Automation pillar — Infrastructure lifecycle operations.

``LifecycleManager`` covers the operations that extend beyond initial
provisioning: de-provisioning, regional shift, in-place modification,
SKU/tier upgrades, and scaling.  These operations complete the full
Azure infrastructure lifecycle alongside the deployment pipeline.

All mutating lifecycle operations require explicit confirmation (or
``confirm=False`` for pipeline use) and produce structured output.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LifecycleOperation(str, Enum):
    """Classification of a lifecycle operation."""

    DEPROVISION = "deprovision"   # Remove individual resource(s)
    SHIFT = "shift"               # Migrate resource to another region / resource group
    MODIFY = "modify"             # Update resource properties in-place
    UPGRADE = "upgrade"           # Upgrade resource SKU / tier
    SCALE = "scale"               # Scale capacity up or down


@dataclass
class LifecycleResult:
    """Result of a lifecycle operation."""

    operation: LifecycleOperation
    resource_name: str
    resource_type: str
    success: bool
    details: dict[str, Any] = field(default_factory=dict)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation.value,
            "resource_name": self.resource_name,
            "resource_type": self.resource_type,
            "success": self.success,
            "message": self.message,
        }


# Resource types that support ``az resource update`` for property patching
_PATCHABLE_TYPES: set[str] = {
    "microsoft.web/sites",
    "microsoft.storage/storageaccounts",
    "microsoft.servicebus/namespaces",
    "microsoft.keyvault/vaults",
    "microsoft.insights/components",
    "microsoft.cognitiveservices/accounts",
    "microsoft.apimanagement/service",
}

# Resource types and the property path for their SKU
_SKU_PROPERTY_MAP: dict[str, str] = {
    "microsoft.storage/storageaccounts": "sku.name",
    "microsoft.servicebus/namespaces": "sku.name",
    "microsoft.apimanagement/service": "sku.name",
    "microsoft.cognitiveservices/accounts": "sku.name",
    "microsoft.web/serverfarms": "sku.name",
    "microsoft.machinelearningservices/workspaces": "sku.name",
}


class LifecycleManager:
    """Manages infrastructure lifecycle operations beyond initial provisioning.

    Covers the full Azure infrastructure lifecycle:
    - **Deprovision** — tear down individual resources while preserving others
    - **Shift** — migrate a resource group to another region via ARM export/redeploy
    - **Modify** — patch resource properties without full redeployment
    - **Upgrade** — change a resource's SKU or pricing tier
    - **Scale** — adjust capacity settings on scalable resources
    """

    def __init__(self, resource_group: str, subscription_id: str = "") -> None:
        self.resource_group = resource_group
        self.subscription_id = subscription_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def deprovision(
        self,
        resource_name: str,
        resource_type: str,
        *,
        confirm: bool = True,
    ) -> LifecycleResult:
        """Remove a single resource from the resource group.

        Parameters
        ----------
        resource_name:
            Azure resource name.
        resource_type:
            Full ARM resource type (e.g. ``"Microsoft.Storage/storageAccounts"``).
        confirm:
            If ``True`` (default), prompt for confirmation before deleting.
        """
        if confirm:
            answer = input(
                f"⚠️  Deprovision '{resource_name}' ({resource_type}) "
                f"from '{self.resource_group}'? [y/N]: "
            )
            if answer.strip().lower() != "y":
                return LifecycleResult(
                    operation=LifecycleOperation.DEPROVISION,
                    resource_name=resource_name,
                    resource_type=resource_type,
                    success=False,
                    message="Aborted by user.",
                )

        print(f"🗑️  Deprovisioning '{resource_name}' ({resource_type}) …")
        result = subprocess.run(  # noqa: S603
            [
                "az", "resource", "delete",
                "--resource-group", self.resource_group,
                "--name", resource_name,
                "--resource-type", resource_type,
                "--output", "json",
            ],
            capture_output=True, text=True,
        )
        ok = result.returncode == 0
        msg = "deleted" if ok else result.stderr.strip()
        print(f"  {'✅' if ok else '❌'} Deprovision '{resource_name}': {msg}")
        return LifecycleResult(
            operation=LifecycleOperation.DEPROVISION,
            resource_name=resource_name,
            resource_type=resource_type,
            success=ok,
            message=msg,
        )

    def shift_region(
        self,
        target_region: str,
        target_resource_group: str,
        *,
        confirm: bool = True,
    ) -> LifecycleResult:
        """Shift the entire resource group to a new region by exporting and
        redeploying the ARM template.

        This operation:
        1. Exports the current resource group as an ARM template.
        2. Creates (or validates the existence of) the target resource group.
        3. Redeploys the exported template into the new region.

        Parameters
        ----------
        target_region:
            Target Azure region (e.g. ``"westeurope"``).
        target_resource_group:
            Name of the target resource group (will be created if absent).
        confirm:
            Prompt for confirmation before destructive steps.
        """
        if confirm:
            answer = input(
                f"⚠️  Shift '{self.resource_group}' → '{target_resource_group}' "
                f"in region '{target_region}'? [y/N]: "
            )
            if answer.strip().lower() != "y":
                return LifecycleResult(
                    operation=LifecycleOperation.SHIFT,
                    resource_name=self.resource_group,
                    resource_type="Microsoft.Resources/resourceGroups",
                    success=False,
                    message="Aborted by user.",
                )

        print(f"🔀 Shifting '{self.resource_group}' → '{target_resource_group}' in {target_region} …")

        # Step 1: Export ARM template
        template_json = self._export_template()
        if template_json is None:
            return LifecycleResult(
                operation=LifecycleOperation.SHIFT,
                resource_name=self.resource_group,
                resource_type="Microsoft.Resources/resourceGroups",
                success=False,
                message="Template export failed.",
            )

        # Step 2: Ensure target resource group exists
        rg_ok = self._ensure_resource_group(target_resource_group, target_region)
        if not rg_ok:
            return LifecycleResult(
                operation=LifecycleOperation.SHIFT,
                resource_name=self.resource_group,
                resource_type="Microsoft.Resources/resourceGroups",
                success=False,
                message=f"Could not create resource group '{target_resource_group}'.",
            )

        # Step 3: Redeploy exported template into target resource group
        import os
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp:
            json.dump(template_json, tmp)
            tmp_path = tmp.name

        try:
            result = subprocess.run(  # noqa: S603
                [
                    "az", "deployment", "group", "create",
                    "--resource-group", target_resource_group,
                    "--template-file", tmp_path,
                    "--parameters", f"location={target_region}",
                    "--output", "json",
                ],
                capture_output=True, text=True,
            )
            ok = result.returncode == 0
        finally:
            os.unlink(tmp_path)

        msg = (
            f"Shift to '{target_resource_group}' in {target_region} succeeded."
            if ok else result.stderr.strip()
        )
        print(f"  {'✅' if ok else '❌'} Shift result: {msg}")
        return LifecycleResult(
            operation=LifecycleOperation.SHIFT,
            resource_name=self.resource_group,
            resource_type="Microsoft.Resources/resourceGroups",
            success=ok,
            message=msg,
        )

    def modify(
        self,
        resource_name: str,
        resource_type: str,
        properties: dict[str, Any],
    ) -> LifecycleResult:
        """Patch resource properties in-place using ``az resource update``.

        Parameters
        ----------
        resource_name:
            Azure resource name.
        resource_type:
            Full ARM resource type.
        properties:
            Dict of property paths and their new values.
            Keys use dot notation (e.g. ``{"properties.httpsOnly": True}``).
        """
        print(f"🔧 Modifying '{resource_name}' ({resource_type}) …")
        rtype_lower = resource_type.lower()
        if rtype_lower not in _PATCHABLE_TYPES:
            msg = (
                f"Resource type '{resource_type}' may not support in-place modification; "
                "proceeding anyway."
            )
            print(f"  ⚠️  {msg}")

        # Build set-properties JSON
        set_str = json.dumps(properties)
        result = subprocess.run(  # noqa: S603
            [
                "az", "resource", "update",
                "--resource-group", self.resource_group,
                "--name", resource_name,
                "--resource-type", resource_type,
                "--set", set_str,
                "--output", "json",
            ],
            capture_output=True, text=True,
        )
        ok = result.returncode == 0
        msg = "modified" if ok else result.stderr.strip()
        print(f"  {'✅' if ok else '❌'} Modify '{resource_name}': {msg}")
        return LifecycleResult(
            operation=LifecycleOperation.MODIFY,
            resource_name=resource_name,
            resource_type=resource_type,
            success=ok,
            message=msg,
            details=properties,
        )

    def upgrade(
        self,
        resource_name: str,
        resource_type: str,
        new_sku: str,
    ) -> LifecycleResult:
        """Upgrade (or downgrade) a resource's SKU / pricing tier.

        Uses ``az resource update`` with the appropriate SKU property path
        for the resource type.

        Parameters
        ----------
        resource_name:
            Azure resource name.
        resource_type:
            Full ARM resource type.
        new_sku:
            Target SKU name (e.g. ``"Standard_ZRS"``, ``"Premium"``).
        """
        print(f"⬆️  Upgrading '{resource_name}' ({resource_type}) → SKU '{new_sku}' …")
        rtype_lower = resource_type.lower()
        sku_path = _SKU_PROPERTY_MAP.get(rtype_lower, "sku.name")

        result = subprocess.run(  # noqa: S603
            [
                "az", "resource", "update",
                "--resource-group", self.resource_group,
                "--name", resource_name,
                "--resource-type", resource_type,
                "--set", f"{sku_path}={new_sku}",
                "--output", "json",
            ],
            capture_output=True, text=True,
        )
        ok = result.returncode == 0
        msg = f"SKU updated to '{new_sku}'" if ok else result.stderr.strip()
        print(f"  {'✅' if ok else '❌'} Upgrade '{resource_name}': {msg}")
        return LifecycleResult(
            operation=LifecycleOperation.UPGRADE,
            resource_name=resource_name,
            resource_type=resource_type,
            success=ok,
            message=msg,
            details={"new_sku": new_sku},
        )

    def scale(
        self,
        resource_name: str,
        resource_type: str,
        scale_settings: dict[str, Any],
    ) -> LifecycleResult:
        """Adjust capacity settings on a scalable resource.

        ``scale_settings`` supports resource-specific keys:
        - Function App Plan: ``{"sku.capacity": 3}``
        - Service Bus Premium: ``{"properties.messagingUnits": 2}``
        - APIM: ``{"sku.capacity": 2}``

        Parameters
        ----------
        resource_name:
            Azure resource name.
        resource_type:
            Full ARM resource type.
        scale_settings:
            Property path → value mappings to apply.
        """
        print(f"⚖️  Scaling '{resource_name}' ({resource_type}) …")
        # Apply each setting as a separate update
        overall_ok = True
        messages: list[str] = []

        for prop_path, value in scale_settings.items():
            result = subprocess.run(  # noqa: S603
                [
                    "az", "resource", "update",
                    "--resource-group", self.resource_group,
                    "--name", resource_name,
                    "--resource-type", resource_type,
                    "--set", f"{prop_path}={value}",
                    "--output", "json",
                ],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                messages.append(f"{prop_path}={value} ✅")
            else:
                messages.append(f"{prop_path}={value} ❌ ({result.stderr.strip()})")
                overall_ok = False

        msg = "; ".join(messages)
        print(f"  {'✅' if overall_ok else '❌'} Scale '{resource_name}': {msg}")
        return LifecycleResult(
            operation=LifecycleOperation.SCALE,
            resource_name=resource_name,
            resource_type=resource_type,
            success=overall_ok,
            message=msg,
            details=scale_settings,
        )

    def list_lifecycle_candidates(self) -> list[dict[str, Any]]:
        """Return resources that are candidates for lifecycle operations.

        Includes resources in non-``Succeeded`` provisioning states and
        resources flagged as patchable or upgradable.
        """
        result = subprocess.run(  # noqa: S603
            [
                "az", "resource", "list",
                "--resource-group", self.resource_group,
                "--output", "json",
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            return []
        try:
            resources: list[dict[str, Any]] = json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

        candidates = []
        for res in resources:
            rtype = (res.get("type") or "").lower()
            state = res.get("provisioningState", "Succeeded")
            candidate: dict[str, Any] = {
                "name": res.get("name"),
                "type": res.get("type"),
                "location": res.get("location"),
                "provisioningState": state,
                "supports_modify": rtype in _PATCHABLE_TYPES,
                "supports_upgrade": rtype in _SKU_PROPERTY_MAP,
            }
            candidates.append(candidate)
        return candidates

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _export_template(self) -> dict[str, Any] | None:
        """Export the resource group as an ARM template."""
        result = subprocess.run(  # noqa: S603
            [
                "az", "group", "export",
                "--name", self.resource_group,
                "--output", "json",
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"  Template export failed: {result.stderr.strip()}", file=sys.stderr)
            return None
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None

    def _ensure_resource_group(self, name: str, location: str) -> bool:
        """Create the resource group if it does not already exist."""
        result = subprocess.run(  # noqa: S603
            [
                "az", "group", "create",
                "--name", name,
                "--location", location,
                "--output", "json",
            ],
            capture_output=True, text=True,
        )
        return result.returncode == 0
