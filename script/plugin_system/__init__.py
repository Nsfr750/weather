"""
Plugin system for the Weather Application.

This module provides the base classes and utilities for creating and managing plugins.
"""
__all__ = [
    'BasePlugin', 
    'PluginManager',
    'BaseWeatherProvider', 
    'WeatherDataPoint', 
    'WeatherForecast',
    'WeatherCondition',
    'WeatherProviderManager',
    'BaseFeaturePlugin',
    'FeatureManager',
    'create_legacy_plugin_wrapper',
    'register_legacy_providers'
]

# Core plugin system
from .plugin_manager import BasePlugin, PluginManager

# Weather provider system
from .weather_provider import (
    BaseWeatherProvider,
    WeatherDataPoint,
    WeatherForecast,
    WeatherCondition,
    WeatherProviderManager
)

# Feature plugin system
from .feature import (
    BaseFeaturePlugin,
    FeatureManager
)

# Legacy compatibility
from .legacy_compat import (
    create_legacy_plugin_wrapper,
    register_legacy_providers
)

# Set up logging
import logging
logger = logging.getLogger(__name__)
