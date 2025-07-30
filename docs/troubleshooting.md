# Troubleshooting Guide

This guide helps you resolve common issues you might encounter while using the Weather App.

## Table of Contents
- [Common Issues](#common-issues)
- [Log Files](#log-files)
- [Debugging](#debugging)
- [Performance Issues](#performance-issues)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Getting Help](#getting-help)

## Common Issues

### 1. Application Won't Start

**Symptoms**:
- The application crashes immediately after launch
- You see an error message about missing dependencies
- The application window doesn't appear

**Solutions**:
1. **Check System Requirements**:
   - Ensure you have Python 3.10 or higher installed
   - Verify all system dependencies are installed
   - Check disk space and permissions

2. **Reinstall Dependencies**:
   ```bash
   # Activate your virtual environment first
   pip install --upgrade -r requirements.txt
   ```

3. **Check for Conflicting Software**:
   - Temporarily disable antivirus/firewall
   - Close other applications that might be conflicting

4. **Reset Configuration**:
   ```bash
   # Backup your config first
   mv ~/.config/WeatherApp/config.ini ~/.config/WeatherApp/config.ini.bak
   ```

### 2. No Weather Data Displayed

**Symptoms**:
- The app opens but shows "No data available"
- Weather information doesn't update
- Location cannot be found

**Solutions**:
1. **Check Internet Connection**:
   - Verify your device is connected to the internet
   - Try accessing a website in your browser

2. **Verify API Keys**:
   - Check if your API key is valid and not expired
   - Ensure the API key has the correct permissions
   - Try regenerating the API key

3. **Provider Status**:
   - Check if the weather service is experiencing outages
   - Try switching to a different weather provider

4. **Location Services**:
   - Ensure location services are enabled
   - Try entering the location manually

### 3. High CPU or Memory Usage

**Symptoms**:
- The app becomes slow or unresponsive
- Your computer's fan runs loudly
- Other applications become slow

**Solutions**:
1. **Reduce Update Frequency**:
   - Increase the update interval in Settings > Weather
   - Disable automatic location updates if not needed

2. **Disable Animations**:
   - Go to Settings > Display
   - Toggle off "Enable animations"

3. **Clear Cache**:
   ```bash
   # Linux/macOS
   rm -rf ~/.cache/WeatherApp
   
   # Windows
   rmdir /s /q %LOCALAPPDATA%\WeatherApp\Cache
   ```

4. **Check for Memory Leaks**:
   - Monitor memory usage in Task Manager
   - Report any consistent memory growth

## Log Files

Log files contain detailed information about application events and errors. They are essential for troubleshooting.

### Log Locations

- **Linux/macOS**: `~/.local/share/WeatherApp/logs/`
- **Windows**: `%APPDATA%\WeatherApp\logs\`
- **macOS**: `~/Library/Logs/WeatherApp/`

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General application events
- **WARNING**: Potentially harmful situations
- **ERROR**: Errors that might still allow the app to continue
- **CRITICAL**: Severe errors that cause the app to crash

### Viewing Logs

1. **From the Application**:
   - Go to Help > View Logs
   - Filter by log level
   - Search for specific terms

2. **From Command Line**:
   ```bash
   # Linux/macOS
   tail -f ~/.local/share/WeatherApp/logs/app.log
   
   # Windows
   Get-Content -Path "$env:APPDATA\WeatherApp\logs\app.log" -Wait
   ```

## Debugging

### Enabling Debug Mode

1. **From Command Line**:
   ```bash
   python -m script.main --debug
   ```

2. **From Configuration**:
   ```ini
   [Logging]
   level = DEBUG
   ```

### Common Error Messages

#### "API Rate Limit Exceeded"
- **Cause**: Too many requests to the weather API
- **Solution**:
  - Wait before making more requests
  - Upgrade your API plan if needed
  - Implement proper caching

#### "Invalid API Key"
- **Cause**: The provided API key is invalid or expired
- **Solution**:
  - Verify the key is correct
  - Check for extra spaces
  - Generate a new key if needed

#### "Location Not Found"
- **Cause**: The specified location doesn't exist
- **Solution**:
  - Check for typos
  - Try a nearby larger city
  - Use coordinates instead of city name

### Using a Debugger

1. **VS Code**:
   - Set breakpoints in your code
   - Press F5 to start debugging
   - Use the debug console to inspect variables

2. **pdb (Python Debugger)**:
   ```python
   import pdb; pdb.set_trace()  # Add this line where you want to break
   ```

## Performance Issues

### Slow Startup

1. **Disable Unnecessary Plugins**:
   - Check for third-party plugins
   - Disable unused providers

2. **Optimize Imports**:
   - Use lazy loading for heavy modules
   - Remove unused imports

### High Memory Usage

1. **Check for Memory Leaks**:
   - Monitor memory usage over time
   - Look for objects that aren't being garbage collected

2. **Reduce Cache Size**:
   ```ini
   [Cache]
   max_size = 100  # MB
   ```

### Network Issues

1. **Check Connection**:
   ```bash
   ping api.openweathermap.org
   ```

2. **Proxy Settings**:
   - Configure proxy in Settings > Network
   - Check firewall settings

## Frequently Asked Questions

### Q: How do I update the application?
A: Use your package manager or download the latest version from GitHub.

### Q: Why is the weather data not updating?
A: Check your internet connection and API key. The app caches data to reduce API calls.

### Q: How do I change the temperature unit?
A: Go to Settings > Display > Units and select your preferred unit.

### Q: The app is using too much battery. What can I do?
A: Reduce the update frequency and disable unnecessary features like animations.

### Q: How do I report a bug?
A: Please open an issue on our [GitHub repository](https://github.com/Nsfr750/weather/issues) with detailed steps to reproduce the issue.

## Getting Help

If you've tried the solutions above and are still experiencing issues:

1. **Check the Documentation**:
   - [User Guide](usage.md)
   - [Configuration](configuration.md)
   - [API Documentation](api.md)

2. **Search Existing Issues**:
   - [GitHub Issues](https://github.com/Nsfr750/weather/issues)
   - [FAQ](https://github.com/Nsfr750/weather/wiki/FAQ)

3. **Ask the Community**:
   - [Discord](https://discord.gg/ryqNeuRYjD)
   - [GitHub Discussions](https://github.com/Nsfr750/weather/discussions)

4. **Contact Support**:
   - Email: nsfr750@yandex.com
   - Include your system information and error logs

### When Reporting an Issue

Please include the following information:
1. Weather App version
2. Operating System and version
3. Steps to reproduce the issue
4. Expected vs. actual behavior
5. Relevant error messages or logs
6. Screenshots if applicable

## Emergency Recovery

If the application becomes completely unresponsive:

1. **Force Quit**:
   - Windows: Ctrl+Alt+Delete → Task Manager → End Task
   - macOS: Command+Option+Esc → Force Quit
   - Linux: `pkill -f weather`

2. **Reset Configuration**:
   ```bash
   # Linux/macOS
   rm -rf ~/.config/WeatherApp
   
   # Windows
   rmdir /s /q %APPDATA%\WeatherApp
   ```

3. **Reinstall**:
   ```bash
   pip uninstall weather-app
   pip install --no-cache-dir weather-app
   ```

Remember to back up your configuration before making any changes!
