"""
OpenMeteo Weather Provider

This module provides weather data using the Open-Meteo.com API.
It implements the standard weather provider interface used by the application.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from pathlib import Path

# Local imports
from lang.language_manager import get_language_manager

logger = logging.getLogger(__name__)

class OpenMeteoProvider:
    """Weather provider implementation for Open-Meteo.com API."""
    
    BASE_URL = "https://api.open-meteo.com/v1/"
    
    def __init__(self, api_key: str = "", units: str = "metric"):
        """Initialize the OpenMeteo provider.
        
        Args:
            api_key: Not required for Open-Meteo.com (kept for interface compatibility)
            units: Units system to use (metric or imperial)
        """
        self.units = units
        self.cache = {}
        self.history = []
        self.max_history = 10  # Number of historical queries to keep
        self.language_manager = get_language_manager()
        
        # Initialize weather code translations
        self._init_weather_descriptions()
        
    def get_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location.
        
        Args:
            location: City name or coordinates (lat,lon)
            
        Returns:
            Dictionary containing weather data
        """
        try:
            # First get coordinates for the location
            coords = self._geocode(location)
            if not coords:
                return {"error": f"Could not find location: {location}"}
                
            # Get current weather with additional parameters
            params = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "current_weather": "true",
                "temperature_unit": "celsius" if self.units == "metric" else "fahrenheit",
                "windspeed_unit": "kmh" if self.units == "metric" else "mph",
                "precipitation_unit": "mm",
                "timezone": "auto",
                "forecast_days": 1,
                # Add parameters for additional weather data
                "current": [
                    "apparent_temperature",  # For feels_like
                    "relative_humidity_2m",  # For humidity
                    "surface_pressure",      # For pressure
                    "visibility"             # For visibility
                ]
            }
            
            response = requests.get(f"{self.BASE_URL}forecast", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Format the data to match our standard format
            current = data.get("current_weather", {})
            current_units = data.get("current_units", {})
            current_data = data.get("current", {})
            
            location_name = self._reverse_geocode(coords["latitude"], coords["longitude"])
            
            # Extract additional weather data
            feels_like = current_data.get("apparent_temperature")
            humidity = current_data.get("relative_humidity_2m")
            pressure = current_data.get("surface_pressure")
            visibility = current_data.get("visibility")
            
            # Convert units if needed
            if pressure is not None and current_units.get("surface_pressure") == "hPa":
                pressure = round(float(pressure), 1)  # Round to 1 decimal place
                
            if visibility is not None and current_units.get("visibility") == "m":
                # Convert meters to kilometers for metric, or miles for imperial
                if self.units == "metric":
                    visibility = round(float(visibility) / 1000, 1)  # Convert to km
                else:
                    visibility = round(float(visibility) * 0.000621371, 1)  # Convert to miles
            
            weather_data = {
                "location": location_name or location,
                "temperature": current.get("temperature"),
                "feels_like": feels_like,
                "description": self._get_weather_description(current.get("weathercode")),
                "icon": self._get_weather_icon(current.get("weathercode")),
                "humidity": humidity,
                "wind_speed": current.get("windspeed"),
                "wind_direction": current.get("winddirection"),
                "pressure": pressure,
                "visibility": visibility,
                "clouds": None,  # Not available in the free API
                "sunrise": None,  # Available in daily forecast
                "sunset": None,  # Available in daily forecast
                "timestamp": datetime.fromisoformat(current.get("time")),
                "coordinates": coords,
                "source": "Open-Meteo.com"
            }
            
            # Add to history
            self._add_to_history(weather_data)
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return {"error": str(e)}
    
    def get_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a location.
        
        Args:
            location: City name or coordinates (lat,lon)
            days: Number of days to forecast (1-16)
            
        Returns:
            Dictionary containing forecast data
        """
        try:
            # First get coordinates for the location
            coords = self._geocode(location)
            if not coords:
                return {"error": f"Could not find location: {location}"}
                
            # Get forecast
            params = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "daily": [
                    "weathercode", "temperature_2m_max", "temperature_2m_min",
                    "apparent_temperature_max", "apparent_temperature_min",
                    "sunrise", "sunset", "precipitation_sum", "windspeed_10m_max"
                ],
                "temperature_unit": "celsius" if self.units == "metric" else "fahrenheit",
                "windspeed_unit": "kmh" if self.units == "metric" else "mph",
                "precipitation_unit": "mm",
                "timezone": "auto",
                "forecast_days": min(max(days, 1), 16)  # Clamp between 1-16 days
            }
            
            response = requests.get(f"{self.BASE_URL}forecast", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Format the forecast data
            daily = data.get("daily", {})
            forecast_days = []
            
            for i in range(len(daily.get("time", []))):
                day = {
                    "date": daily["time"][i],
                    "temp_max": daily["temperature_2m_max"][i],
                    "temp_min": daily["temperature_2m_min"][i],
                    "feels_like_max": daily["apparent_temperature_max"][i],
                    "feels_like_min": daily["apparent_temperature_min"][i],
                    "weather_code": daily["weathercode"][i],
                    "description": self._get_weather_description(daily["weathercode"][i]),
                    "icon": self._get_weather_icon(daily["weathercode"][i]),
                    "precipitation": daily["precipitation_sum"][i],
                    "wind_speed": daily["windspeed_10m_max"][i],
                    "sunrise": daily["sunrise"][i],
                    "sunset": daily["sunset"][i]
                }
                forecast_days.append(day)
            
            return {
                "location": self._reverse_geocode(coords["latitude"], coords["longitude"]) or location,
                "days": forecast_days,
                "coordinates": coords,
                "source": "Open-Meteo.com"
            }
            
        except Exception as e:
            logger.error(f"Error getting forecast: {e}")
            return {"error": str(e)}
    
    def get_historical_weather(self, location: str, date: str) -> Dict[str, Any]:
        """Get historical weather data for a location and date.
        
        Args:
            location: City name or coordinates (lat,lon)
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing historical weather data
        """
        try:
            # First get coordinates for the location
            coords = self._geocode(location)
            if not coords:
                return {"error": f"Could not find location: {location}"}
                
            # Check if date is in the future or too far in the past
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            today = datetime.utcnow().date()
            
            if target_date > today:
                return {"error": "Cannot get historical data for future dates"}
                
            if (today - target_date).days > 365 * 10:  # Limit to 10 years
                return {"error": "Historical data only available for the past 10 years"}
            
            # Get historical data
            params = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "start_date": date,
                "end_date": date,
                "hourly": ["temperature_2m", "weathercode", "windspeed_10m", "precipitation"],
                "temperature_unit": "celsius" if self.units == "metric" else "fahrenheit",
                "windspeed_unit": "kmh" if self.units == "metric" else "mph",
                "precipitation_unit": "mm",
                "timezone": "auto"
            }
            
            response = requests.get(f"{self.BASE_URL}archive", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Calculate daily aggregates
            hourly = data.get("hourly", {})
            if not hourly.get("time"):
                return {"error": f"No historical data available for {date}"}
                
            temps = hourly.get("temperature_2m", [])
            weather_codes = hourly.get("weathercode", [])
            
            if not temps or not weather_codes:
                return {"error": "Incomplete historical data"}
            
            # Get most common weather code for the day
            from collections import Counter
            most_common_code = Counter(weather_codes).most_common(1)[0][0]
            
            historical_data = {
                "location": self._reverse_geocode(coords["latitude"], coords["longitude"]) or location,
                "date": date,
                "temperature_avg": sum(temps) / len(temps) if temps else None,
                "temperature_max": max(temps) if temps else None,
                "temperature_min": min(temps) if temps else None,
                "weather_code": most_common_code,
                "description": self._get_weather_description(most_common_code),
                "icon": self._get_weather_icon(most_common_code),
                "precipitation": sum(hourly.get("precipitation", [0])),
                "wind_speed_avg": sum(hourly.get("windspeed_10m", [0])) / len(hourly.get("windspeed_10m", [1])),
                "coordinates": coords,
                "source": "Open-Meteo.com (Historical)"
            }
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical weather: {e}")
            return {"error": str(e)}
    
    def _geocode(self, location: str) -> Optional[Dict[str, float]]:
        """Convert location name to coordinates using Open-Meteo geocoding."""
        if not location:
            return None
            
        # Check if location is already in coordinates format (lat,lon)
        if "," in location:
            try:
                lat, lon = map(float, location.split(","))
                return {"latitude": lat, "longitude": lon}
            except (ValueError, IndexError):
                pass
                
        # Try to geocode the location name
        try:
            params = {
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json"
            }
            
            response = requests.get("https://geocoding-api.open-meteo.com/v1/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                return {
                    "latitude": result.get("latitude"),
                    "longitude": result.get("longitude"),
                    "name": result.get("name"),
                    "admin1": result.get("admin1"),
                    "country": result.get("country")
                }
                
        except Exception as e:
            logger.error(f"Geocoding error for {location}: {e}")
            
        return None
    
    def _reverse_geocode(self, lat: float, lon: float) -> str:
        """Convert coordinates to location name using OpenStreetMap Nominatim as fallback.
        
        Note: According to Nominatim's usage policy, you must include a custom user agent
        and respect their usage limits (max 1 request per second).
        """
        # First try OpenStreetMap Nominatim as it's more reliable for reverse geocoding
        try:
            # Create a proper user agent that identifies your application
            headers = {
                'User-Agent': 'WeatherApp/1.0 (https://github.com/Nsfr750/weather; nsfr750@yandex.com)'
            }
            
            response = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    'lat': lat,
                    'lon': lon,
                    'format': 'jsonv2',  # Use v2 of the API
                    'accept-language': 'en',
                    'zoom': 10,  # Get more detailed location info
                    'addressdetails': 1
                },
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract location name from the response
            if 'display_name' in data:
                return data['display_name']
                
            # Fallback to address components if display_name is not available
            address = data.get('address', {})
            location_parts = []
            for key in ['city', 'town', 'village', 'hamlet', 'municipality', 'county', 'state', 'country']:
                if key in address:
                    location_parts.append(address[key])
            
            if location_parts:
                return ', '.join(location_parts[:3])  # Return up to 3 most specific parts
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.warning(self.language_manager.tr("nominatim_rate_limit_exceeded"))
            else:
                logger.warning(self.language_manager.tr("nominatim_reverse_geocoding_failed").format(lat=lat, lon=lon, error=str(e)))
        except Exception as e:
            logger.warning(self.language_manager.tr("reverse_geocoding_error").format(lat=lat, lon=lon, error=str(e)))
        
        # Fallback to just showing coordinates
        return f"{lat:.4f}, {lon:.4f}"
    
    def _init_weather_descriptions(self) -> None:
        """Initialize weather code translations."""
        # WMO Weather interpretation codes (WW) with translation keys
        self.weather_code_keys = {
            0: "weather_clear_sky",
            1: "weather_mainly_clear",
            2: "weather_partly_cloudy",
            3: "weather_overcast",
            45: "weather_fog",
            48: "weather_depositing_rime_fog",
            51: "weather_light_drizzle",
            53: "weather_moderate_drizzle",
            55: "weather_dense_drizzle",
            56: "weather_light_freezing_drizzle",
            57: "weather_dense_freezing_drizzle",
            61: "weather_slight_rain",
            63: "weather_moderate_rain",
            65: "weather_heavy_rain",
            66: "weather_light_freezing_rain",
            67: "weather_heavy_freezing_rain",
            71: "weather_slight_snow_fall",
            73: "weather_moderate_snow_fall",
            75: "weather_heavy_snow_fall",
            77: "weather_snow_grains",
            80: "weather_slight_rain_showers",
            81: "weather_moderate_rain_showers",
            82: "weather_violent_rain_showers",
            85: "weather_slight_snow_showers",
            86: "weather_heavy_snow_showers",
            95: "weather_thunderstorm",
            96: "weather_thunderstorm_slight_hail",
            99: "weather_thunderstorm_heavy_hail"
        }
        
        # Default English translations
        self.default_weather_descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
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
        
        # We'll use default descriptions if translations aren't available
        # The actual translations should be added to the language files
        pass
    
    def _get_weather_description(self, code: int) -> str:
        """Convert weather code to description."""
        if code not in self.weather_code_keys:
            return self.default_weather_descriptions.get(code, "Unknown weather")
            
        key = self.weather_code_keys[code]
        translated = self.language_manager.tr(key)
        
        # If translation not found, return the default description
        if translated == key and code in self.default_weather_descriptions:
            return self.default_weather_descriptions[code]
            
        return translated
    
    def _get_weather_icon(self, code: int) -> str:
        """Convert weather code to icon name."""
        # Map weather codes to icon names
        icon_map = {
            # Clear
            0: "01d",
            # Mainly clear, partly cloudy, and overcast
            1: "02d", 2: "03d", 3: "04d",
            # Fog and fog depositing rime
            45: "50d", 48: "50d",
            # Drizzle
            51: "09d", 53: "09d", 55: "09d",
            56: "13d", 57: "13d",  # Freezing drizzle
            # Rain
            61: "10d", 63: "10d", 65: "10d",
            66: "13d", 67: "13d",  # Freezing rain
            # Snow fall
            71: "13d", 73: "13d", 75: "13d", 77: "13d",
            # Rain showers
            80: "09d", 81: "09d", 82: "09d",
            # Snow showers
            85: "13d", 86: "13d",
            # Thunderstorm
            95: "11d", 96: "11d", 99: "11d"
        }
        return icon_map.get(code, "01d")
    
    def _add_to_history(self, weather_data: Dict[str, Any]) -> None:
        """Add weather data to history."""
        if not weather_data or "error" in weather_data:
            return
            
        # Add timestamp if not present
        if "timestamp" not in weather_data:
            weather_data["timestamp"] = datetime.utcnow()
            
        # Add to history
        self.history.insert(0, weather_data)
        
        # Trim history to max size
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get weather query history."""
        return self.history
    
    def clear_history(self) -> None:
        """Clear weather query history."""
        self.history = []
    
    def set_units(self, units: str) -> None:
        """Set the units system.
        
        Args:
            units: Units system to use (metric or imperial)
        """
        if units in ["metric", "imperial"]:
            self.units = units
            logger.info(f"Units set to: {units}")
        else:
            logger.warning(self.language_manager.tr("invalid_units").format(units=units))
