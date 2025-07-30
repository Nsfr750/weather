"""
Weather Providers Package.

This package contains the base provider class and all weather provider implementations.
"""

import importlib
import logging
from typing import Dict, Type, Any, Optional

from .base_provider import BaseProvider, WeatherData

# Configure logging
logger = logging.getLogger(__name__)

# Provider module to class name mapping (handles case sensitivity)
PROVIDER_MAPPING = {
    'openweathermap': 'OpenWeatherMapProvider',
    'weatherapi': 'WeatherAPIProvider',
    'accuweather': 'AccuWeatherProvider'
}

# Initialize provider registry
_PROVIDERS: Dict[str, Type[BaseProvider]] = {}

# Try to import all provider modules
for module_name, class_name in PROVIDER_MAPPING.items():
    try:
        module = importlib.import_module(f'.{module_name}', __package__)
        provider_class = getattr(module, class_name, None)
        if provider_class and issubclass(provider_class, BaseProvider):
            _PROVIDERS[module_name.lower()] = provider_class
            logger.info(f"Successfully loaded provider: {module_name}")
        else:
            logger.warning(f"Invalid provider class in {module_name}: {class_name}")
    except ImportError as e:
        logger.warning(f"Could not import provider {module_name}: {e}")
    except Exception as e:
        logger.error(f"Error initializing provider {module_name}: {e}")

# Define __all__ for explicit exports
__all__ = [
    'BaseProvider',
    'WeatherData',
    'get_provider',
    'get_available_providers'
]

# Add provider classes to __all__
for provider_class in _PROVIDERS.values():
    __all__.append(provider_class.__name__)


def get_provider(provider_name: str, **kwargs) -> BaseProvider:
    """Get a weather provider instance by name.
    
    Args:
        provider_name: Name of the provider to get
        **kwargs: Additional arguments to pass to the provider constructor
        
    Returns:
        An instance of the requested provider
        
    Raises:
        ValueError: If the provider is not found
    """
    provider_name = provider_name.lower()
    provider_class = _PROVIDERS.get(provider_name)
    if not provider_class:
        available = ', '.join(f"'{p}'" for p in _PROVIDERS.keys())
        raise ValueError(
            f"Unknown provider: '{provider_name}'. "
            f"Available providers: {available or 'none'}"
        )
    
    # Filter kwargs to only include parameters that the provider's __init__ accepts
    import inspect
    init_params = inspect.signature(provider_class.__init__).parameters
    valid_kwargs = {k: v for k, v in kwargs.items() if k in init_params}
    
    return provider_class(**valid_kwargs)


def get_available_providers() -> Dict[str, str]:
    """Get a dictionary of available weather providers.
    
    Returns:
        dict: Dictionary mapping provider names to their display names
    """
    return {
        name: provider.display_name 
        for name, provider in _PROVIDERS.items()
    }
