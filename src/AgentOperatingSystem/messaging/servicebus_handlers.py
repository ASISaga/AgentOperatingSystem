"""
AOS Service Bus Request Handlers

Handles incoming Service Bus messages and delegates to appropriate AOS components.
This module processes requests from external applications (like BusinessInfinity)
and sends back responses.
"""

import logging
from datetime import datetime
from typing import Callable, Dict

from .contracts import (
    AgentResponsePayload,
    AOSMessage,
    AOSMessageType,
    ErrorPayload,
    StorageResultPayload,
    WorkflowResultPayload,
)

logger = logging.getLogger("AOS.ServiceBusHandlers")


class AOSServiceBusHandlers:
    """
    Handles Service Bus messages for AOS operations.

    This class processes incoming requests and dispatches them to
    the appropriate AOS components.
    """

    def __init__(self, aos_instance=None):
        """
        Initialize handlers with AOS instance.

        Args:
            aos_instance: Optional AgentOperatingSystem instance
        """
        self.aos = aos_instance
        self.logger = logger
        self._handlers: Dict[str, Callable] = {}
        self._register_handlers()

    def _register_handlers(self):
        """Register message type handlers."""
        self._handlers = {
            AOSMessageType.AGENT_QUERY.value: self._handle_agent_query,
            AOSMessageType.AGENT_LIST.value: self._handle_agent_list,
            AOSMessageType.AGENT_STATUS.value: self._handle_agent_status,
            AOSMessageType.WORKFLOW_EXECUTE.value: self._handle_workflow_execute,
            AOSMessageType.WORKFLOW_STATUS.value: self._handle_workflow_status,
            AOSMessageType.STORAGE_GET.value: self._handle_storage_get,
            AOSMessageType.STORAGE_SET.value: self._handle_storage_set,
            AOSMessageType.STORAGE_DELETE.value: self._handle_storage_delete,
            AOSMessageType.STORAGE_LIST.value: self._handle_storage_list,
            AOSMessageType.MCP_CALL.value: self._handle_mcp_call,
            AOSMessageType.HEALTH_CHECK.value: self._handle_health_check,
            AOSMessageType.PING.value: self._handle_ping,
        }

    async def process_message(self, message: AOSMessage) -> AOSMessage:
        """
        Process an incoming Service Bus message.

        Args:
            message: The incoming AOSMessage

        Returns:
            Response AOSMessage
        """
        message_type = message.header.message_type
        handler = self._handlers.get(message_type)

        if not handler:
            self.logger.warning("No handler for message type: %s", message_type)
            return self._create_error_response(
                message,
                "UNKNOWN_MESSAGE_TYPE",
                f"No handler for message type: {message_type}"
            )

        try:
            self.logger.info("Processing message: %s (id=%s)", message_type, message.header.message_id)
            return await handler(message)
        except Exception as error:
            self.logger.error("Error processing message %s: %s", message_type, str(error))
            return self._create_error_response(
                message,
                "PROCESSING_ERROR",
                str(error)
            )

    def _create_error_response(
        self,
        original: AOSMessage,
        error_code: str,
        error_message: str
    ) -> AOSMessage:
        """Create an error response message."""
        return AOSMessage.create_response(
            original,
            AOSMessageType.ERROR,
            ErrorPayload(
                error_code=error_code,
                error_message=error_message
            ).to_dict(),
            source="aos"
        )

    # Agent Handlers

    async def _handle_agent_query(self, message: AOSMessage) -> AOSMessage:
        """Handle agent query request."""
        payload = message.payload
        agent_id = payload.get("agent_id")
        query = payload.get("query", "")
        context = payload.get("context", {})

        try:
            if self.aos:
                # Get agent from AOS
                agent = self.aos.get_agent(agent_id) if hasattr(self.aos, 'get_agent') else None

                if agent:
                    # Process query through agent
                    if hasattr(agent, 'process_query'):
                        result = await agent.process_query(query, context)
                    elif hasattr(agent, 'ask'):
                        result = await agent.ask(query, context)
                    else:
                        result = {"response": f"Agent {agent_id} processed query", "query": query}

                    response_payload = AgentResponsePayload(
                        agent_id=agent_id,
                        response=result.get("response", str(result)),
                        confidence=result.get("confidence", 0.8),
                        sources=result.get("sources", []),
                        metadata=result.get("metadata", {})
                    )
                else:
                    response_payload = AgentResponsePayload(
                        agent_id=agent_id,
                        response="",
                        error=f"Agent not found: {agent_id}"
                    )
            else:
                # Mock response when AOS not available
                response_payload = AgentResponsePayload(
                    agent_id=agent_id,
                    response=f"Mock response to: {query}",
                    confidence=0.5,
                    metadata={"mock": True}
                )

            return AOSMessage.create_response(
                message,
                AOSMessageType.AGENT_RESPONSE,
                response_payload.to_dict(),
                source="aos"
            )

        except Exception as error:
            self.logger.error("Agent query error: %s", str(error))
            return self._create_error_response(message, "AGENT_QUERY_ERROR", str(error))

    async def _handle_agent_list(self, message: AOSMessage) -> AOSMessage:
        """Handle agent list request."""
        try:
            if self.aos and hasattr(self.aos, 'list_agents'):
                agents = self.aos.list_agents()
            else:
                # Default agents
                agents = [
                    {"id": "ceo", "name": "CEO Agent", "status": "available"},
                    {"id": "cto", "name": "CTO Agent", "status": "available"},
                    {"id": "cfo", "name": "CFO Agent", "status": "available"},
                ]

            return AOSMessage.create_response(
                message,
                AOSMessageType.AGENT_STATUS,
                {"agents": agents},
                source="aos"
            )
        except Exception as error:
            return self._create_error_response(message, "AGENT_LIST_ERROR", str(error))

    async def _handle_agent_status(self, message: AOSMessage) -> AOSMessage:
        """Handle agent status request."""
        agent_id = message.payload.get("agent_id")

        try:
            if self.aos and hasattr(self.aos, 'get_agent_status'):
                status = self.aos.get_agent_status(agent_id)
            else:
                status = {"agent_id": agent_id, "status": "available", "load": 0.0}

            return AOSMessage.create_response(
                message,
                AOSMessageType.AGENT_STATUS,
                status,
                source="aos"
            )
        except Exception as error:
            return self._create_error_response(message, "AGENT_STATUS_ERROR", str(error))

    # Workflow Handlers

    async def _handle_workflow_execute(self, message: AOSMessage) -> AOSMessage:
        """Handle workflow execution request."""
        payload = message.payload
        workflow_id = payload.get("workflow_id")
        workflow_name = payload.get("workflow_name")
        inputs = payload.get("inputs", {})

        try:
            start_time = datetime.utcnow()

            if self.aos and hasattr(self.aos, 'execute_workflow'):
                result = await self.aos.execute_workflow(workflow_name, inputs)
                status = "completed"
                outputs = result
                error = None
            else:
                # Mock workflow execution
                outputs = {"result": f"Workflow {workflow_name} executed", "inputs": inputs}
                status = "completed"
                error = None

            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            response_payload = WorkflowResultPayload(
                workflow_id=workflow_id,
                status=status,
                outputs=outputs,
                error=error,
                execution_time_ms=execution_time
            )

            return AOSMessage.create_response(
                message,
                AOSMessageType.WORKFLOW_RESULT,
                response_payload.to_dict(),
                source="aos"
            )

        except Exception as error:
            self.logger.error("Workflow execution error: %s", str(error))
            return AOSMessage.create_response(
                message,
                AOSMessageType.WORKFLOW_RESULT,
                WorkflowResultPayload(
                    workflow_id=workflow_id,
                    status="failed",
                    error=str(error)
                ).to_dict(),
                source="aos"
            )

    async def _handle_workflow_status(self, message: AOSMessage) -> AOSMessage:
        """Handle workflow status request."""
        workflow_id = message.payload.get("workflow_id")

        try:
            if self.aos and hasattr(self.aos, 'get_workflow_status'):
                status = self.aos.get_workflow_status(workflow_id)
            else:
                status = {"workflow_id": workflow_id, "status": "unknown"}

            return AOSMessage.create_response(
                message,
                AOSMessageType.WORKFLOW_STATUS,
                status,
                source="aos"
            )
        except Exception as error:
            return self._create_error_response(message, "WORKFLOW_STATUS_ERROR", str(error))

    # Storage Handlers

    async def _handle_storage_get(self, message: AOSMessage) -> AOSMessage:
        """Handle storage get request."""
        payload = message.payload
        container = payload.get("container", "default")
        key = payload.get("key")

        try:
            if self.aos and hasattr(self.aos, 'storage_manager'):
                data = await self.aos.storage_manager.get(container, key)
                success = data is not None
            else:
                data = None
                success = False

            return AOSMessage.create_response(
                message,
                AOSMessageType.STORAGE_RESULT,
                StorageResultPayload(
                    operation="get",
                    success=success,
                    data=data
                ).to_dict(),
                source="aos"
            )
        except Exception as error:
            return self._create_error_response(message, "STORAGE_GET_ERROR", str(error))

    async def _handle_storage_set(self, message: AOSMessage) -> AOSMessage:
        """Handle storage set request."""
        payload = message.payload
        container = payload.get("container", "default")
        key = payload.get("key")
        value = payload.get("value")

        try:
            if self.aos and hasattr(self.aos, 'storage_manager'):
                await self.aos.storage_manager.set(container, key, value)
                success = True
            else:
                success = True  # Mock success

            return AOSMessage.create_response(
                message,
                AOSMessageType.STORAGE_RESULT,
                StorageResultPayload(
                    operation="set",
                    success=success
                ).to_dict(),
                source="aos"
            )
        except Exception as error:
            return self._create_error_response(message, "STORAGE_SET_ERROR", str(error))

    async def _handle_storage_delete(self, message: AOSMessage) -> AOSMessage:
        """Handle storage delete request."""
        payload = message.payload
        container = payload.get("container", "default")
        key = payload.get("key")

        try:
            if self.aos and hasattr(self.aos, 'storage_manager'):
                await self.aos.storage_manager.delete(container, key)
                success = True
            else:
                success = True  # Mock success

            return AOSMessage.create_response(
                message,
                AOSMessageType.STORAGE_RESULT,
                StorageResultPayload(
                    operation="delete",
                    success=success
                ).to_dict(),
                source="aos"
            )
        except Exception as error:
            return self._create_error_response(message, "STORAGE_DELETE_ERROR", str(error))

    async def _handle_storage_list(self, message: AOSMessage) -> AOSMessage:
        """Handle storage list request."""
        payload = message.payload
        container = payload.get("container", "default")
        prefix = payload.get("prefix", "")

        try:
            if self.aos and hasattr(self.aos, 'storage_manager'):
                keys = await self.aos.storage_manager.list(container, prefix)
            else:
                keys = []

            return AOSMessage.create_response(
                message,
                AOSMessageType.STORAGE_RESULT,
                StorageResultPayload(
                    operation="list",
                    success=True,
                    keys=keys
                ).to_dict(),
                source="aos"
            )
        except Exception as error:
            return self._create_error_response(message, "STORAGE_LIST_ERROR", str(error))

    # MCP Handlers

    async def _handle_mcp_call(self, message: AOSMessage) -> AOSMessage:
        """Handle MCP call request."""
        payload = message.payload
        server_name = payload.get("server")
        method = payload.get("method")
        args = payload.get("args", {})

        try:
            if self.aos and hasattr(self.aos, 'mcp_client_manager'):
                result = await self.aos.mcp_client_manager.call(server_name, method, args)
            else:
                result = {"mock": True, "server": server_name, "method": method}

            return AOSMessage.create_response(
                message,
                AOSMessageType.MCP_RESULT,
                {"result": result},
                source="aos"
            )
        except Exception as error:
            return self._create_error_response(message, "MCP_CALL_ERROR", str(error))

    # System Handlers

    async def _handle_health_check(self, message: AOSMessage) -> AOSMessage:
        """Handle health check request."""
        try:
            if self.aos:
                health = {
                    "status": "healthy",
                    "aos_version": getattr(self.aos, 'version', '1.0.0'),
                    "timestamp": datetime.utcnow().isoformat(),
                    "components": {
                        "storage": self.aos.storage_manager is not None if hasattr(self.aos, 'storage_manager') else False,
                        "messaging": True,
                        "agents": True
                    }
                }
            else:
                health = {
                    "status": "degraded",
                    "message": "AOS instance not available",
                    "timestamp": datetime.utcnow().isoformat()
                }

            return AOSMessage.create_response(
                message,
                AOSMessageType.HEALTH_RESPONSE,
                health,
                source="aos"
            )
        except Exception as error:
            return self._create_error_response(message, "HEALTH_CHECK_ERROR", str(error))

    async def _handle_ping(self, message: AOSMessage) -> AOSMessage:
        """Handle ping request."""
        return AOSMessage.create_response(
            message,
            AOSMessageType.PONG,
            {"pong": True, "timestamp": datetime.utcnow().isoformat()},
            source="aos"
        )


__all__ = ["AOSServiceBusHandlers"]
