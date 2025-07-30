# Weather Providers

The Weather App supports multiple weather data providers. This document describes each provider, their features, and how to configure them.

## Available Providers

### 1. OpenWeatherMap (Default)
- **Description**: Global weather data with extensive coverage and high accuracy
- **Features**:
  - Current weather conditions
  - 5-day/3-hour forecast
  - Weather alerts
  - Air quality index
  - UV index
  - Historical data (with subscription)
- **API Key Required**: Yes (Free tier available)
- **Rate Limits**:
  - Free: 60 calls/minute, 1,000,000 calls/month
  - Paid: Up to 200,000 calls/minute
- **Coverage**: Global
- **Website**: [OpenWeatherMap](https://openweathermap.org/)

### 2. Open-Meteo
- **Description**: Open-source weather API with high resolution and no API key required for basic usage
- **Features**:
  - Hyperlocal forecasts
  - Historical data
  - Air quality data
  - Marine weather
  - Climate data
- **API Key Required**: No (for basic usage)
- **Rate Limits**:
  - Free: 10,000 calls/day
  - No API key: 2,000 calls/day
- **Coverage**: Global
- **Website**: [Open-Meteo](https://open-meteo.com/)

### 3. WeatherAPI.com
- **Description**: Simple and reliable weather data with generous free tier
- **Features**:
  - Current weather
  - Forecast (up to 14 days)
  - Time zone information
  - Astronomy data
  - Sports weather
- **API Key Required**: Yes
- **Rate Limits**:
  - Free: 1,000,000 calls/month
  - No daily limit
- **Coverage**: Global
- **Website**: [WeatherAPI.com](https://www.weatherapi.com/)

### 4. Tomorrow.io (formerly ClimaCell)
- **Description**: Advanced weather intelligence platform
- **Features**:
  - Minute-by-minute forecasts
  - Real-time weather maps
  - Severe weather alerts
  - Air quality and pollen
  - Road risk
- **API Key Required**: Yes
- **Rate Limits**: Varies by plan
- **Coverage**: Global
- **Website**: [Tomorrow.io](https://www.tomorrow.io/)

### 5. AccuWeather
- **Description**: Premium weather service with high accuracy
- **Features**:
  - MinuteCast minute-by-minute precipitation
  - Daily and hourly forecasts
  - Weather alerts
  - Historical data
  - Tropical weather
- **API Key Required**: Yes
- **Rate Limits**: Varies by plan
- **Coverage**: Global
- **Website**: [AccuWeather API](https://developer.accuweather.com/)

## Configuration

### Setting Up API Keys

1. Obtain an API key from your preferred provider
2. Open Settings > Weather Providers
3. Select the provider
4. Enter your API key in the provided field
5. Configure any additional options
6. Click "Save"

### Provider-Specific Settings

Each provider may have additional configuration options:

- **Base URL**: Override the default API endpoint
- **Timeout**: Set request timeout in seconds (default: 10)
- **Retry Attempts**: Number of retry attempts on failure (default: 3)
- **Cache Duration**: How long to cache responses (in minutes, default: 30)
- **Language**: Preferred language for weather data
- **Units**: Metric or Imperial units

### Environment Variables

You can set API keys via environment variables:

```bash
# Windows
set OPENWEATHERMAP_API_KEY=your_api_key
set OPENMETEO_API_KEY=your_api_key
set WEATHERAPI_API_KEY=your_api_key

# Unix/macOS
export OPENWEATHERMAP_API_KEY=your_api_key
export OPENMETEO_API_KEY=your_api_key
export WEATHERAPI_API_KEY=your_api_key
```

## Fallback Mechanism

The app implements an intelligent fallback system:

1. If the primary provider fails, it automatically tries the next available provider
2. The fallback order is configurable in Settings > Weather Providers
3. A notification is shown when falling back to a different provider
4. Failed requests are automatically retried with exponential backoff

## Adding a New Provider

To add a new weather provider:

1. Create a new Python file in `script/providers/`
2. Implement the required methods from `BaseWeatherProvider`:
   ```python
   class MyWeatherProvider(BaseWeatherProvider):
       NAME = "My Weather"
       SETTINGS = [
           Setting("api_key", "API Key", "text"),
           Setting("base_url", "API Base URL", "text", "https://api.myweather.com/v1"),
       ]
       
       async def get_current_weather(self, location):
           # Implementation
           pass
           
       async def get_forecast(self, location, days=5):
           # Implementation
           pass
   ```
3. Register the provider in `script/providers/__init__.py`
4. Add translations for the provider name in `translations.py`
5. Update the documentation

## Best Practices

1. **API Key Security**:
   - Never commit API keys to version control
   - Use environment variables for production
   - Restrict API keys to specific domains/IPs when possible

2. **Rate Limiting**:
   - Respect the provider's rate limits
   - Implement proper caching
   - Use exponential backoff for retries

3. **Error Handling**:
   - Handle network errors gracefully
   - Provide meaningful error messages
   - Log errors for debugging

## Troubleshooting

### Common Issues

- **Invalid API Key**:
  - Verify the key is correct and active
  - Check for leading/trailing spaces
  - Ensure the key has the required permissions

- **Rate Limit Exceeded**:
  - Check your usage against the provider's limits
  - Implement caching to reduce API calls
  - Consider upgrading your plan if needed

- **No Data**:
  - Verify the location is supported by the provider
  - Check the provider's status page for outages
  - Try a different location to isolate the issue

### Debugging

1. Enable debug logging in Settings > Advanced
2. Check the application logs for detailed error messages
3. Use the "Test Connection" button in provider settings
4. Try the provider's API directly using tools like curl or Postman

## Support

For issues specific to weather data providers:

1. Check the provider's API documentation
2. Verify your API key and usage limits
3. Contact the provider's support if needed

For application-specific issues, please open an issue on our [GitHub repository](https://github.com/Nsfr750/weather/issues).
