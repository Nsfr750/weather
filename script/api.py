"""
weather_api.py
Centralized module for fetching weather data from OpenWeatherMap.
"""
import requests
import logging
from datetime import datetime, timedelta
import datetime as dt

BASE_URL = 'https://api.openweathermap.org/data/2.5/'
# Using One Call 2.5 which is available in the free tier
ONE_CALL_URL = 'https://api.openweathermap.org/data/2.5/onecall'

class WeatherAPI:
    def __init__(self, api_key, units='metric', language='en'):
        self.api_key = api_key
        self.units = units
        self.language = language
        self.last_fetch = {}
        self.cache = {}
        self.cache_duration = timedelta(minutes=10)

    def _make_request(self, endpoint, params):
        """Helper method to make API requests with error handling and caching"""
        cache_key = (endpoint, tuple(sorted(params.items())))
        now = dt.datetime.now()
        
        # Check cache first
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if now - timestamp < self.cache_duration:
                return data
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.cache[cache_key] = (data, now)
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f'API request failed: {e}')
            # Return cached data if available, even if expired
            if cache_key in self.cache:
                logging.warning('Using cached data due to API error')
                return self.cache[cache_key][0]
            raise Exception(f'Failed to fetch data: {str(e)}')

    def fetch_weather(self, city):
        """Fetch current weather and forecast for a city"""
        params = {
            'q': city,
            'appid': self.api_key,
            'units': self.units,
            'lang': self.language
        }
        
        try:
            # Get current weather
            weather = self._make_request(BASE_URL + 'weather', params)
            
            # Get forecast
            forecast = self._make_request(BASE_URL + 'forecast', params)
            
            return weather, forecast
            
        except Exception as e:
            logging.error(f'Error in fetch_weather: {e}')
            raise

    def fetch_alerts(self, city):
        """Fetch weather alerts for a city using One Call API"""
        try:
            # First get coordinates for the city
            geocode_params = {
                'q': city,
                'appid': self.api_key,
                'limit': 1
            }
            geocode_url = 'http://api.openweathermap.org/geo/1.0/direct'
            location_data = self._make_request(geocode_url, geocode_params)
            
            if not location_data:
                return {'alerts': []}
                
            lat = location_data[0]['lat']
            lon = location_data[0]['lon']
            
            # Get alerts using One Call API
            one_call_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': self.units,
                'lang': self.language,
                'exclude': 'minutely,hourly,daily'
            }
            
            try:
                data = self._make_request(ONE_CALL_URL, one_call_params)
                return {'alerts': data.get('alerts', [])}
            except Exception as e:
                logging.warning(f'Could not fetch alerts: {e}')
                return {'alerts': []}
                
        except Exception as e:
            logging.error(f'Error in fetch_alerts: {e}')
            return {'alerts': []}

    def update_config(self, **kwargs):
        """Update API configuration"""
        if 'api_key' in kwargs:
            self.api_key = kwargs['api_key']
        if 'units' in kwargs:
            self.units = kwargs['units']
        if 'language' in kwargs:
            self.language = kwargs['language']

    def update_config(self, api_key=None, units=None, language=None):
        if api_key is not None:
            self.api_key = api_key
        if units is not None:
            self.units = units
        if language is not None:
            self.language = language
