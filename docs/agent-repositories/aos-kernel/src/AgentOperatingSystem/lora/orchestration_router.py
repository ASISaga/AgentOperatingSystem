"""LoRAOrchestrationRouter — maps orchestration steps to LoRA adapters.

The Foundry Agent Service calls :meth:`LoRAOrchestrationRouter.resolve_adapters`
at the start of each orchestration step to determine which LoRA adapter(s)
should be loaded into the base model for the agents participating in that step.

The router works from two data sources (checked in order):

1. An explicit **step mapping** registered via :meth:`register_step_mapping`
   that directly maps ``(orchestration_type, step_name)`` pairs to adapter
   names.
2. An **agent-to-persona** mapping that derives the adapter from the persona
   associated with each agent ID.

This two-level approach means the router remains useful even before any
explicit step mappings have been configured.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from AgentOperatingSystem.lora.registry import LoRAAdapterRegistry

logger = logging.getLogger(__name__)

# Type alias for a step key (orchestration_type, step_name)
StepKey = Tuple[str, str]


class LoRAOrchestrationRouter:
    """Determines which LoRA adapters to activate for each orchestration step.

    :param registry: A :class:`LoRAAdapterRegistry` used to resolve adapter IDs.
    """

    def __init__(self, registry: LoRAAdapterRegistry) -> None:
        self.registry = registry
        # (orchestration_type, step_name) → list of adapter names (persona types)
        self._step_mappings: Dict[StepKey, List[str]] = {}
        # agent_id → persona_type
        self._agent_personas: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def register_step_mapping(
        self,
        orchestration_type: str,
        step_name: str,
        adapter_personas: List[str],
    ) -> None:
        """Register a direct step → adapter persona mapping.

        :param orchestration_type: High-level orchestration category
            (e.g. ``"strategic_review"``, ``"content_campaign"``).
        :param step_name: Specific step within that orchestration
            (e.g. ``"executive_summary"``, ``"brand_messaging"``).
        :param adapter_personas: Ordered list of persona types whose adapters
            should be activated for this step.
        """
        self._step_mappings[(orchestration_type, step_name)] = list(adapter_personas)
        logger.debug(
            "Registered step mapping %s/%s → %s",
            orchestration_type,
            step_name,
            adapter_personas,
        )

    def register_agent_persona(self, agent_id: str, persona_type: str) -> None:
        """Associate an agent ID with a persona type for fallback routing.

        :param agent_id: Local agent identifier.
        :param persona_type: Persona label that maps to a LoRA adapter.
        """
        self._agent_personas[agent_id] = persona_type
        logger.debug("Registered agent persona %s → %s", agent_id, persona_type)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def resolve_adapters(
        self,
        orchestration_type: str,
        step_name: str,
        agent_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Return the adapter records to load for an orchestration step.

        Resolution order:

        1. If a step mapping exists for ``(orchestration_type, step_name)``,
           return the adapters for those personas.
        2. Otherwise, derive personas from *agent_ids* (if provided) using the
           agent-to-persona map.
        3. Silently skip any persona that has no registered adapter.

        :param orchestration_type: Orchestration category.
        :param step_name: Step name within the orchestration.
        :param agent_ids: Agent IDs participating in this step (used for
            fallback routing).
        :returns: List of adapter record dicts (may be empty if no adapters
            are applicable).
        """
        personas = self._step_mappings.get((orchestration_type, step_name))
        if personas is None and agent_ids:
            personas = [
                self._agent_personas[aid]
                for aid in agent_ids
                if aid in self._agent_personas
            ]

        if not personas:
            logger.debug(
                "No adapter mapping found for %s/%s — base model will be used",
                orchestration_type,
                step_name,
            )
            return []

        adapters: List[Dict[str, Any]] = []
        for persona in personas:
            try:
                adapters.append(self.registry.get_adapter_by_persona(persona))
            except KeyError:
                logger.debug(
                    "Persona %r has no registered adapter — skipping",
                    persona,
                )
        return adapters

    def get_adapter_id_for_agent(self, agent_id: str) -> str:
        """Return the adapter ID for a single agent.

        Looks up the agent's persona and then queries the registry.

        :raises KeyError: If the agent has no persona mapping or the persona
            has no registered adapter.
        """
        persona = self._agent_personas.get(agent_id)
        if persona is None:
            raise KeyError(f"Agent {agent_id!r} has no persona mapping")
        return self.registry.get_adapter_id(persona)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def step_mapping_count(self) -> int:
        """Number of registered step mappings."""
        return len(self._step_mappings)

    @property
    def agent_persona_count(self) -> int:
        """Number of agent→persona mappings."""
        return len(self._agent_personas)
