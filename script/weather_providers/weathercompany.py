"""
Weather Company (IBM) provider implementation.

Note: This is a basic implementation. The Weather Company (IBM) requires an API key
and has specific terms of service for API usage.
"""
import requests
import base64
import json
from datetime import datetime
import os
import logging
from .base_provider import WeatherProvider

class WeatherCompanyProvider(WeatherProvider):
    """Weather data provider for The Weather Company (IBM) API."""
    
    BASE_URL = 'https://api.weather.com/v3/wx/'
    AUTH_URL = 'https://login.ng.bluemix.net/oauth/token'
    
    def __init__(self, api_key=None, username=None, password=None, units='metric', language='en'):
        super().__init__(api_key, units, language)
        self.name = "The Weather Company (IBM)"
        self.api_key = api_key or os.environ.get('WEATHERCOMPANY_API_KEY')
        self.username = username or os.environ.get('WEATHERCOMPANY_USERNAME')
        self.password = password or os.environ.get('WEATHERCOMPANY_PASSWORD')
        self.token = None
        self.token_expiry = None
        
        # Map language codes to Weather Company format
        self._lang_map = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-BR',
            'ru': 'ru-RU',
            'ar': 'ar-AR',
            'ja': 'ja-JP',
            'zh': 'zh-CN',
            'ko': 'ko-KR'
        }
        
        # Default to English if language not in map
        self.language = self._lang_map.get(language, 'en-US')
    
    def _get_auth_token(self):
        """Get an authentication token using API key, username and password."""
        if not all([self.api_key, self.username, self.password]):
            raise ValueError("API key, username, and password are required for The Weather Company")
            
        # Check if we have a valid token
        if self.token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.token
            
        # Get new token
        auth_string = f"{self.api_key}:{self.username}:{self.password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f"Basic {encoded_auth}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(
                self.AUTH_URL,
                headers=headers,
                data='grant_type=client_credentials',
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            self.token = data['access_token']
            # Set token expiry slightly before actual expiry to be safe
            self.token_expiry = datetime.now() + timedelta(seconds=data.get('expires_in', 3600) - 300)
            
            return self.token
            
        except Exception as e:
            raise Exception(f"Failed to get authentication token: {str(e)}")
    
    def _make_request(self, endpoint, params=None):
        """Make a request to The Weather Company API."""
        if not self.api_key or self.api_key == 'YOUR_API_KEY_HERE':
            raise ValueError("Weather Company API key is required. Please sign up at https://www.ibm.com/weather/")
            
        if params is None:
            params = {}
            
        # Add common parameters
        params.update({
            'language': self.language,
            'format': 'json',
            'units': 'm' if self.units == 'metric' else 'e'
        })
        
        # Get auth token
        try:
            token = self._get_auth_token()
            headers = {
                'Authorization': f"Bearer {token}",
                'Accept': 'application/json'
            }
            
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=headers,
                params=params,
                timeout=15
            )
            
            # If token expired, refresh and try again
            if response.status_code == 401:
                self.token = None
                token = self._get_auth_token()
                headers['Authorization'] = f"Bearer {token}"
                response = requests.get(
                    f"{self.BASE_URL}{endpoint}",
                    headers=headers,
                    params=params,
                    timeout=15
                )
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def _geocode_location(self, location):
        """Convert location name to coordinates using The Weather Company's geocoding."""
        if ',' in location:  # Already coordinates
            lat, lon = location.split(',')
            return float(lat.strip()), float(lon.strip())
            
        # Use The Weather Company's geocoding
        data = self._make_request('location/search', {
            'query': location,
            'locationType': 'city',
            'countryCode': 'US'  # Default, can be made configurable
        })
        
        if not data.get('location'):
            raise ValueError(f"Location '{location}' not found")
            
        return data['location']['latitude'][0], data['location']['longitude'][0]
    
    def get_current_weather(self, location):
        """Get current weather for a location."""
        try:
            lat, lon = self._geocode_location(location)
            
            # Get current conditions
            data = self._make_request('observations/current', {
                'geocode': f"{lat},{lon}",
                'units': 'm' if self.units == 'metric' else 'e'
            })
            
            obs = data['observation']
            
            return {
                'temp': obs['temp'],
                'feels_like': obs['feels_like'],
                'humidity': obs['rh'],
                'pressure': obs['pressure'],
                'wind_speed': obs['wspd'],
                'wind_direction': obs['wdir'],
                'description': obs['wx_phrase'],
                'icon': self._get_weather_icon(obs['wx_icon']),
                'visibility': obs.get('vis', 10),  # Default 10 miles/16 km
                'clouds': obs.get('cloud_cover', 0),
                'rain': obs.get('precip_hrly', 0),
                'snow': obs.get('snow_hrly', 0),
                'dt': obs['valid_time_gmt'],
                'sunrise': obs.get('sunrise_time', 0),
                'sunset': obs.get('sunset_time', 0),
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
            data = self._make_request('forecast/daily/5day', {
                'geocode': f"{lat},{lon}",
                'units': 'm' if self.units == 'metric' else 'e'
            })
            
            forecast = []
            for i in range(min(len(data['dayOfWeek']), days)):
                forecast.append({
                    'dt': data['validTimeLocal'][i],
                    'temp': {
                        'max': data['temperatureMax'][i],
                        'min': data['temperatureMin'][i]
                    },
                    'feels_like': {
                        'max': data['temperatureMax'][i],  # Not always available
                        'min': data['temperatureMin'][i]   # Not always available
                    },
                    'weather': [{
                        'description': data['narrative'][i],
                        'icon': self._get_weather_icon(data['daypart'][0]['iconCode'][i*2]),
                        'code': data['daypart'][0]['iconCode'][i*2]
                    }],
                    'wind_speed': data['daypart'][0]['windSpeed'][i*2],
                    'wind_deg': data['daypart'][0]['windDirectionCardinal'][i*2],
                    'pop': data['daypart'][0]['precipChance'][i*2],
                    'rain': data.get('qpf', [0]*(i+1))[i],
                    'snow': data.get('snow', [0]*(i+1))[i],
                    'humidity': data['daypart'][0]['relativeHumidity'][i*2],
                    'pressure': data['daypart'][0].get('pressureMeanSeaLevel', [None]*(i+1))[i*2]
                })
                
            return forecast
            
        except Exception as e:
            raise Exception(f"Failed to get forecast: {str(e)}")
    
    def get_alerts(self, location):
        """Get weather alerts for a location."""
        try:
            lat, lon = self._geocode_location(location)
            
            data = self._make_request('alerts', {
                'geocode': f"{lat},{lon}",
                'language': self.language
            })
            
            alerts = []
            for alert in data.get('alerts', []):
                alerts.append({
                    'event': alert['event_description'],
                    'start': alert['start_time'],
                    'end': alert['end_time'],
                    'description': alert['description'],
                    'severity': alert.get('severity', 'moderate'),
                    'type': alert.get('type', 'weather')
                })
                
            return alerts
            
        except Exception as e:
            logging.error(f"Failed to get alerts: {str(e)}")
            return []
    
    def validate_api_key(self, api_key, username=None, password=None):
        """Validate the API key, username, and password."""
        if not all([api_key, username, password]):
            return False, "API key, username, and password are required for The Weather Company"
            
        # Test the credentials by trying to get an auth token
        try:
            auth_string = f"{api_key}:{username}:{password}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            response = requests.post(
                self.AUTH_URL,
                headers={
                    'Authorization': f"Basic {encoded_auth}",
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data='grant_type=client_credentials',
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "API credentials are valid"
            else:
                return False, f"API credentials validation failed: {response.status_code}"
                
        except Exception as e:
            return False, f"Error validating API credentials: {str(e)}"
    
    def update_config(self, **kwargs):
        """Update provider configuration."""
        if 'api_key' in kwargs:
            self.api_key = kwargs['api_key']
        if 'username' in kwargs:
            self.username = kwargs['username']
        if 'password' in kwargs:
            self.password = kwargs['password']
        if 'units' in kwargs:
            self.units = kwargs['units']
        if 'language' in kwargs:
            self.language = self._lang_map.get(kwargs['language'], 'en-US')
    
    def _get_weather_icon(self, icon_code):
        """Convert Weather Company icon code to standard icon name."""
        # This is a simplified mapping - adjust based on actual icon codes
        icon_map = {
            # Clear
            1: '01d',  # Sunny
            2: '01n',  # Clear (night)
            # Partly Cloudy
            3: '02d',  # Mostly Sunny
            4: '02n',  # Mostly Clear (night)
            # Cloudy
            5: '03d',  # Partly Sunny
            6: '03d',  # Intermittent Clouds
            7: '04d',  # Hazy Sunshine
            8: '04d',  # Mostly Cloudy
            # Rain
            11: '09d',  # Fog
            12: '09d',  # Showers
            13: '09d',  # Scattered Showers
            14: '13d',  # Rain and Snow
            15: '13d',  # Snow
            16: '13d',  # Freezing Rain
            17: '11d',  # Thunderstorm
            18: '50d',  # Haze
            # Add more mappings as needed
        }
        return icon_map.get(icon_code, '01d')  # Default to sunny
