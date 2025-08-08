"""
config_utils.py
Utility class for managing application configuration in a modular way.
"""
import json
import os
import requests
from pathlib import Path

# Import language manager
from lang.language_manager import LanguageManager

# Ensure config directory exists
CONFIG_DIR = Path('config')
CONFIG_DIR.mkdir(exist_ok=True)

CONFIG_FILE = CONFIG_DIR / 'config.json'
DEFAULT_CONFIG = {
    'units': 'metric',
    'language': 'en',  # Default to English
    'theme': 'dark',   # Only dark theme is supported
    'provider': 'openmeteo',  # Default provider
    'map': {
        'default_zoom': 6,
        'default_center': [51.505, -0.09],  # Default center (London)
        'min_zoom': 1,
        'max_zoom': 18,
        'tile_size': 256,
        'attribution': 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://openweathermap.org/">OpenWeather</a>',
    },
    'providers': {
        'open-meteo': {
            'api_key': '',  # Open-Meteo doesn't require an API key for basic usage
            'endpoints': {
                'forecast': 'https://api.open-meteo.com/v1/forecast',
                'geocoding': 'https://geocoding-api.open-meteo.com/v1/search',
            }
        },
        'openweathermap': {
            'api_key': '',  # OpenWeatherMap API key
            'endpoints': {
                'current': 'https://api.openweathermap.org/data/2.5/weather',
                'forecast': 'https://api.openweathermap.org/data/2.5/forecast',
                'onecall': 'https://api.openweathermap.org/data/2.5/onecall',
                'geocoding': 'http://api.openweathermap.org/geo/1.0/direct',
                'reverse_geocoding': 'http://api.openweathermap.org/geo/1.0/reverse',
            },
            'tile_servers': {
                'base': 'https://tile.openweathermap.org/map/{layer}/{z}/{x}/{y}.png?appid={api_key}',
                'clouds': 'https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid={api_key}',
                'precipitation': 'https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid={api_key}',
                'pressure': 'https://tile.openweathermap.org/map/pressure_new/{z}/{x}/{y}.png?appid={api_key}',
                'wind': 'https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid={api_key}',
                'temperature': 'https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid={api_key}',
            },
            'map_layers': {
                'temperature': {
                    'name': 'Temperature',
                    'enabled': True,
                    'opacity': 0.7,
                    'legend': {
                        'title': '°C',
                        'colors': ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8',
                                 '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
                    }
                },
                'precipitation': {
                    'name': 'Precipitation',
                    'enabled': True,
                    'opacity': 0.7,
                    'legend': {
                        'title': 'mm',
                        'colors': ['#f7f7f7', '#d9f0d3', '#a6dba0', '#5aae61', '#1b7837', '#00441b']
                    }
                },
                'wind': {
                    'name': 'Wind Speed',
                    'enabled': True,
                    'opacity': 0.7,
                    'legend': {
                        'title': 'm/s',
                        'colors': ['#ffffcc', '#c7e9b4', '#7fcdbb', '#41b6c4', '#2c7fb8', '#253494']
                    }
                },
                'clouds': {
                    'name': 'Clouds',
                    'enabled': True,
                    'opacity': 0.5,
                    'legend': {
                        'title': '%',
                        'colors': ['#f7f7f7', '#d9d9d9', '#bdbdbd', '#969696', '#636363', '#252525']
                    }
                },
                'pressure': {
                    'name': 'Pressure',
                    'enabled': True,
                    'opacity': 0.7,
                    'legend': {
                        'title': 'hPa',
                        'colors': ['#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7',
                                 '#d1e5f0', '#92c5de', '#4393c3', '#2166ac', '#053061']
                    }
                }
            },
            'default_layers': ['temperature', 'precipitation', 'wind', 'clouds', 'pressure'],
            'update_interval': 10,  # minutes
            'max_requests_per_minute': 60  # API rate limit
        },
    }
}

# Test endpoints for API key validation
VALIDATION_ENDPOINTS = {
    'open-meteo': 'https://api.open-meteo.com/v1/forecast?latitude=51.51&longitude=-0.13&current_weather=true',
    'openweathermap': 'https://api.openweathermap.org/data/2.5/weather?q=London,uk&appid={api_key}',
}

class ConfigManager:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()
        # Ensure all providers exist in the config
        self._ensure_providers_config()

    def _ensure_providers_config(self):
        """Ensure all providers have their configuration in the config."""
        if 'providers' not in self.config:
            self.config['providers'] = {}
            
        # Ensure all default providers exist in the config
        for provider, config in DEFAULT_CONFIG['providers'].items():
            if provider not in self.config['providers']:
                self.config['providers'][provider] = config.copy()
            else:
                # Ensure all required keys exist for each provider
                for key, value in config.items():
                    if key not in self.config['providers'][provider]:
                        self.config['providers'][provider][key] = value
        
        # Save if we made any changes
        if 'providers' not in self.config or any(provider not in self.config['providers'] for provider in DEFAULT_CONFIG['providers']):
            self.save_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Backward compatibility: migrate old config to new format
                    if 'api_key' in config and 'providers' not in config:
                        config['providers'] = {
                            'openmeteo': {
                                'api_key': config.get('api_key', '')
                            }
                        }
                        # Remove the old api_key from root
                        if 'api_key' in config:
                            del config['api_key']
                    return {**DEFAULT_CONFIG, **config}
            except Exception as e:
                print(f"Error loading config: {e}")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def update(self, **kwargs):
        # Handle provider-specific updates
        if 'provider' in kwargs and 'api_key' in kwargs:
            provider = kwargs.pop('provider')
            self.set_provider_api_key(provider, kwargs.pop('api_key'))
            
        # Handle provider config updates
        if 'provider_config' in kwargs:
            provider_config = kwargs.pop('provider_config')
            if isinstance(provider_config, dict) and 'provider' in provider_config:
                provider = provider_config.pop('provider')
                self.update_provider_config(provider, provider_config)
        
        # Update remaining config
        self.config.update(kwargs)
        self.save_config()

    def get_config(self):
        return self.config.copy()
    
    def get_provider_config(self, provider):
        """Get configuration for a specific provider."""
        return self.config['providers'].get(provider, {}).copy()
    
    def update_provider_config(self, provider, config):
        """Update configuration for a specific provider."""
        if provider not in self.config['providers']:
            self.config['providers'][provider] = {}
        self.config['providers'][provider].update(config)
        self.save_config()
    
    def set_provider_api_key(self, provider, api_key):
        """Set the API key for a specific provider."""
        if provider not in self.config['providers']:
            self.config['providers'][provider] = {}
        self.config['providers'][provider]['api_key'] = api_key
        self.save_config()
    
    def get_provider_api_key(self, provider):
        """Get the API key for a specific provider."""
        return self.config['providers'].get(provider, {}).get('api_key', '')
    
    def get_current_provider(self):
        """Get the current active provider."""
        return self.config.get('provider', 'openmeteo')
    
    def set_current_provider(self, provider):
        """Set the current active provider."""
        if provider in self.config['providers']:
            self.config['provider'] = provider
            self.save_config()
    
    def get_available_providers(self):
        """Get a list of all available providers."""
        return list(self.config['providers'].keys())
