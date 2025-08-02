"""
history.py
Handles storage and retrieval of historical weather data.
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
import pytz

# Configure logging
logger = logging.getLogger(__name__)

# Set feature metadata
PLUGIN_NAME = "history"
PLUGIN_DISPLAY_NAME = "History"
PLUGIN_DESCRIPTION = "Provides weather data history"
PLUGIN_AUTHOR = "Nsfr750"
PLUGIN_VERSION = "1.0.0"

@dataclass
class HistoricalWeatherData:
    """Data class for storing historical weather data."""
    timestamp: str
    location: str
    temperature: float
    condition: str
    humidity: float
    wind_speed: float
    wind_direction: float
    pressure: float
    visibility: Optional[float] = None
    icon: Optional[str] = None
    provider: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert historical weather data to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoricalWeatherData':
        """Create HistoricalWeatherData from dictionary."""
        return cls(**data)


class WeatherHistoryManager:
    """Manages storage and retrieval of historical weather data."""
    
    def __init__(self, data_dir: Optional[Path] = None, max_entries: int = 1000):
        """Initialize the weather history manager.
        
        Args:
            data_dir: Directory to store history data. Defaults to ~/.weather_app/history.
            max_entries: Maximum number of entries to keep in history.
        """
        self.max_entries = max_entries
        
        # Set up data directory
        if data_dir is None:
            self.data_dir = Path.home() / '.weather_app' / 'history'
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache of historical data
        self._history: Dict[str, List[HistoricalWeatherData]] = {}
        
        # Load existing data
        self._load_history()
    
    def _get_history_file(self) -> Path:
        """Get the path to the history file."""
        return self.data_dir / 'weather_history.json'
    
    def _load_history(self) -> None:
        """Load historical weather data from disk."""
        history_file = self._get_history_file()
        if not history_file.exists():
            self._history = {}
            return
            
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Convert the loaded data back to HistoricalWeatherData objects
            self._history = {}
            for location, entries in data.items():
                self._history[location] = [
                    HistoricalWeatherData.from_dict(entry) 
                    for entry in entries
                ]
                
            logger.info(f"Loaded weather history for {len(self._history)} locations")
            
        except Exception as e:
            logger.error(f"Error loading weather history: {e}")
            self._history = {}
    
    def _save_history(self) -> None:
        """Save historical weather data to disk."""
        try:
            # Ensure directory exists
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert HistoricalWeatherData objects to dictionaries
            data_to_save = {
                location: [entry.to_dict() for entry in entries]
                for location, entries in self._history.items()
            }
            
            # Save to file
            with open(self._get_history_file(), 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving weather history: {e}")
    
    def add_weather_data(
        self, 
        location: str, 
        weather_data: Union[Dict[str, Any], 'WeatherData'],
        provider: str = "unknown"
    ) -> None:
        """Add weather data to the history.
        
        Args:
            location: Location name or identifier
            weather_data: Weather data to add (either dict or WeatherData instance)
            provider: Name of the weather provider
        """
        try:
            # Convert to HistoricalWeatherData
            if isinstance(weather_data, dict):
                entry = HistoricalWeatherData(
                    timestamp=datetime.utcnow().isoformat(),
                    location=location,
                    temperature=weather_data.get('temperature', 0),
                    condition=weather_data.get('condition', 'unknown'),
                    humidity=weather_data.get('humidity', 0),
                    wind_speed=weather_data.get('wind_speed', 0),
                    wind_direction=weather_data.get('wind_direction', 0),
                    pressure=weather_data.get('pressure', 0),
                    visibility=weather_data.get('visibility'),
                    icon=weather_data.get('icon'),
                    provider=provider,
                    metadata={
                        'source': 'manual',
                        **weather_data.get('metadata', {})
                    }
                )
            else:
                # Assume it's a WeatherData instance
                entry = HistoricalWeatherData(
                    timestamp=datetime.utcnow().isoformat(),
                    location=location,
                    temperature=weather_data.temperature,
                    condition=weather_data.condition,
                    humidity=weather_data.humidity,
                    wind_speed=weather_data.wind_speed,
                    wind_direction=getattr(weather_data, 'wind_direction', 0),
                    pressure=weather_data.pressure,
                    visibility=getattr(weather_data, 'visibility', None),
                    icon=getattr(weather_data, 'icon', None),
                    provider=provider,
                    metadata={
                        'source': 'api',
                        **getattr(weather_data, 'metadata', {})
                    }
                )
            
            # Add to in-memory cache
            if location not in self._history:
                self._history[location] = []
            
            self._history[location].append(entry)
            
            # Keep only the most recent entries
            if len(self._history[location]) > self.max_entries:
                self._history[location] = self._history[location][-self.max_entries:]
            
            # Save to disk
            self._save_history()
            
        except Exception as e:
            logger.error(f"Error adding weather data to history: {e}")
    
    def get_weather_history(
        self, 
        location: str, 
        days_back: int = 7,
        limit: Optional[int] = None
    ) -> List[HistoricalWeatherData]:
        """Get historical weather data for a location.
        
        Args:
            location: Location name or identifier
            days_back: Number of days of history to retrieve
            limit: Maximum number of entries to return (None for no limit)
            
        Returns:
            List of HistoricalWeatherData objects, most recent first
        """
        if location not in self._history:
            return []
        
        # Filter by date if needed
        if days_back > 0:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            history = [
                entry for entry in self._history[location]
                if datetime.fromisoformat(entry.timestamp) >= cutoff_date
            ]
        else:
            history = self._history[location].copy()
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            history = history[-limit:]
        
        # Return most recent first
        return sorted(history, key=lambda x: x.timestamp, reverse=True)
    
    def clear_history(self, location: Optional[str] = None) -> None:
        """Clear weather history for a specific location or all locations.
        
        Args:
            location: Location to clear history for. If None, clears all history.
        """
        if location is None:
            self._history = {}
        elif location in self._history:
            del self._history[location]
        
        # Save changes to disk
        self._save_history()
        
        logger.info(f"Cleared weather history for location: {location or 'all'}")
    
    def get_locations(self) -> List[str]:
        """Get a list of all locations with history data.
        
        Returns:
            List of location names
        """
        return list(self._history.keys())
