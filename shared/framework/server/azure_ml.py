import os
from typing import Dict, Any
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import OnlineEndpoint
import requests

class AzureMLAdapters:
    def __init__(self):
        self.subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        self.resource_group = os.environ["AZURE_RESOURCE_GROUP"]
        self.workspace = os.environ["AZURE_ML_WORKSPACE"]
        self.credential = DefaultAzureCredential()
        self.ml = MLClient(self.credential, self.subscription_id, self.resource_group, self.workspace)

    def endpoint_uri_and_key(self, endpoint_name: str):
        ep: OnlineEndpoint = self.ml.online_endpoints.get(endpoint_name)
        # Assuming key auth; alternatively use AAD tokens
        primary_key = self.ml.online_endpoints.list_keys(endpoint_name).primary_key
        return ep.scoring_uri, primary_key

    def score(self, endpoint_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        uri, key = self.endpoint_uri_and_key(endpoint_name)
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
        resp = requests.post(uri, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
