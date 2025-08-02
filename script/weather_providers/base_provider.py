"""
Legacy Base Provider for Weather Providers.

This module provides a base class for weather providers that need to maintain
compatibility with the legacy provider system while using the new plugin system.

Note: New providers should inherit directly from BaseWeatherProvider in the
plugin system rather than using this class.
"""
import json
import logging
from abc import abstractmethod
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, ClassVar, Union, Tuple

import requests
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

from script.plugin_system.weather_provider import (
    BaseWeatherProvider,
    WeatherDataPoint,
    WeatherForecast,
    WeatherCondition
)

# Configure logging
logger = logging.getLogger(__name__)


class _BaseProviderMeta(type(QObject), type(BaseWeatherProvider)):
    """Metaclass to combine QObject and BaseWeatherProvider metaclasses."""
    def __new__(mcls, name, bases, namespace):
        # Create the class with both metaclasses
        return super().__new__(mcls, name, bases, namespace)


class BaseProvider(BaseWeatherProvider, QObject, metaclass=_BaseProviderMeta):
    """Legacy base class for weather providers with QObject compatibility.
    
    This class is provided for backward compatibility. New providers should
    inherit directly from BaseWeatherProvider in the plugin system.
    
    This class extends BaseWeatherProvider with QObject functionality for signals
    and slots, and provides common functionality for all weather providers.
    """
    
    # Signals for UI updates
    api_key_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    connection_status_changed = pyqtSignal(bool)
    
    # Class variables
    DEFAULT_CONFIG_DIR = Path.home() / '.weather_app'
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / 'providers.json'
    
    # Provider metadata (override in subclasses)
    name: ClassVar[str] = 'base'
    description: ClassVar[str] = 'Base weather provider'
    author: ClassVar[str] = 'Nsfr750'
    version: ClassVar[str] = '1.0.0'
    
    # Settings schema for the plugin system
    settings_schema: ClassVar[Dict[str, Any]] = {
        'api_key': {
            'type': 'string',
            'title': 'API Key',
            'description': 'API key for the weather provider',
            'required': True,
            'secret': True
        },
        'offline_mode': {
            'type': 'boolean',
            'title': 'Offline Mode',
            'description': 'Enable offline mode (use cached data if available)',
            'default': False
        }
    }
    
    def __init__(self, **kwargs):
        """Initialize the base provider.
        
        Args:
            **kwargs: Provider-specific configuration options
        """
        # Initialize QObject first
        QObject.__init__(self)
        
        # Initialize BaseWeatherProvider with plugin metadata
        super().__init__()
        
        # Initialize instance variables
        self._api_key = kwargs.get('api_key')
        self._offline_mode = kwargs.get('offline_mode', False)
        self._settings = QSettings("WeatherApp", "WeatherProviders")
        
        # Load provider-specific settings
        self.load_settings()
    
    @property
    def api_key(self) -> Optional[str]:
        """Get the current API key."""
        return self._api_key
    
    @api_key.setter
    def api_key(self, value: str) -> None:
        """Set the API key and emit signal if changed."""
        if self._api_key != value:
            self._api_key = value
            self.api_key_changed.emit(self.name)
            self.save_settings()
    
    @property
    def offline_mode(self) -> bool:
        """Get the offline mode status."""
        return self._offline_mode
    
    @offline_mode.setter
    def offline_mode(self, value: bool) -> None:
        """Set the offline mode status."""
        if self._offline_mode != value:
            self._offline_mode = value
            self.save_settings()
    
    async def initialize(self, app=None) -> bool:
        """Initialize the provider.
        
        Args:
            app: Reference to the main application instance
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        # Load settings from persistent storage
        self.load_settings()
        
        # Validate API key if required
        if self.settings_schema.get('api_key', {}).get('required', True):
            if not self._api_key:
                logger.warning("No API key provided for %s", self.name)
                return False
                
        return True
    
    def cleanup(self) -> None:
        """Clean up resources used by the provider."""
        # Save settings before cleanup
        self.save_settings()
        
    # Abstract methods from BaseWeatherProvider
    @abstractmethod
    async def get_current_weather(self, location: str, **kwargs) -> WeatherDataPoint:
        """Get current weather for a location.
        
        Args:
            location: Location to get weather for (city name, coordinates, etc.)
            **kwargs: Additional parameters specific to the provider
            
        Returns:
            WeatherDataPoint with current weather information
            
        Raises:
            Exception: If there's an error fetching the weather data
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_forecast(self, location: str, days: int = 5, **kwargs) -> WeatherForecast:
        """Get weather forecast for a location.
        
        Args:
            location: Location to get forecast for
            days: Number of days to forecast (1-16, depends on provider)
            **kwargs: Additional parameters specific to the provider
            
        Returns:
            WeatherForecast with forecast data
            
        Raises:
            Exception: If there's an error fetching the forecast data
        """
        raise NotImplementedError
    
    # Helper methods
    def save_settings(self) -> None:
        """Save provider settings to persistent storage."""
        settings = {
            'api_key': self._api_key,
            'offline_mode': self._offline_mode
        }
        
        # Save to QSettings
        self._settings.beginGroup(f"provider_{self.name}")
        for key, value in settings.items():
            if value is not None:
                self._settings.setValue(key, value)
        self._settings.endGroup()
        
        # Also save to JSON file for backup/portability
        self._save_to_json(settings)
    
    def _save_to_json(self, settings: Dict[str, Any]) -> None:
        """Save settings to JSON file.
        
        Args:
            settings: Dictionary of settings to save
        """
        try:
            # Create config directory if it doesn't exist
            self.DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
            # Load existing settings
            existing_settings = {}
            if self.DEFAULT_CONFIG_FILE.exists():
                with open(self.DEFAULT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    try:
                        existing_settings = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning("Invalid JSON in config file, overwriting")
            
            # Update with new settings
            existing_settings[self.name] = settings
            
            # Save to file
            with open(self.DEFAULT_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing_settings, f, indent=4)
                
        except Exception as e:
            logger.error("Error saving settings to JSON: %s", e)
    
    def load_settings(self) -> None:
        """Load provider settings from persistent storage."""
        # First try loading from QSettings
        self._settings.beginGroup(f"provider_{self.name}")
        
        # Load settings with fallback to instance values
        self._api_key = self._settings.value('api_key', self._api_key)
        self._offline_mode = self._settings.value('offline_mode', self._offline_mode, type=bool)
        
        self._settings.endGroup()
        
        # If no settings found, try loading from JSON
        if not self._api_key:
            self._load_from_json()
    
    def _load_from_json(self) -> None:
        """Load settings from JSON file."""
        try:
            if not self.DEFAULT_CONFIG_FILE.exists():
                return
                
            with open(self.DEFAULT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            if self.name in settings:
                provider_settings = settings[self.name]
                if not self._api_key and 'api_key' in provider_settings:
                    self._api_key = provider_settings['api_key']
                if 'offline_mode' in provider_settings:
                    self._offline_mode = provider_settings['offline_mode']
                    
        except Exception as e:
            logger.error("Error loading settings from JSON: %s", e)
    
    async def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the provider's API.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            Dictionary containing the JSON response
            
        Raises:
            Exception: If the request fails or returns an error
        """
        if self._offline_mode:
            raise RuntimeError("Cannot make HTTP request in offline mode")
            
        if not self._api_key and self.settings_schema.get('api_key', {}).get('required', True):
            raise ValueError(f"API key is required for {self.name}")
            
        # Add API key to params if required
        request_params = params.copy() if params else {}
        if self._api_key and 'key' not in request_params:
            request_params['key'] = self._api_key
            
        # Make the request asynchronously
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=request_params, timeout=10) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            # Update connection status
            self.connection_status_changed.emit(True)
            return data
            
        except aiohttp.ClientError as e:
            self.connection_status_changed.emit(False)
            logger.error("API request failed: %s", str(e))
            raise Exception(f"Failed to fetch data from {self.name}: {str(e)}") from e
    
    @classmethod
    def get_provider_class(cls, provider_name: str) -> Type['BaseProvider']:
        """Get the provider class by name.
        
        Args:
            provider_name: The name of the provider to get
            
        Returns:
            The provider class
            
        Raises:
            ValueError: If the provider is not found
        """
        # Import all provider modules to register them
        from script.weather_providers.openmeteo import OpenMeteoProvider
        
        providers = {
            'openmeteo': OpenMeteoProvider,
        }
        
        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
            
        return provider_class
    
    @classmethod
    def create_provider(cls, provider_name: str, **kwargs) -> 'BaseProvider':
        """Create a provider instance by name.
        
        Args:
            provider_name: The name of the provider to create
            **kwargs: Additional arguments to pass to the provider constructor
            
        Returns:
            An instance of the requested provider
            
        Raises:
            ValueError: If the provider is not found or cannot be instantiated
        """
        provider_class = cls.get_provider_class(provider_name)
        return provider_class(**kwargs)
    
    def __str__(self) -> str:
        """String representation of the provider."""
        return f"{self.display_name} ({'configured' if self.validate_api_key() else 'not configured'})"
