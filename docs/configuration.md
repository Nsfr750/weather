# Configuration Guide

This document outlines the configuration options available for the Weather application.

## Configuration File Location

The main configuration file is located at `config/config.ini`.

## Available Settings

### [DEFAULT] Section
- `language`: Default language for the application (e.g., 'en' for English, 'it' for Italian)
- `units`: Measurement units ('metric' or 'imperial')
- `theme`: Application theme ('light' or 'dark')
- `refresh_interval`: Data refresh interval in minutes (default: 30)

### [LOGGING] Section
- `level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `max_size`: Maximum log file size in MB
- `backup_count`: Number of log files to keep

### [CACHE] Section
- `enabled`: Enable/disable caching (true/false)
- `ttl`: Cache time-to-live in seconds
- `path`: Path to cache directory

## Example Configuration

```ini
[DEFAULT]
language = en
units = metric
theme = dark
refresh_interval = 30

[LOGGING]
level = INFO
max_size = 10
backup_count = 5

[CACHE]
enabled = true
ttl = 3600
path = ./cache
```

## Environment Variables

You can override any setting using environment variables with the prefix `WEATHER_`:

```bash
# Example:
export WEATHER_DEFAULT_LANGUAGE=it
export WEATHER_DEFAULT_UNITS=metric
```

## Notes

- Changes to the configuration require a restart of the application to take effect.
- The configuration file is automatically created with default values if it doesn't exist.
