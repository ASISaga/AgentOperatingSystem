"""AIGateway — client for routing AI requests through the APIM-based AI Gateway.

The AI Gateway is an API Management (APIM) layer that sits in front of
Azure AI Services, providing rate limiting, JWT validation, and centralised
routing to model deployments.

Usage::

    from aos_client.gateway import AIGateway

    async with AIGateway(
        gateway_url="https://my-apim.azure-api.net/ai",
        credential=credential,
    ) as gw:
        response = await gw.chat_completion(
            messages=[{"role": "user", "content": "Hello!"}],
        )
        print(response)
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Configuration model
# ------------------------------------------------------------------


class GatewayConfig(BaseModel):
    """Pydantic configuration model for the AI Gateway.

    Args:
        gateway_url: Base URL of the APIM AI Gateway endpoint.
        default_model: Default model deployment name used when callers
            do not specify one explicitly.
        max_retries: Maximum number of retry attempts for transient
            failures and rate-limited responses.
        backoff_factor: Multiplicative factor applied between retries
            (exponential back-off).
        timeout_seconds: Per-request timeout in seconds.
        rate_limit_retry: When ``True``, automatically retry requests
            that receive an HTTP 429 response, honouring the
            ``Retry-After`` header when present.
    """

    gateway_url: str
    default_model: str = "gpt-4o"
    max_retries: int = 3
    backoff_factor: float = 0.5
    timeout_seconds: int = 30
    rate_limit_retry: bool = True


# ------------------------------------------------------------------
# AI Gateway client
# ------------------------------------------------------------------


class AIGateway:
    """Client for routing AI requests through the APIM-based AI Gateway.

    The gateway exposes an OpenAI-compatible API surface and handles
    authentication, rate-limit management, and retry logic on behalf
    of the caller.

    Args:
        gateway_url: Base URL of the AI Gateway
            (e.g. ``"https://my-apim.azure-api.net/ai"``).
        credential: Azure credential used to obtain a Bearer token.
            When ``None``, requests are sent without authentication
            (suitable for local development).
        default_model: Default model deployment name.
        retry_config: Optional dictionary with retry tunables
            (``max_retries``, ``backoff_factor``).
    """

    def __init__(
        self,
        gateway_url: str,
        credential: Optional[Any] = None,
        default_model: str = "gpt-4o",
        retry_config: Optional[dict] = None,
    ) -> None:
        self.gateway_url = gateway_url.rstrip("/")
        self.credential = credential
        self.default_model = default_model

        retry_config = retry_config or {}
        self.max_retries: int = retry_config.get("max_retries", 3)
        self.backoff_factor: float = retry_config.get("backoff_factor", 0.5)
        self.timeout_seconds: int = retry_config.get("timeout_seconds", 30)

        self._session: Optional[Any] = None  # aiohttp.ClientSession placeholder

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "AIGateway":
        try:
            import aiohttp  # type: ignore[import-untyped]

            timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
            self._session = aiohttp.ClientSession(timeout=timeout)
        except ImportError:
            logger.warning("aiohttp not installed — HTTP calls will not work")
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    # ------------------------------------------------------------------
    # Public API — Chat / Completion / Embedding
    # ------------------------------------------------------------------

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> dict:
        """Route a chat completion request through the AI Gateway.

        Constructs a standard OpenAI-compatible payload and forwards it
        to the gateway for processing.

        Args:
            messages: Conversation messages in OpenAI chat format
                (list of ``{"role": ..., "content": ...}`` dicts).
            model: Model deployment name. Falls back to
                :attr:`default_model` when ``None``.
            temperature: Sampling temperature (0.0 – 2.0).
            max_tokens: Maximum number of tokens to generate.
            **kwargs: Additional parameters forwarded to the gateway.

        Returns:
            Gateway response dictionary containing the completion result.
        """
        payload: Dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            **kwargs,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        return await self._request("POST", "/chat/completions", json=payload)

    async def completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> dict:
        """Route a text completion request through the AI Gateway.

        Args:
            prompt: The text prompt to complete.
            model: Model deployment name. Falls back to
                :attr:`default_model` when ``None``.
            max_tokens: Maximum number of tokens to generate.
            **kwargs: Additional parameters forwarded to the gateway.

        Returns:
            Gateway response dictionary containing the completion result.
        """
        payload: Dict[str, Any] = {
            "model": model or self.default_model,
            "prompt": prompt,
            **kwargs,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        return await self._request("POST", "/completions", json=payload)

    async def embedding(
        self,
        input_text: str,
        model: Optional[str] = None,
    ) -> dict:
        """Route an embedding request through the AI Gateway.

        Args:
            input_text: Text to generate embeddings for.
            model: Model deployment name. Falls back to
                :attr:`default_model` when ``None``.

        Returns:
            Gateway response dictionary containing the embedding vector(s).
        """
        payload: Dict[str, Any] = {
            "model": model or self.default_model,
            "input": input_text,
        }
        return await self._request("POST", "/embeddings", json=payload)

    # ------------------------------------------------------------------
    # Public API — Discovery / Health
    # ------------------------------------------------------------------

    async def list_models(self) -> List[dict]:
        """List available model deployments via the AI Gateway.

        Returns:
            List of dictionaries describing each available model.
        """
        data = await self._request("GET", "/models")
        return data.get("data", [])

    async def health_check(self) -> dict:
        """Check gateway availability and latency.

        Returns:
            Dictionary with ``status`` and ``latency_ms`` keys.
        """
        start = time.monotonic()
        data = await self._request("GET", "/health")
        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        data["latency_ms"] = elapsed_ms
        return data

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[Any] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> dict:
        """Core HTTP helper with retry and rate-limit handling.

        Args:
            method: HTTP method (``"GET"``, ``"POST"``, etc.).
            path: URL path relative to the gateway base URL.
            json: Optional JSON body for the request.
            params: Optional query parameters.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            RuntimeError: If the client is not used as an async context
                manager.
            aiohttp.ClientResponseError: On non-retryable HTTP errors.
        """
        if self._session is None:
            raise RuntimeError(
                "AIGateway must be used as an async context manager: "
                "async with AIGateway(...) as gw: ..."
            )

        url = f"{self.gateway_url}{path}"
        headers = await self._auth_headers()

        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with self._session.request(
                    method, url, json=json, params=params, headers=headers,
                ) as resp:
                    if resp.status == 429:
                        retry_after = resp.headers.get("Retry-After")
                        wait = (
                            float(retry_after)
                            if retry_after
                            else self.backoff_factor * (2 ** (attempt - 1))
                        )
                        logger.warning(
                            "Rate limited (429) on %s %s — retrying in %.1fs "
                            "(attempt %d/%d)",
                            method, path, wait, attempt, self.max_retries,
                        )
                        last_exc = RuntimeError(
                            f"Rate limited (429) on {method} {path} after "
                            f"{self.max_retries} attempts"
                        )
                        await asyncio.sleep(wait)
                        continue

                    resp.raise_for_status()
                    return await resp.json()

            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                wait = self.backoff_factor * (2 ** (attempt - 1))
                logger.warning(
                    "Request %s %s failed (attempt %d/%d): %s — retrying in %.1fs",
                    method, path, attempt, self.max_retries, exc, wait,
                )
                await asyncio.sleep(wait)

        raise last_exc  # type: ignore[misc]

    async def _auth_headers(self) -> Dict[str, str]:
        """Obtain authorisation headers from the configured credential.

        Returns:
            Dictionary containing the ``Authorization`` header, or an
            empty dictionary when no credential is configured.
        """
        if self.credential is None:
            return {}
        try:
            token = self.credential.get_token(
                "https://cognitiveservices.azure.com/.default",
            )
            return {"Authorization": f"Bearer {token.token}"}
        except Exception as exc:
            logger.warning(
                "Failed to obtain auth token: %s. Proceeding without authentication.",
                exc,
            )
            return {}
