"""
Example Weather Provider Plugin

This is an example plugin that demonstrates the plugin configuration system.
"""
import logging
from typing import Dict, Any, Optional

from script.plugin_system.plugin_manager import BasePlugin

logger = logging.getLogger(__name__)

class ExampleWeatherProvider(BasePlugin):
    """An example weather provider plugin with configurable settings."""
    
    # Plugin metadata
    name = "Example Plugin"
    author = "Nsfr750"
    version = "1.0.0"
    description = "An example weather provider plugin with configurable settings."
    
    # Configuration schema
    config_schema = {
        'api_key': {
            'type': str,
            'label': 'API Key',
            'description': 'Your API key for the example weather service',
            'default': 'demo_key'
        },
        'units': {
            'type': str,
            'label': 'Units',
            'description': 'Temperature units to use',
            'default': 'metric',
            'options': [
                ('metric', 'Metric (°C)'),
                ('imperial', 'Imperial (°F)')
            ]
        },
        'update_interval': {
            'type': int,
            'label': 'Update Interval (minutes)',
            'description': 'How often to update weather data',
            'default': 30,
            'min': 5,
            'max': 1440  # 24 hours
        },
        'enable_alerts': {
            'type': bool,
            'label': 'Enable Weather Alerts',
            'description': 'Enable severe weather alerts',
            'default': True
        },
        'location_override': {
            'type': str,
            'label': 'Location Override',
            'description': 'Override location for testing (leave empty to use app location)',
            'default': '',
            'required': False
        }
    }
    
    def __init__(self):
        """Initialize the example weather provider plugin."""
        super().__init__()
        
        # Initialize with default values
        self.units = 'metric'
        self.language = 'en'
        self.offline_mode = False
        self.initialized = False
        self.app = None
        
    def _apply_config(self):
        """Apply configuration from the plugin's config."""
        if not hasattr(self, '_config'):
            self._config = {}
            
        # Apply configuration
        self.units = self._config.get('units', 'metric')
        self.language = self._config.get('language', 'en')
        self.offline_mode = self._config.get('offline_mode', False)
    
    def initialize(self, app: Any = None) -> bool:
        """Initialize the plugin.
        
        Args:
            app: Reference to the main application (optional)
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.app = app
        
        try:
            # Apply configuration
            self._apply_config()
            
            if self.offline_mode:
                logger.info(f"{self.name} running in offline mode")
                
            logger.info(f"Successfully initialized {self.name}")
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing {self.name}: {e}", exc_info=True)
            self.initialized = False
            return False
    
    def get_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """Get current weather for a location."""
        if not self.initialized:
            logger.error("Plugin not initialized")
            return None
            
        try:
            # Use location override if set
            location_to_use = self.config.get('location_override') or location
            
            # In a real plugin, you would make an API call here
            # This is just an example that returns dummy data
            return {
                'location': location_to_use,
                'temperature': 22.5 if self.config.get('units') == 'metric' else 72.5,
                'condition': 'sunny',
                'humidity': 65,
                'wind_speed': 12.3,
                'wind_direction': 'NW',
                'provider': self.name,
                'timestamp': '2023-01-01T12:00:00Z'  # In a real plugin, use current time
            }
            
        except Exception as e:
            logger.error(f"Error getting weather: {e}", exc_info=True)
            return None
    
    def on_config_changed(self, new_config: Dict[str, Any]) -> None:
        """Handle configuration changes."""
        # Call parent to update the config
        super().on_config_changed(new_config)
        
        # Apply any runtime changes needed
        logger.info(f"Configuration updated: {self.config}")
        
        # In a real plugin, you might want to restart any background tasks
        # or update API clients with new settings here
        if 'api_key' in new_config:
            logger.info("API key was updated")
            # Reinitialize API client with new key if needed
            # self._init_api_client()
    
    def cleanup(self) -> None:
        """Clean up resources used by the plugin."""
        logger.info(f"Cleaning up {self.name}")
        # Clean up any resources like timers, threads, etc.
        self.initialized = False

# Plugin entry point
def create_plugin() -> ExampleWeatherProvider:
    """Create an instance of the plugin."""
    return ExampleWeatherProvider()
