"""Client application registration with the Agent Operating System.

When a client application registers with AOS, AOS provisions the
necessary Azure infrastructure (Service Bus queues, topics, subscriptions,
managed identity role assignments) so the client app can communicate
asynchronously.

Usage::

    from aos_client.registration import AOSRegistration

    reg = AOSRegistration(aos_endpoint="https://my-aos.azurewebsites.net")
    app_info = await reg.register_app(
        app_name="business-infinity",
        workflows=["strategic-review", "market-analysis", "budget-approval"],
    )
    print(app_info.service_bus_connection_string)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AppRegistration(BaseModel):
    """Registration record for a client application in AOS."""

    app_name: str = Field(..., description="Unique application name")
    app_id: Optional[str] = Field(None, description="Azure AD application ID")
    workflows: List[str] = Field(default_factory=list, description="Registered workflow names")
    service_bus_connection_string: Optional[str] = Field(
        None, description="Provisioned Service Bus connection string"
    )
    request_queue: str = Field(
        default="aos-orchestration-requests",
        description="Service Bus queue for orchestration requests",
    )
    result_topic: str = Field(
        default="aos-orchestration-results",
        description="Service Bus topic for orchestration results",
    )
    result_subscription: Optional[str] = Field(
        None, description="Service Bus subscription for this app's results"
    )
    status: str = Field(default="pending", description="Registration status")
    provisioned_resources: Dict[str, Any] = Field(
        default_factory=dict,
        description="Map of provisioned Azure resource IDs",
    )


class AOSRegistration:
    """Handles client application registration with AOS.

    Upon registration, AOS provisions the necessary Azure infrastructure
    for async communication: Service Bus queues, topics, subscriptions,
    and managed identity role assignments.

    Args:
        aos_endpoint: Base URL of the AOS Function App.
        credential: Azure credential for authenticated registration.
    """

    def __init__(
        self,
        aos_endpoint: str,
        credential: Optional[Any] = None,
    ) -> None:
        self.aos_endpoint = aos_endpoint.rstrip("/")
        self.credential = credential
        self._session: Optional[Any] = None

    async def __aenter__(self) -> "AOSRegistration":
        try:
            import aiohttp  # type: ignore[import-untyped]

            self._session = aiohttp.ClientSession()
        except ImportError:
            logger.warning("aiohttp not installed — registration will not work")
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def register_app(
        self,
        app_name: str,
        workflows: Optional[List[str]] = None,
        app_id: Optional[str] = None,
    ) -> AppRegistration:
        """Register a client application with AOS.

        AOS provisions the required Azure infrastructure (Service Bus
        queues, subscriptions, managed identity assignments) and returns
        connection details.

        Args:
            app_name: Unique application name.
            workflows: List of workflow names the app exposes.
            app_id: Azure AD application ID (for access control).

        Returns:
            :class:`AppRegistration` with provisioned connection details.

        Raises:
            RuntimeError: If registration fails.
        """
        if self._session is None:
            raise RuntimeError(
                "AOSRegistration must be used as an async context manager"
            )

        payload = {
            "app_name": app_name,
            "workflows": workflows or [],
            "app_id": app_id,
        }

        headers = await self._auth_headers()
        async with self._session.post(
            f"{self.aos_endpoint}/api/apps/register",
            json=payload,
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

        registration = AppRegistration(**data)
        logger.info(
            "Registered app '%s' with AOS — queue=%s subscription=%s",
            app_name,
            registration.request_queue,
            registration.result_subscription,
        )
        return registration

    async def get_app_status(self, app_name: str) -> AppRegistration:
        """Get the registration status of a client application.

        Args:
            app_name: Application name.

        Returns:
            :class:`AppRegistration` with current status.
        """
        if self._session is None:
            raise RuntimeError(
                "AOSRegistration must be used as an async context manager"
            )

        headers = await self._auth_headers()
        async with self._session.get(
            f"{self.aos_endpoint}/api/apps/{app_name}",
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

        return AppRegistration(**data)

    async def deregister_app(self, app_name: str) -> None:
        """Remove a client application registration from AOS.

        Args:
            app_name: Application name to deregister.
        """
        if self._session is None:
            raise RuntimeError(
                "AOSRegistration must be used as an async context manager"
            )

        headers = await self._auth_headers()
        async with self._session.delete(
            f"{self.aos_endpoint}/api/apps/{app_name}",
            headers=headers,
        ) as resp:
            resp.raise_for_status()

        logger.info("Deregistered app '%s' from AOS", app_name)

    async def _auth_headers(self) -> Dict[str, str]:
        if self.credential is None:
            return {}
        try:
            token = self.credential.get_token("https://management.azure.com/.default")
            return {"Authorization": f"Bearer {token.token}"}
        except Exception as exc:
            logger.warning("Failed to obtain auth token: %s", exc)
            return {}
