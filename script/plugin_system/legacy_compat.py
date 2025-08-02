"""
Legacy compatibility layer for weather providers.

This module provides utilities to help migrate from the old provider system
to the new plugin-based system.
"""
import logging
from typing import Dict, Any, Optional, Type, TYPE_CHECKING, List, Union

from .weather_provider import BaseWeatherProvider, WeatherDataPoint, WeatherForecast, WeatherCondition
from ..weather_providers.base_provider import BaseProvider

if TYPE_CHECKING:
    # These imports are only used for type checking
    from .weather_provider import BaseWeatherProvider as BaseWeatherProviderType
    from ..weather_providers.base_provider import BaseProvider as BaseProviderType

logger = logging.getLogger(__name__)

class LegacyProviderWrapper:
    """Wrapper to make legacy providers work with the new plugin system."""
    
    def __init__(self, legacy_provider_class: Type['BaseProvider'], **kwargs) -> None:
        """Initialize the wrapper with a legacy provider class."""
        self.legacy_provider_class = legacy_provider_class
        self.legacy_provider = None
        self._settings = kwargs
    
    def initialize(self, app: Any = None) -> bool:
        """Initialize the legacy provider."""
        try:
            self.legacy_provider = self.legacy_provider_class(**self._settings)
            return True
        except Exception as e:
            logger.error(
                "Failed to initialize legacy provider %s: %s",
                self.legacy_provider_class.__name__,
                e
            )
            return False
    
    async def get_current_weather(self, location: str, **kwargs) -> Dict[str, Any]:
        """Get current weather using the legacy provider."""
        if not self.legacy_provider:
            raise RuntimeError("Legacy provider not initialized")
        
        try:
            # Convert async/await to sync if needed
            if hasattr(self.legacy_provider, 'get_current_weather_async'):
                return await self.legacy_provider.get_current_weather_async(location, **kwargs)
            
            # Fall back to sync method (this will block the event loop!)
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as pool:
                return await loop.run_in_executor(
                    pool,
                    lambda: self.legacy_provider.get_current_weather(location, **kwargs)
                )
        except Exception as e:
            logger.error("Error getting current weather from legacy provider: %s", e)
            raise
    
    async def get_forecast(self, location: str, days: int = 5, **kwargs) -> Dict[str, Any]:
        """Get weather forecast using the legacy provider."""
        if not self.legacy_provider:
            raise RuntimeError("Legacy provider not initialized")
        
        try:
            if hasattr(self.legacy_provider, 'get_forecast_async'):
                return await self.legacy_provider.get_forecast_async(
                    location,
                    days=days,
                    **kwargs
                )
            
            if hasattr(self.legacy_provider, 'get_forecast'):
                # Fall back to sync method (this will block the event loop!)
                import asyncio
                from concurrent.futures import ThreadPoolExecutor
                
                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as pool:
                    return await loop.run_in_executor(
                        pool,
                        lambda: self.legacy_provider.get_forecast(location, days=days, **kwargs)
                    )
            
            # If no forecast method is available, return current weather as a fallback
            logger.warning(
                "Legacy provider doesn't support forecast, falling back to current weather"
            )
            return await self.get_current_weather(location, **kwargs)
        except Exception as e:
            logger.error("Error getting forecast from legacy provider: %s", e)
            raise
    
    def cleanup(self) -> None:
        """Clean up the legacy provider."""
        if self.legacy_provider and hasattr(self.legacy_provider, 'cleanup'):
            self.legacy_provider.cleanup()
        self.legacy_provider = None


def create_legacy_plugin_wrapper(
    legacy_provider_class: Type['BaseProvider']
) -> Type['BaseWeatherProvider']:
    """Create a plugin class that wraps a legacy provider.
    
    Args:
        legacy_provider_class: The legacy provider class to wrap
        
    Returns:
        A new class that inherits from BaseWeatherProvider and wraps the legacy provider
    """
    class LegacyPluginWrapper(BaseWeatherProvider):
        """Wrapper for legacy weather providers to work with the new plugin system."""
        
        name = getattr(legacy_provider_class, 'display_name', legacy_provider_class.__name__)
        description = f"Legacy wrapper for {legacy_provider_class.__name__}"
        author = "Legacy Provider"
        version = "1.0.0"
        
        # Copy settings schema from legacy provider if available
        settings_schema = getattr(legacy_provider_class, 'settings_schema', {})
        
        def __init__(self, **kwargs) -> None:
            """Initialize the legacy plugin wrapper."""
            super().__init__(**kwargs)
            self.wrapper = LegacyProviderWrapper(legacy_provider_class, **kwargs)
        
        async def initialize(self, app: Any = None) -> bool:
            """Initialize the legacy provider."""
            return self.wrapper.initialize(app)
        
        async def get_current_weather(
            self,
            location: str,
            **kwargs
        ) -> Dict[str, Any]:
            """Get current weather using the legacy provider."""
            return await self.wrapper.get_current_weather(location, **kwargs)
        
        async def get_forecast(
            self,
            location: str,
            days: int = 5,
            **kwargs
        ) -> Dict[str, Any]:
            """Get weather forecast using the legacy provider."""
            return await self.wrapper.get_forecast(location, days=days, **kwargs)
        
        def cleanup(self) -> None:
            """Clean up the legacy provider."""
            self.wrapper.cleanup()
            super().cleanup()
    
    # Set a proper name for the wrapper class
    LegacyPluginWrapper.__name__ = f"Legacy{legacy_provider_class.__name__}Wrapper"
    LegacyPluginWrapper.__qualname__ = LegacyPluginWrapper.__name__
    
    return LegacyPluginWrapper


class LegacyWeatherProvider(BaseWeatherProvider):
    """Legacy weather provider compatibility layer.
    
    This class provides a bridge between the legacy provider system
    and the new plugin-based system.
    """
    
    def __init__(self, provider_name: str, **kwargs):
        """Initialize the legacy weather provider.
        
        Args:
            provider_name: Name of the legacy provider to wrap
            **kwargs: Additional arguments to pass to the legacy provider
        """
        super().__init__(**kwargs)
        self.provider_name = provider_name
        self.legacy_provider = None
    
    async def initialize(self) -> bool:
        """Initialize the legacy provider."""
        try:
            # Import the legacy provider module
            module_name = f"script.weather_providers.{self.provider_name}"
            module = __import__(module_name, fromlist=[f"{self.provider_name.capitalize()}Provider"])
            provider_class = getattr(module, f"{self.provider_name.capitalize()}Provider")
            
            # Initialize the legacy provider
            self.legacy_provider = provider_class(
                api_key=self.api_key,
                units=self.units,
                language=self.language
            )
            
            # Call initialize if it exists
            if hasattr(self.legacy_provider, 'initialize'):
                if hasattr(self.legacy_provider.initialize, '__await__'):
                    await self.legacy_provider.initialize()
                else:
                    self.legacy_provider.initialize()
            
            return True
            
        except Exception as e:
            logger.error("Failed to initialize legacy provider %s: %s", self.provider_name, e)
            return False
    
    async def get_current_weather(self, location: str, **kwargs) -> WeatherDataPoint:
        """Get current weather data for a location."""
        if not self.legacy_provider:
            raise RuntimeError("Legacy provider not initialized")
        
        try:
            if hasattr(self.legacy_provider, 'get_current_weather_async'):
                data = await self.legacy_provider.get_current_weather_async(location, **kwargs)
            else:
                data = self.legacy_provider.get_current_weather(location, **kwargs)
            
            # Convert to WeatherDataPoint if needed
            if not isinstance(data, WeatherDataPoint):
                data = self._convert_to_weather_data_point(data)
                
            return data
            
        except Exception as e:
            logger.error("Error getting current weather from legacy provider: %s", e)
            raise
    
    async def get_forecast(self, location: str, days: int = 5, **kwargs) -> List[WeatherDataPoint]:
        """Get weather forecast for a location."""
        if not self.legacy_provider:
            raise RuntimeError("Legacy provider not initialized")
        
        try:
            if hasattr(self.legacy_provider, 'get_forecast_async'):
                forecast = await self.legacy_provider.get_forecast_async(location, days, **kwargs)
            else:
                forecast = self.legacy_provider.get_forecast(location, days, **kwargs)
            
            # Convert to list of WeatherDataPoint if needed
            if forecast and not isinstance(forecast[0], WeatherDataPoint):
                forecast = [self._convert_to_weather_data_point(item) for item in forecast]
                
            return forecast
            
        except Exception as e:
            logger.error("Error getting forecast from legacy provider: %s", e)
            raise
    
    def _convert_to_weather_data_point(self, data: Dict[str, Any]) -> WeatherDataPoint:
        """Convert legacy weather data to a WeatherDataPoint."""
        return WeatherDataPoint(
            temperature=data.get('temperature'),
            condition=WeatherCondition.from_string(data.get('condition', 'unknown')),
            humidity=data.get('humidity'),
            wind_speed=data.get('wind_speed'),
            wind_direction=data.get('wind_direction'),
            pressure=data.get('pressure'),
            visibility=data.get('visibility'),
            timestamp=data.get('timestamp'),
            location=data.get('location'),
            icon=data.get('icon')
        )


def register_legacy_providers(
    plugin_manager: 'PluginManager',
    provider_classes: Dict[str, Type['BaseProvider']]
) -> None:
    """Register legacy provider classes with the plugin system.
    
    Args:
        plugin_manager: The plugin manager instance
        provider_classes: Dictionary of provider names to provider classes
    """
    for provider_name, provider_class in provider_classes.items():
        try:
            wrapper_class = create_legacy_plugin_wrapper(provider_class)
            try:
                # Create an instance of the wrapper class and register it
                plugin_instance = wrapper_class()
                plugin_manager._register_plugin(plugin_instance)
                logger.info(f"Successfully registered legacy provider: {provider_name}")
            except Exception as e:
                logger.error(f"Failed to register legacy provider {provider_name}: {e}", exc_info=True)
        except Exception as e:
            logger.error("Failed to register legacy provider %s: %s", provider_name, e, exc_info=True)
