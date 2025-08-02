"""
OpenWeatherMap Plugin for the Weather App.

This plugin provides weather data using the OpenWeatherMap API.
"""

import asyncio
import logging
import sys
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from script.plugin_system.weather_provider import (
    BaseWeatherProvider,
    WeatherDataPoint,
    WeatherForecast,
    WeatherCondition
)

logger = logging.getLogger(__name__)

class OpenWeatherMapProvider(BaseWeatherProvider):
    """OpenWeatherMap weather provider implementation."""
        
    # Define settings schema
    settings_schema = {
        "api_key": {
            "type": "string",
            "required": True,
            "secret": True,
            "display_name": "API Key",
            "description": "Your OpenWeatherMap API key"
        },
        "units": {
            "type": "string",
            "required": False,
            "default": "metric",
            "options": ["metric", "imperial", "standard"],
            "display_name": "Units",
            "description": "Temperature units (metric, imperial, or standard)"
        }
    }
    
    def __init__(self, config=None, **kwargs):
        """Initialize the OpenWeatherMap provider.
        
        Args:
            config: Configuration dictionary containing api_key, units, language, etc.
            **kwargs: Additional configuration parameters (merged with config)
        """
        # Merge config dict with kwargs
        if config is None:
            config = {}
        config.update(kwargs)
        
        # Set default values from config or environment
        if 'api_key' not in config:
            config['api_key'] = os.environ.get('OPENWEATHERMAP_API_KEY', '')
        if 'units' not in config:
            config['units'] = 'metric'
        if 'language' not in config:
            config['language'] = 'en'
            
        # Store config for later use before calling parent __init__
        self._config = config.copy()
        
        # Initialize with default values that will be overridden by parent
        self.api_key = config.get('api_key', '')
        self._api_key = self.api_key
        self.units = config.get('units', 'metric')
        self.language = config.get('language', 'en')
        self.offline_mode = config.get('offline_mode', False)
        
        # Set provider metadata
        self.name = "openweathermap"
        self.display_name = "OpenWeatherMap"
        self.description = "Provides weather data using the OpenWeatherMap API"
        self.author = "Nsfr750"
        self.version = "1.1.0"
        
        # Initialize the base class
        super().__init__(**config)
        
        # For compatibility with BaseWeatherProvider's _validate_settings
        self.settings = config
        
        # Set provider metadata
        self.name = "openweathermap"
        self.display_name = "OpenWeatherMap"
        self.description = "Provides weather data using the OpenWeatherMap API"
        self.author = "Nsfr750"
        self.version = "1.1.0"
        
        # For compatibility with BaseWeatherProvider's _validate_settings
        self.settings = config
        
        # Initialize session for connection pooling
        self.session = requests.Session()
        
        # API endpoints
        self.current_weather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        
        logger.info(f"Initialized OpenWeatherMap provider with units: {self.units}, language: {self.language}")
    
    async def get_current_weather(self, location: str) -> WeatherDataPoint:
        """Get current weather for a location.
        
        Args:
            location: City name, ZIP code, or coordinates (lat,lon)
            
        Returns:
            WeatherDataPoint with current weather data
        """
        params = {
            'q': location,
            'appid': self._api_key,
            'units': self.units,
            'lang': self.language
        }
        
        try:
            data = await self._make_request(self.current_weather_url, params)
            return self._parse_current_weather(data)
        except Exception as e:
            logger.error(f"Failed to get current weather: {e}")
            raise
    
    async def _get_coordinates(self, location: str) -> tuple[float, float]:
        """Get latitude and longitude for a location name.
        
        Args:
            location: Location name (e.g., 'London,UK' or 'New York,US')
            
        Returns:
            Tuple of (latitude, longitude)
            
        Raises:
            ValueError: If the location cannot be found or if there's an API error
        """
        # Check if location is already in coordinates format (lat,lon)
        if ',' in location and all(part.strip().lstrip('-').replace('.', '').isdigit() 
                                 for part in location.split(',')):
            try:
                lat, lon = map(float, location.split(','))
                logger.debug(f"Using provided coordinates: ({lat}, {lon})")
                return lat, lon
            except (ValueError, TypeError) as e:
                logger.debug(f"Failed to parse coordinates from '{location}': {e}")
                pass
        
        # Try to get coordinates by making a weather API call directly
        # This works because the weather API can resolve location names
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': location,
            'appid': self._api_key,
            'units': self.units
        }
        
        try:
            logger.debug(f"Resolving location: {location}")
            data = await self._make_request(weather_url, params)
            
            if not data or 'coord' not in data:
                logger.warning(f"No coordinates found for location: {location}")
                # Try with a different format (city,country)
                if ',' not in location:
                    location = f"{location},GB"  # Default to UK
                    logger.debug(f"Trying with country code: {location}")
                    params['q'] = location
                    data = await self._make_request(weather_url, params)
                    
                    if not data or 'coord' not in data:
                        raise ValueError(f"Location not found: {location}")
                else:
                    raise ValueError(f"Location not found: {location}")
            
            coord = data.get('coord', {})
            lat = coord.get('lat')
            lon = coord.get('lon')
            
            if lat is None or lon is None:
                raise ValueError(f"Could not determine coordinates for location: {location}")
                
            logger.info(f"Resolved location '{location}' to coordinates: ({lat}, {lon})")
            return lat, lon
            
        except Exception as e:
            logger.error(f"Failed to get coordinates for location '{location}': {e}", exc_info=True)
            # Try one more time with a default location if all else fails
            if location.lower() != 'london,gb':
                logger.info(f"Falling back to default location: London,GB")
                return await self._get_coordinates("London,GB")
            raise ValueError(f"Failed to resolve location: {location}") from e
    
    def _validate_settings(self) -> None:
        """Validate the provider settings."""
        if not self.api_key:
            error_msg = (
                "OpenWeatherMap API key is required.\n\n"
                "You can get a free API key by signing up at:\n"
                "https://home.openweathermap.org/users/sign_up\n\n"
                "After signing up, you can find your API key in your account settings.\n"
                "Once you have your API key, you can:\n"
                "1. Set it in the application settings, or\n"
                "2. Set the OPENWEATHERMAP_API_KEY environment variable"
            )
            logger.warning(error_msg)
            # Instead of raising an error, we'll set offline mode
            self.offline_mode = True
            return
            
        # If we have an API key, continue with parent validation
        super()._validate_settings()
    
    async def initialize(self) -> bool:
        """Initialize the weather provider and verify API key.
        
        Returns:
            bool: True if initialization was successful, False otherwise
            
        Raises:
            ValueError: If initialization fails due to missing or invalid API key
        """
        if hasattr(self, '_initialized') and self._initialized:
            return True
            
        try:
            # Test the API key with a simple request
            test_params = {
                'q': 'London,UK',  # Test with a known location
                'appid': self.api_key,
                'units': self.config.get('units', 'metric'),
                'lang': self.config.get('language', 'en')
            }
            
            # Use the async _make_request method
            response = await self._make_request(
                self.current_weather_url,
                params=test_params
            )
            
            if response.get('cod') == 200:
                self._initialized = True
                logger.info(f"Successfully initialized {self.name} provider")
                return True
            elif response.get('cod') == 401:
                error_msg = "Invalid OpenWeatherMap API key. Please check your API key and try again."
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                error_msg = f"Failed to validate API key. Response: {response}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            error_msg = f"Failed to initialize OpenWeatherMap provider: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
    
    async def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the OpenWeatherMap API.
        
        Args:
            url: The URL to make the request to
            params: Optional query parameters
            
        Returns:
            The JSON response as a dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If the API returns an error
        """
        if params is None:
            params = {}
            
        # Add common parameters
        params.update({
            'appid': self._api_key,
            'units': self.units,
            'lang': self.language
        })
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.session.get(url, params=params, timeout=10)
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', 'Unknown error')
                    logger.error(f"API error: {error_msg}")
                    raise ValueError(f"API error: {error_msg}") from e
                except ValueError:
                    pass
            raise
            
    async def get_forecast(self, location: str, days: int = 5, **kwargs) -> WeatherForecast:
        """
        Get weather forecast for a location.
        
        Args:
            location: Location name or coordinates (format: "lat,lon")
            days: Number of days to forecast (1-16)
            **kwargs: Additional parameters for the API request
            
        Returns:
            WeatherForecast object with forecast data
        """
        if not self._api_key:
            raise ValueError("OpenWeatherMap API key is required")
            
        # Get coordinates for location
        lat, lon = await self._get_coordinates(location)
        
        # Build parameters for the API request
        params = {
            'lat': lat,
            'lon': lon,
            'cnt': days * 8  # 8 data points per day (3-hour intervals)
        }
        
        # Add any additional parameters from kwargs
        params.update(kwargs)
        
        try:
            # Make the request using the helper method
            data = await self._make_request(self.forecast_url, params)
            
            # Parse the response
            return self._parse_forecast(data)
            
        except Exception as e:
            logger.error(f"Failed to get forecast: {e}")
            raise
    
    def _map_condition_code(self, code: int) -> WeatherCondition:
        """Map OpenWeatherMap condition code to WeatherCondition enum."""
        # Thunderstorm
        if 200 <= code <= 232:
            return WeatherCondition.THUNDERSTORM
        # Drizzle
        elif 300 <= code <= 321:
            return WeatherCondition.DRIZZLE
        # Rain
        elif 500 <= code <= 531:
            return WeatherCondition.RAIN
        # Snow
        elif 600 <= code <= 622:
            return WeatherCondition.SNOW
        # Atmosphere
        elif 700 <= code <= 781:
            if code == 781:  # Tornado
                return WeatherCondition.TORNADO
            return WeatherCondition.FOG
        # Clear
        elif code == 800:
            return WeatherCondition.CLEAR
        # Clouds
        elif 801 <= code <= 804:
            return WeatherCondition.CLOUDS
        # Default to clear
        return WeatherCondition.CLEAR
        
    def _parse_current_weather(self, data: Dict[str, Any]) -> WeatherDataPoint:
        """Parse current weather data from API response."""
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        wind = data.get('wind', {})
        sys_data = data.get('sys', {})
        
        # Map OpenWeatherMap condition code to our WeatherCondition enum
        condition_code = weather.get('id', 800)
        condition = self._map_condition_code(condition_code)
        
        # Get the appropriate icon based on condition and time of day
        icon = weather.get('icon', '01d')
        
        # Create the WeatherDataPoint with the correct parameters
        return WeatherDataPoint(
            timestamp=datetime.fromtimestamp(data.get('dt', 0)),
            temperature=main.get('temp', 0.0),
            feels_like=main.get('feels_like', 0.0),
            humidity=main.get('humidity', 0),
            pressure=main.get('pressure', 0),
            wind_speed=wind.get('speed', 0.0),
            wind_direction=wind.get('deg', 0),
            condition=condition,
            description=weather.get('description', ''),
            icon=f"https://openweathermap.org/img/wn/{icon}@2x.png",
            visibility=data.get('visibility', 10000) / 1000.0,  # Convert to km
            precipitation=(data.get('rain', {}).get('1h', 0) or 
                         data.get('snow', {}).get('1h', 0) or 0),
            uv_index=None,  # Not available in current weather API
            dew_point=main.get('dew_point', None),
            wind_gust=wind.get('gust', 0.0)
        )
    
    def _parse_forecast(self, data: Dict[str, Any]) -> WeatherForecast:
        """Parse forecast data from API response."""
        city = data.get('city', {})
        forecast_list = data.get('list', [])
        
        # Parse each forecast point
        forecast_points = []
        for point in forecast_list:
            main = point.get('main', {})
            weather = point.get('weather', [{}])[0]
            wind = point.get('wind', {})
            clouds = point.get('clouds', {})
            
            # Map condition code to WeatherCondition enum
            condition_code = weather.get('id', 800)
            condition = self._map_condition_code(condition_code)
            
            # Get icon URL
            icon = weather.get('icon', '01d')
            
            # Calculate total precipitation (rain + snow) in mm
            precipitation = (point.get('rain', {}).get('3h', 0) or 
                           point.get('snow', {}).get('3h', 0) or 0)
            
            # Create the weather data point with the correct parameters
            forecast_points.append(WeatherDataPoint(
                timestamp=datetime.fromtimestamp(point.get('dt', 0)),
                temperature=main.get('temp', 0.0),
                feels_like=main.get('feels_like', 0.0),
                humidity=main.get('humidity', 0),
                pressure=main.get('pressure', 0),
                wind_speed=wind.get('speed', 0.0),
                wind_direction=wind.get('deg', 0),
                condition=condition,
                description=weather.get('description', ''),
                icon=f"https://openweathermap.org/img/wn/{icon}@2x.png",
                precipitation=precipitation,
                cloudiness=clouds.get('all', 0),
                visibility=point.get('visibility'),
                wind_gust=wind.get('gust', 0.0)
            ))
        
        # For simplicity, we'll use the first forecast point as the current weather
        # In a real implementation, you'd want to get the current weather from the API
        current = forecast_points[0] if forecast_points else None
        
        # For OpenWeatherMap, we don't have separate hourly and daily forecasts in this implementation
        # So we'll just use the same forecast points for both
        return WeatherForecast(
            location=city.get('name', 'Unknown'),
            latitude=city.get('coord', {}).get('lat', 0),
            longitude=city.get('coord', {}).get('lon', 0),
            timezone=data.get('timezone', 'UTC'),
            current=current,
            hourly=forecast_points,
            daily=[],  # Daily forecasts would be parsed separately
            alerts=[]  # Alerts would be parsed from the API response if available
        )


# Plugin class that will be discovered by the plugin system
class OpenWeatherMapPlugin:
    """OpenWeatherMap plugin for the Weather App."""
    
    def __init__(self):
        self.name = "openweathermap"
        self.display_name = "OpenWeatherMap"
        self.version = "1.0.0"
        self.author = "Weather App Team"
        self.description = "Provides weather data using the OpenWeatherMap API"
        self._provider = None
    
    def get_weather_provider(self, **kwargs) -> OpenWeatherMapProvider:
        """Create and return an instance of the OpenWeatherMap provider.
        
        Args:
            **kwargs: Configuration options for the provider
            
        Returns:
            An instance of OpenWeatherMapProvider
            
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        try:
            # Validate API key is provided
            if not kwargs.get('api_key'):
                raise ValueError("API key is required for OpenWeatherMap provider")
                
            # Set default units if not provided
            if 'units' not in kwargs:
                kwargs['units'] = 'metric'
                
            return OpenWeatherMapProvider(**kwargs)
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenWeatherMap provider: {str(e)}")
            raise
    
    def get_settings_schema(self) -> dict:
        """Get the settings schema for this plugin.
        
        Returns:
            Dictionary containing the settings schema
        """
        return OpenWeatherMapProvider.settings_schema
        
    def initialize(self):
        """Initialize the plugin.
        
        This method is called when the plugin is loaded.
        Can be used to perform any necessary setup.
        """
        logger.info(f"Initialized {self.display_name} plugin v{self.version}")
        return True
