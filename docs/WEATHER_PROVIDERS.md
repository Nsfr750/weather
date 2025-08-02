# Weather Provider Configuration Guide

This document provides instructions for setting up and configuring the various weather provider plugins available in the Weather App.

## Available Weather Providers

1. **OpenWeatherMap**
   - Website: [https://openweathermap.org/](https://openweathermap.org/)
   - API Key: Sign up for a free API key at [https://home.openweathermap.org/api_keys](https://home.openweathermap.org/api_keys)
   - Environment Variable: `OPENWEATHERMAP_API_KEY`

2. **AccuWeather**
   - Website: [https://developer.accuweather.com/](https://developer.accuweather.com/)
   - API Key: Sign up for a free API key at [https://developer.accuweather.com/user/me/apps](https://developer.accuweather.com/user/me/apps)
   - Environment Variable: `ACCUWEATHER_API_KEY`


## Configuration

### Using Environment Variables

1. Create a `.env` file in the project root directory
2. Add your API keys and credentials as shown in the `.env.example` file
3. The application will automatically load these variables when starting

Example `.env` file:

```env
# OpenWeatherMap
OPENWEATHERMAP_API_KEY=your_api_key_here

# AccuWeather
ACCUWEATHER_API_KEY=your_api_key_here

```

### Using Application Settings

You can also configure the API keys through the application settings UI:

1. Open the application
2. Go to Settings > Weather Providers
3. Select the provider you want to configure
4. Enter your API key and other required credentials
5. Click "Save" to apply the changes

## Troubleshooting

### Missing API Key

If you see an error about a missing API key:
1. Make sure you've obtained an API key from the provider's website
2. Verify the API key is correctly set in your `.env` file or application settings
3. Ensure the environment variable name matches exactly what's expected

### Authentication Errors

If you're getting authentication errors:
1. Double-check that your API key is correct and hasn't expired
2. For providers that require multiple credentials (like The Weather Company), ensure all required fields are provided
3. Check if your account has the necessary permissions/quotas

### Rate Limiting

Some providers have rate limits on their free plans. If you're experiencing rate limit errors:
1. Check your provider's documentation for rate limits
2. Consider upgrading to a paid plan if you need higher limits
3. Implement caching to reduce the number of API calls

## Testing Your Setup

To verify that your API keys are working correctly:

1. Start the application
2. Check the logs for any authentication or connection errors
3. Try searching for a location to ensure weather data is being retrieved

## Support

For additional help, please refer to:
- [Project Documentation](docs/)
- [GitHub Issues](https://github.com/yourusername/weatherapp/issues)
- [Community Forum](https://community.weatherapp.com)
