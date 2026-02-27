"""Tests for AOSServiceBus communication layer."""

import json
import pytest

from aos_client.service_bus import AOSServiceBus, DEFAULT_REQUEST_QUEUE, DEFAULT_RESULT_TOPIC
from aos_client.models import OrchestrationResult, OrchestrationStatus, OrchestrationStatusEnum


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
                "status": "completed",
                "agent_ids": ["ceo"],
                "results": {"ceo": {"decision": "approve"}},
                "summary": "Approved",
            }
        }
        result = AOSServiceBus.parse_orchestration_result(data)
        assert isinstance(result, OrchestrationResult)
        assert result.orchestration_id == "orch-1"
        assert result.status == OrchestrationStatusEnum.COMPLETED
        assert result.summary == "Approved"

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
                "status": "completed",
            }
        }).encode("utf-8")
        result = AOSServiceBus.parse_orchestration_result(data)
        assert result.orchestration_id == "orch-3"

    def test_parse_orchestration_status(self):
        data = {
            "payload": {
                "orchestration_id": "orch-4",
                "status": "running",
                "progress": 0.5,
            }
        }
        status = AOSServiceBus.parse_orchestration_status(data)
        assert isinstance(status, OrchestrationStatus)
        assert status.status == OrchestrationStatusEnum.RUNNING
        assert status.progress == 0.5

    def test_build_result_message(self):
        result = OrchestrationResult(
            orchestration_id="orch-5",
            status=OrchestrationStatusEnum.COMPLETED,
            summary="Done",
        )
        message = AOSServiceBus.build_result_message(result, app_name="test-app")
        assert message["message_type"] == "orchestration_result"
        assert message["app_name"] == "test-app"
        assert message["payload"]["orchestration_id"] == "orch-5"

    @pytest.mark.asyncio
    async def test_send_requires_context_manager(self):
        from aos_client.models import OrchestrationRequest

        bus = AOSServiceBus(app_name="test")
        request = OrchestrationRequest(agent_ids=["ceo"], task={"type": "test"})
        with pytest.raises(RuntimeError, match="Service Bus not available"):
            await bus.send_orchestration_request(request)
