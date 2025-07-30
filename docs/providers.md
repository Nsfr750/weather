# Weather Providers

The Weather App supports multiple weather data providers. This document describes each provider and how to configure them.

## Available Providers

### 1. OpenWeatherMap
- **Description**: Global weather data with extensive coverage
- **Features**: Current weather, forecasts, and weather alerts
- **API Key Required**: Yes
- **Free Tier**: 1,000,000 calls/month (60 calls/minute)
- **Website**: [OpenWeatherMap](https://openweathermap.org/)

### 2. Open-Meteo
- **Description**: Open-source weather API with high resolution
- **Features**: Hyperlocal forecasts and historical data
- **API Key Required**: No (for basic usage)
- **Rate Limits**: 10,000 calls/day (free tier)
- **Website**: [Open-Meteo](https://open-meteo.com/)

### 3. Weather.com (The Weather Company)
- **Description**: Professional-grade weather data
- **Features**: Minute-by-minute forecasts and severe weather alerts
- **API Key Required**: Yes
- **Free Tier**: Limited free trial available
- **Website**: [Weather.com API](https://www.weather.com/services/weather-api)

### 4. Breezy Weather
- **Description**: Lightweight weather provider
- **Features**: Basic weather data with minimal API requirements
- **API Key Required**: No
- **Rate Limits**: None (self-hosted)
- **Website**: [Breezy Weather](https://breezy-weather.com/)

### 5. QuickWeather
- **Description**: Fast and simple weather API
- **Features**: Current conditions and short-term forecasts
- **API Key Required**: Yes
- **Free Tier**: 100 calls/day
- **Website**: [QuickWeather](https://quickweather.io/)

### 6. Weather Company (IBM)
- **Description**: Enterprise-grade weather data
- **Features**: Advanced forecasting and analytics
- **API Key Required**: Yes
- **Free Tier**: Limited free tier available
- **Website**: [IBM Weather](https://www.ibm.com/weather/)

### 7. Alliander
- **Description**: Specialized in European weather data
- **Features**: Focus on energy sector requirements
- **API Key Required**: Yes
- **Free Tier**: Contact for pricing
- **Website**: [Alliander](https://www.alliander.com/)

## Configuration

### Setting Up API Keys

1. Obtain an API key from your preferred provider
2. Open Settings > Weather Providers
3. Select the provider
4. Enter your API key in the provided field
5. Click "Save"

### Provider-Specific Settings

Each provider may have additional configuration options:

- **Base URL**: Override the default API endpoint
- **Timeout**: Set request timeout in seconds
- **Retry Attempts**: Number of retry attempts on failure
- **Cache Duration**: How long to cache responses (in minutes)

## Fallback Mechanism

The app implements a fallback mechanism:

1. If the primary provider fails, it automatically tries the next available provider
2. The order of fallback can be configured in settings
3. A notification is shown when falling back to a different provider

## Adding a New Provider

To add a new weather provider:

1. Create a new Python class in `script/providers/`
2. Implement the required methods from `BaseWeatherProvider`
3. Register the provider in `script/providers/__init__.py`
4. Add translations for the provider name in `translations.py`

## Troubleshooting

### Common Issues

- **Invalid API Key**: Verify the key is correctly copied and has the right permissions
- **Rate Limit Exceeded**: Check your provider's rate limits and consider upgrading your plan
- **No Data**: Ensure the location is supported by the provider

### Logs

Check the application logs for detailed error messages related to provider issues. The logs will show which provider failed and why.

## Best Practices

1. Always use environment variables for API keys in production
2. Implement proper error handling for API failures
3. Cache responses to reduce API calls
4. Respect rate limits and implement backoff strategies
