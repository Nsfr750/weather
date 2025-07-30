"""
Base weather provider module.

This module contains the base class for all weather providers.
"""

import abc
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, ClassVar

import requests
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class WeatherData:
    """Data class to hold weather information."""
    temperature: float
    condition: str
    humidity: float
    wind_speed: float
    wind_direction: float
    pressure: float
    visibility: Optional[float] = None
    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    icon: Optional[str] = None
    last_updated: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert weather data to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherData':
        """Create WeatherData from dictionary."""
        return cls(**data)


class _BaseProviderMeta(type(QObject), type(ABC)):
    """Metaclass to combine QObject and ABC metaclasses."""
    pass


class BaseProvider(QObject, ABC, Generic[T], metaclass=_BaseProviderMeta):
    """Base class for all weather providers.
    
    This class provides common functionality and interface for all weather providers.
    """
    
    # Signal emitted when the API key changes
    api_key_changed = pyqtSignal(str)
    
    # Default settings
    DEFAULT_CONFIG_DIR = Path.home() / '.weather_app'
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / 'providers.json'
    
    # Provider configuration
    name: ClassVar[str] = 'base'
    display_name: ClassVar[str] = 'Base Provider'
    requires_api_key: ClassVar[bool] = True
    api_key_name: ClassVar[str] = 'api_key'
    
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        """Initialize the base provider.
        
        Args:
            api_key: Optional API key for the provider
            offline_mode: If True, the provider will work in offline mode
        """
        super().__init__()
        self._api_key = api_key
        self._offline_mode = offline_mode
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
        self._offline_mode = value
    
    @abstractmethod
    def get_current_weather(self, location: str) -> WeatherData:
        """Get current weather for a location.
        
        Args:
            location: Location to get weather for (city name, coordinates, etc.)
            
        Returns:
            WeatherData object with current weather information
            
        Raises:
            Exception: If there's an error fetching the weather data
        """
        pass
    
    @abstractmethod
    def get_forecast(self, location: str, days: int = 5) -> List[WeatherData]:
        """Get weather forecast for a location.
        
        Args:
            location: Location to get forecast for
            days: Number of days to forecast (1-16, depends on provider)
            
        Returns:
            List of WeatherData objects for each forecast period
        """
        pass
    
    def validate_api_key(self) -> bool:
        """Validate the current API key.
        
        Returns:
            bool: True if the API key is valid, False otherwise
        """
        if not self.requires_api_key:
            return True
            
        if not self._api_key:
            logger.warning(f"No API key provided for {self.name}")
            return False
            
        # Default implementation assumes the key is valid if it exists
        # Override in subclasses for actual validation
        return True
    
    def save_settings(self) -> None:
        """Save provider settings to persistent storage."""
        settings = {
            'api_key': self._api_key,
            'offline_mode': self._offline_mode,
            'provider_name': self.name
        }
        
        # Save to QSettings
        self._settings.beginGroup(f"provider_{self.name}")
        for key, value in settings.items():
            if value is not None:
                self._settings.setValue(key, value)
        self._settings.endGroup()
        
        # Also save to JSON file for backup/portability
        self._save_to_json(settings)
    
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
            settings = self._load_from_json()
            if settings:
                self._api_key = settings.get('api_key')
                self._offline_mode = settings.get('offline_mode', self._offline_mode)
    
    def _save_to_json(self, settings: Dict[str, Any]) -> None:
        """Save settings to JSON file.
        
        Args:
            settings: Dictionary of settings to save
        """
        try:
            # Ensure config directory exists
            self.DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
            # Load existing settings
            existing = {}
            if self.DEFAULT_CONFIG_FILE.exists():
                with open(self.DEFAULT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    try:
                        existing = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning("Invalid JSON in config file, will be overwritten")
            
            # Update with new settings
            providers = existing.get('providers', {})
            providers[self.name] = settings
            existing['providers'] = providers
            
            # Save back to file
            with open(self.DEFAULT_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=4)
                
        except Exception as e:
            logger.error(f"Error saving settings to JSON: {e}")
    
    def _load_from_json(self) -> Dict[str, Any]:
        """Load settings from JSON file.
        
        Returns:
            Dictionary of settings for this provider, or empty dict if not found
        """
        try:
            if not self.DEFAULT_CONFIG_FILE.exists():
                return {}
                
            with open(self.DEFAULT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('providers', {}).get(self.name, {})
                
        except Exception as e:
            logger.error(f"Error loading settings from JSON: {e}")
            return {}
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the provider's API.
        
        Args:
            url: The URL to request
            params: Query parameters to include in the request
            
        Returns:
            The JSON response as a dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if self._offline_mode:
            raise ConnectionError("Offline mode is enabled")
            
        if not self._api_key and self.requires_api_key:
            raise ValueError(f"API key is required for {self.name}")
            
        # Add API key to params if needed
        if self.requires_api_key and self.api_key_name not in (params or {}):
            params = params or {}
            params[self.api_key_name] = self._api_key
            
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    @classmethod
    def get_provider_class(cls, provider_name: str) -> Type['BaseProvider']:
        """Get a provider class by name.
        
        Args:
            provider_name: The name of the provider to get
            
        Returns:
            The provider class
            
        Raises:
            ValueError: If the provider is not found
        """
        # Import all provider modules to register them
        from script.weather_providers.openweathermap import OpenWeatherMapProvider
        from script.weather_providers.weatherapi import WeatherAPIProvider
        from script.weather_providers.accuweather import AccuWeatherProvider
        
        providers = {
            'openweathermap': OpenWeatherMapProvider,
            'weatherapi': WeatherAPIProvider,
            'accuweather': AccuWeatherProvider,
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
