# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for development installations)

## Installation Methods

### Method 1: Using pip (Recommended)

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. After installation, run the application with:
   ```bash
   python -m script.main
   ```

   Or if installed via pip:
   ```bash
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

- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Disk Space**: 100MB free space
- **Display**: 1024x768 minimum resolution

## Troubleshooting

If you encounter any issues during installation, please check the [Troubleshooting](troubleshooting.md) guide or open an issue on our [GitHub repository](https://github.com/Nsfr750/weather/issues).
