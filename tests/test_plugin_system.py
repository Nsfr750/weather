#!/usr/bin/env python3
"""
Test script for the Weather App plugin system.

This script tests the discovery and loading of weather provider plugins.
"""

import sys
import logging
import asyncio
from pathlib import Path

# Add script directory to path
script_dir = Path(__file__).parent.absolute()
sys.path.append(str(script_dir))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_plugin_system():
    """Test the plugin system by discovering and loading all available plugins."""
    from script.plugin_system import PluginManager
    from script.plugin_system.weather_provider import BaseWeatherProvider
    
    logger.info("Starting plugin system test...")
    
    # Initialize plugin manager
    plugin_manager = PluginManager()
    
    # Set up plugin paths
    plugins_dir = script_dir / "script" / "plugin_system" / "plugins" / "weather_providers"
    plugin_manager.plugin_paths = [plugins_dir]
    
    # Load plugins
    logger.info("Loading plugins...")
    plugin_manager.load_plugins()
    
    # List discovered plugins
    logger.info(f"Discovered {len(plugin_manager.plugins)} plugins:")
    for plugin_name, plugin in plugin_manager.plugins.items():
        logger.info(f"- {plugin_name} (version: {getattr(plugin, 'version', 'unknown')})")
    
    # Test OpenWeatherMap plugin
    if 'openweathermap' in plugin_manager.plugins:
        logger.info("\nTesting OpenWeatherMap plugin...")
        plugin = plugin_manager.plugins['openweathermap']
        
        # Get weather provider instance
        try:
            # In a real app, you would get the API key from config
            api_key = "YOUR_API_KEY_HERE"  # Replace with actual API key for testing
            
            provider = plugin.get_weather_provider(
                api_key=api_key,
                units="metric",
                language="en"
            )
            
            # Test current weather
            logger.info("Fetching current weather for London...")
            try:
                current = await provider.get_current_weather("London,UK")
                logger.info(f"Current weather in {current.location_name}, {current.country}:")
                logger.info(f"  Temperature: {current.temperature}°C (feels like {current.feels_like}°C)")
                logger.info(f"  Condition: {current.condition_text}")
                logger.info(f"  Wind: {current.wind_speed} m/s, {current.wind_direction}°")
            except Exception as e:
                logger.error(f"Failed to get current weather: {e}")
            
            # Test forecast
            logger.info("\nFetching 3-day forecast for London...")
            try:
                forecast = await provider.get_forecast("London,UK", days=3)
                logger.info(f"Forecast for {forecast.location_name}, {forecast.country}:")
                
                # Group forecast by day
                from datetime import datetime, timezone
                import calendar
                
                # Find unique days in the forecast
                days = {}
                for point in forecast.forecast:
                    dt = datetime.fromtimestamp(point.timestamp, tz=timezone.utc)
                    day_name = calendar.day_name[dt.weekday()]
                    date_str = dt.strftime('%Y-%m-%d')
                    
                    if date_str not in days:
                        days[date_str] = {
                            'day_name': day_name,
                            'date': date_str,
                            'high': point.temperature,
                            'low': point.temperature,
                            'conditions': {}
                        }
                    else:
                        if point.temperature > days[date_str]['high']:
                            days[date_str]['high'] = point.temperature
                        if point.temperature < days[date_str]['low']:
                            days[date_str]['low'] = point.temperature
                    
                    # Track condition frequencies
                    cond = point.condition_text
                    days[date_str]['conditions'][cond] = days[date_str]['conditions'].get(cond, 0) + 1
                
                # Print daily forecast
                for date, day_data in days.items():
                    # Find most common condition
                    if day_data['conditions']:
                        common_condition = max(day_data['conditions'].items(), key=lambda x: x[1])[0]
                    else:
                        common_condition = "Unknown"
                    
                    logger.info(
                        f"  {day_data['day_name']} ({day_data['date']}): "
                        f"{day_data['low']:.1f}°C - {day_data['high']:.1f}°C, {common_condition}"
                    )
                    
            except Exception as e:
                logger.error(f"Failed to get forecast: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenWeatherMap provider: {e}")
    else:
        logger.warning("OpenWeatherMap plugin not found in discovered plugins")
    
    logger.info("\nPlugin system test completed.")

if __name__ == "__main__":
    asyncio.run(test_plugin_system())
