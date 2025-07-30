# Troubleshooting Guide

This guide helps you resolve common issues you might encounter while using the Weather App.

## Common Issues

### 1. Application Won't Start

**Symptoms**:
- The application crashes immediately after launch
- You see an error message about missing dependencies

**Solutions**:
1. Verify Python 3.8 or higher is installed:
   ```bash
   python --version
   ```
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Check the error log at:
   - Windows: `%APPDATA%\WeatherApp\logs\app.log`
   - macOS: `~/Library/Logs/WeatherApp/app.log`
   - Linux: `~/.local/share/WeatherApp/logs/app.log`

### 2. No Weather Data Displayed

**Symptoms**:
- The app opens but shows "No data available"
- Weather information doesn't update

**Solutions**:
1. Check your internet connection
2. Verify your API key is correctly set in Settings
3. Try switching to a different weather provider
4. Check if the weather service is experiencing outages

### 3. Invalid API Key Error

**Symptoms**:
- Error message: "Invalid API key"
- Weather data fails to load

**Solutions**:
1. Verify the API key is correct and hasn't expired
2. Check if you've exceeded your API quota
3. For OpenWeatherMap, ensure you've activated your API key via email
4. Try generating a new API key

### 4. Location Not Found

**Symptoms**:
- Error: "Location not found"
- The app can't find your city

**Solutions**:
1. Check for typos in the city name
2. Try including the country code (e.g., "London, GB")
3. Use English names for non-English cities
4. Try a nearby larger city

### 5. High CPU or Memory Usage

**Symptoms**:
- The app becomes slow or unresponsive
- Your computer's fan runs loudly

**Solutions**:
1. Close and reopen the application
2. Reduce the update frequency in Settings
3. Disable animations in Settings > Display
4. Check for memory leaks in the logs

## Log Files

The application creates log files that can help diagnose issues. The log level can be changed in Settings or via command line:

```bash
python -m script.main --log-level DEBUG
```

### Log Locations

- **Windows**: `%APPDATA%\WeatherApp\logs\`
- **macOS**: `~/Library/Logs/WeatherApp/`
- **Linux**: `~/.local/share/WeatherApp/logs/`

## Common Error Messages

### "Could not connect to weather service"
- Check your internet connection
- Verify the weather service is operational
- Try a different weather provider

### "Invalid configuration"
- Reset the configuration file (see below)
- Check for syntax errors in the config file

### "Out of memory"
- Close other applications
- Reduce the number of locations in your favorites
- Restart the application

## Resetting the Application

### Reset Settings
1. Close the application
2. Delete the configuration file:
   - Windows: `%APPDATA%\WeatherApp\config.ini`
   - macOS: `~/Library/Application Support/WeatherApp/config.ini`
   - Linux: `~/.config/WeatherApp/config.ini`
3. Restart the application

### Clear Cache
Delete the cache directory:
- Windows: `%LOCALAPPDATA%\WeatherApp\cache`
- macOS: `~/Library/Caches/WeatherApp`
- Linux: `~/.cache/WeatherApp`

## Performance Issues

### Slow Loading Times
1. Clear the cache
2. Reduce the number of favorite locations
3. Check your internet connection speed

### High Memory Usage
1. Close and reopen the application
2. Reduce the number of days in the forecast
3. Disable background updates when minimized

## Known Issues

### Windows
- Some visual glitches on high-DPI displays
  - Fix: Right-click the application icon > Properties > Compatibility > Change high DPI settings > Enable "Override high DPI scaling behavior"

### macOS
- Menu bar might not appear in fullscreen mode
  - Workaround: Use windowed mode or show the menu bar in fullscreen (System Preferences > General)

### Linux
- Some themes might cause visual issues
  - Try using the default GTK theme

## Getting Help

If you've tried the solutions above and are still experiencing issues:

1. Check the [GitHub Issues](https://github.com/Nsfr750/weather/issues) for similar problems
2. Create a new issue with:
   - A clear description of the problem
   - Steps to reproduce
   - Your operating system and version
   - The contents of the relevant log file
   - Any error messages you see

## Reporting Bugs

When reporting a bug, please include:

1. Steps to reproduce the issue
2. Expected behavior
3. Actual behavior
4. Environment details:
   - Operating system and version
   - Python version
   - Application version
5. Relevant log output

## Contributing Fixes

If you've found a solution to an issue, we'd love your contribution! Please see our [Development Guide](development.md) for instructions on how to submit a pull request.
