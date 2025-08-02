"""
Weather Providers Package.

This module provides access to weather providers through the plugin system.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING

from script.plugin_system.weather_provider import WeatherDataPoint as WeatherData
from script.plugin_system.weather_provider import BaseWeatherProvider

if TYPE_CHECKING:
    from script.plugin_system.plugin_manager import PluginManager

# Configure logging
logger = logging.getLogger(__name__)

# Plugin manager will be set by the main application
plugin_manager = None  # type: ignore[assignment]

def set_plugin_manager(manager: 'PluginManager') -> None:
    """Set the plugin manager instance to use.
    
    This should be called by the main application to provide the shared plugin manager.
    
    Args:
        manager: The plugin manager instance to use
    """
    global plugin_manager
    plugin_manager = manager

# Define __all__ for explicit exports
__all__ = [
    'WeatherData',
    'get_provider',
    'set_plugin_manager',
    'get_available_providers'
]

def get_provider(provider_name: str, **kwargs) -> BaseWeatherProvider:
    """Get a weather provider instance by name.
    
    Args:
        provider_name: Name of the provider to get
        **kwargs: Additional arguments to pass to the provider constructor
        
    Returns:
        An instance of the requested provider
        
    Raises:
        ValueError: If the provider is not found
    """
    # Get all weather provider plugins
    providers = plugin_manager.get_plugins(BaseWeatherProvider)
    
    # Find the requested provider (case-insensitive)
    provider_name_lower = provider_name.lower()
    for name, provider_class in providers.items():
        if name.lower() == provider_name_lower:
            try:
                return provider_class(**kwargs)
            except Exception as e:
                logger.error(f"Error creating provider {name}: {e}")
                raise
    
    raise ValueError(f"Weather provider not found: {provider_name}")

def get_available_providers() -> Dict[str, str]:
    """Get a dictionary of available weather providers.
    
    Returns:
        dict: Dictionary mapping provider names to their display names
    """
    providers = {}
    for name, provider_class in plugin_manager.get_plugins(BaseWeatherProvider).items():
        display_name = getattr(provider_class, 'display_name', name)
        providers[name] = display_name
    return providers
