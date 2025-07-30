# User Guide

## Getting Started

1. **Launch the Application**
   - Double-click the application icon or run from the command line
   - The main window will open with the default location's weather
   - On first run, you'll be guided through the initial setup

2. **Search for a Location**
   - Type a city name in the search box
   - Press Enter or click the search button (🔍)
   - For more accurate results, include the country code (e.g., "Paris, FR")
   - Right-click on the map to select a location

## Main Interface

### Weather Display
- **Current Weather**: Shows temperature, conditions, and additional details
  - Tap on any metric to toggle between units (e.g., °C/°F, km/h/mph)
  - Hover over icons for more information
- **5-Day Forecast**: Displays the weather forecast for the next 5 days
  - Click on a day to see hourly forecasts
  - Color-coded precipitation probability
- **Weather Details**: Includes:
  - Feels like temperature
  - Humidity and dew point
  - Wind speed and direction
  - Pressure and visibility
  - UV index and air quality
  - Sunrise and sunset times

### Navigation
- **Search Bar**: Find weather for any location
  - Recent searches are saved automatically
  - Search by city name, ZIP code, or coordinates
- **Theme Toggle**: Switch between light, dark, or system theme
- **Menu Bar**: Access additional features and settings
  - File: New window, settings, quit
  - View: Toggle UI elements, refresh data
  - Favorites: Manage saved locations
  - Help: Documentation, about, check for updates

## Features

### Favorites
- **Add to Favorites**: Click the star (☆) to save a location
- **View Favorites**: Access saved locations from the Favorites menu
  - Reorder favorites by drag and drop
  - Right-click for quick actions
- **Sync Favorites**: Enable cloud sync in settings
- **Remove from Favorites**: Click the filled star (★) to remove

### Settings
1. Click the gear icon (⚙️) or go to Menu > Settings
2. Configure options like:
   - **General**: Language, theme, units
   - **Weather**: Provider settings, update frequency
   - **Display**: Layout, animations, font size
   - **Notifications**: Weather alerts, rain alerts
   - **Advanced**: Cache, logging, developer options
3. Click "Save" to apply changes

### Command Line Interface

```bash
# Basic usage
weather-app [location] [options]

# Examples
weather-app "New York, US"
weather-app --provider openweathermap --units metric
weather-app --config ~/.config/weather/config.ini

# Options
  -h, --help            Show help message and exit
  -v, --version         Show version information
  -c, --config FILE     Specify configuration file
  -d, --debug           Enable debug mode
  --provider PROVIDER   Set weather provider
  --units {metric,imperial}
                        Set units system
  --lang LANG           Set language code
  --theme {light,dark,system}
                        Set color theme
  --no-gui              Run in console mode
```

## Keyboard Shortcuts

### Global Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl + F` | Focus search bar |
| `Ctrl + ,` | Open Settings |
| `Ctrl + Q` | Quit Application |
| `F1` | Show Help |
| `Esc` | Close dialogs or clear search |
| `F5` | Refresh weather data |
| `Ctrl + R` | Refresh all data |
| `Ctrl + W` | Close current window |
| `Ctrl + N` | New window |

### Navigation
| Shortcut | Action |
|----------|--------|
| `Ctrl + Tab` | Switch between locations |
| `Ctrl + F` | Toggle favorites |
| `Ctrl + L` | Toggle location list |
| `Ctrl + M` | Toggle map view |

## Tips & Tricks

- **Right-click** on any weather card for quick actions
- **Double-click** the temperature to toggle between Celsius and Fahrenheit
- **Middle-click** on the map to set a custom location
- Use **mouse wheel** on the forecast to scroll through hours
- **Drag and drop** to reorder favorite locations
- **Pin** the window to stay on top of other applications
- Use **system tray** icon for quick access

## Mobile Experience

- **Swipe left/right** to switch between locations
- **Pull down** to refresh
- **Pinch to zoom** on the map
- **Tap and hold** for context menus

## Troubleshooting

If you encounter any issues:
1. Check your internet connection
2. Verify your API keys in Settings
3. Try switching to a different weather provider
4. Check the application logs for errors
5. Restart the application
6. Reset settings if needed

For additional help, please visit our [GitHub repository](https://github.com/Nsfr750/weather) or check the [Troubleshooting Guide](troubleshooting.md).

## Feedback

We welcome your feedback! Please let us know:
- What features you'd like to see
- Any bugs you encounter
- Your experience with the application

You can submit feedback through the application (Help > Send Feedback) or on our [GitHub Issues](https://github.com/Nsfr750/weather/issues) page.
