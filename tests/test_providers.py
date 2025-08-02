#!/usr/bin/env python3
"""
Test script for weather provider plugins.

This script tests the functionality of each weather provider plugin
and verifies that they can successfully retrieve weather data.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Test location
TEST_LOCATION = "New York,US"

def print_weather_data(provider_name, data):
    """Print weather data in a formatted way."""
    print(f"\n{'='*50}")
    print(f"{provider_name} Weather Data")
    print("="*50)
    
    if not data:
        print("No data received")
        return
        
    if hasattr(data, 'current'):
        # Handle WeatherForecast object
        current = data.current
        print(f"Location: {data.location}")
        print(f"Temperature: {current.temperature}°C (Feels like: {current.feels_like}°C)")
        print(f"Condition: {current.condition.value} - {current.description}")
        print(f"Humidity: {current.humidity}%")
        print(f"Wind: {current.wind_speed} m/s, {current.wind_direction}°")
        print(f"Pressure: {current.pressure} hPa")
        
        if hasattr(data, 'daily') and data.daily:
            print("\nDaily Forecast:")
            for i, day in enumerate(data.daily[:3], 1):  # Show next 3 days
                print(f"  Day {i}: {day.temperature}°C, {day.condition.value}")
    else:
        # Handle single WeatherDataPoint
        print(f"Temperature: {data.temperature}°C")
        print(f"Condition: {data.condition.value}")
        print(f"Description: {data.description}")
    
    print("="*50 + "\n")

async def test_provider(provider_class, **kwargs):
    """Test a weather provider and return its data."""
    try:
        # Initialize provider
        provider = provider_class(**kwargs)
        
        # Test initialization - handle both sync and async initialize methods
        if hasattr(provider, 'initialize'):
            if asyncio.iscoroutinefunction(provider.initialize):
                # Handle async initialize
                if not await provider.initialize():
                    logger.error(f"Failed to initialize {provider.name}")
                    return None
            else:
                # Handle sync initialize (for backward compatibility)
                if not provider.initialize():
                    logger.error(f"Failed to initialize {provider.name}")
                    return None
        
        # Test current weather
        logger.info(f"Testing {provider.name}...")
        current = await provider.get_current_weather(TEST_LOCATION)
        
        # Test forecast if available
        forecast = None
        if hasattr(provider, 'get_forecast'):
            forecast = await provider.get_forecast(TEST_LOCATION, days=3)
        
        return {
            'current': current,
            'forecast': forecast,
            'provider': provider
        }
    except Exception as e:
        logger.error(f"Error testing {provider_class.__name__}: {str(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            logger.error(traceback.format_exc())
        return None

async def main():
    """Main test function."""
    # Import available providers
    from plugins.weather_providers.openweathermap_plugin import OpenWeatherMapProvider
    from plugins.weather_providers.accuweather_plugin import AccuWeatherProvider
    
    # List of available providers to test with their required config
    providers = [
        (OpenWeatherMapProvider, {
            'api_key': os.getenv('OPENWEATHERMAP_API_KEY')
        }),
        (AccuWeatherProvider, {
            'api_key': os.getenv('ACCUWEATHER_API_KEY')
        })
    ]
    
    # Test each provider
    results = {}
    for provider_class, config in providers:
        provider_name = provider_class.__name__
        logger.info(f"\n{'*'*30}")
        logger.info(f"Testing {provider_name}...")
        logger.info(f"{'*'*30}")
        
        result = await test_provider(provider_class, **config)
        if result:
            results[provider_name] = result
            print_weather_data(provider_name, result['forecast'] or result['current'])
    
    # Print summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    print(f"Total providers tested: {len(providers)}")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(providers) - len(results)}")
    
    if results:
        print("\nSuccessful providers:")
        for name in results:
            print(f"- {name}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
