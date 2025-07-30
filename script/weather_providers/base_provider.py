"""
Base class for weather data providers.
All weather data providers should inherit from this class.
"""

class WeatherProvider:
    """Base class for all weather data providers."""
    
    def __init__(self, api_key=None, units='metric', language='en'):
        """Initialize the weather provider.
        
        Args:
            api_key (str): API key for the weather service
            units (str): Units for measurements ('metric' or 'imperial')
            language (str): Language for weather descriptions
        """
        self.api_key = api_key
        self.units = units
        self.language = language
        self.name = "Base Provider"
    
    def get_current_weather(self, location):
        """Get current weather for a location.
        
        Args:
            location (str): City name or coordinates (lat,lon)
            
        Returns:
            dict: Weather data in a standardized format
        """
        raise NotImplementedError("Subclasses must implement get_current_weather")
    
    def get_forecast(self, location, days=5):
        """Get weather forecast for a location.
        
        Args:
            location (str): City name or coordinates (lat,lon)
            days (int): Number of forecast days (max depends on provider)
            
        Returns:
            dict: Forecast data in a standardized format
        """
        raise NotImplementedError("Subclasses must implement get_forecast")
    
    def get_alerts(self, location):
        """Get weather alerts for a location.
        
        Args:
            location (str): City name or coordinates (lat,lon)
            
        Returns:
            list: List of alerts in a standardized format
        """
        raise NotImplementedError("Subclasses must implement get_alerts")
    
    def update_config(self, api_key=None, units=None, language=None):
        """Update provider configuration.
        
        Args:
            api_key (str, optional): New API key
            units (str, optional): New units ('metric' or 'imperial')
            language (str, optional): New language code
        """
        if api_key is not None:
            self.api_key = api_key
        if units is not None:
            self.units = units
        if language is not None:
            self.language = language
    
    def validate_api_key(self, api_key):
        """Validate the API key.
        
        Args:
            api_key (str): API key to validate
            
        Returns:
            tuple: (is_valid, message)
        """
        raise NotImplementedError("Subclasses must implement validate_api_key")
