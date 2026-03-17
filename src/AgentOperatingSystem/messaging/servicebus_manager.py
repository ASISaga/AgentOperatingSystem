"""
Azure Service Bus Management Utilities for AOS

Provides management utilities for Azure Service Bus topics and subscriptions.
"""

import os
import logging
from typing import Optional

try:
    from azure.servicebus.aio import ServiceBusAdministrationClient, ServiceBusClient
    from azure.servicebus import ServiceBusMessage
    from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
    AZURE_SERVICE_BUS_AVAILABLE = True
except ImportError:
    AZURE_SERVICE_BUS_AVAILABLE = False
    logging.warning("Azure Service Bus SDK not available")


class ServiceBusManager:
    """
    Azure Service Bus management utilities.

    Handles creation and management of topics, subscriptions, and queues.
    """

    def __init__(self, connection_str: Optional[str] = None):
        self.logger = logging.getLogger("AOS.ServiceBusManager")
        self.connection_str = connection_str or os.getenv('SERVICE_BUS_CONNECTION_STRING') or os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')

        if not AZURE_SERVICE_BUS_AVAILABLE:
            self.logger.warning("Azure Service Bus SDK not available")
            self.admin_client = None
            self.client = None
            return

        if not self.connection_str:
            self.logger.warning("No Service Bus connection string provided")
            self.admin_client = None
            self.client = None
            return

        try:
            self.admin_client = ServiceBusAdministrationClient.from_connection_string(self.connection_str)
            self.client = ServiceBusClient.from_connection_string(self.connection_str)
            self.logger.info("Service Bus clients initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Service Bus clients: {e}")
            self.admin_client = None
            self.client = None

    async def create_topic(self, topic_name: str) -> bool:
        """
        Create a Service Bus topic if it doesn't exist.

        Args:
            topic_name: Name of the topic to create

        Returns:
            True if created or already exists, False on error
        """
        if not self.admin_client:
            self.logger.error("Service Bus Administration Client not available")
            return False

        try:
            # Check if topic already exists
            await self.admin_client.get_topic_runtime_properties(topic_name)
            self.logger.debug(f"Topic '{topic_name}' already exists")
            return True

        except ResourceNotFoundError:
            # Topic doesn't exist, create it
            try:
                await self.admin_client.create_topic(topic_name)
                self.logger.info(f"Created topic '{topic_name}'")
                return True
            except ResourceExistsError:
                # Topic was created by another process
                self.logger.debug(f"Topic '{topic_name}' was created by another process")
                return True
            except Exception as e:
                self.logger.error(f"Failed to create topic '{topic_name}': {e}")
                return False
        except Exception as e:
            self.logger.error(f"Error checking topic '{topic_name}': {e}")
            return False

    async def create_subscription(self, topic_name: str, subscription_name: str) -> bool:
        """
        Create a Service Bus subscription if it doesn't exist.

        Args:
            topic_name: Name of the topic
            subscription_name: Name of the subscription to create

        Returns:
            True if created or already exists, False on error
        """
        if not self.admin_client:
            self.logger.error("Service Bus Administration Client not available")
            return False

        try:
            # Check if subscription already exists
            await self.admin_client.get_subscription_runtime_properties(topic_name, subscription_name)
            self.logger.debug(f"Subscription '{subscription_name}' on topic '{topic_name}' already exists")
            return True

        except ResourceNotFoundError:
            # Subscription doesn't exist, create it
            try:
                await self.admin_client.create_subscription(topic_name, subscription_name)
                self.logger.info(f"Created subscription '{subscription_name}' on topic '{topic_name}'")
                return True
            except ResourceExistsError:
                # Subscription was created by another process
                self.logger.debug(f"Subscription '{subscription_name}' was created by another process")
                return True
            except Exception as e:
                self.logger.error(f"Failed to create subscription '{subscription_name}' on topic '{topic_name}': {e}")
                return False
        except Exception as e:
            self.logger.error(f"Error checking subscription '{subscription_name}' on topic '{topic_name}': {e}")
            return False

    async def delete_topic(self, topic_name: str) -> bool:
        """
        Delete a Service Bus topic.

        Args:
            topic_name: Name of the topic to delete

        Returns:
            True if deleted or doesn't exist, False on error
        """
        if not self.admin_client:
            self.logger.error("Service Bus Administration Client not available")
            return False

        try:
            await self.admin_client.delete_topic(topic_name)
            self.logger.info(f"Deleted topic '{topic_name}'")
            return True
        except ResourceNotFoundError:
            self.logger.debug(f"Topic '{topic_name}' doesn't exist")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete topic '{topic_name}': {e}")
            return False

    async def delete_subscription(self, topic_name: str, subscription_name: str) -> bool:
        """
        Delete a Service Bus subscription.

        Args:
            topic_name: Name of the topic
            subscription_name: Name of the subscription to delete

        Returns:
            True if deleted or doesn't exist, False on error
        """
        if not self.admin_client:
            self.logger.error("Service Bus Administration Client not available")
            return False

        try:
            await self.admin_client.delete_subscription(topic_name, subscription_name)
            self.logger.info(f"Deleted subscription '{subscription_name}' from topic '{topic_name}'")
            return True
        except ResourceNotFoundError:
            self.logger.debug(f"Subscription '{subscription_name}' on topic '{topic_name}' doesn't exist")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete subscription '{subscription_name}' from topic '{topic_name}': {e}")
            return False

    async def list_topics(self) -> list:
        """
        List all topics in the Service Bus namespace.

        Returns:
            List of topic names
        """
        if not self.admin_client:
            self.logger.error("Service Bus Administration Client not available")
            return []

        try:
            topics = []
            async for topic in self.admin_client.list_topics():
                topics.append(topic.name)
            return topics
        except Exception as e:
            self.logger.error(f"Failed to list topics: {e}")
            return []

    async def list_subscriptions(self, topic_name: str) -> list:
        """
        List all subscriptions for a topic.

        Args:
            topic_name: Name of the topic

        Returns:
            List of subscription names
        """
        if not self.admin_client:
            self.logger.error("Service Bus Administration Client not available")
            return []

        try:
            subscriptions = []
            async for subscription in self.admin_client.list_subscriptions(topic_name):
                subscriptions.append(subscription.subscription_name)
            return subscriptions
        except Exception as e:
            self.logger.error(f"Failed to list subscriptions for topic '{topic_name}': {e}")
            return []

    async def get_topic_info(self, topic_name: str) -> dict:
        """
        Get information about a topic.

        Args:
            topic_name: Name of the topic

        Returns:
            Dictionary with topic information
        """
        if not self.admin_client:
            return {"error": "Service Bus Administration Client not available"}

        try:
            properties = await self.admin_client.get_topic_runtime_properties(topic_name)
            return {
                "name": topic_name,
                "active_message_count": properties.active_message_count,
                "dead_letter_message_count": properties.dead_letter_message_count,
                "scheduled_message_count": properties.scheduled_message_count,
                "transfer_message_count": properties.transfer_message_count,
                "size_in_bytes": properties.size_in_bytes,
                "subscription_count": properties.subscription_count
            }
        except Exception as e:
            self.logger.error(f"Failed to get topic info for '{topic_name}': {e}")
            return {"error": str(e)}

    def is_available(self) -> bool:
        """Check if Service Bus management is available"""
        return AZURE_SERVICE_BUS_AVAILABLE and self.admin_client is not None

    # === Messaging Operations ===

    async def send_message(self, queue_or_topic_name: str, message_content: str, properties: dict = None) -> bool:
        """
        Send message to a Service Bus queue or topic.

        Args:
            queue_or_topic_name: Name of the queue or topic
            message_content: Message content (string or JSON)
            properties: Optional message properties

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.client:
            self.logger.error("Service Bus client not available")
            return False

        try:
            # Create message
            message = ServiceBusMessage(message_content)

            # Add properties if provided
            if properties:
                for key, value in properties.items():
                    message.application_properties[key] = value

            # Try to send to queue first, then topic
            try:
                async with self.client.get_queue_sender(queue_or_topic_name) as sender:
                    await sender.send_messages(message)
                self.logger.info(f"Sent message to queue '{queue_or_topic_name}'")
                return True
            except Exception:
                # Try as topic
                async with self.client.get_topic_sender(queue_or_topic_name) as sender:
                    await sender.send_messages(message)
                self.logger.info(f"Sent message to topic '{queue_or_topic_name}'")
                return True

        except Exception as e:
            self.logger.error(f"Failed to send message to '{queue_or_topic_name}': {e}")
            return False

    async def receive_messages(self, queue_or_subscription_name: str, topic_name: str = None, max_messages: int = 1, max_wait_time: float = 5.0) -> list:
        """
        Receive messages from a Service Bus queue or subscription.

        Args:
            queue_or_subscription_name: Queue name or subscription name
            topic_name: Topic name (required if receiving from subscription)
            max_messages: Maximum number of messages to receive
            max_wait_time: Maximum wait time in seconds

        Returns:
            List of received messages
        """
        if not self.client:
            self.logger.error("Service Bus client not available")
            return []

        try:
            messages = []

            if topic_name:
                # Receive from subscription
                async with self.client.get_subscription_receiver(topic_name, queue_or_subscription_name) as receiver:
                    received_msgs = await receiver.receive_messages(max_message_count=max_messages, max_wait_time=max_wait_time)

                    for msg in received_msgs:
                        messages.append({
                            "message_id": msg.message_id,
                            "content": str(msg),
                            "enqueued_time": msg.enqueued_time_utc.isoformat() if msg.enqueued_time_utc else None,
                            "delivery_count": msg.delivery_count,
                            "properties": dict(msg.application_properties) if msg.application_properties else {}
                        })

                        # Complete the message
                        await receiver.complete_message(msg)
            else:
                # Receive from queue
                async with self.client.get_queue_receiver(queue_or_subscription_name) as receiver:
                    received_msgs = await receiver.receive_messages(max_message_count=max_messages, max_wait_time=max_wait_time)

                    for msg in received_msgs:
                        messages.append({
                            "message_id": msg.message_id,
                            "content": str(msg),
                            "enqueued_time": msg.enqueued_time_utc.isoformat() if msg.enqueued_time_utc else None,
                            "delivery_count": msg.delivery_count,
                            "properties": dict(msg.application_properties) if msg.application_properties else {}
                        })

                        # Complete the message
                        await receiver.complete_message(msg)

            self.logger.info(f"Received {len(messages)} messages")
            return messages

        except Exception as e:
            self.logger.error(f"Failed to receive messages: {e}")
            return []

    async def peek_messages(self, queue_or_subscription_name: str, topic_name: str = None, max_messages: int = 1) -> list:
        """
        Peek messages from a Service Bus queue or subscription without receiving them.

        Args:
            queue_or_subscription_name: Queue name or subscription name
            topic_name: Topic name (required if peeking subscription)
            max_messages: Maximum number of messages to peek

        Returns:
            List of peeked messages
        """
        if not self.client:
            self.logger.error("Service Bus client not available")
            return []

        try:
            messages = []

            if topic_name:
                # Peek from subscription
                async with self.client.get_subscription_receiver(topic_name, queue_or_subscription_name) as receiver:
                    peeked_msgs = await receiver.peek_messages(max_message_count=max_messages)

                    for msg in peeked_msgs:
                        messages.append({
                            "message_id": msg.message_id,
                            "content": str(msg),
                            "enqueued_time": msg.enqueued_time_utc.isoformat() if msg.enqueued_time_utc else None,
                            "delivery_count": msg.delivery_count,
                            "properties": dict(msg.application_properties) if msg.application_properties else {}
                        })
            else:
                # Peek from queue
                async with self.client.get_queue_receiver(queue_or_subscription_name) as receiver:
                    peeked_msgs = await receiver.peek_messages(max_message_count=max_messages)

                    for msg in peeked_msgs:
                        messages.append({
                            "message_id": msg.message_id,
                            "content": str(msg),
                            "enqueued_time": msg.enqueued_time_utc.isoformat() if msg.enqueued_time_utc else None,
                            "delivery_count": msg.delivery_count,
                            "properties": dict(msg.application_properties) if msg.application_properties else {}
                        })

            self.logger.info(f"Peeked {len(messages)} messages")
            return messages

        except Exception as e:
            self.logger.error(f"Failed to peek messages: {e}")
            return []

    def get_messaging_status(self) -> dict:
        """Get Service Bus messaging status"""
        return {
            "available": AZURE_SERVICE_BUS_AVAILABLE,
            "admin_client_ready": self.admin_client is not None,
            "messaging_client_ready": self.client is not None,
            "connection_configured": self.connection_str is not None
        }