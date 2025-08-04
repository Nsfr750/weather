"""
History Manager for Weather Application

This module provides functionality to manage the search history,
including saving to and loading from a JSON file.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Import language manager
from lang.language_manager import LanguageManager

# Default history file path
HISTORY_FILE = Path("config/history.json")

class HistoryManager:
    """Manages the search history for the Weather application."""
    
    def __init__(self, history_file: Optional[Path] = None):
        """Initialize the HistoryManager.
        
        Args:
            history_file: Optional path to the history file. If not provided,
                        uses the default location.
        """
        self.history_file = history_file or HISTORY_FILE
        self.history: List[Dict[str, Any]] = []
        self.max_entries = 20  # Maximum number of history entries to keep
        self._ensure_history_file()
        self.load_history()
    
    def _ensure_history_file(self) -> None:
        """Ensure the history file and its directory exist."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.history_file.exists():
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2)
        except Exception as e:
            logger.error(f"Error ensuring history file exists: {e}")
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load the search history from the history file.
        
        Returns:
            List of history entries, each containing location, temperature, and timestamp.
        """
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                    # Ensure we have a list
                    if not isinstance(self.history, list):
                        logger.warning("History file corrupted, resetting to empty list")
                        self.history = []
            return self.history
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            self.history = []
            return []
    
    def save_history(self) -> bool:
        """Save the current history to the history file.
        
        Returns:
            bool: True if save was successful, False otherwise.
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error saving history: {e}")
            return False
    
    def add_entry(
        self, 
        location: str, 
        temperature: float, 
        timestamp: Optional[datetime] = None,
        feels_like: Optional[float] = None,
        humidity: Optional[float] = None,
        wind_speed: Optional[float] = None,
        pressure: Optional[float] = None,
        visibility: Optional[float] = None
    ) -> None:
        """Add a new entry to the history.
        
        Args:
            location: The location that was searched for.
            temperature: The temperature at that location.
            timestamp: Optional timestamp. If not provided, uses current time.
            feels_like: Optional. The 'feels like' temperature.
            humidity: Optional. The humidity percentage.
            wind_speed: Optional. The wind speed.
            pressure: Optional. The atmospheric pressure.
            visibility: Optional. The visibility distance.
        """
        entry = {
            'location': location,
            'temperature': temperature,
            'timestamp': timestamp or datetime.now(),
            'feels_like': feels_like,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'pressure': pressure,
            'visibility': visibility
        }
        
        # Add to beginning of history (most recent first)
        self.history.insert(0, entry)
        
        # Trim history to max_entries
        if len(self.history) > self.max_entries:
            self.history = self.history[:self.max_entries]
        
        # Save to file
        self.save_history()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the current search history.
        
        Returns:
            List of history entries, most recent first.
        """
        return self.history.copy()
    
    def clear_history(self) -> bool:
        """Clear the search history.
        
        Returns:
            bool: True if clear was successful, False otherwise.
        """
        self.history = []
        return self.save_history()

# Singleton instance
history_manager = HistoryManager()
