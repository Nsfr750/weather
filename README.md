# Weather App

A modern, feature-rich Python weather application with a beautiful, responsive GUI built using Tkinter. Instantly view real-time weather conditions and a 5-day forecast for any city, with support for multiple languages, units, favorites, and more. Designed for usability, extensibility, and a delightful user experience.

---

## 🚀 Features

- **Current Weather:** Real-time temperature, humidity, wind speed, and weather icon
- **5-Day Forecast:** Daily temperature, icon, and weather description
- **Themes:** Toggle between light and dark modes
- **Units:** Choose between Metric (°C, m/s) and Imperial (°F, mph)
- **Favorites:** Save and quickly select your favorite cities
- **Multi-language Support:** English, Spanish, Italian (UI and weather descriptions)
- **Persistent API Key:** Securely stored in `config.json` via the Settings dialog
- **Error Logging:** All errors recorded in `weather_app.log`
- **Log Viewer:** Conveniently view logs from within the app
- **Responsive UI:** Clean, adaptive interface for any screen size
- **Menu Bar:** Quick access to About, Help, Sponsor, Log, and Settings

---

## 🛠️ Getting Started

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Get an API Key**
   - Register for a free API key at [OpenWeatherMap](https://openweathermap.org/api).
3. **Run the app**
   ```bash
   python weather_app.py
   ```
4. **Configure your API Key**
   - Enter your API key in the Settings dialog (recommended), or set the `OPENWEATHER_API_KEY` environment variable.

---

## ⚙️ Configuration

The app uses `config.json` for persistent settings:
- **API Key**: Set in Settings or manually in `config.json` (`api_key` field)
- **Units**: Choose "metric" or "imperial" (UI dropdown or `units` field)
- **Language**: Select from English (`en`), Spanish (`es`), or Italian (`it`) (UI dropdown or `language` field)

Example `config.json`:
```json
{
  "units": "metric",
  "api_key": "YOUR_API_KEY_HERE",
  "language": "en"
}
```

---

## 📝 Usage Tips
- **Favorites**: Click the star next to the city input to add/remove favorites. Use the dropdown to quickly switch.
- **Units & Language**: Change units or language at any time from the top bar. All labels and weather descriptions update instantly.
- **Logs**: Use the Log menu to view error logs for troubleshooting.
- **Settings**: Access API key and other settings from the menu.

---

## 🐞 Troubleshooting
- **Invalid API Key**: Make sure your OpenWeatherMap API key is correct and active.
- **No Weather Data**: Check your internet connection and API key.
- **UI Issues**: If you see display problems, ensure you are using Python 3.7+ and have all dependencies installed.
- **Logs**: Check `weather_app.log` for detailed error messages.

---

## 🤝 Contributing
Pull requests, translations, and feature suggestions are welcome! Please open an issue or PR on GitHub.

---

## 📄 License
GPL-3.0 License. See [LICENSE](LICENSE) for details.
