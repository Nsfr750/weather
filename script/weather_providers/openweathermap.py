"""
OpenWeatherMap Provider Implementation.

This module provides the OpenWeatherMap implementation of the weather provider interface.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests

from .base_provider import BaseProvider, WeatherData

# Configure logging
logger = logging.getLogger(__name__)


class OpenWeatherMapProvider(BaseProvider):
    """OpenWeatherMap weather provider implementation."""
    
    # Provider configuration
    name = 'openweathermap'
    display_name = 'OpenWeatherMap'
    requires_api_key = True
    
    # API endpoints
    BASE_URL = 'https://api.openweathermap.org/data/2.5'
    CURRENT_WEATHER_URL = f"{BASE_URL}/weather"
    FORECAST_URL = f"{BASE_URL}/forecast"
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        units: str = 'metric',
        language: str = 'en',
        offline_mode: bool = False
    ):
        """Initialize the OpenWeatherMap provider.
        
        Args:
            api_key: OpenWeatherMap API key
            units: Units for temperature (metric, imperial, standard)
            language: Language for weather descriptions
            offline_mode: Whether to operate in offline mode
        """
        super().__init__(api_key=api_key, offline_mode=offline_mode)
        self.units = units
        self.language = language
        
        # Set up base parameters for API requests
        self._base_params = {
            'appid': self.api_key,
            'units': self.units,
            'lang': self.language
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
        if not 1 <= days <= 16:
            raise ValueError("Days must be between 1 and 16 for OpenWeatherMap")
        
        params = self._base_params.copy()
        params.update({
            'q': location,
            'cnt': days * 8  # 3-hour forecast for the next 5 days (40 timestamps)
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
            params['q'] = 'London,uk'  # Test with a known location
            
            response = requests.get(
                self.CURRENT_WEATHER_URL,
                params=params,
                timeout=10
            )
            
            # Check if the response indicates an invalid API key
            if response.status_code == 401:
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
        # Extract main weather data
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        wind = data.get('wind', {})
        
        # Get weather condition
        condition = weather.get('description', 'unknown')
        
        # Get temperature and other metrics
        temperature = main.get('temp', 0)
        humidity = main.get('humidity', 0)
        pressure = main.get('pressure', 0)  # hPa
        visibility = data.get('visibility')  # meters
        
        # Get wind information
        wind_speed = wind.get('speed', 0)  # m/s
        wind_direction = wind.get('deg', 0)  # degrees
        
        # Get weather icon
        icon_code = weather.get('icon', '')
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png" if icon_code else ''
        
        # Get last update time
        dt = data.get('dt', 0)
        last_updated = datetime.fromtimestamp(dt).isoformat() if dt else ''
        
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
        forecast_data = data.get('list', [])
        
        # Group forecast by day (8 timestamps per day for 3-hour intervals)
        for i in range(0, len(forecast_data), 8):
            daily_forecasts = forecast_data[i:i+8]
            if not daily_forecasts:
                continue
                
            # Get the first forecast of the day
            forecast = daily_forecasts[0]
            main = forecast.get('main', {})
            weather = forecast.get('weather', [{}])[0]
            
            # Get weather condition
            condition = weather.get('description', 'unknown')
            
            # Get temperature and other metrics
            temp_avg = main.get('temp', 0)
            humidity = main.get('humidity', 0)
            pressure = main.get('pressure', 0)  # hPa
            
            # Get wind information
            wind_speed = forecast.get('wind', {}).get('speed', 0)  # m/s
            
            # Get weather icon
            icon_code = weather.get('icon', '')
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png" if icon_code else ''
            
            # Get forecast date
            dt = forecast.get('dt', 0)
            date = datetime.fromtimestamp(dt).strftime('%Y-%m-%d') if dt else ''
            
            forecast_list.append(
                WeatherData(
                    temperature=temp_avg,
                    condition=condition,
                    humidity=humidity,
                    wind_speed=wind_speed,
                    wind_direction=0,  # Not using wind direction in daily forecast
                    pressure=pressure,
                    icon=icon_url,
                    last_updated=date
                )
            )
        
        return forecast_list[:days]  # Return only the requested number of days
