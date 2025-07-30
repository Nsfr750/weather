"""
Alliander provider implementation.

Note: This is a basic implementation. Alliander's API might have specific requirements
and terms of service for API usage.
"""
import requests
from datetime import datetime, timedelta
import os
import logging
from .base_provider import WeatherProvider

class AllianderProvider(WeatherProvider):
    """Weather data provider for Alliander's weather API."""
    
    BASE_URL = 'https://api.alliander.com/weather/v1/'
    
    def __init__(self, api_key=None, units='metric', language='en'):
        super().__init__(api_key, units, language)
        self.name = "Alliander"
        self.api_key = api_key or os.environ.get('ALLIANDER_API_KEY')
        
        # Alliander API primarily serves Dutch locations and supports limited languages
        self._supported_languages = ['nl', 'en']
        self.language = 'nl' if language == 'nl' else 'en'  # Default to English if not Dutch
    
    def _make_request(self, endpoint, params=None):
        """Make a request to the Alliander API."""
        if not self.api_key or self.api_key == 'YOUR_API_KEY_HERE':
            raise ValueError("Alliander API key is required. Please sign up at https://developer.alliander.com/")
            
        if params is None:
            params = {}
            
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Accept': 'application/json',
            'Accept-Language': self.language
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=headers,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', str(e))
                except:
                    error_msg = e.response.text or str(e)
            raise Exception(f"API request failed: {error_msg}")
    
    def _geocode_location(self, location):
        """Convert location name to coordinates using Alliander's geocoding."""
        if ',' in location:  # Already coordinates
            lat, lon = location.split(',')
            return float(lat.strip()), float(lon.strip())
            
        # Use Alliander's geocoding (if available)
        # Note: This is a placeholder - adjust based on actual API capabilities
        try:
            data = self._make_request('locations', {
                'q': location,
                'limit': 1
            })
            
            if not data or not data.get('results'):
                raise ValueError(f"Location '{location}' not found")
                
            # Get the first result
            result = data['results'][0]
            return result['lat'], result['lon']
            
        except Exception as e:
            # Fallback to OpenStreetMap if Alliander's geocoding fails
            try:
                response = requests.get(
                    'https://nominatim.openstreetmap.org/search',
                    params={'q': location, 'format': 'json', 'limit': 1},
                    headers={'User-Agent': 'WeatherApp/1.0'}
                )
                response.raise_for_status()
                data = response.json()
                if not data:
                    raise ValueError(f"Location '{location}' not found")
                return float(data[0]['lat']), float(data[0]['lon'])
            except Exception as geocode_error:
                raise ValueError(f"Failed to geocode location: {str(geocode_error)}")
    
    def get_current_weather(self, location):
        """Get current weather for a location."""
        try:
            lat, lon = self._geocode_location(location)
            
            # Get current weather
            data = self._make_request('weather/current', {
                'lat': lat,
                'lon': lon,
                'units': self.units
            })
            
            current = data['current']
            
            return {
                'temp': current['temp'],
                'feels_like': current.get('feels_like', current['temp']),
                'humidity': current.get('humidity', 0),
                'pressure': current.get('pressure', 1013),  # Default sea level pressure
                'wind_speed': current.get('wind_speed', 0),
                'wind_direction': current.get('wind_deg', 0),
                'description': current['weather'][0]['description'],
                'icon': self._get_weather_icon(current['weather'][0]['id']),
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
                'units': self.units
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
                        'max': day.get('feels_like', {}).get('day', day['temp']['max']),
                        'min': day.get('feels_like', {}).get('night', day['temp']['min'])
                    },
                    'weather': [{
                        'description': day['weather'][0]['description'],
                        'icon': self._get_weather_icon(day['weather'][0]['id']),
                        'code': day['weather'][0]['id']
                    }],
                    'wind_speed': day.get('wind_speed', 0),
                    'wind_deg': day.get('wind_deg', 0),
                    'pop': day.get('pop', 0),  # Probability of precipitation
                    'rain': day.get('rain', 0),
                    'snow': day.get('snow', 0),
                    'humidity': day.get('humidity', 0),
                    'pressure': day.get('pressure', 0)
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
                    'event': alert.get('event', 'Weather Alert'),
                    'start': alert.get('start', 0),
                    'end': alert.get('end', 0),
                    'description': alert.get('description', ''),
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
            return False, "Please enter a valid Alliander API key"
            
        # Test the API key with a simple request
        try:
            response = requests.get(
                f"{self.BASE_URL}weather/current",
                headers={
                    'Ocp-Apim-Subscription-Key': api_key,
                    'Accept': 'application/json'
                },
                params={
                    'lat': '52.1326',  # Amsterdam
                    'lon': '5.2913',
                    'units': 'metric'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "API key is valid"
            else:
                return False, f"API key validation failed: {response.status_code} - {response.text}"
                
        except Exception as e:
            return False, f"Error validating API key: {str(e)}"
    
    def update_config(self, **kwargs):
        """Update provider configuration."""
        if 'api_key' in kwargs:
            self.api_key = kwargs['api_key']
        if 'units' in kwargs:
            self.units = kwargs['units']
        if 'language' in kwargs:
            lang = kwargs['language']
            self.language = 'nl' if lang == 'nl' else 'en'
    
    def _get_weather_icon(self, code):
        """Convert weather code to icon name."""
        # Map OpenWeatherMap weather codes to icon names
        # https://openweathermap.org/weather-conditions
        if 200 <= code < 300:  # Thunderstorm
            return '11d'
        elif 300 <= code < 400:  # Drizzle
            return '09d'
        elif 500 <= code < 600:  # Rain
            return '10d'
        elif 600 <= code < 700:  # Snow
            return '13d'
        elif 700 <= code < 800:  # Atmosphere
            return '50d'
        elif code == 800:  # Clear
            return '01d'
        elif code == 801:  # Few clouds
            return '02d'
        elif code == 802:  # Scattered clouds
            return '03d'
        elif code == 803 or code == 804:  # Broken/overcast clouds
            return '04d'
        else:
            return '01d'  # Default to clear day
