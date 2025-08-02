"""
Example Feature Plugin

This module demonstrates how to create custom feature plugins for the Weather Application.
It includes examples of different types of features you might want to implement.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

# Set up logging
logger = logging.getLogger(__name__)

# Set feature metadata
PLUGIN_NAME = "example_features"
PLUGIN_DISPLAY_NAME = "Example Features"
PLUGIN_DESCRIPTION = "Example feature plugin for the Weather Application"
PLUGIN_AUTHOR = "Nsfr750"
PLUGIN_VERSION = "1.0.0"

class ExampleFeatureManager:
    """
    Example feature manager that demonstrates various plugin capabilities.
    
    This class can be used as a template for creating new feature plugins.
    It shows how to implement common patterns like configuration, data storage,
    and event handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the example feature manager.
        
        Args:
            config: Optional configuration dictionary
        """
        # Default configuration
        self.config = {
            'enabled': True,
            'max_items': 100,
            'retention_days': 30,
            'notify_enabled': False,
            'custom_setting': 'default_value'
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        # Initialize data storage
        self._data: Dict[str, Any] = {}
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the feature.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if not self.config.get('enabled', True):
            logger.info("Example feature is disabled in configuration")
            return False
            
        try:
            # Initialize any resources here
            self._data = {}
            self._initialized = True
            logger.info("Example feature initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize example feature: {e}")
            self._initialized = False
            return False
    
    def cleanup(self) -> None:
        """Clean up resources used by the feature."""
        self._data.clear()
        self._initialized = False
        logger.info("Example feature cleaned up")
    
    def process_weather_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process weather data and return enhanced data.
        
        Args:
            weather_data: Dictionary containing weather data
            
        Returns:
            Enhanced weather data with additional information
        """
        if not self._initialized:
            logger.warning("Cannot process data: feature not initialized")
            return weather_data
            
        try:
            # Example: Add a greeting based on temperature
            temp = weather_data.get('temperature', 0)
            if temp > 25:
                weather_data['greeting'] = "It's a hot day!"
            elif temp > 15:
                weather_data['greeting'] = "Pleasant weather today!"
            else:
                weather_data['greeting'] = "It's a bit chilly out there!"
                
            # Example: Add a timestamp
            weather_data['processed_at'] = datetime.utcnow().isoformat()
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return weather_data
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate statistics for the given number of days.
        
        Args:
            days: Number of days to include in statistics
            
        Returns:
            Dictionary containing statistics
        """
        if not self._initialized:
            logger.warning("Cannot get statistics: feature not initialized")
            return {}
            
        try:
            # This is a placeholder - in a real implementation, you would
            # calculate actual statistics from stored data
            return {
                'period_days': days,
                'data_points': len(self._data),
                'average_temperature': 20.5,  # Example value
                'max_temperature': 28.0,     # Example value
                'min_temperature': 15.0,     # Example value
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            return {}
    
    def handle_event(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """
        Handle application events.
        
        Args:
            event_name: Name of the event
            event_data: Data associated with the event
        """
        if not self._initialized:
            return
            
        try:
            logger.debug(f"Received event: {event_name}")
            
            # Example: Handle specific events
            if event_name == 'weather_updated':
                location = event_data.get('location', 'unknown')
                logger.info(f"Weather updated for {location}")
                
            elif event_name == 'application_started':
                logger.info("Application started, initializing feature")
                
            elif event_name == 'application_shutdown':
                logger.info("Application shutting down, cleaning up")
                self.cleanup()
                
        except Exception as e:
            logger.error(f"Error handling event {event_name}: {e}")


# Example of how to use the feature manager
if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create an instance with default configuration
    feature = ExampleFeatureManager()
    
    # Initialize the feature
    if feature.initialize():
        # Example usage
        sample_weather = {
            'location': 'Example City',
            'temperature': 22.5,
            'condition': 'sunny',
            'humidity': 65
        }
        
        # Process some weather data
        enhanced_data = feature.process_weather_data(sample_weather)
        print(f"Enhanced weather data: {enhanced_data}")
        
        # Get some statistics
        stats = feature.get_statistics(days=7)
        print(f"Statistics: {stats}")
        
        # Handle some events
        feature.handle_event('weather_updated', {'location': 'Example City'})
        
        # Clean up
        feature.cleanup()
