"""
WeatherAPI Provider Implementation.

This module provides the WeatherAPI.com implementation of the weather provider interface.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests

from .base_provider import BaseProvider, WeatherData

# Configure logging
logger = logging.getLogger(__name__)


class WeatherAPIProvider(BaseProvider):
    """WeatherAPI.com weather provider implementation."""
    
    # Provider configuration
    name = 'weatherapi'
    display_name = 'WeatherAPI.com'
    requires_api_key = True
    api_key_name = 'key'  # WeatherAPI uses 'key' as the parameter name
    
    # API endpoints
    BASE_URL = 'http://api.weatherapi.com/v1'
    CURRENT_WEATHER_URL = f"{BASE_URL}/current.json"
    FORECAST_URL = f"{BASE_URL}/forecast.json"
    
    # Weather condition codes to text mapping
    WEATHER_CONDITIONS = {
        1000: 'clear sky',
        1003: 'partly cloudy',
        1006: 'cloudy',
        1009: 'overcast',
        1030: 'mist',
        1063: 'patchy rain possible',
        1066: 'patchy snow possible',
        1069: 'patchy sleet possible',
        1072: 'patchy freezing drizzle possible',
        1087: 'thundery outbreaks possible',
        1114: 'blowing snow',
        1117: 'blizzard',
        1135: 'fog',
        1147: 'freezing fog',
        1150: 'patchy light drizzle',
        1153: 'light drizzle',
        1168: 'freezing drizzle',
        1171: 'heavy freezing drizzle',
        1180: 'patchy light rain',
        1183: 'light rain',
        1186: 'moderate rain at times',
        1189: 'moderate rain',
        1192: 'heavy rain at times',
        1195: 'heavy rain',
        1198: 'light freezing rain',
        1201: 'moderate or heavy freezing rain',
        1204: 'light sleet',
        1207: 'moderate or heavy sleet',
        1210: 'patchy light snow',
        1213: 'light snow',
        1216: 'patchy moderate snow',
        1219: 'moderate snow',
        1222: 'patchy heavy snow',
        1225: 'heavy snow',
        1237: 'ice pellets',
        1240: 'light rain shower',
        1243: 'moderate or heavy rain shower',
        1246: 'torrential rain shower',
        1249: 'light sleet showers',
        1252: 'moderate or heavy sleet showers',
        1255: 'light snow showers',
        1258: 'moderate or heavy snow showers',
        1261: 'light showers of ice pellets',
        1264: 'moderate or heavy showers of ice pellets',
        1273: 'patchy light rain with thunder',
        1276: 'moderate or heavy rain with thunder',
        1279: 'patchy light snow with thunder',
        1282: 'moderate or heavy snow with thunder',
    }
    
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        """Initialize the WeatherAPI provider."""
        super().__init__(api_key=api_key, offline_mode=offline_mode)
        self._base_params = {
            'key': self.api_key,
            'aqi': 'no',  # Don't include air quality data by default
        }
    
    def get_current_weather(self, location: str) -> WeatherData:
        """Get current weather for a location."""
        params = self._base_params.copy()
        params['q'] = location
        
        # Make the API request
        response = self._make_request(self.CURRENT_WEATHER_URL, params)
        
        # Parse the response
        return self._parse_current_weather(response)
    
    def get_forecast(self, location: str, days: int = 5) -> List[WeatherData]:
        """Get weather forecast for a location."""
        if not 1 <= days <= 14:
            raise ValueError("Days must be between 1 and 14 for WeatherAPI")
        
        params = self._base_params.copy()
        params.update({
            'q': location,
            'days': days,
            'aqi': 'no',
            'alerts': 'no'
        })
        
        # Make the API request
        response = self._make_request(self.FORECAST_URL, params)
        
        # Parse the forecast data
        return self._parse_forecast(response, days)
    
    def validate_api_key(self) -> bool:
        """Validate the current API key."""
        if not self.requires_api_key or not self.api_key:
            return False
            
        try:
            # Make a test request to the API
            params = self._base_params.copy()
            params['q'] = 'London'  # Test with a known location
            
            response = requests.get(
                self.CURRENT_WEATHER_URL,
                params=params,
                timeout=10
            )
            
            # Check if the response indicates an invalid API key
            if response.status_code == 403:
                return False
                
            # If we got a successful response, the key is valid
            if response.status_code == 200:
                return True
                
            # For other status codes, log the error
            logger.warning(f"Unexpected status code during API key validation: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return False
    
    def _parse_current_weather(self, data: Dict[str, Any]) -> WeatherData:
        """Parse current weather data from the API response."""
        current = data.get('current', {})
        location = data.get('location', {})
        
        # Get weather condition
        condition_code = current.get('condition', {}).get('code', 1000)
        condition = self.WEATHER_CONDITIONS.get(condition_code, 'unknown')
        
        # Get temperature and other metrics
        temperature = current.get('temp_c', 0)
        humidity = current.get('humidity', 0)
        pressure = current.get('pressure_mb', 0)  # Convert to hPa
        visibility = current.get('vis_km')
        
        # Get wind information
        wind_speed = current.get('wind_kph', 0) * 0.277778  # Convert to m/s
        wind_direction = current.get('wind_degree', 0)
        
        # Get weather icon
        icon_url = current.get('condition', {}).get('icon', '')
        if icon_url and not icon_url.startswith('http'):
            icon_url = f"https:{icon_url}"
        
        # Get last update time
        last_updated = location.get('localtime', '')
        
        return WeatherData(
            temperature=temperature,
            condition=condition,
            humidity=humidity,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            pressure=pressure,
            visibility=visibility,
            icon=icon_url,
            last_updated=last_updated
        )
    
    def _parse_forecast(self, data: Dict[str, Any], days: int) -> List[WeatherData]:
        """Parse forecast data from the API response."""
        forecast_list = []
        forecast_days = data.get('forecast', {}).get('forecastday', [])
        
        for day_forecast in forecast_days[:days]:
            if not day_forecast:
                continue
                
            # Get the day's forecast
            day = day_forecast.get('day', {})
            condition = day.get('condition', {})
            
            # Get weather condition
            condition_code = condition.get('code', 1000)
            condition_text = self.WEATHER_CONDITIONS.get(condition_code, 'unknown')
            
            # Get temperature and other metrics
            temp_avg = day.get('avgtemp_c', 0)
            humidity = day.get('avghumidity', 0)
            pressure = day.get('pressure_mb', 0)  # Convert to hPa
            
            # Get wind information
            wind_speed = day.get('maxwind_kph', 0) * 0.277778  # Convert to m/s
            
            # Get weather icon
            icon_url = condition.get('icon', '')
            if icon_url and not icon_url.startswith('http'):
                icon_url = f"https:{icon_url}"
            
            # Get forecast date
            date = day_forecast.get('date', '')
            
            forecast_list.append(
                WeatherData(
                    temperature=temp_avg,
                    condition=condition_text,
                    humidity=humidity,
                    wind_speed=wind_speed,
                    wind_direction=0,  # Not provided in daily forecast
                    pressure=pressure,
                    icon=icon_url,
                    last_updated=date
                )
            )
        
        return forecast_list
