"""
Base classes for weather provider plugins.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Type
import logging

from ..plugin_system import BasePlugin

logger = logging.getLogger(__name__)

class WeatherCondition(Enum):
    """Enumeration of possible weather conditions."""
    CLEAR = "clear"
    CLOUDS = "clouds"
    FOG = "fog"
    DRIZZLE = "drizzle"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    MIST = "mist"
    SMOKE = "smoke"
    HAZE = "haze"
    DUST = "dust"
    SAND = "sand"
    ASH = "ash"
    SQUALL = "squall"
    TORNADO = "tornado"
    HURRICANE = "hurricane"

@dataclass
class WeatherDataPoint:
    """A single point of weather data with a timestamp."""
    timestamp: datetime
    temperature: float  # in Celsius
    feels_like: float   # in Celsius
    humidity: int       # percentage
    pressure: int       # hPa
    wind_speed: float   # m/s
    wind_direction: int  # degrees
    condition: WeatherCondition
    description: str
    icon: Optional[str] = None
    precipitation: float = 0.0  # in mm
    cloudiness: int = 0  # percentage
    visibility: Optional[int] = None  # in meters
    uv_index: Optional[float] = None
    dew_point: Optional[float] = None  # in Celsius
    wind_gust: Optional[float] = None  # m/s

@dataclass
class WeatherForecast:
    """Container for weather forecast data."""
    location: str
    latitude: float
    longitude: float
    timezone: str
    current: WeatherDataPoint
    hourly: List[WeatherDataPoint] = field(default_factory=list)
    daily: List[WeatherDataPoint] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_forecast_at(self, dt: datetime) -> Optional[WeatherDataPoint]:
        """Get the forecast for a specific time."""
        for point in self.hourly:
            if point.timestamp == dt:
                return point
        return None

class BaseWeatherProvider(BasePlugin):
    """Base class for weather provider plugins."""
    
    # Provider metadata
    name = "Base Weather Provider"
    api_key_required = True
    settings_schema = {}
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__()
        self.api_key = api_key
        self.settings = kwargs
        self._validate_settings()
    
    def _validate_settings(self) -> None:
        """Validate provider settings against the schema."""
        if self.api_key_required:
            if not self.api_key:
                error_msg = (
                    f"{self.name} requires an API key. "
                    f"Please configure it in the settings.\n\n"
                    f"You can get an API key by signing up at the provider's website.\n"
                    f"Look for the 'API Keys' or 'Developer' section in your account settings."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Additional validation for API key format if needed
            if not isinstance(self.api_key, str) or len(self.api_key.strip()) < 10:
                error_msg = f"Invalid API key format for {self.name}. Please check your configuration."
                logger.error(error_msg)
                raise ValueError(error_msg)
    
    @abstractmethod
    async def get_current_weather(self, location: str, **kwargs) -> WeatherForecast:
        """Get current weather for a location.
        
        Args:
            location: Location name or coordinates (format: "lat,lon")
            **kwargs: Additional parameters specific to the provider
            
        Returns:
            WeatherForecast object with current weather data
        """
        pass
    
    @abstractmethod
    async def get_forecast(self, location: str, days: int = 5, **kwargs) -> WeatherForecast:
        """Get weather forecast for a location.
        
        Args:
            location: Location name or coordinates (format: "lat,lon")
            days: Number of days to forecast (up to provider's limit)
            **kwargs: Additional parameters specific to the provider
            
        Returns:
            WeatherForecast object with forecast data
        """
        pass
    
    def get_settings_schema(self) -> Dict:
        """Get the settings schema for this provider."""
        return self.settings_schema
    
    def set_setting(self, key: str, value: Any) -> None:
        """Update a setting."""
        if key in self.settings_schema:
            self.settings[key] = value
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)

# Alias for backward compatibility with existing plugins
BaseProvider = BaseWeatherProvider

class WeatherProviderManager:
    """Manager for weather provider plugins."""
    
    def __init__(self, plugin_manager):
        """Initialize with a plugin manager instance."""
        self.plugin_manager = plugin_manager
        self.providers: Dict[str, Type[BaseWeatherProvider]] = {}
        self.active_provider: Optional[BaseWeatherProvider] = None
    
    def discover_providers(self) -> None:
        """Discover all available weather provider plugins."""
        for plugin in self.plugin_manager.get_plugins_by_type(BaseWeatherProvider):
            if plugin.name not in self.providers:
                self.providers[plugin.name] = plugin
    
    def get_available_providers(self) -> List[str]:
        """Get names of all available weather providers."""
        return list(self.providers.keys())
    
    def get_provider(self, name: str) -> Optional[Type[BaseWeatherProvider]]:
        """Get a provider class by name."""
        return self.providers.get(name)
    
    def create_provider(self, name: str, **kwargs):
        """Create an instance of a weather provider.
        
        Args:
            name: Name of the provider to create
            **kwargs: Configuration options for the provider
            
        Returns:
            An instance of the requested weather provider
            
        Raises:
            ValueError: If provider creation fails due to missing or invalid configuration
            Exception: If any other error occurs during provider initialization
        """
        try:
            provider_cls = self.get_provider(name)
            return provider_cls(**kwargs)
        except ValueError as ve:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            logger.error(f"Failed to create provider '{name}': {str(e)}")
            raise ValueError(f"Failed to initialize {name} provider: {str(e)}")
    
    def set_active_provider(self, name: str, **kwargs) -> bool:
        """Set the active weather provider."""
        provider = self.create_provider(name, **kwargs)
        if provider:
            self.active_provider = provider
            return True
        return False
    
    async def get_forecast(self, location: str, **kwargs) -> Optional[WeatherForecast]:
        """Get forecast from the active provider."""
        if not self.active_provider:
            raise RuntimeError("No active weather provider")
        return await self.active_provider.get_forecast(location, **kwargs)
    
    async def get_current_weather(self, location: str, **kwargs) -> Optional[WeatherForecast]:
        """Get current weather from the active provider."""
        if not self.active_provider:
            raise RuntimeError("No active weather provider")
        return await self.active_provider.get_current_weather(location, **kwargs)