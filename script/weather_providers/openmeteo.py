"""
Open-Meteo provider implementation.
"""
import logging
import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal, QSettings, QMetaType, pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QLabel, QVBoxLayout, QFormLayout, QLineEdit

# Set up logger
logger = logging.getLogger('script.weather_providers.openmeteo')

# Create a session for aiohttp
async def get_session():
    return aiohttp.ClientSession()

@dataclass
class WeatherDataPoint:
    """A single data point of weather information."""
    temperature: float
    condition: str
    icon: str
    time: datetime
    humidity: float
    wind_speed: float
    wind_direction: float
    pressure: float
    precipitation: float
    cloud_cover: int
    visibility: float
    uv_index: float
    feels_like: float
    dew_point: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the data point to a dictionary."""
        return {
            'temperature': self.temperature,
            'condition': self.condition,
            'icon': self.icon,
            'time': self.time.isoformat(),
            'humidity': self.humidity,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'pressure': self.pressure,
            'precipitation': self.precipitation,
            'cloud_cover': self.cloud_cover,
            'visibility': self.visibility,
            'uv_index': self.uv_index,
            'feels_like': self.feels_like,
            'dew_point': self.dew_point
        }

class BaseWeatherProvider(QObject):
    """Base class for weather providers.
    
    This class defines the interface that all weather providers must implement.
    """
    # Signals
    weather_updated = pyqtSignal(dict)  # Emitted when weather data is updated
    forecast_updated = pyqtSignal(list)  # Emitted when forecast data is updated
    error_occurred = pyqtSignal(str)    # Emitted when an error occurs
    
    # Provider metadata
    name = "Base Weather Provider"
    description = "Base class for weather providers"
    author = ""
    version = "0.0.0"
    api_key_required = True
    
    def __init__(self, **kwargs):
        """Initialize the weather provider."""
        super().__init__()
        self._api_key = kwargs.get('api_key', '')
        self._units = kwargs.get('units', 'metric')
        self._language = kwargs.get('language', 'en')
        self._offline_mode = kwargs.get('offline_mode', False)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the provider."""
        self._initialized = True
        return True
    
    async def cleanup(self):
        """Clean up resources used by the provider."""
        self._initialized = False
    
    async def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location.
        
        Args:
            location: Location string (city name, coordinates, etc.)
            
        Returns:
            Dictionary containing current weather data
        """
        raise NotImplementedError
    
    async def get_forecast(self, location: str, days: int = 5) -> List[Dict[str, Any]]:
        """Get weather forecast for a location.
        
        Args:
            location: Location string (city name, coordinates, etc.)
            days: Number of days to forecast (default: 5)
            
        Returns:
            List of dictionaries containing forecast data
        """
        raise NotImplementedError
    
    def get_settings_widget(self) -> QWidget:
        """Get a widget for configuring the provider.
        
        Returns:
            QWidget: Settings widget
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("No configuration available for this provider."))
        return widget
    
    def save_settings(self):
        """Save provider settings."""
        pass
    
    def load_settings(self):
        """Load provider settings."""
        pass

# Create a metaclass that combines QObject's metaclass
class OpenMeteoMeta(type(QObject)):
    pass

class OpenMeteoProvider(BaseWeatherProvider, QObject, metaclass=OpenMeteoMeta):
    """Weather data provider for Open-Meteo API."""
    
    # Plugin metadata
    name = "Open-Meteo"
    description = "Open-Meteo Weather API Provider"
    author = "Nsfr750"
    version = "1.0.0"
    api_key_required = False  # Open-Meteo doesn't require an API key for basic usage
    
    # Signals
    api_key_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    BASE_URL = 'https://api.open-meteo.com/v1/'
    
    def __init__(self, **kwargs):
        """Initialize the OpenMeteo provider.
        
        Args:
            **kwargs: Configuration options including:
                - api_key: API key (not required for Open-Meteo)
                - units: Units system ('metric' or 'imperial')
                - language: Language code for responses
        """
        # Initialize QObject first
        QObject.__init__(self)
        
        # Initialize the _api_key attribute before BaseWeatherProvider.__init__
        self._api_key = kwargs.get('api_key', '')
        
        # Initialize BaseWeatherProvider with plugin metadata
        BaseWeatherProvider.__init__(self, api_key=self._api_key)
        
        # Initialize instance variables
        self._settings = QSettings("WeatherApp", "WeatherProviders")
        self.units = kwargs.get('units', 'metric')
        self.language = kwargs.get('language', 'en')
        self._offline_mode = kwargs.get('offline_mode', False)
        self._initialized = False
        
        # Load provider-specific settings
        self._load_settings()
    
    def _load_settings(self):
        """Load provider settings from QSettings."""
        try:
            # Load settings from QSettings
            settings = self._settings.value("OpenMeteo", {})
            
            if not isinstance(settings, dict):
                settings = {}
            
            # Apply loaded settings
            self.units = settings.get('units', self.units)
            self.language = settings.get('language', self.language)
            self._offline_mode = settings.get('offline_mode', self._offline_mode)
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save provider settings to QSettings."""
        try:
            # Prepare settings to save
            settings = {
                'units': self.units,
                'language': self.language,
                'offline_mode': self._offline_mode
            }
            
            # Save to QSettings
            self._settings.setValue("OpenMeteo", settings)
            self._settings.sync()
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
        
    async def initialize(self, app=None):
        """Initialize the plugin.
        
        Args:
            app: Reference to the main application instance (optional)
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self._initialized:
            return True
            
        try:
            # Perform any necessary initialization here
            logger.info(f"Initializing {self.name} provider")
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} provider: {str(e)}")
            self._initialized = False
            return False
            
    async def cleanup(self):
        """Clean up resources used by the provider.
        
        This is a coroutine that will be awaited by the application.
        """
        try:
            # Perform any necessary cleanup here
            logger.info(f"Cleaning up {self.name} provider")
            self._initialized = False
        except Exception as e:
            logger.error(f"Error during {self.name} cleanup: {str(e)}")
        
    @property
    def api_key(self):
        """Get the API key."""
        return getattr(self, '_api_key', '')
        
    @api_key.setter
    def api_key(self, value):
        """Set the API key and emit signal if changed."""
        old_value = getattr(self, '_api_key', '')
        self._api_key = value if value is not None else ''
        if old_value != self._api_key:
            self.api_key_changed.emit(self._api_key)
    
    async def _make_request(self, endpoint, params=None):
        """Make an async request to the Open-Meteo API.
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Additional parameters
            
        Returns:
            dict: JSON response
        """
        if params is None:
            params = {}
            
        # Open-Meteo doesn't require an API key for basic usage
        params.update({
            'temperature_unit': 'celsius' if self.units == 'metric' else 'fahrenheit',
            'windspeed_unit': 'kmh' if self.units == 'metric' else 'mph',
            'precipitation_unit': 'mm',
            'timezone': 'auto',
            'timeformat': 'iso8601'
        })
        
        session = await get_session()
        try:
            async with session.get(f"{self.BASE_URL}{endpoint}", params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
        finally:
            await session.close()
    
    async def _geocode_location(self, location):
        """Convert location name to coordinates using Open-Meteo's geocoding."""
        if ',' in location:  # Already coordinates
            lat, lon = location.split(',')
            return float(lat.strip()), float(lon.strip())
            
        # Geocode the location name
        session = await get_session()
        try:
            async with session.get(
                'https://geocoding-api.open-meteo.com/v1/search',
                params={'name': location, 'count': 1, 'language': self.language, 'format': 'json'}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                if not data.get('results'):
                    raise ValueError(f"Location '{location}' not found")
                    
                return data['results'][0]['latitude'], data['results'][0]['longitude']
        except Exception as e:
            logger.error(f"Geocoding failed: {str(e)}")
            raise
        finally:
            await session.close()
    
    async def get_current_weather(self, location):
        """Get current weather for a location."""
        try:
            lat, lon = await self._geocode_location(location)
            
            # Get current weather and daily forecast in one request
            data = await self._make_request('forecast', {
                'latitude': lat,
                'longitude': lon,
                'current_weather': 'true',
                'daily': 'weathercode,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,precipitation_hours,windspeed_10m_max,winddirection_10m_dominant',
                'hourly': 'temperature_2m,relativehumidity_2m,apparent_temperature,precipitation,weathercode,pressure_msl,visibility,windspeed_10m,winddirection_10m',
                'models': 'best_match'
            })
            
            current = data['current_weather']
            
            # Get additional data from hourly (nearest hour)
            now = datetime.utcnow()
            hourly = data['hourly']
            time_index = min(range(len(hourly['time'])), 
                          key=lambda i: abs(datetime.fromisoformat(hourly['time'][i]) - now))
            
            return {
                'temp': current['temperature'],
                'feels_like': hourly['apparent_temperature'][time_index],
                'humidity': hourly['relativehumidity_2m'][time_index] if 'relativehumidity_2m' in hourly else None,
                'pressure': hourly['pressure_msl'][time_index] if 'pressure_msl' in hourly else None,
                'wind_speed': current['windspeed'],
                'wind_direction': current['winddirection'],
                'description': self._get_weather_description(current['weathercode']),
                'icon': self._get_weather_icon(current['weathercode']),
                'visibility': hourly['visibility'][time_index] if 'visibility' in hourly else 10000,  # Default 10km
                'clouds': 0,  # Not directly available in Open-Meteo
                'rain': hourly['precipitation'][time_index] if 'precipitation' in hourly else 0,
                'snow': 0,  # Not directly available in Open-Meteo
                'dt': datetime.fromisoformat(current['time']).timestamp(),
                'sunrise': 0,  # Will be updated from daily data if available
                'sunset': 0,   # Will be updated from daily data if available
                'location': location,
                'coord': {'lat': lat, 'lon': lon}
            }
            
        except Exception as e:
            raise Exception(f"Failed to get current weather: {str(e)}")
    
    async def get_forecast(self, location, days=5):
        """Get weather forecast for a location."""
        try:
            lat, lon = await self._geocode_location(location)
            
            data = await self._make_request('forecast', {
                'latitude': lat,
                'longitude': lon,
                'daily': 'weathercode,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,precipitation_hours,windspeed_10m_max,winddirection_10m_dominant',
                'timezone': 'auto',
                'forecast_days': min(days, 16)  # Open-Meteo supports up to 16 days
            })
            
            forecast = []
            for i in range(min(len(data['daily']['time']), days)):
                forecast.append({
                    'dt': datetime.fromisoformat(data['daily']['time'][i]).timestamp(),
                    'temp': {
                        'max': data['daily']['temperature_2m_max'][i],
                        'min': data['daily']['temperature_2m_min'][i]
                    },
                    'feels_like': {
                        'max': data['daily']['apparent_temperature_max'][i],
                        'min': data['daily']['apparent_temperature_min'][i]
                    },
                    'weather': [{
                        'description': self._get_weather_description(data['daily']['weathercode'][i]),
                        'icon': self._get_weather_icon(data['daily']['weathercode'][i]),
                        'code': data['daily']['weathercode'][i]
                    }],
                    'wind_speed': data['daily']['windspeed_10m_max'][i],
                    'wind_deg': data['daily']['winddirection_10m_dominant'][i],
                    'pop': 0,  # Probability of precipitation not directly available
                    'rain': data['daily']['precipitation_sum'][i],
                    'snow': 0,  # Snow not directly available
                    'humidity': None,  # Not available in daily data
                    'pressure': None   # Not available in daily data
                })
                
            return forecast
            
        except Exception as e:
            raise Exception(f"Failed to get forecast: {str(e)}")
    
    def get_alerts(self, location):
        """Get weather alerts for a location."""
        # Open-Meteo doesn't provide alerts in the free tier
        return []
    
    def validate_api_key(self, api_key):
        """Validate the API key."""
        # Open-Meteo doesn't require an API key for basic usage
        return True, "API key validation not required for Open-Meteo"
    
    def update_config(self, **kwargs):
        """Update provider configuration."""
        if 'api_key' in kwargs:
            self.api_key = kwargs['api_key']
        if 'units' in kwargs:
            self.units = kwargs['units']
        if 'language' in kwargs:
            self.language = kwargs['language']
    
    def _get_weather_description(self, code):
        """Convert weather code to description."""
        # WMO Weather interpretation codes (https://open-meteo.com/en/docs)
        codes = {
            0: 'Clear sky',
            1: 'Mainly clear',
            2: 'Partly cloudy',
            3: 'Overcast',
            45: 'Fog',
            48: 'Depositing rime fog',
            51: 'Light drizzle',
            53: 'Moderate drizzle',
            55: 'Dense drizzle',
            56: 'Light freezing drizzle',
            57: 'Dense freezing drizzle',
            61: 'Slight rain',
            63: 'Moderate rain',
            65: 'Heavy rain',
            66: 'Light freezing rain',
            67: 'Heavy freezing rain',
            71: 'Slight snow fall',
            73: 'Moderate snow fall',
            75: 'Heavy snow fall',
            77: 'Snow grains',
            80: 'Slight rain showers',
            81: 'Moderate rain showers',
            82: 'Violent rain showers',
            85: 'Slight snow showers',
            86: 'Heavy snow showers',
            95: 'Thunderstorm',
            96: 'Thunderstorm with slight hail',
            99: 'Thunderstorm with heavy hail'
        }
        return codes.get(code, 'Unknown')
    
    def _get_weather_icon(self, code):
        """Convert weather code to icon name."""
        # Map Open-Meteo weather codes to icon names
        if code in [0, 1]:
            return '01d'  # Clear sky
        elif code == 2:
            return '02d'  # Partly cloudy
        elif code == 3:
            return '03d'  # Overcast
        elif code in [45, 48]:
            return '50d'  # Fog
        elif code in [51, 53, 55, 56, 57]:
            return '09d'  # Drizzle
        elif code in [61, 63, 65, 66, 67, 80, 81, 82]:
            return '10d'  # Rain
        elif code in [71, 73, 75, 77, 85, 86]:
            return '13d'  # Snow
        elif code in [95, 96, 99]:
            return '11d'  # Thunderstorm
        return '01d'  # Default
