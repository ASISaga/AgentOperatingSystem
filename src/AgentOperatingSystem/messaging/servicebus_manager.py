"""
Azure Service Bus Management Utilities for AOS

Provides management utilities for Azure Service Bus topics and subscriptions.
"""

import os
import logging
from typing import Optional

try:
    from azure.servicebus.aio import ServiceBusAdministrationClient
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
        self.connection_str = connection_str or os.getenv('SERVICE_BUS_CONNECTION_STRING')
        
        if not AZURE_SERVICE_BUS_AVAILABLE:
            self.logger.warning("Azure Service Bus SDK not available")
            self.admin_client = None
            return
        
        if not self.connection_str:
            self.logger.warning("No Service Bus connection string provided")
            self.admin_client = None
            return
        
        try:
            self.admin_client = ServiceBusAdministrationClient.from_connection_string(self.connection_str)
            self.logger.info("Service Bus Administration Client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Service Bus Administration Client: {e}")
            self.admin_client = None
    
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