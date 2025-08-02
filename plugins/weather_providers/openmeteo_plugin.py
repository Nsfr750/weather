"""
Open-Meteo weather provider plugin.

This module implements the Open-Meteo API as a weather provider plugin.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
from script.plugin_system.weather_provider import Dict, Any, List, Optional, Tuple
import logging
import os

from script.plugin_system.weather_provider import (
    BaseWeatherProvider,
    WeatherCondition,
    WeatherDataPoint,
    WeatherForecast
)

# Configure logging
logger = logging.getLogger(__name__)

# Map Open-Meteo weather codes to our WeatherCondition enum
WEATHER_CODE_MAP = {
    0: WeatherCondition.CLEAR,
    1: WeatherCondition.CLEAR,
    2: WeatherCondition.CLOUDS,
    3: WeatherCondition.CLOUDS,
    45: WeatherCondition.FOG,
    48: WeatherCondition.FOG,
    51: WeatherCondition.DRIZZLE,
    53: WeatherCondition.DRIZZLE,
    55: WeatherCondition.DRIZZLE,
    56: WeatherCondition.DRIZZLE,
    57: WeatherCondition.DRIZZLE,
    61: WeatherCondition.RAIN,
    63: WeatherCondition.RAIN,
    65: WeatherCondition.RAIN,
    66: WeatherCondition.RAIN,
    67: WeatherCondition.RAIN,
    71: WeatherCondition.SNOW,
    73: WeatherCondition.SNOW,
    75: WeatherCondition.SNOW,
    77: WeatherCondition.SNOW,
    80: WeatherCondition.RAIN,
    81: WeatherCondition.RAIN,
    82: WeatherCondition.RAIN,
    85: WeatherCondition.SNOW,
    86: WeatherCondition.SNOW,
    95: WeatherCondition.THUNDERSTORM,
    96: WeatherCondition.THUNDERSTORM,
    99: WeatherCondition.THUNDERSTORM
}

class OpenMeteoProvider(BaseWeatherProvider):
    """Open-Meteo weather provider plugin.
    
    This provider fetches weather data from the Open-Meteo API.
    """
    
    # Plugin metadata
    name = "openmeteo"
    version = "2.0.0"
    author = "Nsfr750"
    description = "Provides weather data using the Open-Meteo API"
    
    # Open-Meteo doesn't require an API key for basic usage
    api_key_required = False
    
    # Default settings
    settings_schema = {
        "units": {
            "type": "string",
            "default": "metric",
            "enum": ["metric", "imperial"],
            "description": "Units for temperature and wind speed"
        },
        "language": {
            "type": "string",
            "default": "en",
            "description": "Language for weather descriptions"
        },
        "timezone": {
            "type": "string",
            "default": "auto",
            "description": "Timezone for timestamps (e.g., 'Europe/Rome' or 'auto')"
        }
    }
    
    # API endpoints
    BASE_URL = "https://api.open-meteo.com/v1/"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/"
    
    def __init__(self, config=None, **kwargs):
        """Initialize the OpenMeteo provider.
        
        Args:
            config: Configuration dictionary containing api_key, units, language, etc.
            **kwargs: Additional configuration parameters (merged with config)
        """
        # Merge config dict with kwargs
        if config is None:
            config = {}
        config.update(kwargs)
        
        # Set default values from config or environment
        if 'api_key' not in config:
            config['api_key'] = os.environ.get('OPENMETEO_API_KEY')
        if 'units' not in config:
            config['units'] = 'metric'
        if 'language' not in config:
            config['language'] = 'en'
            
        super().__init__(**config)
        
        # Store config for later use
        self.config = config
        
        # Set instance variables from config with proper defaults
        self.api_key = config.get('api_key', '')
        self._api_key = self.api_key  # For compatibility with base class
        self.units = config.get('units', 'metric')
        self.language = config.get('language', 'en')
        self.offline_mode = config.get('offline_mode', False)
        
        # Initialize session for connection pooling
        self.session: Optional[aiohttp.ClientSession] = None
        self._location_cache: Dict[str, Tuple[float, float]] = {}
        
        # Set provider metadata
        self.name = "openmeteo"
        self.display_name = "OpenMeteo"
        self.description = "Provides weather data using the Open-Meteo API"
        self.author = "Nsfr750"
        self.version = "2.0.0"
        self.requires_api_key = False  # Open-Meteo doesn't require an API key for basic usage
    
    @classmethod
    def __call__(cls, **kwargs):
        """Support legacy provider instantiation.
        
        This allows the provider to be instantiated using the legacy syntax:
            provider = OpenMeteoProvider(units='metric', language='en')
        """
        return cls(config=kwargs)
    
    async def initialize(self, app=None) -> bool:
        """Initialize the provider.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self.offline_mode:
            logger.info("OpenMeteoProvider running in offline mode")
            return True
            
        try:
            self.session = aiohttp.ClientSession()
            logger.info("Successfully initialized OpenMeteo provider")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenMeteoProvider: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if not hasattr(self, 'session') or self.session is None:
            return
            
        if not self.session.closed:
            try:
                # Run the async close in the event loop
                loop = None
                if self.session._loop and self.session._loop.is_running():
                    # If there's a running loop, schedule the close
                    self.session._loop.create_task(self.session.close())
                else:
                    # Otherwise, run it in a new event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self.session.close())
                    finally:
                        if loop.is_running():
                            loop.stop()
                        loop.close()
                        asyncio.set_event_loop(None)
            except Exception as e:
                logger.error(f"Error during session cleanup: {e}", exc_info=True)
            finally:
                self.session = None
    
    async def _geocode_location(self, location: str) -> Tuple[float, float]:
        """Convert location name to coordinates using Open-Meteo's geocoding."""
        if not location:
            raise ValueError("Location cannot be empty")
            
        # Check cache first
        if location in self._location_cache:
            return self._location_cache[location]
            
        # If it's already coordinates, parse them
        if ',' in location:
            try:
                lat, lon = map(float, (x.strip() for x in location.split(',')))
                self._location_cache[location] = (lat, lon)
                return lat, lon
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid coordinate format: {location}. Expected 'lat,lon'") from e
        
        # Otherwise, geocode the location name
        if not self.session:
            raise RuntimeError("Session not initialized")
            
        params = {
            'name': location,
            'count': 1,
            'language': self.get_setting('language', 'en'),
            'format': 'json'
        }
        
        try:
            async with self.session.get(f"{self.GEOCODING_URL}search", params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                if not data.get('results'):
                    raise ValueError(f"Location '{location}' not found")
                
                result = data['results'][0]
                lat, lon = result['latitude'], result['longitude']
                self._location_cache[location] = (lat, lon)
                return lat, lon
                
        except aiohttp.ClientError as e:
            logger.error(f"Geocoding API error: {e}")
            raise ConnectionError(f"Failed to geocode location: {e}") from e
    
    def _map_weather_code(self, code: int) -> WeatherCondition:
        """Map Open-Meteo weather code to our WeatherCondition enum."""
        return WEATHER_CODE_MAP.get(code, WeatherCondition.CLEAR)
    
    def _get_weather_description(self, code: int) -> str:
        """Get a human-readable weather description from the weather code."""
        descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return descriptions.get(code, "Unknown weather conditions")
    
    def _get_weather_icon(self, code: int, is_day: bool = True) -> str:
        """Get a weather icon code based on the weather code."""
        # Simple mapping - you can expand this with more specific icons
        if code in [0, 1]:
            return "01d" if is_day else "01n"
        elif code in [2, 3]:
            return "02d" if is_day else "02n"
        elif code in [45, 48, 51, 53, 55, 56, 57]:
            return "50d"  # mist/fog
        elif code in [61, 63, 65, 66, 67, 80, 81, 82]:
            return "10d" if is_day else "10n"  # rain
        elif code in [71, 73, 75, 77, 85, 86]:
            return "13d"  # snow
        elif code in [95, 96, 99]:
            return "11d"  # thunderstorm
        return "01d"  # default to clear day
    
    async def get_current_weather(self, location: str, **kwargs) -> WeatherForecast:
        """Get current weather for a location."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        # Get coordinates for the location
        lat, lon = await self._geocode_location(location)
        
        # Prepare parameters
        units = self.get_setting('units', 'metric')
        timezone = self.get_setting('timezone', 'auto')
        
        # Make the API request
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': 'true',
            'temperature_unit': 'celsius' if units == 'metric' else 'fahrenheit',
            'windspeed_unit': 'kmh' if units == 'metric' else 'mph',
            'precipitation_unit': 'mm',
            'timezone': timezone,
            'timeformat': 'iso8601',
            'current': [
                'temperature_2m', 'relative_humidity_2m', 'apparent_temperature',
                'weather_code', 'surface_pressure', 'wind_speed_10m',
                'wind_direction_10m', 'visibility', 'is_day'
            ],
            'hourly': [
                'temperature_2m', 'relative_humidity_2m', 'apparent_temperature',
                'weather_code', 'surface_pressure', 'visibility', 'wind_speed_10m',
                'wind_direction_10m', 'precipitation', 'is_day'
            ],
            'daily': [
                'weather_code', 'temperature_2m_max', 'temperature_2m_min',
                'apparent_temperature_max', 'apparent_temperature_min',
                'precipitation_sum', 'precipitation_hours', 'wind_speed_10m_max',
                'wind_gusts_10m_max', 'wind_direction_10m_dominant', 'sunrise', 'sunset'
            ]
        }
        
        try:
            async with self.session.get(f"{self.BASE_URL}forecast", params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Process current weather
                current = data.get('current_weather', {})
                current_hourly = data.get('hourly', {})
                current_daily = data.get('daily', {})
                
                # Get the current hour's data from hourly if available
                current_hour = None
                if 'time' in current_hourly and len(current_hourly['time']) > 0:
                    current_time = current.get('time')
                    if current_time in current_hourly['time']:
                        idx = current_hourly['time'].index(current_time)
                        current_hour = {k: v[idx] for k, v in current_hourly.items() if k != 'time'}
                
                # Create current weather data point
                current_dt = datetime.fromisoformat(current['time'].replace('Z', '+00:00'))
                is_day = current_hour.get('is_day', 1) if current_hour else 1
                
                current_data = WeatherDataPoint(
                    timestamp=current_dt,
                    temperature=current.get('temperature', 0.0),
                    feels_like=current_hour.get('apparent_temperature', current.get('temperature', 0.0)) if current_hour else 0.0,
                    humidity=current_hour.get('relative_humidity_2m', 0) if current_hour else 0,
                    pressure=current_hour.get('surface_pressure', 1013) if current_hour else 1013,
                    wind_speed=current.get('windspeed', 0.0),
                    wind_direction=current.get('winddirection', 0),
                    condition=self._map_weather_code(current.get('weathercode', 0)),
                    description=self._get_weather_description(current.get('weathercode', 0)),
                    icon=self._get_weather_icon(current.get('weathercode', 0), is_day=is_day),
                    precipitation=current_hour.get('precipitation', 0.0) if current_hour else 0.0,
                    visibility=current_hour.get('visibility', 10000) if current_hour else 10000,
                    wind_gust=current.get('windgusts_10m', 0.0) if 'windgusts_10m' in current else None,
                    uv_index=None,  # Not available in current weather
                    dew_point=None  # Need to calculate or get from API
                )
                
                # Create forecast object
                forecast = WeatherForecast(
                    location=location,
                    latitude=lat,
                    longitude=lon,
                    timezone=data.get('timezone', 'UTC'),
                    current=current_data
                )
                
                # Process hourly forecast (next 48 hours)
                if 'time' in data.get('hourly', {}):
                    for i in range(min(48, len(data['hourly']['time']))):
                        time_str = data['hourly']['time'][i]
                        hour_dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        is_day_hour = data['hourly'].get('is_day', [1] * len(data['hourly']['time']))[i]
                        
                        forecast.hourly.append(WeatherDataPoint(
                            timestamp=hour_dt,
                            temperature=data['hourly']['temperature_2m'][i],
                            feels_like=data['hourly'].get('apparent_temperature', [0.0] * len(data['hourly']['time']))[i],
                            humidity=data['hourly'].get('relative_humidity_2m', [0] * len(data['hourly']['time']))[i],
                            pressure=data['hourly'].get('surface_pressure', [1013] * len(data['hourly']['time']))[i],
                            wind_speed=data['hourly'].get('wind_speed_10m', [0.0] * len(data['hourly']['time']))[i],
                            wind_direction=data['hourly'].get('wind_direction_10m', [0] * len(data['hourly']['time']))[i],
                            condition=self._map_weather_code(data['hourly'].get('weather_code', [0] * len(data['hourly']['time']))[i]),
                            description=self._get_weather_description(data['hourly'].get('weather_code', [0] * len(data['hourly']['time']))[i]),
                            icon=self._get_weather_icon(data['hourly'].get('weather_code', [0] * len(data['hourly']['time']))[i], is_day=is_day_hour),
                            precipitation=data['hourly'].get('precipitation', [0.0] * len(data['hourly']['time']))[i],
                            visibility=data['hourly'].get('visibility', [10000] * len(data['hourly']['time']))[i],
                            wind_gust=data['hourly'].get('wind_gusts_10m', [0.0] * len(data['hourly']['time']))[i] if 'wind_gusts_10m' in data['hourly'] else None
                        ))
                
                # Process daily forecast (next 7 days)
                if 'time' in data.get('daily', {}):
                    for i in range(min(7, len(data['daily']['time']))):
                        day_str = data['daily']['time'][i]
                        day_dt = datetime.strptime(day_str, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
                        
                        forecast.daily.append(WeatherDataPoint(
                            timestamp=day_dt,
                            temperature=data['daily'].get('temperature_2m_max', [0.0] * len(data['daily']['time']))[i],
                            feels_like=data['daily'].get('apparent_temperature_max', [0.0] * len(data['daily']['time']))[i],
                            humidity=None,  # Daily humidity not directly available
                            pressure=None,  # Daily pressure not directly available
                            wind_speed=data['daily'].get('wind_speed_10m_max', [0.0] * len(data['daily']['time']))[i],
                            wind_direction=data['daily'].get('wind_direction_10m_dominant', [0] * len(data['daily']['time']))[i],
                            condition=self._map_weather_code(data['daily'].get('weather_code', [0] * len(data['daily']['time']))[i]),
                            description=self._get_weather_description(data['daily'].get('weather_code', [0] * len(data['daily']['time']))[i]),
                            icon=self._get_weather_icon(data['daily'].get('weather_code', [0] * len(data['daily']['time']))[i], is_day=True),
                            precipitation=data['daily'].get('precipitation_sum', [0.0] * len(data['daily']['time']))[i],
                            wind_gust=data['daily'].get('wind_gusts_10m_max', [0.0] * len(data['daily']['time']))[i] if 'wind_gusts_10m_max' in data['daily'] else None,
                            uv_index=None  # UV index not in free API
                        ))
                
                return forecast
                
        except aiohttp.ClientError as e:
            logger.error(f"Open-Meteo API error: {e}")
            raise ConnectionError(f"Failed to fetch weather data: {e}") from e
    
    async def get_forecast(self, location: str, days: int = 5, **kwargs) -> WeatherForecast:
        """Get weather forecast for a location.
        
        Args:
            location: Location string (e.g., "New York,US" or "London")
            days: Number of days to forecast (1-16, default: 5)
            
        Returns:
            WeatherForecast: Forecast data including current and daily forecasts
            
        Raises:
            ValueError: If location is not found or no forecast data is available
        """
        # First get current weather data
        current_data = await self.get_current_weather(location, **kwargs)
        
        # Get the location coordinates
        lat, lon = await self._geocode_location(location)
        
        # Prepare parameters for the forecast request
        units = self.units
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': [
                'weather_code', 'temperature_2m_max', 'temperature_2m_min',
                'apparent_temperature_max', 'apparent_temperature_min',
                'sunrise', 'sunset', 'precipitation_sum', 'precipitation_hours',
                'wind_speed_10m_max', 'wind_gusts_10m_max', 'wind_direction_10m_dominant'
            ],
            'timezone': 'auto',
            'forecast_days': min(days, 16),  # Max 16 days
            'temperature_unit': 'celsius' if units == 'metric' else 'fahrenheit',
            'wind_speed_unit': 'kmh' if units == 'metric' else 'mph',
            'precipitation_unit': 'mm'
        }
        
        try:
            # Make the API request
            if not self.session:
                raise RuntimeError("Session not initialized")
                
            async with self.session.get(f"{self.BASE_URL}forecast", params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Parse the daily forecast
                daily_data = data.get('daily', {})
                daily_forecasts = []
                
                for i in range(min(len(daily_data.get('time', [])), days)):
                    try:
                        date = datetime.fromisoformat(daily_data['time'][i])
                        
                        # Create a WeatherDataPoint for each day
                        forecast = WeatherDataPoint(
                            timestamp=date,
                            temperature=daily_data.get('temperature_2m_max', [0.0])[i],
                            feels_like=daily_data.get('apparent_temperature_max', [0.0])[i],
                            temperature_min=daily_data.get('temperature_2m_min', [0.0])[i],
                            feels_like_min=daily_data.get('apparent_temperature_min', [0.0])[i],
                            condition=self._map_weather_code(daily_data.get('weather_code', [0])[i]),
                            description=self._get_weather_description(daily_data.get('weather_code', [0])[i]),
                            icon=self._get_weather_icon(daily_data.get('weather_code', [0])[i], is_day=True),
                            wind_speed=daily_data.get('wind_speed_10m_max', [0.0])[i],
                            wind_direction=daily_data.get('wind_direction_10m_dominant', [0])[i],
                            wind_gust=daily_data.get('wind_gusts_10m_max', [0.0])[i],
                            precipitation=daily_data.get('precipitation_sum', [0.0])[i],
                            precipitation_hours=daily_data.get('precipitation_hours', [0.0])[i],
                            sunrise=datetime.fromisoformat(daily_data['sunrise'][i]) if i < len(daily_data.get('sunrise', [])) else None,
                            sunset=datetime.fromisoformat(daily_data['sunset'][i]) if i < len(daily_data.get('sunset', [])) else None,
                            humidity=None,  # Not available in daily forecast
                            pressure=None,  # Not available in daily forecast
                            uv_index=None,  # Not available in daily forecast
                            dew_point=None  # Not available in daily forecast
                        )
                        daily_forecasts.append(forecast)
                    except (IndexError, KeyError, ValueError) as e:
                        logger.warning(f"Error parsing daily forecast data for day {i}: {e}")
                        continue
                
                # Create and return the WeatherForecast object
                return WeatherForecast(
                    location=location,
                    latitude=lat,
                    longitude=lon,
                    timezone=data.get('timezone', 'UTC'),
                    current=current_data,
                    hourly=[],  # Not implemented in this example
                    daily=daily_forecasts,
                    alerts=[]  # Not available in the free API
                )
                
        except aiohttp.ClientError as e:
            logger.error(f"Failed to fetch forecast data: {e}")
            raise ConnectionError(f"Failed to fetch forecast data: {e}") from e

# This makes the plugin discoverable by the plugin system
# The plugin manager looks for a PLUGIN_CLASS variable that points to the plugin class
PLUGIN_CLASS = OpenMeteoProvider

# For backward compatibility with the plugin manager
__plugin__ = OpenMeteoProvider
