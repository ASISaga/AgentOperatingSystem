# Azure Service Bus Management Utilities for AOS
import os
from typing import Optional
from azure.servicebus.aio import ServiceBusAdministrationClient

class ServiceBusManager:
    def __init__(self, connection_str: Optional[str] = None):
        self.connection_str = connection_str or os.getenv('SERVICE_BUS_CONNECTION_STRING')
        self.admin_client = ServiceBusAdministrationClient.from_connection_string(self.connection_str)

    async def create_topic(self, topic_name: str):
        if not await self.admin_client.get_topic_runtime_properties(topic_name):
            await self.admin_client.create_topic(topic_name)

    async def create_subscription(self, topic_name: str, subscription_name: str):
        if not await self.admin_client.get_subscription_runtime_properties(topic_name, subscription_name):
            await self.admin_client.create_subscription(topic_name, subscription_name)

    async def delete_topic(self, topic_name: str):
        await self.admin_client.delete_topic(topic_name)

    async def delete_subscription(self, topic_name: str, subscription_name: str):
        await self.admin_client.delete_subscription(topic_name, subscription_name)

# Usage example:
# sb_manager = ServiceBusManager()
# await sb_manager.create_topic('mcp-topic')
# await sb_manager.create_subscription('mcp-topic', 'aos-sub')
