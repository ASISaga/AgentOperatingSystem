"""Regional validation logic.

Checks Azure service availability per region using both a curated
known-good list and (optionally) the Azure Resource Manager provider API
via ``az provider show``.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any


# Service name → Azure resource provider type
_SERVICE_PROVIDER_MAP: dict[str, str] = {
    "storage": "Microsoft.Storage",
    "keyvault": "Microsoft.KeyVault",
    "functions": "Microsoft.Web",
    "functions-premium": "Microsoft.Web",
    "servicebus": "Microsoft.ServiceBus",
    "servicebus-premium": "Microsoft.ServiceBus",
    "appinsights": "Microsoft.Insights",
    "loganalytics": "Microsoft.OperationalInsights",
    "identity": "Microsoft.ManagedIdentity",
    "azureml": "Microsoft.MachineLearningServices",
    "acr": "Microsoft.ContainerRegistry",
}

# Regions known to support the full AOS service set
_KNOWN_GOOD_REGIONS: set[str] = {
    "eastus", "eastus2", "westus2", "westus3",
    "centralus", "northcentralus", "southcentralus",
    "westeurope", "northeurope", "uksouth", "ukwest",
    "southeastasia", "eastasia", "japaneast",
    "australiaeast", "canadacentral",
}

_GEOGRAPHY_DEFAULTS: dict[str, dict[str, list[str]]] = {
    "americas": {
        "primary": ["eastus", "westus2", "centralus"],
        "ml": ["eastus", "eastus2", "westus2"],
    },
    "europe": {
        "primary": ["westeurope", "northeurope", "uksouth"],
        "ml": ["westeurope", "northeurope", "uksouth"],
    },
    "asia": {
        "primary": ["southeastasia", "eastasia", "japaneast"],
        "ml": ["southeastasia", "japaneast", "eastasia"],
    },
}

_ENV_TIER: dict[str, int] = {"dev": 0, "staging": 1, "prod": 2}


class RegionalValidator:
    """Validates Azure region capabilities for AOS services."""

    def validate_region(self, region: str, services: list[str]) -> dict[str, bool]:
        """Return a mapping of *service* → *available* for the given region.

        Uses the known-good list for a fast path and falls back to querying
        ``az provider show`` for unknown regions.
        """
        results: dict[str, bool] = {}
        for svc in services:
            if region in _KNOWN_GOOD_REGIONS:
                results[svc] = True
            else:
                results[svc] = self._check_provider(region, svc)
        return results

    def select_optimal_regions(
        self, environment: str, geography: str
    ) -> dict[str, str]:
        """Return ``{"primary": ..., "ml": ...}`` for the given context."""
        geo = geography.lower() if geography else "americas"
        candidates = _GEOGRAPHY_DEFAULTS.get(geo, _GEOGRAPHY_DEFAULTS["americas"])
        tier = _ENV_TIER.get(environment, 0)

        primary = candidates["primary"][min(tier, len(candidates["primary"]) - 1)]
        ml = candidates["ml"][min(tier, len(candidates["ml"]) - 1)]
        return {"primary": primary, "ml": ml}

    def get_region_summary(
        self, region: str, services: list[str]
    ) -> dict[str, str]:
        """Return a human-readable availability summary per service."""
        availability = self.validate_region(region, services)
        summary: dict[str, str] = {}
        for svc, ok in availability.items():
            summary[svc] = "Available" if ok else "Not confirmed"
        return summary

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _check_provider(region: str, service: str) -> bool:
        """Query the Azure RM provider API for a specific service."""
        provider = _SERVICE_PROVIDER_MAP.get(service)
        if not provider:
            return False
        try:
            result = subprocess.run(
                [
                    "az", "provider", "show",
                    "--namespace", provider,
                    "--query", "resourceTypes[].locations[]",
                    "--output", "json",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return False
            locations: list[str] = json.loads(result.stdout)
            normalised = [loc.lower().replace(" ", "") for loc in locations]
            return region.lower().replace(" ", "") in normalised
        except (json.JSONDecodeError, OSError):
            return False
