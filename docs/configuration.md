# Configuration Guide

## Overview

The Weather App can be configured through the Settings dialog or by manually editing the configuration file. This guide covers all available configuration options.

## Settings Dialog

Access the Settings dialog by clicking the gear icon (⚙️) or navigating to Menu > Settings.

### General Tab

- **Language**: Select the application language
- **Theme**: Choose between Light, Dark, or System
- **Units**: Toggle between Metric and Imperial units
- **Start Minimized**: Launch the app in the system tray
- **Check for Updates**: Enable/disable automatic update checks

### Weather Providers

- **Active Provider**: Select your preferred weather data source
- **Provider Settings**: Configure API keys and options for each provider

### Display

- **Show Alerts**: Toggle weather alerts display
- **Animations**: Enable/disable UI animations
- **Font Size**: Adjust the base font size

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

[OpenWeatherMap]
api_key = your_api_key_here

[OpenMeteo]
api_key = your_api_key_here

[UI]
show_alerts = true
animations = true
font_size = 12
```

## Environment Variables

Some settings can be configured using environment variables:

- `WEATHER_APP_CONFIG_DIR`: Override the configuration directory
- `WEATHER_APP_CACHE_DIR`: Set a custom cache directory
- `WEATHER_APP_LOG_LEVEL`: Set the log level (DEBUG, INFO, WARNING, ERROR)

## Command Line Arguments

Run the application with these command line arguments:

```bash
# Specify a configuration file
python -m script.main --config /path/to/config.ini

# Set log level
python -m script.main --log-level DEBUG

# Run in portable mode (stores data in the application directory)
python -m script.main --portable

# Show help
python -m script.main --help
```

## Resetting Configuration

To reset all settings to their defaults:

1. Close the application
2. Delete the configuration file
3. Restart the application

## Troubleshooting

- If settings don't persist, check file permissions for the config directory
- For issues with API keys, verify they are correctly set in the configuration
- Check the application logs for configuration-related errors
