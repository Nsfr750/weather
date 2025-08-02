"""
Core plugin system for the Weather Application.

This module provides the base classes and utilities for creating and managing plugins.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Type, TypeVar, Optional, Any, Type
import importlib.util
import inspect
import json
import os
import pkgutil
import sys
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='BasePlugin')

class BasePlugin(ABC):
    """Base class for all plugins."""
    
    # Plugin metadata
    name: str = "Unnamed Plugin"
    author: str = "Unknown"
    version: str = "0.1.0"
    description: str = "No description provided"
    
    # Configuration schema - define this in subclasses to support configuration
    # Example:
    # config_schema = {
    #     'api_key': {
    #         'type': str,
    #         'label': 'API Key',
    #         'description': 'Your API key for the service',
    #         'default': ''
    #     },
    #     'use_https': {
    #         'type': bool,
    #         'label': 'Use HTTPS',
    #         'description': 'Use HTTPS for API requests',
    #         'default': True
    #     }
    # }
    config_schema: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self):
        self._config = {}
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the current configuration for this plugin."""
        return self._config
    
    @config.setter
    def config(self, value: Dict[str, Any]) -> None:
        """Set the configuration for this plugin."""
        self._config = value or {}
        
        # Apply default values from schema if they're not set
        if hasattr(self, 'config_schema'):
            for key, field in self.config_schema.items():
                if key not in self._config and 'default' in field:
                    self._config[key] = field['default']
    
    @abstractmethod
    def initialize(self, app: Any = None) -> bool:
        """Initialize the plugin.
        
        Args:
            app: Reference to the main application instance
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up resources used by the plugin.
        
        This method is called when the plugin is being unloaded.
        """
        pass
    
    def on_config_changed(self, new_config: Dict[str, Any]) -> None:
        """Called when the plugin's configuration is changed.
        
        Override this method in your plugin to react to configuration changes.
        
        Args:
            new_config: The new configuration values
        """
        self.config = new_config


class PluginManager:
    """Manages the loading and unloading of plugins."""
    
    CONFIG_DIR = Path('config')
    PLUGIN_CONFIG_FILE = CONFIG_DIR / 'plugins.json'
    
    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        """Initialize the plugin manager.
        
        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self.plugins: Dict[str, Type[BasePlugin]] = {}
        self.plugin_instances: Dict[str, BasePlugin] = {}
        self.plugin_dirs = plugin_dirs or []
        
        # Log the directories we'll be searching for plugins
        logger.info(f"Initializing PluginManager with directories: {[str(d) for d in self.plugin_dirs]}")
        
        # Create config directory if it doesn't exist
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._load_configs()
        
        # Create plugin directories if they don't exist
        for path in self.plugin_dirs:
            path.mkdir(parents=True, exist_ok=True)
            (path / "__init__.py").touch(exist_ok=True)
    
    def _load_configs(self) -> None:
        """Load plugin configurations from the config file."""
        self._configs = {}
        
        # Create config directory if it doesn't exist
        if not self.CONFIG_DIR.exists():
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load config file if it exists
        if self.PLUGIN_CONFIG_FILE.exists():
            try:
                with open(self.PLUGIN_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self._configs = json.load(f)
                logger.info(f"Loaded plugin configurations from {self.PLUGIN_CONFIG_FILE}")
            except Exception as e:
                logger.error(f"Error loading plugin configs: {e}", exc_info=True)
                self._configs = {}
    
    def _save_configs(self) -> None:
        """Save plugin configurations to the config file."""
        try:
            with open(self.PLUGIN_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._configs, f, indent=4, ensure_ascii=False)
            logger.debug(f"Saved plugin configurations to {self.PLUGIN_CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Error saving plugin configs: {e}", exc_info=True)
    
    def get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """Get the configuration for a plugin.
        
        Args:
            plugin_id: The ID of the plugin
            
        Returns:
            The plugin's configuration dictionary
        """
        return self._configs.get(plugin_id, {})
    
    def set_plugin_config(self, plugin_id: str, config: Dict[str, Any]) -> None:
        """Set the configuration for a plugin.
        
        Args:
            plugin_id: The ID of the plugin
            config: The new configuration dictionary
        """
        self._configs[plugin_id] = config
        self._save_configs()
        
        # Update the config of the plugin instance if it's already loaded
        if plugin_id in self.plugin_instances:
            self.plugin_instances[plugin_id].config = config
    
    def get_all_plugins(self) -> List[Type[BasePlugin]]:
        """Get a list of all loaded plugin classes.
        
        Returns:
            List of plugin classes
        """
        return list(self.plugins.values())
    
    def load_plugins(self) -> None:
        """Load all plugins from the configured directories."""
        if not self.plugin_dirs:
            logger.warning("No plugin directories configured")
            return
            
        for plugin_dir in self.plugin_dirs:
            plugin_dir = Path(plugin_dir).resolve()  # Convert to absolute path
            if not plugin_dir.exists():
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
                continue
                
            if not plugin_dir.is_dir():
                logger.warning(f"Plugin path is not a directory: {plugin_dir}")
                continue
                
            logger.info(f"Scanning for plugins in: {plugin_dir}")
            
            # Find all Python files in the plugin directory
            python_files = list(plugin_dir.glob("**/*.py"))
            logger.info(f"Found {len(python_files)} Python files in {plugin_dir}")
            
            for file_path in python_files:
                # Skip __init__.py and files starting with _
                if file_path.name.startswith('_') or file_path.name == '__init__.py':
                    logger.debug(f"Skipping non-plugin file: {file_path}")
                    continue
                    
                logger.debug(f"Found potential plugin file: {file_path}")
                
                # Convert file path to module path
                try:
                    # Calculate the relative path from the plugin directory
                    rel_path = file_path.relative_to(plugin_dir)
                    # Convert to module path (e.g., 'plugins.weather_providers.openmeteo_plugin')
                    module_name = str(rel_path.with_suffix('')).replace(os.sep, '.')
                    logger.info(f"Attempting to import module {module_name} from {file_path}")
                    
                    # Add the plugin directory's parent to sys.path if not already there
                    # This allows imports to work relative to the project root
                    plugin_parent = str(plugin_dir.parent)
                    if plugin_parent not in sys.path:
                        logger.debug(f"Adding to sys.path: {plugin_parent}")
                        sys.path.insert(0, plugin_parent)
                    
                    # Import the module
                    try:
                        # Use importlib to load the module from file
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        if spec is None or spec.loader is None:
                            logger.warning(f"Could not load plugin from {file_path}: Invalid module spec")
                            continue
                        
                        # Create a new module and execute it
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module  # Add to sys.modules
                        spec.loader.exec_module(module)
                        
                        # Debug: List all attributes in the module
                        module_attrs = [attr for attr in dir(module) if not attr.startswith('_')]
                        logger.debug(f"Module {module_name} attributes: {module_attrs}")
                        
                        # Look for PLUGIN_CLASS in the module
                        if hasattr(module, 'PLUGIN_CLASS'):
                            plugin_class = module.PLUGIN_CLASS
                            logger.info(f"Found PLUGIN_CLASS in {module_name}: {plugin_class.__name__}")
                            
                            if not inspect.isclass(plugin_class):
                                logger.warning(f"PLUGIN_CLASS in {file_path} is not a class: {plugin_class}")
                                continue
                                
                            if not issubclass(plugin_class, BasePlugin):
                                logger.warning(
                                    f"PLUGIN_CLASS in {file_path} is not a subclass of BasePlugin. "
                                    f"Got: {plugin_class.__mro__}"
                                )
                                continue
                            
                            # Get plugin name, defaulting to class name if not specified
                            plugin_name = getattr(plugin_class, 'name', plugin_class.__name__)
                            logger.info(f"Registering plugin: {plugin_name} (class: {plugin_class.__name__}) from {file_path}")
                            
                            # Register the plugin
                            self.register_plugin(plugin_class)
                            logger.info(f"Successfully registered plugin: {plugin_name}")
                        else:
                            logger.debug(f"No PLUGIN_CLASS found in {module_name}")
                            
                    except ImportError as e:
                        logger.error(f"Import error in {file_path}: {e}")
                    except SyntaxError as e:
                        logger.error(f"Syntax error in {file_path}: {e}")
                    except Exception as e:
                        logger.error(f"Unexpected error loading plugin from {file_path}: {e}", exc_info=True)
                        
                except Exception as e:
                    logger.error(f"Error processing plugin file {file_path}: {e}", exc_info=True)
                finally:
                    # Clean up sys.path to avoid duplicate entries
                    if 'plugin_parent' in locals() and plugin_parent in sys.path:
                        sys.path.remove(plugin_parent)
                    
    def register_plugin(self, plugin_class: Type[BasePlugin]) -> None:
        """Register a plugin class.
        
        Args:
            plugin_class: The plugin class to register
        """
        if not issubclass(plugin_class, BasePlugin):
            logger.error(f"Cannot register {plugin_class.__name__}: Not a subclass of BasePlugin")
            return
            
        plugin_name = getattr(plugin_class, 'name', plugin_class.__name__)
        
        if plugin_name in self.plugins:
            logger.warning(f"Plugin with name '{plugin_name}' already registered. Skipping.")
            return
            
        logger.info(f"Registering plugin: {plugin_name} (class: {plugin_class.__name__})")
        self.plugins[plugin_name] = plugin_class
        
        # Create and initialize an instance of the plugin
        try:
            plugin_instance = plugin_class()
            self.plugin_instances[plugin_name] = plugin_instance
            logger.debug(f"Created instance of plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"Failed to create instance of plugin {plugin_name}: {e}")
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin by name.
        
        Args:
            name: The name of the plugin to retrieve
            
        Returns:
            Optional[BasePlugin]: The plugin instance, or None if not found
        """
        return self.plugins.get(name)
    
    def get_plugins_by_type(self, plugin_type: Type[T]) -> Dict[str, Type[T]]:
        """Get all plugins of a specific type.
        
        Args:
            plugin_type: The type of plugins to retrieve
            
        Returns:
            Dict[str, Type[T]]: Dictionary mapping plugin names to plugin classes of the specified type
        """
        return {name: plugin_class for name, plugin_class in self.plugins.items() 
                if issubclass(plugin_class, plugin_type)}
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin.
        
        Args:
            name: The name of the plugin to unload
            
        Returns:
            bool: True if the plugin was unloaded successfully, False otherwise
        """
        if name in self.plugins:
            try:
                self.plugins[name].cleanup()
                del self.plugins[name]
                logger.info(f"Successfully unloaded plugin: {name}")
                return True
            except Exception as e:
                logger.error(f"Error unloading plugin {name}: {e}")
        return False
    
    def unload_all(self) -> None:
        """Unload all plugins."""
        for name in list(self.plugins.keys()):
            self.unload_plugin(name)
            
    def get_plugins(self, base_class: Type[T] = None) -> Dict[str, T]:
        """Get all loaded plugins, optionally filtered by base class.
        
        This is provided for backward compatibility with legacy code.
        
        Args:
            base_class: Optional base class to filter plugins by
                
        Returns:
            Dict mapping plugin names to plugin instances
        """
        if base_class is None:
            return self.instances.copy()
                
        return {
            name: instance for name, instance in self.instances.items()
            if isinstance(instance, base_class)
        }
            
    def is_plugin_loaded(self, plugin_name: str) -> bool:
        """Check if a plugin is currently loaded.
        
        This is provided for backward compatibility with legacy code.
        
        Args:
            plugin_name: The name of the plugin to check
                
        Returns:
            bool: True if the plugin is loaded, False otherwise
        """
        return plugin_name in self.instances
