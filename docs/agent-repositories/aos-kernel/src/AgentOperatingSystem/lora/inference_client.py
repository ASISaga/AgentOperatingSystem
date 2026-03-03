"""LoRAInferenceClient — high-level inference client for Multi-LoRA inference.

Abstracts the Azure AI Model Inference API so that callers only need to
specify a *persona* name.  The client:

1. Looks up the correct ``adapter_id`` from the :class:`LoRAAdapterRegistry`
   based on the requested persona.
2. Passes the ``adapter_id`` via the ``extra_body`` field (also aliased as
   ``model_extras`` in the Azure AI Inference SDK) so the Managed Online
   Endpoint loads the requested LoRA adapter without evicting the base
   Llama-3.3-70B-Instruct weights from VRAM.

When no inference client is provided the class operates in local/stub mode,
which is suitable for unit tests and local development.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from AgentOperatingSystem.lora.registry import LoRAAdapterRegistry

logger = logging.getLogger(__name__)


class LoRAInferenceClient:
    """Inference client that routes requests to the correct LoRA adapter.

    :param registry: A :class:`LoRAAdapterRegistry` used to resolve persona
        names to adapter IDs.
    :param inference_client: An ``azure.ai.inference.ChatCompletionsClient``
        (or compatible object with a ``complete`` method).  When ``None``, the
        client runs in stub mode.
    :param endpoint_url: Scoring URI of the Managed Online Endpoint.
    :param default_persona: Persona to use when none is specified per request.
    """

    def __init__(
        self,
        registry: LoRAAdapterRegistry,
        inference_client: Any = None,
        endpoint_url: str = "",
        default_persona: str = "",
    ) -> None:
        self.registry = registry
        self._inference_client = inference_client
        self.endpoint_url = endpoint_url
        self.default_persona = default_persona

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def complete(
        self,
        messages: List[Dict[str, str]],
        persona: str = "",
        adapter_id: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a chat-completion request with the specified LoRA adapter loaded.

        The adapter is resolved (in order of precedence) from:

        1. The explicit *adapter_id* argument.
        2. A registry lookup by *persona* name (falling back to
           :attr:`default_persona`).
        3. No adapter if neither is available (pure base-model inference).

        The resolved ``adapter_id`` is injected into ``extra_body`` before
        the request is forwarded to the Azure AI Inference endpoint.

        :param messages: Chat messages in ``[{"role": ..., "content": ...}]``
            format.
        :param persona: Persona name used to look up the adapter from the
            registry.
        :param adapter_id: Explicit adapter ID (overrides registry lookup).
        :param max_tokens: Maximum number of tokens to generate.
        :param temperature: Sampling temperature.
        :param extra_body: Additional fields to merge into the request body.
        :returns: Response dictionary with ``id``, ``choices``, and
            ``adapter_id`` fields.
        """
        resolved_adapter_id = self._resolve_adapter_id(persona, adapter_id)

        body: Dict[str, Any] = dict(extra_body or {})
        if resolved_adapter_id:
            # Pass adapter via extra_body / model_extras per Azure AI Inference spec
            body["adapter_id"] = resolved_adapter_id
            body.setdefault("model_extras", {})["adapter_id"] = resolved_adapter_id

        if self._inference_client is not None:
            try:
                response = await self._call_inference_api(messages, max_tokens, temperature, body)
                response["adapter_id"] = resolved_adapter_id
                return response
            except Exception as exc:
                logger.warning("Inference API call failed: %s — returning stub response", exc)

        # Stub response for local development and testing
        return self._stub_response(messages, resolved_adapter_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_adapter_id(self, persona: str, explicit_adapter_id: Optional[str]) -> str:
        """Resolve the adapter ID from persona or explicit override."""
        if explicit_adapter_id:
            return explicit_adapter_id
        target_persona = persona or self.default_persona
        if not target_persona:
            return ""
        try:
            return self.registry.get_adapter_id(target_persona)
        except KeyError:
            logger.debug("No adapter registered for persona %r — proceeding without adapter", target_persona)
            return ""

    async def _call_inference_api(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        extra_body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Forward the request to the Azure AI Inference API."""
        response = await self._inference_client.complete(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_body=extra_body,
        )
        if hasattr(response, "model_dump"):
            return response.model_dump()
        if hasattr(response, "__dict__"):
            return dict(response.__dict__)
        return dict(response)

    @staticmethod
    def _stub_response(messages: List[Dict[str, str]], adapter_id: str) -> Dict[str, Any]:
        """Return a deterministic stub response (used in local mode)."""
        return {
            "id": f"stub-{uuid.uuid4()}",
            "adapter_id": adapter_id,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"[stub] Responding as adapter={adapter_id or 'base'} "
                        f"to: {messages[-1]['content'][:80] if messages else ''}",
                    },
                    "finish_reason": "stop",
                }
            ],
            "created": datetime.now(timezone.utc).isoformat(),
            "model": "Meta-Llama-3.3-70B-Instruct",
        }
