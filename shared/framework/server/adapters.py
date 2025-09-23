from typing import Dict, Any, List
from .azure_ml import AzureMLAdapters

class LegendAdapterRouter:
    def __init__(self, registry: Dict[str, Any]):
        self.registry = registry
        self.ml = AzureMLAdapters()

    def endpoint_for(self, legend: str, role: str) -> str:
        for a in self.registry["adapters"]:
            if a["legend"] == legend and a["role"] == role:
                return a["endpoint_name"]
        raise ValueError(f"No adapter for legend={legend}, role={role}")

    def score(self, legend: str, role: str, evidence: Dict[str, Any], principles: List[str]) -> Dict[str, Any]:
        endpoint = self.endpoint_for(legend, role)
        payload = {"legend": legend, "role": role, "principles": principles, "evidence": evidence}
        return self.ml.score(endpoint, payload)
