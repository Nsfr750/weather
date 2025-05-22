# Weather App

A modern, responsive Python weather application with a graphical user interface (GUI) built using Tkinter. Get real-time weather conditions and a 5-day forecast for any city, with support for light/dark themes and a clean, adaptive layout.

## Features
- **Current Weather:** Real-time temperature, humidity, wind speed, and weather icon
- **5-Day Forecast:** Daily temperature, weather icon, and description
- **Themes:** Light and dark mode support
- **Responsive UI:** Clean interface that adapts to any screen size
- **Menu Bar:** Quick access to About, Help, Sponsor, and Settings
- **API Key Management:** Easily set your OpenWeatherMap API key in Settings

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Obtain a free API key from [OpenWeatherMap](https://openweathermap.org/api).
3. Run the app:
   ```bash
   python weather_app.py
   ```
4. Enter your API key when prompted in Settings, or set the `OPENWEATHER_API_KEY` environment variable.

## File Overview
- `weather_app.py`: Main application code
- `about.py`, `help.py`, `menu.py`, `sponsor.py`, `version.py`: Modular dialogs and utilities
- `requirements.txt`: Python dependencies

## Screenshots
*Add your screenshots here!*

## License
MIT License
