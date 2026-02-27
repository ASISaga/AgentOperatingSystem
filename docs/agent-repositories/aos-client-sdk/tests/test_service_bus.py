"""Tests for AOSServiceBus communication layer."""

import json
import pytest

from aos_client.service_bus import AOSServiceBus, DEFAULT_REQUEST_QUEUE, DEFAULT_RESULT_TOPIC
from aos_client.models import OrchestrationPurpose, OrchestrationStatus, OrchestrationStatusEnum


class TestAOSServiceBus:
    """AOSServiceBus unit tests."""

    def test_init_defaults(self):
        bus = AOSServiceBus()
        assert bus.connection_string is None
        assert bus.request_queue == DEFAULT_REQUEST_QUEUE
        assert bus.result_topic == DEFAULT_RESULT_TOPIC
        assert bus.app_name is None

    def test_init_custom(self):
        bus = AOSServiceBus(
            connection_string="Endpoint=sb://test.servicebus.windows.net/;SharedAccessKey=xxx",
            request_queue="custom-queue",
            result_topic="custom-topic",
            app_name="my-app",
        )
        assert bus.request_queue == "custom-queue"
        assert bus.result_topic == "custom-topic"
        assert bus.app_name == "my-app"

    def test_parse_orchestration_result_from_dict(self):
        data = {
            "payload": {
                "orchestration_id": "orch-1",
                "status": "active",
                "agent_ids": ["ceo"],
                "purpose": "Drive strategic growth",
            }
        }
        result = AOSServiceBus.parse_orchestration_result(data)
        assert isinstance(result, OrchestrationStatus)
        assert result.orchestration_id == "orch-1"
        assert result.status == OrchestrationStatusEnum.ACTIVE
        assert result.purpose == "Drive strategic growth"

    def test_parse_orchestration_result_from_json_string(self):
        data = json.dumps({
            "payload": {
                "orchestration_id": "orch-2",
                "status": "failed",
                "error": "Agent timeout",
            }
        })
        result = AOSServiceBus.parse_orchestration_result(data)
        assert result.orchestration_id == "orch-2"
        assert result.status == OrchestrationStatusEnum.FAILED

    def test_parse_orchestration_result_from_bytes(self):
        data = json.dumps({
            "payload": {
                "orchestration_id": "orch-3",
                "status": "active",
            }
        }).encode("utf-8")
        result = AOSServiceBus.parse_orchestration_result(data)
        assert result.orchestration_id == "orch-3"

    def test_parse_orchestration_status(self):
        data = {
            "payload": {
                "orchestration_id": "orch-4",
                "status": "active",
                "purpose": "Monitor market trends",
            }
        }
        status = AOSServiceBus.parse_orchestration_status(data)
        assert isinstance(status, OrchestrationStatus)
        assert status.status == OrchestrationStatusEnum.ACTIVE

    def test_build_result_message(self):
        status = OrchestrationStatus(
            orchestration_id="orch-5",
            status=OrchestrationStatusEnum.STOPPED,
            purpose="Drive growth",
        )
        message = AOSServiceBus.build_result_message(status, app_name="test-app")
        assert message["message_type"] == "orchestration_result"
        assert message["app_name"] == "test-app"
        assert message["payload"]["orchestration_id"] == "orch-5"

    @pytest.mark.asyncio
    async def test_send_requires_context_manager(self):
        from aos_client.models import OrchestrationPurpose, OrchestrationRequest

        bus = AOSServiceBus(app_name="test")
        request = OrchestrationRequest(
            agent_ids=["ceo"],
            purpose=OrchestrationPurpose(purpose="Test purpose"),
        )
        with pytest.raises(RuntimeError, match="Service Bus not available"):
            await bus.send_orchestration_request(request)
