# Configuration Guide

## Overview

The Weather App can be configured through the Settings dialog, environment variables, or by manually editing the configuration file. This guide covers all available configuration options.

## Settings Dialog

Access the Settings dialog by clicking the gear icon (⚙️) or navigating to Menu > Settings.

### General Tab

- **Language**: Select the application language (supports 20+ languages)
- **Theme**: Choose between Light, Dark, or System theme
- **Units**: Toggle between Metric and Imperial units
- **Start Minimized**: Launch the app in the system tray
- **Check for Updates**: Enable/disable automatic update checks
- **Auto-Refresh**: Set automatic refresh interval (5-60 minutes)
- **Location Services**: Enable/disable automatic location detection

### Weather Providers

- **Active Provider**: Select your preferred weather data source
- **Provider Settings**: Configure API keys and options for each provider
- **Fallback Order**: Set the order of fallback providers
- **Cache Duration**: Set how long to cache weather data (5-60 minutes)

### Display

- **Show Alerts**: Toggle weather alerts display
- **Animations**: Enable/disable UI animations
- **Font Size**: Adjust the base font size (10-24px)
- **Compact Mode**: Enable compact view for smaller screens
- **Show Details**: Toggle detailed weather information

## Configuration File

Advanced users can directly edit the configuration file located at:
- **Windows**: `%APPDATA%\WeatherApp\config.ini`
- **macOS**: `~/Library/Application Support/WeatherApp/config.ini`
- **Linux**: `~/.config/WeatherApp/config.ini`

### Example Configuration

```ini
[General]
language = en
theme = dark
units = metric
start_minimized = false
check_updates = true
auto_refresh = 15
location_services = true

[UI]
show_alerts = true
animations = true
font_size = 12
compact_mode = false
show_details = true

[OpenWeatherMap]
enabled = true
api_key = your_api_key_here
units = metric
language = en

[OpenMeteo]
enabled = true
api_key = your_api_key_here
units = metric
language = en

[Cache]
enabled = true
duration = 30  # minutes
max_size = 100  # MB

[Logging]
level = INFO
max_size = 10  # MB
backup_count = 3
```

## Environment Variables

You can override configuration settings using environment variables. These take precedence over the configuration file.

### General
- `WEATHER_APP_CONFIG_DIR`: Override the configuration directory
- `WEATHER_APP_CACHE_DIR`: Set a custom cache directory
- `WEATHER_APP_LOG_LEVEL`: Set the log level (DEBUG, INFO, WARNING, ERROR)
- `WEATHER_APP_LANGUAGE`: Set the default language (e.g., en, es, fr)
- `WEATHER_APP_THEME`: Set the default theme (light, dark, system)
- `WEATHER_APP_UNITS`: Set the default units (metric, imperial)

### Provider-Specific
- `OPENWEATHERMAP_API_KEY`: API key for OpenWeatherMap
- `OPENMETEO_API_KEY`: API key for OpenMeteo
- `WEATHERAPI_API_KEY`: API key for WeatherAPI.com

### Development
- `WEATHER_APP_DEBUG`: Enable debug mode (true/false)
- `WEATHER_APP_DEVELOPER_MODE`: Enable developer features
- `WEATHER_APP_NO_UPDATE_CHECK`: Disable update checking

## Command Line Arguments

Run the application with these command line arguments:

```bash
# Specify a configuration file
python -m script.main --config /path/to/config.ini

# Set log level
python -m script.main --log-level DEBUG

# Run in portable mode (stores data in the application directory)
python -m script.main --portable

# Reset all settings to defaults
python -m script.main --reset-settings

# Show help
python -m script.main --help
```

## Configuration Precedence

1. Command line arguments
2. Environment variables
3. Configuration file
4. Default values

## Resetting Configuration

To reset all settings to their defaults:

1. Close the application
2. Delete the configuration file
3. Restart the application

Or use the command line:
```bash
python -m script.main --reset-settings
```

## Troubleshooting

- If settings don't persist, check file permissions for the config directory
- For issues with API keys, verify they are correctly set in the configuration
- Check the application logs for configuration-related errors
- Use the `--debug` flag to get more detailed error messages

## Backup and Restore

1. **Backup**: Copy the configuration file to a safe location
2. **Restore**: Replace the configuration file with your backup
3. **Sync**: The configuration file can be synced across devices using cloud storage

## Security Considerations

- Never share your configuration file if it contains API keys
- Use environment variables for sensitive information in shared environments
- Set appropriate file permissions on the configuration directory
