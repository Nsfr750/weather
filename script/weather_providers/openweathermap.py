"""
OpenWeatherMap provider implementation.
"""
import requests
from .base_provider import WeatherProvider

class OpenWeatherMapProvider(WeatherProvider):
    """Weather data provider for OpenWeatherMap API."""
    
    BASE_URL = 'https://api.openweathermap.org/data/2.5/'
    
    def __init__(self, api_key=None, units='metric', language='en'):
        super().__init__(api_key, units, language)
        self.name = "OpenWeatherMap"
    
    def _make_request(self, endpoint, params=None):
        """Make a request to the OpenWeatherMap API.
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Additional parameters
            
        Returns:
            dict: JSON response
        """
        if params is None:
            params = {}
            
        params.update({
            'appid': self.api_key,
            'units': self.units,
            'lang': self.language
        })
        
        response = requests.get(f"{self.BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_current_weather(self, location):
        """Get current weather for a location."""
        try:
            params = {'q': location} if ',' not in location else {'lat': location.split(',')[0], 'lon': location.split(',')[1]}
            data = self._make_request('weather', params)
            
            return {
                'temp': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_deg': data['wind'].get('deg', 0),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'visibility': data.get('visibility', 10000) / 1000,  # Convert to km
                'clouds': data['clouds']['all'],
                'sunrise': data['sys']['sunrise'],
                'sunset': data['sys']['sunset'],
                'location': data['name'],
                'country': data['sys']['country'],
                'timestamp': data['dt']
            }
        except Exception as e:
            raise Exception(f"Failed to get current weather: {str(e)}")
    
    def get_forecast(self, location, days=5):
        """Get weather forecast for a location."""
        try:
            params = {
                'q': location if ',' not in location else None,
                'lat': location.split(',')[0] if ',' in location else None,
                'lon': location.split(',')[1] if ',' in location else None,
                'cnt': days * 8  # 8 data points per day (3-hour intervals)
            }
            params = {k: v for k, v in params.items() if v is not None}
            
            data = self._make_request('forecast', params)
            
            forecast = []
            for item in data['list']:
                forecast.append({
                    'timestamp': item['dt'],
                    'temp': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'wind_speed': item['wind']['speed'],
                    'wind_deg': item['wind'].get('deg', 0),
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'pop': item.get('pop', 0)  # Probability of precipitation
                })
            
            return forecast
        except Exception as e:
            raise Exception(f"Failed to get forecast: {str(e)}")
    
    def get_alerts(self, location):
        """Get weather alerts for a location."""
        try:
            params = {
                'q': location if ',' not in location else None,
                'lat': location.split(',')[0] if ',' in location else None,
                'lon': location.split(',')[1] if ',' in location else None,
                'exclude': 'current,minutely,hourly,daily'
            }
            params = {k: v for k, v in params.items() if v is not None}
            
            data = self._make_request('onecall', params)
            
            alerts = []
            for alert in data.get('alerts', []):
                alerts.append({
                    'event': alert.get('event', ''),
                    'start': alert.get('start', 0),
                    'end': alert.get('end', 0),
                    'description': alert.get('description', ''),
                    'sender': alert.get('sender', '')
                })
            
            return alerts
        except Exception as e:
            # If no alerts, the API returns 404
            if '404' in str(e):
                return []
            raise Exception(f"Failed to get alerts: {str(e)}")
    
    def validate_api_key(self, api_key):
        """Validate the OpenWeatherMap API key."""
        try:
            test_params = {
                'q': 'London',
                'appid': api_key
            }
            response = requests.get(f"{self.BASE_URL}weather", params=test_params, timeout=5)
            
            if response.status_code == 200:
                return True, "API key is valid"
            elif response.status_code == 401:
                return False, "Invalid API key"
            else:
                return False, f"API error: {response.status_code} - {response.text}"
        except requests.RequestException as e:
            return False, f"Connection error: {str(e)}"
