"""
weather_api.py
Centralized module for fetching weather data from OpenWeatherMap.
"""
import requests

BASE_URL = 'https://api.openweathermap.org/data/2.5/'

class WeatherAPI:
    def __init__(self, api_key, units='metric', language='en'):
        self.api_key = api_key
        self.units = units
        self.language = language

    def fetch_weather(self, city):
        params = {
            'q': city,
            'appid': self.api_key,
            'units': self.units,
            'lang': self.language
        }
        # Current weather
        r = requests.get(BASE_URL + 'weather', params=params)
        if r.status_code != 200:
            raise Exception(r.json().get('message', 'API error'))
        weather = r.json()
        # Forecast (5 day, 3-hour intervals)
        r2 = requests.get(BASE_URL + 'forecast', params=params)
        if r2.status_code != 200:
            raise Exception(r2.json().get('message', 'API error'))
        forecast = r2.json()
        return weather, forecast

    def update_config(self, api_key=None, units=None, language=None):
        if api_key is not None:
            self.api_key = api_key
        if units is not None:
            self.units = units
        if language is not None:
            self.language = language
