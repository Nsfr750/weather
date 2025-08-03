#!/usr/bin/env python3
"""
Weather Icons Downloader v1.6.0

This script downloads weather icons from OpenWeatherMap to be used in the application.
"""

import os
import sys
import requests
from pathlib import Path

def download_weather_icons():
    """Download weather icons from OpenWeatherMap."""
    # Base URL for OpenWeatherMap icons
    base_url = "https://openweathermap.org/img/wn/"
    
    # List of icon codes to download
    icon_codes = [
        "01d", "01n",  # clear sky
        "02d", "02n",  # few clouds
        "03d", "03n",  # scattered clouds
        "04d", "04n",  # broken clouds
        "09d", "09n",  # shower rain
        "10d", "10n",  # rain
        "11d", "11n",  # thunderstorm
        "13d", "13n",  # snow
        "50d", "50n"   # mist
    ]
    
    # Create assets directory if it doesn't exist
    assets_dir = Path("assets/weather_icons")
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Download each icon
    for code in icon_codes:
        icon_url = f"{base_url}{code}@2x.png"
        icon_path = assets_dir / f"{code}.png"
        
        # Skip if file already exists
        if icon_path.exists():
            print(f"Skipping {code} - already exists")
            continue
            
        try:
            response = requests.get(icon_url, stream=True)
            response.raise_for_status()
            
            with open(icon_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            print(f"Downloaded {code} icon")
            
        except Exception as e:
            print(f"Error downloading {code}: {e}")
    
    print("\nWeather icons downloaded successfully!")

if __name__ == "__main__":
    download_weather_icons()
