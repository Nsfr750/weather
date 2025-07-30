# Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (for development installations)
- System dependencies:
  - **Windows**: Microsoft Visual C++ Build Tools
  - **macOS**: Xcode Command Line Tools
  - **Linux**: Build essentials (gcc, make, etc.)

## Installation Methods

### Method 1: Using pip (Recommended)

1. Create a virtual environment (recommended):
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Unix/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install the package:
   ```bash
   pip install git+https://github.com/Nsfr750/weather.git
   ```

### Method 2: From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/Nsfr750/weather.git
   cd weather
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Unix/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. After installation, run the application with:
   ```bash
   # From source
   python -m script.main
   
   # If installed via pip
   weather-app
   ```

2. The application should open in a new window.

## Updating

### For pip installation:
```bash
pip install --upgrade git+https://github.com/Nsfr750/weather.git
```

### For source installation:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## System Requirements

- **OS**: Windows 10/11 64-bit, macOS 10.15+, or Linux (64-bit)
- **CPU**: 64-bit processor
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Disk Space**: 200MB free space (SSD recommended)
- **Display**: 1280x720 minimum resolution
- **Internet Connection**: Required for weather data

## Platform-Specific Notes

### Windows
- Install the latest Microsoft Visual C++ Redistributable
- Ensure your system is up to date with Windows Update

### macOS
- Requires Xcode Command Line Tools (install with `xcode-select --install`)
- May require additional permissions for location services

### Linux
- Install required build tools:
  ```bash
  # Debian/Ubuntu
  sudo apt-get install build-essential python3-dev
  
  # Fedora
  sudo dnf install python3-devel gcc
  
  # Arch Linux
  sudo pacman -S base-devel python
  ```

## Troubleshooting

If you encounter any issues during installation, please check the [Troubleshooting](troubleshooting.md) guide or open an issue on our [GitHub repository](https://github.com/Nsfr750/weather/issues).

Common issues include:
- Missing system dependencies
- Permission errors (use `--user` flag or run as administrator)
- Outdated pip version (update with `python -m pip install --upgrade pip`)
- Conflicting Python installations (use `python3` explicitly if needed)
