"""
Weather Providers Package

This package contains implementations of various weather data providers.
"""

from .base_provider import WeatherProvider
from .openweathermap import OpenWeatherMapProvider
from .openmeteo import OpenMeteoProvider
from .weatherdotcom import WeatherDotComProvider
from .breezyweather import BreezyWeatherProvider
from .quickweather import QuickWeatherProvider
from .weathercompany import WeatherCompanyProvider
from .alliander import AllianderProvider

# Map of provider names to their classes
PROVIDERS = {
    'openweathermap': OpenWeatherMapProvider,
    'open-meteo': OpenMeteoProvider,
    'weather.com': WeatherDotComProvider,
    'breezy-weather': BreezyWeatherProvider,
    'quickweather': QuickWeatherProvider,
    'weathercompany': WeatherCompanyProvider,
    'alliander': AllianderProvider,
    # Add new providers here
}


def get_provider(name, *args, **kwargs):
    """Get a weather provider by name.
    
    Args:
        name (str): Name of the provider (e.g., 'openweathermap')
        *args: Positional arguments to pass to the provider's constructor
        **kwargs: Keyword arguments to pass to the provider's constructor
        
    Returns:
        WeatherProvider: An instance of the requested weather provider
        
    Raises:
        ValueError: If the provider is not found
    """
    provider_class = PROVIDERS.get(name.lower())
    if not provider_class:
        raise ValueError(f"Unknown weather provider: {name}")
    return provider_class(*args, **kwargs)


def get_available_providers():
    """Get a list of available weather providers.
    
    Returns:
        list: List of available provider names
    """
    return list(PROVIDERS.keys())
