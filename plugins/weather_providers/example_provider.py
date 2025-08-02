"""
Example weather provider plugin for the Weather Application.

This module demonstrates how to create a custom weather provider.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import random

from script.plugin_system.weather_provider import (
    BaseWeatherProvider,
    WeatherCondition,
    WeatherDataPoint,
    WeatherForecast
)

class ExampleWeatherProvider(BaseWeatherProvider):
    """Example weather provider that generates random weather data."""
    
    name = "Example Weather Provider"
    author = "Nsfr750"
    description = "Example provider that generates random weather data for testing"
    api_key_required = False
    version = "1.0.0"

    # Settings schema for the provider's configuration UI
    settings_schema = {
        "temperature_offset": {
            "type": "number",
            "default": 0,
            "description": "Temperature offset in Celsius"
        },
        "humidity_offset": {
            "type": "integer",
            "default": 0,
            "min": -20,
            "max": 20,
            "description": "Humidity offset in percentage points"
        },
        "enable_extreme_weather": {
            "type": "boolean",
            "default": False,
            "description": "Enable extreme weather conditions"
        }
    }
    
    def __init__(self, config=None, **kwargs):
        """Initialize the example provider.
        
        Args:
            config: Configuration dictionary containing settings
            **kwargs: Additional configuration parameters (merged with config)
        """
        # Merge config dict with kwargs
        if config is None:
            config = {}
        config.update(kwargs)
        
        # Set default values from config or environment
        if 'units' not in config:
            config['units'] = 'metric'
        if 'language' not in config:
            config['language'] = 'en'
            
        super().__init__(**config)
        
        # Store config for later use
        self.config = config
        
        # Set instance variables from config with proper defaults
        self.units = config.get('units', 'metric')
        self.language = config.get('language', 'en')
        self.offline_mode = config.get('offline_mode', False)
        self._weather_cache: Dict[str, WeatherForecast] = {}
    
    @classmethod
    def __call__(cls, **kwargs):
        """Support legacy provider instantiation.
        
        This allows the provider to be instantiated using the legacy syntax:
            provider = ExampleWeatherProvider(units='metric', language='en')
        """
        return cls(config=kwargs)
    
    async def initialize(self, app=None) -> bool:
        """Initialize the provider.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.app = app
        if self.offline_mode:
            logger.info("ExampleWeatherProvider running in offline mode")
            return True
            
        try:
            logger.info("Successfully initialized ExampleWeatherProvider")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ExampleWeatherProvider: {e}")
            return False
    
    async def get_current_weather(self, location: str, **kwargs) -> WeatherForecast:
        """Get current weather for a location."""
        # Check cache first
        cache_key = f"current_{location}"
        if cache_key in self._weather_cache:
            return self._weather_cache[cache_key]
        
        # Generate random weather data
        temp = self._generate_temperature()
        condition = self._random_condition()
        
        current = WeatherDataPoint(
            timestamp=datetime.utcnow(),
            temperature=temp,
            feels_like=temp + random.uniform(-2, 2),
            humidity=random.randint(30, 80) + self.get_setting("humidity_offset", 0),
            pressure=random.randint(980, 1040),
            wind_speed=random.uniform(0.5, 10.0),
            wind_direction=random.randint(0, 359),
            condition=condition,
            description=f"Example {condition.value} weather",
            icon=f"01d" if condition == WeatherCondition.CLEAR else f"02d",
            precipitation=random.uniform(0, 5) if condition in [WeatherCondition.RAIN, WeatherCondition.DRIZZLE] else 0,
            cloudiness=random.randint(0, 100) if condition == WeatherCondition.CLOUDS else 0,
            uv_index=random.uniform(0, 11),
            dew_point=temp - random.uniform(2, 10),
            wind_gust=random.uniform(5, 20)
        )
        
        # Create a simple forecast with just current weather
        forecast = WeatherForecast(
            location=location,
            latitude=0.0,
            longitude=0.0,
            timezone="UTC",
            current=current
        )
        
        # Cache the result
        self._weather_cache[cache_key] = forecast
        return forecast
    
    async def get_forecast(self, location: str, days: int = 5, **kwargs) -> WeatherForecast:
        """Get weather forecast for a location."""
        cache_key = f"forecast_{location}_{days}"
        if cache_key in self._weather_cache:
            return self._weather_cache[cache_key]
        
        # Get current weather first
        current_forecast = await self.get_current_weather(location, **kwargs)
        forecast = WeatherForecast(
            location=location,
            latitude=0.0,
            longitude=0.0,
            timezone="UTC",
            current=current_forecast.current
        )
        
        # Generate hourly forecast (next 48 hours)
        now = datetime.utcnow()
        for i in range(48):
            hour_time = now + timedelta(hours=i+1)
            temp = self._generate_temperature(hour_time.hour)
            condition = self._random_condition()
            
            forecast.hourly.append(WeatherDataPoint(
                timestamp=hour_time,
                temperature=temp,
                feels_like=temp + random.uniform(-2, 2),
                humidity=random.randint(30, 80) + self.get_setting("humidity_offset", 0),
                pressure=random.randint(980, 1040),
                wind_speed=random.uniform(0.5, 15.0),
                wind_direction=random.randint(0, 359),
                condition=condition,
                description=f"Example {condition.value} weather",
                icon=f"01d" if condition == WeatherCondition.CLEAR else f"02d",
                precipitation=random.uniform(0, 5) if condition in [WeatherCondition.RAIN, WeatherCondition.DRIZZLE] else 0,
                cloudiness=random.randint(0, 100) if condition == WeatherCondition.CLOUDS else 0,
                uv_index=random.uniform(0, 11),
                dew_point=temp - random.uniform(2, 10),
                wind_gust=random.uniform(5, 25)
            ))
        
        # Generate daily forecast
        for i in range(days):
            day_time = now + timedelta(days=i+1)
            temp = self._generate_temperature(12)  # Midday temperature
            condition = self._random_condition()
            
            forecast.daily.append(WeatherDataPoint(
                timestamp=day_time.replace(hour=12, minute=0, second=0, microsecond=0),
                temperature=temp,
                feels_like=temp + random.uniform(-1, 1),
                humidity=random.randint(40, 70) + self.get_setting("humidity_offset", 0),
                pressure=random.randint(990, 1030),
                wind_speed=random.uniform(1, 8),
                wind_direction=random.randint(0, 359),
                condition=condition,
                description=f"Example {condition.value} weather",
                icon=f"01d" if condition == WeatherCondition.CLEAR else f"02d",
                precipitation=random.uniform(0, 3) if condition in [WeatherCondition.RAIN, WeatherCondition.DRIZZLE] else 0,
                cloudiness=random.randint(0, 80) if condition == WeatherCondition.CLOUDS else 0,
                uv_index=random.uniform(1, 10),
                dew_point=temp - random.uniform(3, 8),
                wind_gust=random.uniform(3, 15)
            ))
        
        # Cache the result
        self._weather_cache[cache_key] = forecast
        return forecast
    
    def _generate_temperature(self, hour: int = 12) -> float:
        """Generate a realistic temperature based on the time of day."""
        # Base temperature varies by time of day (colder at night, warmer during day)
        base_temp = 15 + 10 * (0.5 + 0.5 * (1 - abs(12 - hour) / 12))
        # Add some randomness
        temp = base_temp + random.uniform(-5, 5)
        # Apply user's temperature offset
        return temp + self.get_setting("temperature_offset", 0)
    
    def _random_condition(self) -> WeatherCondition:
        """Generate a random weather condition."""
        if self.get_setting("enable_extreme_weather", False):
            conditions = list(WeatherCondition)
        else:
            # Exclude extreme weather conditions
            extreme = {
                WeatherCondition.TORNADO,
                WeatherCondition.HURRICANE,
                WeatherCondition.THUNDERSTORM,
                WeatherCondition.ASH,
                WeatherCondition.SQUALL
            }
            conditions = [c for c in WeatherCondition if c not in extreme]
        
        weights = {
            WeatherCondition.CLEAR: 0.4,
            WeatherCondition.CLOUDS: 0.3,
            WeatherCondition.RAIN: 0.15,
            WeatherCondition.DRIZZLE: 0.1
        }
        
        # Default weight for conditions not in the weights dict
        default_weight = 0.05 / (len(conditions) - len(weights))
        
        weighted_conditions = []
        for condition in conditions:
            weight = weights.get(condition, default_weight)
            weighted_conditions.append((condition, weight))
        
        # Normalize weights
        total = sum(w for _, w in weighted_conditions)
        normalized = [(c, w/total) for c, w in weighted_conditions]
        
        # Select a random condition based on weights
        r = random.random()
        upto = 0
        for condition, weight in normalized:
            if upto + weight >= r:
                return condition
            upto += weight
        return conditions[-1]  # fallback
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self._weather_cache.clear()
        self._is_initialized = False

# This makes the plugin discoverable by the plugin system
PLUGIN_CLASS = ExampleWeatherProvider
