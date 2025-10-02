"""
Decision Engine for AgentOperatingSystem (AOS)
Provides generic, reusable decision engine functionality with integrated config loading and adapter routing.

Config loading (principles, decision tree, adapters) is now handled by DecisionConfigLoader.
Adapter routing is handled by DecisionAdapterRouter.
Message models (Envelope, MessagesQuery, UiAction) are available in aos_message.py.
"""


import os
import json
from typing import Any, Dict, List, Tuple, Optional
from jsonschema import validate
from ..servicebus_manager import ServiceBusManager

# --- Config Loader Integration ---
class DecisionConfigLoader:
    """Unified loader for principles, decision tree, and adapters config."""
    BASE = os.getenv("AOS_CONFIG_BASE", os.path.join(os.path.dirname(__file__), "configs"))

    @staticmethod
    def load_json(path: str):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_validated(data_path: str, schema_path: str):
        data, schema = DecisionConfigLoader.load_json(data_path), DecisionConfigLoader.load_json(schema_path)
        validate(instance=data, schema=schema)
        return data

    @classmethod
    def load_principles(cls):
        return cls.load_validated(os.path.join(cls.BASE, "principles.example.json"),
                                  os.path.join(cls.BASE, "principles.schema.json"))

    @classmethod
    def load_decision_tree(cls):
        return cls.load_validated(os.path.join(cls.BASE, "decision_tree.example.json"),
                                  os.path.join(cls.BASE, "decision_tree.schema.json"))

    @classmethod
    def load_adapters(cls):
        return cls.load_validated(os.path.join(cls.BASE, "adapters.example.json"),
                                  os.path.join(cls.BASE, "adapters.schema.json"))

# --- Adapter Router Integration ---
class DecisionAdapterRouter:
    def __init__(self, registry: Dict[str, Any], ml_adapter=None):
        self.registry = registry
        self.ml = ml_adapter

    def endpoint_for(self, legend: str, role: str) -> str:
        for a in self.registry["adapters"]:
            if a["legend"] == legend and a["role"] == role:
                return a["endpoint_name"]
        raise ValueError(f"No adapter for legend={legend}, role={role}")

    def score(self, legend: str, role: str, evidence: Dict[str, Any], principles: List[str]) -> Dict[str, Any]:
        endpoint = self.endpoint_for(legend, role)
        payload = {"legend": legend, "role": role, "principles": principles, "evidence": evidence}
        if self.ml:
            return self.ml.score(endpoint, payload)
        return {"error": "ML adapter not configured"}


class Governance:
    """Generic governance functionality for decision auditing and score blending"""
    
    def __init__(self, servicebus_manager=None):
        self.servicebus_manager = servicebus_manager or ServiceBusManager()

    def blend_scores(self, scores: List[Dict[str, float]], method: str, weights: Dict[str, float] = None) -> Dict[str, float]:
        """Blend decision scores using different methods"""
        labels = {label for s in scores for label in s.keys()}
        blended = {}
        for label in labels:
            if method == "weighted" and weights:
                total, wsum = 0.0, 0.0
                for i, s in enumerate(scores):
                    w = list(weights.values())[i] if i < len(weights) else 1.0
                    total += w * s.get(label, 0.0)
                    wsum += w
                blended[label] = total / max(wsum, 1e-9)
            elif method == "mean":
                vals = [s.get(label, 0.0) for s in scores]
                blended[label] = sum(vals) / max(len(vals), 1)
            elif method == "median":
                vals = sorted([s.get(label, 0.0) for s in scores])
                n = len(vals)
                blended[label] = (vals[n//2] if n % 2 else 0.5*(vals[n//2-1]+vals[n//2])) if n else 0.0
            else:
                blended[label] = 0.0
        return blended

    def audit_log(self, event_type: str, payload: dict):
        """Log decision events for audit purposes"""
        if self.servicebus_manager:
            self.servicebus_manager.publish_message(event_type, payload)



class DecisionEngine:
    """Generic decision engine for multi-criteria decision making, with integrated config and adapter logic."""

    def __init__(self, tree: Optional[Dict[str, Any]] = None, adapters: Optional[Dict[str, Any]] = None, principles: Optional[Dict[str, Any]] = None, ml_adapter=None):
        # If not provided, load from config
        if tree is None or adapters is None or principles is None:
            config = DecisionConfigLoader
            tree = tree or config.load_decision_tree()
            adapters = adapters or config.load_adapters()
            principles = principles or config.load_principles()
        self.tree = tree
        self.adapters = adapters
        self.governance = Governance()
        self.principles_map = {p["principle_id"]: p for p in principles.get("principles", [])}
        self.adapter_router = DecisionAdapterRouter(self.adapters, ml_adapter=ml_adapter)

    def run_node(self, node: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single decision node"""
        # This is a simplified version - actual implementation would depend on adapter system
        applied = []
        per_legend_scores = []
        
        # Apply governance blending
        gov = node.get("governance", {"blend": "mean"})
        blended = self.governance.blend_scores(per_legend_scores, method=gov.get("blend", "mean"), weights=gov.get("weights"))
        
        # Select best choice
        choice = max(blended.items(), key=lambda kv: kv[1])[0] if blended else "default"
        
        # Audit log
        self.governance.audit_log("decision.node.completed", {
            "node_id": node.get("node_id"),
            "role": node.get("role"),
            "blended": blended,
            "choice": choice
        })
        
        return {"choice": choice, "blended": blended, "applied": applied}

    def next_node(self, current: Dict[str, Any], choice: str) -> Dict[str, Any]:
        """Find next node based on choice"""
        for output in current.get("outputs", []):
            if output.get("label") == choice:
                next_node_id = output.get("next_node")
                if not next_node_id or next_node_id == "END":
                    return None
                for node in self.tree.get("nodes", []):
                    if node.get("node_id") == next_node_id:
                        return node
        return None

    def run(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete decision tree"""
        nodes = self.tree.get("nodes", [])
        if not nodes:
            return {"error": "No nodes in decision tree"}
            
        node = nodes[0]
        path = []
        
        while node:
            result = self.run_node(node, evidence)
            path.append({"node_id": node.get("node_id"), "result": result})
            node = self.next_node(node, result["choice"])
        
        self.governance.audit_log("decision.tree.completed", {
            "tree_id": self.tree.get("tree_id"),
            "path": path
        })
        
        return {"tree_id": self.tree.get("tree_id"), "path": path}


class GovernanceError(Exception):
    """Exception raised when governance validation fails"""
    pass


def validate_request(context: str = None, payload: Dict[str, Any] = None) -> bool:
    """
    Generic request validation function
    Can be extended for domain-specific validation rules
    """
    if not payload:
        return True
        
    # Basic validation rules
    if context == "training" and payload.get("role") != "Governance":
        if not payload.get("demo", False):
            raise GovernanceError("Training not permitted for this role.")
    
    return True