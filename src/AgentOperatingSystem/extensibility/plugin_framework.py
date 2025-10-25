"""
Plugin Framework for AgentOperatingSystem

Enables registration and management of plugins including new policies,
connectors, message types, and hot-swappable adapters.
"""

from typing import Dict, Any, List, Optional, Callable, Type
from datetime import datetime
from abc import ABC, abstractmethod
import logging
from enum import Enum
import importlib
import inspect


class PluginType(str, Enum):
    """Types of plugins that can be registered"""
    POLICY = "policy"
    CONNECTOR = "connector"
    MESSAGE_TYPE = "message_type"
    ADAPTER = "adapter"
    HANDLER = "handler"
    VALIDATOR = "validator"


class PluginStatus(str, Enum):
    """Status of a plugin"""
    REGISTERED = "registered"
    LOADED = "loaded"
    ACTIVE = "active"
    DISABLED = "disabled"
    FAILED = "failed"


class Plugin(ABC):
    """
    Base class for all plugins.
    
    All plugins must extend this class and implement the required methods.
    """
    
    def __init__(self, plugin_id: str, name: str, version: str):
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self.status = PluginStatus.REGISTERED
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """
        Shutdown the plugin gracefully.
        
        Returns:
            True if shutdown successful
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities provided by this plugin.
        
        Returns:
            List of capability names
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information.
        
        Returns:
            Dictionary with plugin details
        """
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "capabilities": self.get_capabilities(),
            "metadata": self.metadata
        }


class PolicyPlugin(Plugin):
    """
    Base class for policy plugins.
    
    Policy plugins can add new policy rules, validators, and enforcers.
    """
    
    @abstractmethod
    async def evaluate_policy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate policy against given context.
        
        Args:
            context: Context to evaluate
            
        Returns:
            Evaluation result with decision and rationale
        """
        pass


class ConnectorPlugin(Plugin):
    """
    Base class for connector plugins.
    
    Connector plugins enable integration with external systems.
    """
    
    @abstractmethod
    async def connect(self, config: Dict[str, Any]) -> bool:
        """
        Establish connection to external system.
        
        Args:
            config: Connection configuration
            
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from external system.
        
        Returns:
            True if disconnection successful
        """
        pass
    
    @abstractmethod
    async def send(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send data to external system.
        
        Args:
            data: Data to send
            
        Returns:
            Response from external system
        """
        pass
    
    @abstractmethod
    async def receive(self) -> Optional[Dict[str, Any]]:
        """
        Receive data from external system.
        
        Returns:
            Received data or None
        """
        pass


class MessageTypePlugin(Plugin):
    """
    Base class for message type plugins.
    
    Message type plugins define new message types and their schemas.
    """
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for this message type.
        
        Returns:
            JSON schema definition
        """
        pass
    
    @abstractmethod
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Validate a message against this type's schema.
        
        Args:
            message: Message to validate
            
        Returns:
            True if valid
        """
        pass


class PluginRegistry:
    """
    Registry for managing plugins.
    
    Handles registration, loading, activation, and lifecycle management
    of all plugins in the system.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.Extensibility.PluginRegistry")
        self.plugins: Dict[str, Plugin] = {}
        self.plugins_by_type: Dict[PluginType, List[str]] = {
            plugin_type: [] for plugin_type in PluginType
        }
        self.plugin_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_plugin(
        self,
        plugin: Plugin,
        plugin_type: PluginType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a plugin with the system.
        
        Args:
            plugin: Plugin instance to register
            plugin_type: Type of plugin
            metadata: Optional metadata about the plugin
            
        Returns:
            True if registration successful
        """
        try:
            if plugin.plugin_id in self.plugins:
                self.logger.warning(f"Plugin already registered: {plugin.plugin_id}")
                return False
            
            self.plugins[plugin.plugin_id] = plugin
            self.plugins_by_type[plugin_type].append(plugin.plugin_id)
            
            if metadata:
                plugin.metadata.update(metadata)
                self.plugin_metadata[plugin.plugin_id] = metadata
            
            plugin.status = PluginStatus.REGISTERED
            
            self.logger.info(
                f"Registered plugin: {plugin.name} ({plugin.plugin_id}) "
                f"type: {plugin_type.value}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register plugin {plugin.plugin_id}: {e}")
            return False
    
    async def load_plugin(self, plugin_id: str) -> bool:
        """
        Load a registered plugin.
        
        Args:
            plugin_id: ID of plugin to load
            
        Returns:
            True if loading successful
        """
        if plugin_id not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin = self.plugins[plugin_id]
        
        try:
            if await plugin.initialize():
                plugin.status = PluginStatus.LOADED
                self.logger.info(f"Loaded plugin: {plugin.name} ({plugin_id})")
                return True
            else:
                plugin.status = PluginStatus.FAILED
                self.logger.error(f"Failed to initialize plugin: {plugin_id}")
                return False
                
        except Exception as e:
            plugin.status = PluginStatus.FAILED
            self.logger.error(f"Error loading plugin {plugin_id}: {e}")
            return False
    
    async def activate_plugin(self, plugin_id: str) -> bool:
        """
        Activate a loaded plugin.
        
        Args:
            plugin_id: ID of plugin to activate
            
        Returns:
            True if activation successful
        """
        if plugin_id not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin = self.plugins[plugin_id]
        
        if plugin.status != PluginStatus.LOADED:
            self.logger.error(
                f"Cannot activate plugin {plugin_id}: "
                f"status is {plugin.status.value}, must be loaded"
            )
            return False
        
        try:
            plugin.status = PluginStatus.ACTIVE
            self.logger.info(f"Activated plugin: {plugin.name} ({plugin_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error activating plugin {plugin_id}: {e}")
            return False
    
    async def deactivate_plugin(self, plugin_id: str) -> bool:
        """
        Deactivate an active plugin.
        
        Args:
            plugin_id: ID of plugin to deactivate
            
        Returns:
            True if deactivation successful
        """
        if plugin_id not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin = self.plugins[plugin_id]
        
        if plugin.status != PluginStatus.ACTIVE:
            self.logger.warning(f"Plugin not active: {plugin_id}")
            return True
        
        try:
            plugin.status = PluginStatus.DISABLED
            self.logger.info(f"Deactivated plugin: {plugin.name} ({plugin_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deactivating plugin {plugin_id}: {e}")
            return False
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_id: ID of plugin to unload
            
        Returns:
            True if unloading successful
        """
        if plugin_id not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin = self.plugins[plugin_id]
        
        try:
            # Deactivate if active
            if plugin.status == PluginStatus.ACTIVE:
                await self.deactivate_plugin(plugin_id)
            
            # Shutdown the plugin
            await plugin.shutdown()
            
            # Remove from registry
            del self.plugins[plugin_id]
            
            # Remove from type index
            for plugin_type, plugin_ids in self.plugins_by_type.items():
                if plugin_id in plugin_ids:
                    plugin_ids.remove(plugin_id)
            
            if plugin_id in self.plugin_metadata:
                del self.plugin_metadata[plugin_id]
            
            self.logger.info(f"Unloaded plugin: {plugin.name} ({plugin_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        Get a plugin by ID.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_id)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """
        Get all plugins of a specific type.
        
        Args:
            plugin_type: Type of plugins to retrieve
            
        Returns:
            List of plugin instances
        """
        plugin_ids = self.plugins_by_type.get(plugin_type, [])
        return [self.plugins[pid] for pid in plugin_ids if pid in self.plugins]
    
    def get_active_plugins(self) -> List[Plugin]:
        """
        Get all active plugins.
        
        Returns:
            List of active plugin instances
        """
        return [
            plugin for plugin in self.plugins.values()
            if plugin.status == PluginStatus.ACTIVE
        ]
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all registered plugins with their info.
        
        Returns:
            List of plugin information dictionaries
        """
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    async def reload_plugin(self, plugin_id: str) -> bool:
        """
        Reload a plugin (unload and load again).
        
        Args:
            plugin_id: ID of plugin to reload
            
        Returns:
            True if reload successful
        """
        if plugin_id not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin = self.plugins[plugin_id]
        was_active = plugin.status == PluginStatus.ACTIVE
        
        # Preserve plugin info before unloading
        plugin_type = None
        for ptype, pids in self.plugins_by_type.items():
            if plugin_id in pids:
                plugin_type = ptype
                break
        
        metadata = self.plugin_metadata.get(plugin_id, {})
        
        # Unload
        if not await self.unload_plugin(plugin_id):
            return False
        
        # Re-register and load
        self.register_plugin(plugin, plugin_type, metadata)
        
        if not await self.load_plugin(plugin_id):
            return False
        
        # Re-activate if it was active before
        if was_active:
            return await self.activate_plugin(plugin_id)
        
        return True
