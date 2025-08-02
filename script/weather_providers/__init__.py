"""
Weather Providers Package.

This module provides access to weather providers.
"""

import logging
from typing import Dict, Any, Optional

from .openmeteo import OpenMeteoProvider, WeatherDataPoint as WeatherData

# Configure logging
logger = logging.getLogger(__name__)

# Define __all__ for explicit exports
__all__ = [
    'WeatherData',
    'get_provider',
    'get_available_providers'
]

def get_provider(provider_name: str, **kwargs) -> OpenMeteoProvider:
    """Get a weather provider instance by name.
    
    Args:
        provider_name: Name of the provider to get (only 'openmeteo' is supported)
        **kwargs: Additional arguments to pass to the provider constructor
        
    Returns:
        An instance of the requested provider
        
    Raises:
        ValueError: If the provider is not found
    """
    if provider_name.lower() != 'openmeteo':
        raise ValueError(f"Weather provider '{provider_name}' not found. Only 'openmeteo' is supported.")
        
    # Create and return an instance of the OpenMeteo provider
    return OpenMeteoProvider(**kwargs)

def get_available_providers() -> Dict[str, str]:
    """Get a dictionary of available weather providers.
    
    Returns:
        dict: Dictionary mapping provider names to their display names
    """
    # Only the OpenMeteo provider is supported
    return {'openmeteo': 'OpenMeteo'}
