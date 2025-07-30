# 🌦️ Weather App

A modern, feature-rich Python weather application with a beautiful, responsive GUI built using PyQt6. Get real-time weather conditions, forecasts, and alerts for any location worldwide. The app supports multiple weather providers, languages, and units, making it a versatile tool for users everywhere.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Discord](https://img.shields.io/discord/1234567890123456789?color=7289da&label=Discord&logo=discord&logoColor=white)](https://discord.gg/ryqNeuRYjD)

![Weather App Screenshot](assets/screenshot.png)

## ✨ Features

- **Multiple Weather Providers**: Choose from 8 different weather data sources
  - OpenWeatherMap (default)
  - Open-Meteo
  - Weather.com
  - Breezy Weather
  - QuickWeather
  - Weather Company (IBM)
  - Alliander
  - Accuweather
  
- **Comprehensive Weather Data**
  - Current conditions with detailed metrics
  - 5-day forecast with hourly breakdowns
  - Weather alerts and warnings
  - Air quality index (AQI) and UV index
  - Sunrise/sunset and moon phase information

- **User Experience**
  - Clean, modern UI with light/dark themes
  - Support for multiple languages (English, Spanish, French, German, Italian, Russian, Arabic, Japanese)
  - Customizable units (metric/imperal)
  - Favorite locations with quick access
  - Responsive design for different screen sizes

- **Advanced Features**
  - Automatic location detection
  - Weather maps and radar integration
  - Severe weather alerts
  - Historical weather data
  - Export weather data (CSV/JSON)

- **For Developers**
  - Well-documented codebase
  - Comprehensive test suite
  - Plugin system for weather providers
  - RESTful API for integration
  - Docker support for easy deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Git
- pip (Python package manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nsfr750/weather.git
   cd weather
   ```

2. **Set up a virtual environment (recommended)**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Unix/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python -m script.main
   ```

### Configuration

1. Get an API key from one of the supported weather providers (e.g., [OpenWeatherMap](https://openweathermap.org/api))
2. Launch the application and go to Settings > API Keys
3. Enter your API key and save the settings

## 📚 Documentation

For detailed documentation, please visit our [documentation website](https://nsfr750.github.io/weather/) or check the `/docs` directory in the repository.

- [User Guide](docs/usage.md)
- [Configuration](docs/configuration.md)
- [Developer Guide](docs/development.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report bugs, or suggest new features.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- All the amazing weather data providers
- The PyQt community for the excellent GUI framework
- All contributors who have helped improve this project

## 📞 Support

For support, please join our [Discord server](https://discord.gg/ryqNeuRYjD) or open an issue on GitHub.

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/Nsfr750">Nsfr750</a>
  <br>
  <a href="https://www.paypal.me/3dmega">
    <img src="https://img.shields.io/badge/Support%20me-PayPal-ff5a5f?style=for-the-badge&logo=paypal" alt="Support me on PayPal">
  </a>
  <a href="https://www.patreon.com/Nsfr750">
    <img src="https://img.shields.io/badge/Support%20me-Patreon-FF424D?style=for-the-badge&logo=patreon" alt="Support me on Patreon">
  </a>
</div>
