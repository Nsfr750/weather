"""
QuickWeather provider implementation.

Note: This is a basic implementation. QuickWeather might have specific API requirements.
"""
import requests
from datetime import datetime
import os
import logging
from .base_provider import WeatherProvider

class QuickWeatherProvider(WeatherProvider):
    """Weather data provider for QuickWeather API."""
    
    BASE_URL = 'https://api.quickweather.com/v1/'
    
    def __init__(self, api_key=None, units='metric', language='en'):
        super().__init__(api_key, units, language)
        self.name = "QuickWeather"
        self.api_key = api_key or os.environ.get('QUICKWEATHER_API_KEY')
        
        # Map language codes to QuickWeather format
        self._lang_map = {
            'en': 'en',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'it': 'it',
            'pt': 'pt',
            'ru': 'ru',
            'ar': 'ar',
            'ja': 'ja',
            'zh': 'zh',
            'ko': 'ko'
        }
        
        # Default to English if language not in map
        self.language = self._lang_map.get(language, 'en')
    
    def _make_request(self, endpoint, params=None):
        """Make a request to the QuickWeather API."""
        if not self.api_key or self.api_key == 'YOUR_API_KEY_HERE':
            raise ValueError("QuickWeather API key is required. Please sign up at https://quickweather.com/")
            
        if params is None:
            params = {}
            
        params.update({
            'key': self.api_key,
            'lang': self.language,
            'units': 'metric' if self.units == 'metric' else 'imperial'
        })
        
        try:
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def _geocode_location(self, location):
        """Convert location name to coordinates using QuickWeather's geocoding."""
        if ',' in location:  # Already coordinates
            lat, lon = location.split(',')
            return float(lat.strip()), float(lon.strip())
            
        # Use QuickWeather's geocoding
        data = self._make_request('geocode', {
            'q': location,
            'limit': 1
        })
        
        if not data or not data.get('results'):
            raise ValueError(f"Location '{location}' not found")
            
        # Get the first result
        result = data['results'][0]
        return result['lat'], result['lon']
    
    def get_current_weather(self, location):
        """Get current weather for a location."""
        try:
            lat, lon = self._geocode_location(location)
            
            # Get current weather
            data = self._make_request('current', {
                'lat': lat,
                'lon': lon
            })
            
            current = data['current']
            
            return {
                'temp': current['temp'],
                'feels_like': current['feels_like'],
                'humidity': current['humidity'],
                'pressure': current['pressure'],
                'wind_speed': current['wind_speed'],
                'wind_direction': current['wind_deg'],
                'description': current['weather'][0]['description'],
                'icon': current['weather'][0]['icon'],
                'visibility': current.get('visibility', 10000),  # Default 10km
                'clouds': current.get('clouds', 0),
                'rain': current.get('rain', {}).get('1h', 0),
                'snow': current.get('snow', {}).get('1h', 0),
                'dt': current['dt'],
                'sunrise': current.get('sunrise', 0),
                'sunset': current.get('sunset', 0),
                'location': location,
                'coord': {'lat': lat, 'lon': lon}
            }
            
        except Exception as e:
            raise Exception(f"Failed to get current weather: {str(e)}")
    
    def get_forecast(self, location, days=5):
        """Get weather forecast for a location."""
        try:
            lat, lon = self._geocode_location(location)
            
            # Get daily forecast
            data = self._make_request('forecast/daily', {
                'lat': lat,
                'lon': lon,
                'cnt': days
            })
            
            forecast = []
            for day in data['daily'][:days]:
                forecast.append({
                    'dt': day['dt'],
                    'temp': {
                        'max': day['temp']['max'],
                        'min': day['temp']['min']
                    },
                    'feels_like': {
                        'max': day['feels_like']['day'],
                        'min': day['feels_like']['night']
                    },
                    'weather': [{
                        'description': day['weather'][0]['description'],
                        'icon': day['weather'][0]['icon'],
                        'code': day['weather'][0]['id']
                    }],
                    'wind_speed': day['wind_speed'],
                    'wind_deg': day['wind_deg'],
                    'pop': day.get('pop', 0),  # Probability of precipitation
                    'rain': day.get('rain', 0),
                    'snow': day.get('snow', 0),
                    'humidity': day['humidity'],
                    'pressure': day['pressure']
                })
                
            return forecast
            
        except Exception as e:
            raise Exception(f"Failed to get forecast: {str(e)}")
    
    def get_alerts(self, location):
        """Get weather alerts for a location."""
        try:
            lat, lon = self._geocode_location(location)
            
            data = self._make_request('alerts', {
                'lat': lat,
                'lon': lon
            })
            
            alerts = []
            for alert in data.get('alerts', []):
                alerts.append({
                    'event': alert['event'],
                    'start': alert['start'],
                    'end': alert['end'],
                    'description': alert['description'],
                    'severity': alert.get('severity', 'moderate'),
                    'type': alert.get('tags', ['weather'])[0]
                })
                
            return alerts
            
        except Exception as e:
            logging.error(f"Failed to get alerts: {str(e)}")
            return []
    
    def validate_api_key(self, api_key):
        """Validate the API key by making a test request."""
        if not api_key or api_key == 'YOUR_API_KEY_HERE':
            return False, "Please enter a valid QuickWeather API key"
            
        # Test the API key with a simple request
        try:
            response = requests.get(
                f"{self.BASE_URL}current",
                params={
                    'key': api_key,
                    'lat': '40.7128',  # New York
                    'lon': '-74.0060',
                    'units': 'metric'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "API key is valid"
            else:
                return False, f"API key validation failed: {response.status_code}"
                
        except Exception as e:
            return False, f"Error validating API key: {str(e)}"
    
    def update_config(self, **kwargs):
        """Update provider configuration."""
        if 'api_key' in kwargs:
            self.api_key = kwargs['api_key']
        if 'units' in kwargs:
            self.units = kwargs['units']
        if 'language' in kwargs:
            self.language = self._lang_map.get(kwargs['language'], 'en')
