#!/usr/bin/env python3
"""
Script to configure the OpenWeatherMap API key for weather maps.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import the config manager
from script.config_utils import ConfigManager

def main():
    print("OpenWeatherMap API Key Setup")
    print("=" * 50)
    print("\nThis script will help you set up your OpenWeatherMap API key for weather maps.")
    print("You can get a free API key by signing up at: https://openweathermap.org/api")
    print("The free tier includes 1,000,000 calls/month which is more than enough for personal use.\n")
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Get current API key if it exists
    current_key = config_manager.get_provider_api_key('openweathermap')
    
    if current_key:
        print(f"Current OpenWeatherMap API key: {current_key[:4]}...{current_key[-4:]}")
        change = input("Do you want to change it? (y/N): ").strip().lower()
        if change != 'y':
            print("API key not changed.")
            return
    
    # Get new API key
    while True:
        api_key = input("\nEnter your OpenWeatherMap API key: ").strip()
        if not api_key:
            print("Error: API key cannot be empty!")
            continue
            
        # Simple validation (just checks if it's not empty for now)
        if len(api_key) < 20:
            print("Warning: The API key seems too short. Please double-check your key.")
            confirm = input("Are you sure this is correct? (y/N): ").strip().lower()
            if confirm != 'y':
                continue
        
        # Save the API key
        config_manager.update_provider_config('openweathermap', {'api_key': api_key})
        print("\nAPI key saved successfully!")
        print("You can now use the weather maps in the application.")
        break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    
    input("\nPress Enter to exit...")
