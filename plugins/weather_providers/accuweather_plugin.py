"""
AccuWeather Provider Implementation.
# Plugin metadata
__plugin_name__ = "Accuweather"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Accuweather weather provider plugin"


This module provides the AccuWeather implementation of the weather provider interface.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import logging
import os
from script.plugin_system.weather_provider import datetime
from script.plugin_system.weather_provider import Dict, List, Optional, Any

import requests

from script.plugin_system.weather_provider import BaseWeatherProvider, WeatherDataPoint, WeatherForecast, WeatherCondition

# Configure logging
logger = logging.getLogger(__name__)

class AccuWeatherProvider(BaseWeatherProvider):
    """AccuWeather weather provider implementation."""
    
    # Provider metadata
    name = 'accuweather'
    display_name = 'AccuWeather'
    requires_api_key = True
    description = "Provides weather data using the AccuWeather API"
    author = "Nsfr750"
    version = "1.1.0"
    
    BASE_URL = 'http://dataservice.accuweather.com'
    LOCATION_AUTOCOMPLETE = f"{BASE_URL}/locations/v1/cities/autocomplete"
    CURRENT_WEATHER = f"{BASE_URL}/currentconditions/v1/{{location_key}}"
    FORECAST = f"{BASE_URL}/forecasts/v1/daily/5day/{{location_key}}"
    
    def __init__(self, config=None, **kwargs):
        """Initialize the AccuWeather provider.
        
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
            config['api_key'] = os.environ.get('ACCUWEATHER_API_KEY')
        if 'units' not in config:
            config['units'] = 'metric'
        if 'language' not in config:
            config['language'] = 'en'
            
        super().__init__(**config)
        
        # Store config for later use
        self.config = config
        
        # Set instance variables from config with proper defaults
        self.api_key = config.get('api_key', 'FuOHwt5hJQz3esuyl6yJrRBSRKqw3mjX')
        self._api_key = self.api_key  # For compatibility with base class
        self.units = config.get('units', 'metric')
        self.language = config.get('language', 'en')
        self.offline_mode = config.get('offline_mode', False)
        
        # Initialize session for connection pooling
        self.session = requests.Session()
                
        # Initialize caches and state
        self._location_cache = {}
        self._initialized = False
        
    async def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the AccuWeather API.
        
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
            
        # Add API key to all requests
        params['apikey'] = self.api_key
        
        # Add language parameter if not already specified
        if 'language' not in params and self.language:
            params['language'] = self.language
            
        # Add metric/imperial units parameter
        if 'metric' not in params and 'details' not in params:
            params['metric'] = self.units == 'metric'
            
        try:
            # Make the request asynchronously
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
    
    async def initialize(self) -> bool:
        """Initialize the weather provider.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self._initialized:
            return True
            
        try:
            # Test the API key by making a simple request
            if not self.offline_mode and self.api_key:
                test_params = {'q': 'london'}
                await self._make_request(self.LOCATION_AUTOCOMPLETE, test_params)
                
            self._initialized = True
            logger.info(f"Successfully initialized {self.display_name} provider")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize {self.display_name} provider: {str(e)}"
            logger.error(error_msg)
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                if e.response.status_code == 401:
                    error_msg = f"Invalid API key for {self.display_name}. Please check your configuration."
            raise ValueError(error_msg) from e
        
    async def get_current_weather(self, location: str) -> WeatherDataPoint:
        """Get current weather for a location.
        
        Args:
            location: Location string (e.g., "New York,US" or "London")
            
        Returns:
            WeatherDataPoint: Current weather data
            
        Raises:
            ValueError: If location is not found or no weather data is available
        """
        location_key = await self._get_location_key(location)
        if not location_key:
            raise ValueError(f"Location not found: {location}")
            
        url = self.CURRENT_WEATHER.format(location_key=location_key)
        params = {
            'apikey': self.api_key, 
            'details': 'true',
            'language': self.language
        }
        
        response = await self._make_request(url, params)
        if not response or not isinstance(response, list) or not response:
            raise ValueError("No current weather data available")
            
        return self._parse_current_weather(response[0])
    
    async def get_forecast(self, location: str, days: int = 5) -> WeatherForecast:
        """Get weather forecast for a location.
        
        Args:
            location: Location string (e.g., "New York,US" or "London")
            days: Number of days to forecast (1-5)
            
        Returns:
            WeatherForecast: Forecast data including current and daily forecasts
            
        Raises:
            ValueError: If location is not found or no forecast data is available
        """
        # First get current weather to include in the forecast
        current = await self.get_current_weather(location)
        
        # Get the location key for the forecast request
        location_key = await self._get_location_key(location)
        if not location_key:
            raise ValueError(f"Location not found: {location}")
            
        # Get the forecast data
        url = self.FORECAST.format(location_key=location_key)
        params = {
            'apikey': self.api_key,
            'metric': 'true' if self.units == 'metric' else 'false',
            'details': 'true',
            'language': self.language
        }
        
        response = await self._make_request(url, params)
        if not response:
            raise ValueError("No forecast data available")
        
        # Parse the forecast data
        daily_forecasts = self._parse_forecast(response, days)
        
        # Create a WeatherForecast object
        return WeatherForecast(
            location=location,
            latitude=0,  # Not available in the response
            longitude=0,  # Not available in the response
            timezone="UTC",  # Default timezone, adjust if timezone info is available
            current=current,
            hourly=[],  # AccuWeather doesn't provide hourly data in the free tier
            daily=daily_forecasts,
            alerts=[]  # No alerts in the response
        )
    
    def validate_api_key(self) -> bool:
        if not self.requires_api_key or not self.api_key:
            return False
            
        try:
            params = {'apikey': self.api_key, 'q': 'London'}
            response = requests.get(self.LOCATION_AUTOCOMPLETE, params=params, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return False
    
    async def _get_location_key(self, location: str) -> Optional[str]:
        """Get the location key for a given location string.
        
        Args:
            location: Location string in format "City,CountryCode" or "City"
            
        Returns:
            str: Location key if found, None otherwise
        """
        if not location:
            return None
            
        # Check cache first
        if location in self._location_cache:
            return self._location_cache[location]
            
        try:
            # Try with the full location string first (e.g., "New York,US")
            params = {
                'apikey': self.api_key,
                'q': location,
                'language': self.language
            }
            
            # Make the API request
            response = await self._make_request(self.LOCATION_AUTOCOMPLETE, params)
            
            if not response or not isinstance(response, list) or not response:
                # If no results, try with just the city name
                if ',' in location:
                    city_name = location.split(',')[0].strip()
                    params['q'] = city_name
                    response = await self._make_request(self.LOCATION_AUTOCOMPLETE, params)
                    
                    if not response or not isinstance(response, list) or not response:
                        return None
            
            # Get the first result's key
            location_key = response[0].get('Key')
            if location_key:
                # Cache the result
                self._location_cache[location] = location_key
                
            return location_key
            
        except Exception as e:
            logger.error(f"Error getting location key for {location}: {e}")
            return None
    
    def _parse_current_weather(self, data: Dict[str, Any]) -> WeatherDataPoint:
        """Parse current weather data from AccuWeather API response.
        
        Args:
            data: Raw weather data from AccuWeather API
            
        Returns:
            WeatherDataPoint: Parsed weather data
        """
        temperature = data.get('Temperature', {}).get('Metric', {}).get('Value', 0)
        condition = data.get('WeatherText', 'Unknown')
        
        # Map AccuWeather condition to our WeatherCondition enum
        condition_map = {
            'sunny': WeatherCondition.CLEAR,
            'clear': WeatherCondition.CLEAR,
            'mostly sunny': WeatherCondition.CLEAR,
            'partly sunny': WeatherCondition.CLOUDS,
            'mostly cloudy': WeatherCondition.CLOUDS,
            'cloudy': WeatherCondition.CLOUDS,
            'overcast': WeatherCondition.CLOUDS,
            'fog': WeatherCondition.FOG,
            'drizzle': WeatherCondition.DRIZZLE,
            'rain': WeatherCondition.RAIN,
            'showers': WeatherCondition.RAIN,
            'thunderstorm': WeatherCondition.THUNDERSTORM,
            'snow': WeatherCondition.SNOW,
            'flurries': WeatherCondition.SNOW,
            'ice': WeatherCondition.SNOW,
            'sleet': WeatherCondition.SNOW,
            'windy': WeatherCondition.SQUALL,  # Using SQUALL as the closest match for WIND
            'tornado': WeatherCondition.SQUALL,  # Using SQUALL as the closest match for TORNADO
            'hurricane': WeatherCondition.SQUALL,  # Using SQUALL as the closest match for HURRICANE
        }
        
        # Get the condition from the map, default to CLEAR
        condition_str = condition.lower()
        weather_condition = condition_map.get(condition_str, WeatherCondition.CLEAR)
        
        # Get the weather icon
        icon_num = data.get('WeatherIcon', 1)
        icon_url = f"https://developer.accuweather.com/sites/default/files/{icon_num:02d}-s.png"
        
        # Create and return the WeatherDataPoint
        return WeatherDataPoint(
            timestamp=datetime.now(),  # Current time as fallback
            temperature=temperature,
            feels_like=data.get('RealFeelTemperature', {}).get('Metric', {}).get('Value', temperature),
            humidity=data.get('RelativeHumidity', 0),
            pressure=data.get('Pressure', {}).get('Metric', {}).get('Value', 0),
            wind_speed=data.get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', 0) * 0.277778,  # km/h to m/s
            wind_direction=data.get('Wind', {}).get('Direction', {}).get('Degrees', 0),
            condition=weather_condition,
            description=condition,
            icon=icon_url,
            visibility=data.get('Visibility', {}).get('Metric', {}).get('Value'),
            wind_gust=data.get('WindGust', {}).get('Speed', {}).get('Metric', {}).get('Value', 0) * 0.277778  # km/h to m/s
        )
    
    def _parse_forecast(self, data: Dict[str, Any], days: int) -> List[WeatherDataPoint]:
        """Parse forecast data from AccuWeather API response.
        
        Args:
            data: Raw forecast data from AccuWeather API
            days: Number of days to include in the forecast
            
        Returns:
            List[WeatherDataPoint]: List of forecast data points
        """
        forecast_list = []
        
        for day_data in data.get('DailyForecasts', [])[:days]:
            # Get temperature data
            temp_high = day_data.get('Temperature', {}).get('Maximum', {})
            temp_low = day_data.get('Temperature', {}).get('Minimum', {})
            
            # Get day and night conditions
            day_condition = day_data.get('Day', {}).get('IconPhrase', 'unknown').lower()
            night_condition = day_data.get('Night', {}).get('IconPhrase', 'unknown').lower()
            
            # Map conditions to WeatherCondition enum
            condition_map = {
                'sunny': WeatherCondition.CLEAR,
                'clear': WeatherCondition.CLEAR,
                'mostly sunny': WeatherCondition.CLEAR,
                'partly sunny': WeatherCondition.CLOUDS,
                'mostly cloudy': WeatherCondition.CLOUDS,
                'cloudy': WeatherCondition.CLOUDS,
                'overcast': WeatherCondition.CLOUDS,
                'fog': WeatherCondition.FOG,
                'drizzle': WeatherCondition.DRIZZLE,
                'rain': WeatherCondition.RAIN,
                'showers': WeatherCondition.RAIN,
                'thunderstorm': WeatherCondition.THUNDERSTORM,
                'snow': WeatherCondition.SNOW,
                'flurries': WeatherCondition.SNOW,
                'ice': WeatherCondition.SNOW,
                'sleet': WeatherCondition.SNOW,
                'windy': WeatherCondition.SQUALL,
                'tornado': WeatherCondition.SQUALL,
                'hurricane': WeatherCondition.SQUALL,
            }
            
            # Get condition from map, default to CLEAR
            condition = condition_map.get(day_condition.lower(), WeatherCondition.CLEAR)
            
            # Create a timestamp from the forecast date
            forecast_date = datetime.fromisoformat(day_data.get('Date', '').replace('Z', '+00:00'))
            
            # Create forecast data point for the day
            forecast_list.append(WeatherDataPoint(
                timestamp=forecast_date,
                temperature=temp_high.get('Value', 0) if isinstance(temp_high, dict) else 0,
                feels_like=temp_high.get('Value', 0) if isinstance(temp_high, dict) else 0,  # Assuming feels like is same as temp
                humidity=day_data.get('Day', {}).get('RelativeHumidity', {}).get('Value', 0),
                pressure=day_data.get('Day', {}).get('Pressure', {}).get('Value', 0),
                wind_speed=day_data.get('Day', {}).get('Wind', {}).get('Speed', {}).get('Value', 0) * 0.277778,  # km/h to m/s
                wind_direction=day_data.get('Day', {}).get('Wind', {}).get('Direction', {}).get('Degrees', 0),
                wind_gust=day_data.get('Day', {}).get('WindGust', {}).get('Speed', {}).get('Value', 0) * 0.277778,  # km/h to m/s
                condition=condition,
                description=day_condition,
                icon=f"https://developer.accuweather.com/sites/default/files/{day_data.get('Day', {}).get('Icon', 1):02d}-s.png",
                precipitation=day_data.get('Day', {}).get('PrecipitationProbability', 0),
                cloudiness=day_data.get('Day', {}).get('CloudCover', 0)
            ))
            
        return forecast_list
