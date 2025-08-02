"""
Test script to verify OpenWeatherMap plugin initialization.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv()

# Import the OpenWeatherMap provider
try:
    from plugins.weather_providers.openweathermap_plugin import OpenWeatherMapProvider
    print("Successfully imported OpenWeatherMapProvider")
except ImportError as e:
    print(f"Error importing OpenWeatherMapProvider: {e}")
    sys.exit(1)

# Get API key from environment
api_key = os.getenv('OPENWEATHERMAP_API_KEY')
print(f"API key from .env: {'*' * 8 + api_key[-4:] if api_key else 'Not found'}")

if not api_key:
    print("Error: OPENWEATHERMAP_API_KEY not found in .env file")
    sys.exit(1)

async def test_provider():
    """Test the OpenWeatherMap provider with async/await."""
    try:
        print("\nInitializing OpenWeatherMap provider...")
        provider = OpenWeatherMapProvider(api_key=api_key)
        
        # Initialize the provider
        if not await provider.initialize():
            print("Failed to initialize provider")
            return
            
        print("Provider initialized successfully!")
        
        # Test getting current weather for a location
        print("\nTesting current weather for London, UK...")
        try:
            weather = await provider.get_current_weather("London,UK")
            print(f"Successfully got weather for London, UK:")
            print(f"  Temperature: {weather.temperature}°C")
            print(f"  Feels like: {weather.feels_like}°C")
            print(f"  Condition: {weather.condition.value}")
            print(f"  Description: {weather.description}")
            print(f"  Humidity: {weather.humidity}%")
            print(f"  Pressure: {weather.pressure} hPa")
        except Exception as e:
            print(f"Error getting current weather: {e}")
            import traceback
            traceback.print_exc()
        
        # Test getting forecast
        print("\nTesting 5-day forecast for London, UK...")
        try:
            forecast = await provider.get_forecast("London,UK", days=5)
            print(f"Successfully got forecast data")
            if hasattr(forecast, 'current') and forecast.current:
                print(f"\nCurrent weather:")
                print(f"  Temperature: {forecast.current.temperature}°C")
                print(f"  Condition: {forecast.current.condition.value}")
                
            if hasattr(forecast, 'daily') and forecast.daily:
                print(f"\nDaily forecast ({len(forecast.daily)} days):")
                for i, day in enumerate(forecast.daily[:5]):  # Show up to 5 days
                    date_str = day.timestamp.strftime('%a, %b %d')
                    print(f"  {date_str}: {day.temperature:.1f}°C, {day.condition.value}")
                    
        except Exception as e:
            print(f"Error getting forecast: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Error initializing provider: {e}")
        import traceback
        traceback.print_exc()

# Run the async test
if __name__ == "__main__":
    asyncio.run(test_provider())
