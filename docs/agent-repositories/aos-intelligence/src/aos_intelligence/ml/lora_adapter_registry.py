"""LoRAAdapterRegistry — registers LoRA adapter artefacts in the Foundry Model Registry.

Fine-tuning jobs produce two artefacts that must be stored together:

* ``adapter_model.bin`` — the LoRA weight delta.
* ``adapter_config.json`` — the PEFT configuration (rank, alpha, target modules).

Both are registered as a single **MLflow Model Asset** in the Azure AI Foundry
Model Registry.  Each registration is tagged with:

* ``persona_type`` — e.g. ``"ceo"``, ``"cmo"``, ``"financial_analyst"``
* ``base_model_version`` — the exact base model tag the adapter was trained on
  (e.g. ``"Meta-Llama-3.3-70B-Instruct"``) to enforce lineage compatibility
  checks before deployment.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Canonical base model identifier — matches the Azure ML model asset name used in
# the lora-inference.bicep Managed Online Endpoint deployment.
BASE_MODEL_ID = "Meta-Llama-3.3-70B-Instruct"


class LoRAAdapterRegistry:
    """Register and look up LoRA adapters in the Foundry Model Registry.

    Adapter artefacts (``adapter_model.bin`` + ``adapter_config.json``) are
    registered as MLflow Model Assets so that every adapter has a traceable
    lineage back to its base model and the persona it was trained for.

    :param ml_client: An ``azure.ai.ml.MLClient`` connected to the target
        Azure ML Registry (optional — when absent the registry operates in
        local/stub mode, which is suitable for unit tests and development).
    :param registry_name: Name of the Azure ML Registry that stores adapters.
    """

    def __init__(
        self,
        ml_client: Any = None,
        registry_name: str = "",
    ) -> None:
        self._ml_client = ml_client
        self.registry_name = registry_name
        # In-memory index: adapter_id → record (used in local mode and as cache)
        self._adapters: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    async def register_adapter(
        self,
        persona_type: str,
        adapter_path: str,
        base_model_version: str = BASE_MODEL_ID,
        version: str = "1",
        description: str = "",
        extra_tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Register a LoRA adapter as an MLflow Model Asset.

        :param persona_type: Persona label (e.g. ``"ceo"``).  Used as the
            primary lookup key and stored as an MLflow tag.
        :param adapter_path: Local or remote path to the directory that
            contains ``adapter_model.bin`` and ``adapter_config.json``.
        :param base_model_version: Exact base model tag the adapter targets.
            Stored as an MLflow tag to enforce lineage compatibility.
        :param version: Asset version string.
        :param description: Human-readable description.
        :param extra_tags: Additional key/value tags to attach.
        :returns: Registry record dictionary including the assigned
            ``adapter_id``.
        """
        adapter_id = str(uuid.uuid4())
        tags: Dict[str, str] = {
            "persona_type": persona_type,
            "base_model_version": base_model_version,
        }
        if extra_tags:
            tags.update(extra_tags)

        # Delegate to azure-ai-ml when an ML client is available
        if self._ml_client is not None:
            try:
                from azure.ai.ml.entities import Model  # type: ignore[import]

                model = Model(
                    name=f"lora-adapter-{persona_type}",
                    version=version,
                    path=adapter_path,
                    description=description or f"LoRA adapter for {persona_type} persona",
                    flavors={"python_function": {"loader_module": "mlflow.pyfunc"}},
                    tags=tags,
                )
                registered = self._ml_client.models.create_or_update(model)
                adapter_id = registered.id or adapter_id
                logger.info(
                    "Registered LoRA adapter %s (persona=%s) in registry %s",
                    adapter_id,
                    persona_type,
                    self.registry_name,
                )
            except Exception as exc:
                logger.warning(
                    "Failed to register adapter in ML registry: %s — using local stub",
                    exc,
                )

        record: Dict[str, Any] = {
            "adapter_id": adapter_id,
            "persona_type": persona_type,
            "adapter_path": adapter_path,
            "base_model_version": base_model_version,
            "version": version,
            "description": description,
            "tags": tags,
            "registry_name": self.registry_name,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        # Index by both adapter_id and persona_type for fast lookups
        self._adapters[adapter_id] = record
        self._adapters[persona_type] = record
        return record

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_adapter_by_persona(self, persona_type: str) -> Dict[str, Any]:
        """Return the registry record for *persona_type*.

        :raises KeyError: If no adapter is registered for the persona.
        """
        record = self._adapters.get(persona_type)
        if record is None:
            raise KeyError(f"No LoRA adapter registered for persona {persona_type!r}")
        return dict(record)

    def get_adapter_by_id(self, adapter_id: str) -> Dict[str, Any]:
        """Return the registry record for *adapter_id*.

        :raises KeyError: If the adapter ID is unknown.
        """
        record = self._adapters.get(adapter_id)
        if record is None:
            raise KeyError(f"LoRA adapter {adapter_id!r} not found in registry")
        return dict(record)

    def get_adapter_id(self, persona_type: str) -> str:
        """Convenience helper — return only the adapter ID for *persona_type*.

        :raises KeyError: If no adapter is registered for the persona.
        """
        return self.get_adapter_by_persona(persona_type)["adapter_id"]

    def list_adapters(self) -> List[Dict[str, Any]]:
        """Return all unique adapter records (deduplicated by adapter_id)."""
        seen: Set[str] = set()
        result: List[Dict[str, Any]] = []
        for record in self._adapters.values():
            aid = record["adapter_id"]
            if aid not in seen:
                seen.add(aid)
                result.append(dict(record))
        return result

    @property
    def adapter_count(self) -> int:
        """Number of unique adapters registered."""
        return len(self.list_adapters())
