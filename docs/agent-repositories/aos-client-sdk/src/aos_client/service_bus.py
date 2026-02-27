"""Azure Service Bus async communication for AOS client applications.

Provides bidirectional message-based communication between client apps
and AOS, enabling scale-to-zero architecture where both sides sleep
and wake on Service Bus triggers.

Usage::

    from aos_client.service_bus import AOSServiceBus

    bus = AOSServiceBus(connection_string="Endpoint=sb://...")

    # Send an orchestration request
    await bus.send_orchestration_request(request)

    # Process incoming results (used by Service Bus trigger)
    result = AOSServiceBus.parse_orchestration_result(message_body)
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict, Optional

from aos_client.models import (
    OrchestrationRequest,
    OrchestrationResult,
    OrchestrationStatus,
)

logger = logging.getLogger(__name__)

#: Default queue for client → AOS orchestration requests
DEFAULT_REQUEST_QUEUE = "aos-orchestration-requests"

#: Default topic for AOS → client orchestration results
DEFAULT_RESULT_TOPIC = "aos-orchestration-results"


class AOSServiceBus:
    """Azure Service Bus communication layer for AOS applications.

    Enables async, message-based communication between client apps and
    the Agent Operating System.  Both sides can scale to zero and wake
    on Service Bus triggers.

    Args:
        connection_string: Azure Service Bus connection string.
        request_queue: Queue name for orchestration requests.
            Defaults to ``"aos-orchestration-requests"``.
        result_topic: Topic name for orchestration results.
            Defaults to ``"aos-orchestration-results"``.
        app_name: Client application name (used as subscription filter).
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        request_queue: str = DEFAULT_REQUEST_QUEUE,
        result_topic: str = DEFAULT_RESULT_TOPIC,
        app_name: Optional[str] = None,
    ) -> None:
        self.connection_string = connection_string
        self.request_queue = request_queue
        self.result_topic = result_topic
        self.app_name = app_name
        self._sender: Optional[Any] = None
        self._client: Optional[Any] = None

    async def __aenter__(self) -> "AOSServiceBus":
        if not self.connection_string:
            logger.warning("No Service Bus connection string — messages will not be sent")
            return self
        try:
            from azure.servicebus.aio import ServiceBusClient  # type: ignore[import-untyped]

            self._client = ServiceBusClient.from_connection_string(self.connection_string)
            self._sender = self._client.get_queue_sender(queue_name=self.request_queue)
        except ImportError:
            logger.warning("azure-servicebus not installed — Service Bus disabled")
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._sender:
            await self._sender.close()
            self._sender = None
        if self._client:
            await self._client.close()
            self._client = None

    async def send_orchestration_request(
        self,
        request: OrchestrationRequest,
        correlation_id: Optional[str] = None,
    ) -> str:
        """Send an orchestration request to AOS via Service Bus.

        Args:
            request: Orchestration request to submit.
            correlation_id: Optional correlation ID for tracking.

        Returns:
            Message ID for the sent message.

        Raises:
            RuntimeError: If Service Bus is not configured or available.
        """
        if request.orchestration_id is None:
            request.orchestration_id = str(uuid.uuid4())

        message_body = json.dumps({
            "message_type": "orchestration_request",
            "app_name": self.app_name,
            "payload": request.model_dump(mode="json"),
        })

        message_id = str(uuid.uuid4())

        if self._sender is None:
            raise RuntimeError(
                "Service Bus not available. Use AOSServiceBus as async context "
                "manager and provide a connection string."
            )

        try:
            from azure.servicebus import ServiceBusMessage  # type: ignore[import-untyped]

            message = ServiceBusMessage(
                body=message_body,
                message_id=message_id,
                correlation_id=correlation_id or request.orchestration_id,
                subject="orchestration_request",
                application_properties={
                    "app_name": self.app_name or "",
                    "orchestration_id": request.orchestration_id,
                    "workflow": request.workflow,
                },
            )
            await self._sender.send_messages(message)
            logger.info(
                "Sent orchestration request %s via Service Bus (message_id=%s)",
                request.orchestration_id,
                message_id,
            )
        except ImportError:
            raise RuntimeError("azure-servicebus is required for Service Bus communication")

        return message_id

    # ------------------------------------------------------------------
    # Message parsing helpers (for Service Bus trigger handlers)
    # ------------------------------------------------------------------

    @staticmethod
    def parse_orchestration_result(message_body: str | bytes | Dict[str, Any]) -> OrchestrationResult:
        """Parse an orchestration result from a Service Bus message.

        Args:
            message_body: Raw message body (JSON string, bytes, or dict).

        Returns:
            Parsed :class:`OrchestrationResult`.
        """
        if isinstance(message_body, bytes):
            message_body = message_body.decode("utf-8")
        if isinstance(message_body, str):
            data = json.loads(message_body)
        else:
            data = message_body

        payload = data.get("payload", data)
        return OrchestrationResult(**payload)

    @staticmethod
    def parse_orchestration_status(message_body: str | bytes | Dict[str, Any]) -> OrchestrationStatus:
        """Parse an orchestration status update from a Service Bus message.

        Args:
            message_body: Raw message body (JSON string, bytes, or dict).

        Returns:
            Parsed :class:`OrchestrationStatus`.
        """
        if isinstance(message_body, bytes):
            message_body = message_body.decode("utf-8")
        if isinstance(message_body, str):
            data = json.loads(message_body)
        else:
            data = message_body

        payload = data.get("payload", data)
        return OrchestrationStatus(**payload)

    @staticmethod
    def build_result_message(
        result: OrchestrationResult,
        app_name: str,
    ) -> Dict[str, Any]:
        """Build a Service Bus message body for an orchestration result.

        Used by AOS to send results back to client applications.

        Args:
            result: Completed orchestration result.
            app_name: Target client application name.

        Returns:
            Message body dictionary ready for serialization.
        """
        return {
            "message_type": "orchestration_result",
            "app_name": app_name,
            "payload": result.model_dump(mode="json"),
        }
