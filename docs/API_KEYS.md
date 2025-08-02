# API Key Configuration Guide

This guide explains how to obtain and configure API keys for the various weather providers supported by this application.

## Table of Contents

- [OpenWeatherMap](#openweathermap)
- [AccuWeather](#accuweather)
- [The Weather Company (IBM)](#the-weather-company-ibm)
- [Weather.com](#weathercom)
- [Configuration Methods](#configuration-methods)
  - [Environment Variables](#environment-variables)
  - [Configuration File](#configuration-file)
  - [Runtime Configuration](#runtime-configuration)

## OpenWeatherMap

### Obtaining an API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/)
2. Sign up for a free account
3. Navigate to [API keys](https://home.openweathermap.org/api_keys)
4. Copy your API key

### Required Permissions

- Current Weather Data API (Free tier available)
- 5 Day / 3 Hour Forecast API (Free tier available)

## AccuWeather

### Obtaining an API Key

1. Go to [AccuWeather Developer Portal](https://developer.accuweather.com/)
2. Sign up for a free developer account
3. Create a new application
4. Copy the API key from your application dashboard

### Required APIs

- Locations API
- Current Conditions API
- 5-Day Forecast API

## The Weather Company (IBM)

### Obtaining API Credentials

1. Sign up for an IBM Cloud account at [IBM Cloud](https://cloud.ibm.com/)
2. Enable the Weather Company Data service
3. Create credentials (API key, username, password)
4. Note down all three values

## Weather.com

### Obtaining an API Key

1. Go to [IBM Watson - Weather Company Data](https://www.ibm.com/products/environmental-intelligence-weather-data)
2. Sign up for a free trial or paid plan
3. Create a new application to get your API key

## Configuration Methods

### Environment Variables

You can set API keys as environment variables:

```bash
# Windows
set OPENWEATHERMAP_API_KEY=your_api_key_here
set ACCUWEATHER_API_KEY=your_api_key_here
set WEATHERCOMPANY_API_KEY=your_api_key_here
set WEATHERCOMPANY_USERNAME=your_username_here
set WEATHERCOMPANY_PASSWORD=your_password_here
set WEATHERDOTCOM_API_KEY=your_api_key_here

# Linux/macOS
export OPENWEATHERMAP_API_KEY=your_api_key_here
export ACCUWEATHER_API_KEY=your_api_key_here
export WEATHERCOMPANY_API_KEY=your_api_key_here
export WEATHERCOMPANY_USERNAME=your_username_here
export WEATHERCOMPANY_PASSWORD=your_password_here
export WEATHERDOTCOM_API_KEY=your_api_key_here
```

### Configuration File

Create a `config.ini` file in the application root directory:

```ini
[openweathermap]
api_key = your_api_key_here

[accuweather]
api_key = your_api_key_here

[weathercompany]
api_key = your_api_key_here
username = your_username_here
password = your_password_here

[weatherdotcom]
api_key = your_api_key_here
```

### Runtime Configuration

You can also provide API keys when initializing the weather providers in your code:

```python
from script.plugin_system.weather_provider import WeatherProviderManager

# Initialize provider with API key
provider = WeatherProviderManager()
provider.set_active_provider(
    'openweathermap', 
    api_key='your_api_key_here'
)

# Or for providers with multiple credentials
provider.set_active_provider(
    'weathercompany',
    api_key='your_api_key_here',
    username='your_username_here',
    password='your_password_here'
)
```

## Troubleshooting

- **Invalid API Key**: Double-check that you've copied the entire key correctly
- **Rate Limits**: Free tiers have limits. If you exceed them, you'll need to wait or upgrade your plan
- **Service Availability**: Some services may be temporarily unavailable in certain regions
- **Network Issues**: Ensure your internet connection is stable when making API requests

For additional help, refer to the official documentation of each weather provider or contact their support.
