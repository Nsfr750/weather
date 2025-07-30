"""
AccuWeather Provider Implementation.

This module provides the AccuWeather implementation of the weather provider interface.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests

from .base_provider import BaseProvider, WeatherData

logger = logging.getLogger(__name__)

class AccuWeatherProvider(BaseProvider):
    """AccuWeather weather provider implementation."""
    
    name = 'accuweather'
    display_name = 'AccuWeather'
    requires_api_key = True
    
    BASE_URL = 'http://dataservice.accuweather.com'
    LOCATION_AUTOCOMPLETE = f"{BASE_URL}/locations/v1/cities/autocomplete"
    CURRENT_WEATHER = f"{BASE_URL}/currentconditions/v1/{{location_key}}"
    FORECAST = f"{BASE_URL}/forecasts/v1/daily/5day/{{location_key}}"
    
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        super().__init__(api_key=api_key, offline_mode=offline_mode)
        self._location_cache = {}
        
    def get_current_weather(self, location: str) -> WeatherData:
        location_key = self._get_location_key(location)
        if not location_key:
            raise ValueError(f"Location not found: {location}")
            
        url = self.CURRENT_WEATHER.format(location_key=location_key)
        params = {'apikey': self.api_key, 'details': 'true'}
        
        response = self._make_request(url, params)
        if not response:
            raise ValueError("No current weather data available")
            
        return self._parse_current_weather(response[0])
    
    def get_forecast(self, location: str, days: int = 5) -> List[WeatherData]:
        if not 1 <= days <= 5:
            raise ValueError("AccuWeather supports 1-5 days forecast")
            
        location_key = self._get_location_key(location)
        if not location_key:
            raise ValueError(f"Location not found: {location}")
            
        url = self.FORECAST.format(location_key=location_key)
        params = {'apikey': self.api_key, 'metric': 'true'}
        
        response = self._make_request(url, params)
        if not response or 'DailyForecasts' not in response:
            raise ValueError("No forecast data available")
            
        return self._parse_forecast(response, days)
    
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
    
    def _get_location_key(self, location: str) -> Optional[str]:
        if location in self._location_cache:
            return self._location_cache[location]
            
        params = {'apikey': self.api_key, 'q': location}
        response = self._make_request(self.LOCATION_AUTOCOMPLETE, params)
        
        if not response or not isinstance(response, list) or not response:
            return None
            
        location_key = response[0].get('Key')
        if location_key:
            self._location_cache[location] = location_key
            
        return location_key
    
    def _parse_current_weather(self, data: Dict[str, Any]) -> WeatherData:
        temperature = data.get('Temperature', {}).get('Metric', {}).get('Value', 0)
        condition = data.get('WeatherText', 'Unknown')
        
        return WeatherData(
            temperature=temperature,
            condition=condition.lower(),
            humidity=data.get('RelativeHumidity', 0),
            wind_speed=data.get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', 0) * 0.277778,  # km/h to m/s
            wind_direction=data.get('Wind', {}).get('Direction', {}).get('Degrees', 0),
            pressure=data.get('Pressure', {}).get('Metric', {}).get('Value', 0),
            visibility=data.get('Visibility', {}).get('Metric', {}).get('Value'),
            icon=f"https://developer.accuweather.com/sites/default/files/{data.get('WeatherIcon', 1):02d}-s.png",
            last_updated=data.get('LocalObservationDateTime', '')
        )
    
    def _parse_forecast(self, data: Dict[str, Any], days: int) -> List[WeatherData]:
        forecast_list = []
        
        for day_data in data.get('DailyForecasts', [])[:days]:
            temp = day_data.get('Temperature', {}).get('Maximum', {})
            
            forecast_list.append(WeatherData(
                temperature=temp.get('Value', 0) if isinstance(temp, dict) else 0,
                condition=day_data.get('Day', {}).get('IconPhrase', 'unknown').lower(),
                humidity=day_data.get('Day', {}).get('RelativeHumidity', {}).get('Value', 0),
                wind_speed=day_data.get('Day', {}).get('Wind', {}).get('Speed', {}).get('Value', 0) * 0.277778,
                wind_direction=day_data.get('Day', {}).get('Wind', {}).get('Direction', {}).get('Degrees', 0),
                pressure=day_data.get('Day', {}).get('Pressure', {}).get('Value', 0),
                icon=f"https://developer.accuweather.com/sites/default/files/{day_data.get('Day', {}).get('Icon', 1):02d}-s.png",
                last_updated=day_data.get('Date', '')
            ))
            
        return forecast_list
