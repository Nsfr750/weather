"""
Breezy Weather provider implementation.

Note: This is a basic implementation. Breezy Weather might have specific API requirements.
"""
import requests
from datetime import datetime
import os
from .base_provider import WeatherProvider

class BreezyWeatherProvider(WeatherProvider):
    """Weather data provider for Breezy Weather API."""
    
    BASE_URL = 'https://breezy-weather.p.rapidapi.com/'
    
    def __init__(self, api_key=None, units='metric', language='en'):
        super().__init__(api_key, units, language)
        self.name = "Breezy Weather"
        self.api_key = api_key or os.environ.get('BREEZY_WEATHER_API_KEY')
        
        # Map language codes to Breezy Weather format
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
        """Make a request to the Breezy Weather API."""
        if not self.api_key or self.api_key == 'YOUR_API_KEY_HERE':
            raise ValueError("Breezy Weather API key is required. Please sign up at https://breezy-weather.com/")
            
        if params is None:
            params = {}
            
        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'breezy-weather.p.rapidapi.com'
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def _geocode_location(self, location):
        """Convert location name to coordinates using Breezy Weather's geocoding."""
        if ',' in location:  # Already coordinates
            lat, lon = location.split(',')
            return float(lat.strip()), float(lon.strip())
            
        # Use Breezy Weather's geocoding
        data = self._make_request('locations/search', {
            'q': location,
            'lang': self.language
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
            data = self._make_request('weather/current', {
                'lat': lat,
                'lon': lon,
                'units': self.units,
                'lang': self.language
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
            data = self._make_request('weather/forecast/daily', {
                'lat': lat,
                'lon': lon,
                'cnt': days,
                'units': self.units,
                'lang': self.language
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
                'lon': lon,
                'lang': self.language
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
            return False, "Please enter a valid Breezy Weather API key"
            
        # Test the API key with a simple request
        try:
            headers = {
                'x-rapidapi-key': api_key,
                'x-rapidapi-host': 'breezy-weather.p.rapidapi.com'
            }
            
            response = requests.get(
                f"{self.BASE_URL}weather/current",
                headers=headers,
                params={'lat': '40.7128', 'lon': '-74.0060'},  # New York
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
