# Weather Providers

This document describes the available weather data providers and their configuration.

## Supported Providers

### 1. OpenMeteo
Default provider using the OpenMeteo API.

**Configuration:**
- `api_url`: Base URL for the OpenMeteo API
- `timeout`: Request timeout in seconds
- `cache_ttl`: Cache duration in seconds

### 2. OpenWeatherMap (Planned)
Future integration with OpenWeatherMap API.

**Requirements:**
- API key from OpenWeatherMap
- Active subscription (free tier available)

## Provider Configuration

### Location Settings
- `location`: Can be one of:
  - City name (e.g., "London,UK")
  - Coordinates (e.g., "51.5074,-0.1278")
  - IP-based location (auto-detection)

### Data Refresh
- `auto_refresh`: Enable/disable automatic data refresh
- `refresh_interval`: Refresh interval in minutes

## Example Configuration

```ini
[OPENMETEO]
api_url = https://api.open-meteo.com/v1/
timeout = 10
cache_ttl = 1800

[LOCATION]
location = auto

[REFRESH]
auto_refresh = true
refresh_interval = 30
```

## Adding a New Provider

1. Create a new Python file in `script/weather_providers/`
2. Implement the required interface:
   - `get_current_weather()`
   - `get_forecast()`
   - `get_air_quality()` (optional)
3. Update the provider factory to include your new provider

## Rate Limiting

Each provider may have its own rate limits. The application includes built-in rate limiting and caching to prevent exceeding these limits.
