
# Azure Service Bus MCP Client for AOS
import os
import asyncio
from typing import Any, Dict, Optional
from azure.servicebus.aio import ServiceBusClient, ServiceBusSender, ServiceBusReceiver
from azure.servicebus import ServiceBusMessage
import json
from .mcp_protocol import MCPRequest, MCPResponse


class MCPServiceBusClient:
    """
    Unified MCP client for AOS: supports Azure Service Bus communication and local handler registry/dispatch.
    """
    def __init__(self, connection_str: str, topic_name: str, subscription_name: Optional[str] = None):
        self.connection_str = connection_str
        self.topic_name = topic_name
        self.subscription_name = subscription_name
        self.client = ServiceBusClient.from_connection_string(self.connection_str)
        self.method_handlers = {}

    # Service Bus send/receive
    async def send_message(self, message: Dict[str, Any]):
        async with self.client:
            sender = self.client.get_topic_sender(topic_name=self.topic_name)
            async with sender:
                msg = ServiceBusMessage(json.dumps(message))
                await sender.send_messages(msg)

    async def receive_messages(self, max_messages: int = 1, timeout: int = 5):
        if not self.subscription_name:
            raise ValueError("Subscription name required for receiving messages.")
        async with self.client:
            receiver = self.client.get_subscription_receiver(
                topic_name=self.topic_name,
                subscription_name=self.subscription_name
            )
            async with receiver:
                received_msgs = await receiver.receive_messages(max_message_count=max_messages, max_wait_time=timeout)
                results = []
                for msg in received_msgs:
                    results.append(json.loads(str(msg)))
                    await receiver.complete_message(msg)
                return results

    # Local handler registry/dispatch (for in-process or test use)
    def register_method(self, method_name: str, handler):
        self.method_handlers[method_name] = handler

    async def handle_mcp_request(self, body: dict) -> dict:
        """
        Dispatch an MCP request to a registered handler (if any).
        """
        method = body.get("method")
        params = body.get("params", {})
        id_ = body.get("id")
        if not method:
            return {
                "jsonrpc": "2.0",
                "id": id_,
                "error": {"code": -32600, "message": "Invalid request - method required"}
            }
        try:
            handler = self.method_handlers.get(method)
            if handler:
                return await handler(params, id_)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": id_,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": id_,
                "error": {"code": -32000, "message": str(e)}
            }

# Usage example (to be used in AOS orchestrator or agent):
# sb_client = MCPServiceBusClient(os.getenv('SERVICE_BUS_CONNECTION_STRING'), 'mcp-topic', 'aos-sub')
# await sb_client.send_message({'method': 'ping', 'params': {}, 'id': '1'})
# msgs = await sb_client.receive_messages()
