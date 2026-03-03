"""Internal Foundry integration helpers.

These functions create Foundry service instances from the SDK's internal
modules.  They are separated so that the kernel can operate without the
SDK installed (e.g. in unit tests).
"""

from __future__ import annotations

from typing import Any, Optional


def _create_foundry_service(
    project_client: Any,
    gateway_url: Optional[str] = None,
) -> Any:
    """Create a ``FoundryAgentService`` from the SDK's internal module.

    :param project_client: An ``AIProjectClient`` instance.
    :param gateway_url: Optional AI Gateway URL.
    :returns: A ``FoundryAgentService`` instance.
    """
    from aos_client.foundry import FoundryAgentService

    return FoundryAgentService(
        project_client=project_client,
        gateway_url=gateway_url,
    )
