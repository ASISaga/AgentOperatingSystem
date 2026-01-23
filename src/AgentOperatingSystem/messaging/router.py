"""
AOS Message Router

Intelligent message router for AOS.
Routes messages based on content, agent capabilities, and routing rules.
"""

import logging
from typing import Callable, Dict

from .bus import MessageBus
from .types import Message, MessageType


class MessageRouter:
    """
    Intelligent message router for AOS.

    Routes messages based on content, agent capabilities, and routing rules.
    """

    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.routing_rules: Dict[str, Callable] = {}
        self.agent_handlers: Dict[str, Dict[str, Callable]] = {}
        self.logger = logging.getLogger("AOS.MessageRouter")

    async def register_agent(self, agent_id: str, handlers: Dict[str, Callable]):
        """Register agent message handlers"""
        self.agent_handlers[agent_id] = handlers

        # Subscribe agent to message types it can handle
        message_types = list(handlers.keys())
        await self.message_bus.subscribe(agent_id, message_types)

        self.logger.info("Registered handlers for agent %s: %s", agent_id, message_types)

    async def unregister_agent(self, agent_id: str):
        """Unregister agent handlers"""
        if agent_id in self.agent_handlers:
            del self.agent_handlers[agent_id]

        await self.message_bus.unregister_agent(agent_id)
        self.logger.info("Unregistered agent %s", agent_id)

    async def register_handler(self, message_type: str, handler: Callable):
        """Register a global message handler"""
        self.routing_rules[message_type] = handler
        self.logger.info("Registered global handler for %s", message_type)

    def add_routing_rule(self, rule_name: str, rule_func: Callable):
        """Add custom routing rule"""
        self.routing_rules[rule_name] = rule_func

    async def route_message(self, message: Message) -> bool:
        """Route message to appropriate handlers"""
        try:
            # Check for global handlers first
            if message.type.value in self.routing_rules:
                handler = self.routing_rules[message.type.value]
                await handler(message)
                return True

            # Route to specific agent handlers
            if message.to_agent and message.to_agent in self.agent_handlers:
                agent_handlers = self.agent_handlers[message.to_agent]
                if message.type.value in agent_handlers:
                    handler = agent_handlers[message.type.value]
                    await handler(message)
                    return True

            # For broadcast messages, route to all interested agents
            if message.type == MessageType.BROADCAST:
                success_count = 0
                for agent_id, handlers in self.agent_handlers.items():
                    if message.type.value in handlers:
                        try:
                            await handlers[message.type.value](message)
                            success_count += 1
                        except Exception as error:
                            self.logger.error("Error routing message to %s: %s", agent_id, str(error))

                return success_count > 0

            self.logger.warning("No handler found for message %s of type %s", message.id, message.type.value)
            return False

        except Exception as error:
            self.logger.error("Error routing message %s: %s", message.id, str(error))
            return False
