"""
Weather.com provider implementation.

Note: This is a basic implementation. Weather.com requires an API key and has specific
terms of service for API usage. You'll need to sign up for their developer program.
"""
import requests
from datetime import datetime
from .base_provider import WeatherProvider

class WeatherDotComProvider(WeatherProvider):
    """Weather data provider for Weather.com API."""
    
    BASE_URL = 'https://api.weather.com/v3/wx/'
    
    def __init__(self, api_key=None, units='metric', language='en'):
        super().__init__(api_key, units, language)
        self.name = "Weather.com"
        self.api_key = api_key or os.environ.get('WEATHERDOTCOM_API_KEY')
        
        # Map language codes to Weather.com format
        self._lang_map = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-BR',
            'ru': 'ru-RU',
            'ar': 'ar-AE',
            'ja': 'ja-JP',
            'zh': 'zh-CN',
            'ko': 'ko-KR'
        }
        
        # Default to English if language not in map
        self.language = self._lang_map.get(language, 'en-US')
    
    def _make_request(self, endpoint, params=None):
        """Make a request to the Weather.com API."""
        if not self.api_key or self.api_key == 'YOUR_API_KEY_HERE':
            raise ValueError("Weather.com API key is required. Please sign up at https://www.weather.com/")
            
        if params is None:
            params = {}
            
        params.update({
            'apiKey': self.api_key,
            'language': self.language,
            'format': 'json'
        })
        
        try:
            response = requests.get(f"{self.BASE_URL}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def _geocode_location(self, location):
        """Convert location name to coordinates using Weather.com's geocoding."""
        if ',' in location:  # Already coordinates
            lat, lon = location.split(',')
            return float(lat.strip()), float(lon.strip())
            
        # Use Weather.com's location search
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
                'units': 'm' if self.units == 'metric' else 'e',
                'language': self.language
            })
            
            obs = data['observation']
            
            return {
                'temp': obs['temp'],
                'feels_like': obs['feels_like'],
                'humidity': obs['humidity'],
                'pressure': obs['pressure'],
                'wind_speed': obs['wspd'],
                'wind_direction': obs['wdir'],
                'description': obs['wx_phrase'],
                'icon': self._get_weather_icon(obs['wx_icon']),
                'visibility': obs['visibility'],
                'clouds': obs['cloud_cover'],
                'rain': obs.get('qpf', 0),  # Precipitation in mm
                'snow': obs.get('snow', 0),  # Snow in cm
                'dt': obs['valid_time_gmt'],
                'sunrise': obs['sunrise_time'],
                'sunset': obs['sunset_time'],
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
                'units': 'm' if self.units == 'metric' else 'e',
                'language': self.language
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
                    'rain': data['qpf'][i],
                    'snow': data['snow'][i],
                    'humidity': data['daypart'][0]['relativeHumidity'][i*2],
                    'pressure': data['daypart'][0]['pressureMeanSeaLevel'][i*2] if 'pressureMeanSeaLevel' in data['daypart'][0] else None
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
                    'event': alert['eventDescription'],
                    'start': alert['startTime'],
                    'end': alert['endTime'],
                    'description': alert['description'],
                    'severity': alert['severity'],
                    'type': alert['type']
                })
                
            return alerts
            
        except Exception as e:
            logging.error(f"Failed to get alerts: {str(e)}")
            return []
    
    def validate_api_key(self, api_key):
        """Validate the API key by making a test request."""
        if not api_key or api_key == 'YOUR_API_KEY_HERE':
            return False, "Please enter a valid Weather.com API key"
            
        # Test the API key with a simple request
        try:
            test_params = {
                'apiKey': api_key,
                'geocode': '40.7128,-74.0060',  # New York coordinates
                'format': 'json',
                'units': 'm'
            }
            response = requests.get(
                f"{self.BASE_URL}observations/current",
                params=test_params,
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
            self.language = self._lang_map.get(kwargs['language'], 'en-US')
    
    def _get_weather_icon(self, icon_code):
        """Convert Weather.com icon code to standard icon name."""
        # This is a simplified mapping - Weather.com has many more codes
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
            14: '09d',  # Rain and Snow
            15: '13d',  # Snow
            16: '13d',  # Freezing Rain
            17: '11d',  # Thunderstorm
            18: '50d',  # Haze
            # Add more mappings as needed
        }
        return icon_map.get(icon_code, '01d')  # Default to sunny
