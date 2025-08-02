# Weather App Plugin System

This document provides a comprehensive guide to the Weather App's plugin system, which allows for extending the application with new weather providers and features.

## Table of Contents

1. [Overview](#overview)
2. [Plugin Types](#plugin-types)
   - [Weather Provider Plugins](#weather-provider-plugins)
   - [Feature Plugins](#feature-plugins)
3. [Creating a Weather Provider Plugin](#creating-a-weather-provider-plugin)
   - [Plugin Class](#plugin-class)
   - [Provider Class](#provider-class)
   - [Example Implementation](#example-implementation)
4. [Creating a Feature Plugin](#creating-a-feature-plugin)
5. [Plugin Discovery and Loading](#plugin-discovery-and-loading)
6. [Testing Your Plugin](#testing-your-plugin)
7. [Best Practices](#best-practices)
8. [Legacy Provider Migration](#legacy-provider-migration)

## Overview

The Weather App's plugin system is designed to be modular and extensible. It allows developers to:

- Add support for new weather data providers
- Extend the application with new features
- Customize the behavior of existing components
- Maintain backward compatibility with legacy providers

## Plugin Types

### Weather Provider Plugins

Weather Provider plugins implement the `BaseWeatherProvider` interface and are responsible for:
- Fetching current weather data
- Retrieving weather forecasts
- Converting provider-specific data to a standardized format
- Handling provider-specific authentication

### Feature Plugins

Feature plugins implement the `BaseFeaturePlugin` interface and can:
- Add new UI elements
- Register custom commands
- Extend existing functionality
- Integrate with external services

## Creating a Weather Provider Plugin

### Plugin Class

Every weather provider must have a plugin class that:
1. Provides metadata (name, version, author, etc.)
2. Implements the `get_weather_provider()` method
3. Defines a settings schema for configuration

### Provider Class

The provider class must inherit from `BaseWeatherProvider` and implement:
- `get_current_weather(location: str) -> WeatherDataPoint`
- `get_forecast(location: str, days: int = 5) -> WeatherForecast`

### Example Implementation

```python
# my_weather_plugin.py
from script.plugin_system import BaseWeatherProvider, WeatherDataPoint, WeatherForecast

class MyWeatherProvider(BaseWeatherProvider):
    """My custom weather provider implementation."""
    
    name = "myprovider"
    display_name = "My Weather Provider"
    
    # Settings schema
    settings_schema = {
        "api_key": {
            "type": "string",
            "required": True,
            "secret": True,
            "display_name": "API Key",
            "description": "Your API key for My Weather Provider"
        }
    }
    
    async def get_current_weather(self, location: str) -> WeatherDataPoint:
        # Implementation here
        pass
        
    async def get_forecast(self, location: str, days: int = 5) -> WeatherForecast:
        # Implementation here
        pass

class MyWeatherPlugin:
    """Plugin class for My Weather Provider."""
    
    def __init__(self):
        self.name = "myprovider"
        self.display_name = "My Weather Provider"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "Provides weather data from My Weather Service"
    
    def get_weather_provider(self, **kwargs):
        return MyWeatherProvider(**kwargs)
    
    def get_settings_schema(self):
        return MyWeatherProvider.settings_schema
```

## Creating a Feature Plugin

Feature plugins can add new functionality to the application. Here's a basic example:

```python
# my_feature_plugin.py
from script.plugin_system import BaseFeaturePlugin

class MyFeaturePlugin(BaseFeaturePlugin):
    """My custom feature plugin."""
    
    def __init__(self):
        self.name = "myfeature"
        self.display_name = "My Feature"
        self.version = "1.0.0"
    
    def initialize(self, app):
        """Initialize the plugin with the main application instance."""
        self.app = app
        # Register commands, add menu items, etc.
        
    def on_enable(self):
        """Called when the plugin is enabled."""
        pass
        
    def on_disable(self):
        """Called when the plugin is disabled."""
        pass
```

## Plugin Discovery and Loading

Plugins are automatically discovered from the following locations:
1. `script/plugin_system/plugins/` - Built-in plugins
2. `~/.weather_app/plugins/` - User-installed plugins

## Testing Your Plugin

Use the provided test script to verify your plugin works correctly:

```bash
python test_plugin_system.py
```

## Best Practices

1. **Error Handling**: Always implement proper error handling and provide meaningful error messages.
2. **Rate Limiting**: Respect API rate limits and implement appropriate backoff strategies.
3. **Caching**: Cache API responses when possible to reduce network traffic.
4. **Settings**: Use the settings schema to make your plugin configurable.
5. **Logging**: Use the standard logging module for debugging and error tracking.

## Legacy Provider Migration

If you're migrating from the legacy provider system, you can use the compatibility layer:

```python
from script.plugin_system.legacy_compat import create_legacy_plugin_wrapper

# Wrap a legacy provider class
LegacyPlugin = create_legacy_plugin_wrapper(MyLegacyProvider)

# Register the legacy provider
from script.plugin_system import register_legacy_providers
register_legacy_providers({'myprovider': MyLegacyProvider})
```

For more information, see the source code and examples in the `script/plugin_system/` directory.
