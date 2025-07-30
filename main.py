import sys
import os
import requests
import json
import webbrowser
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import logger from script module
from script.logger import logger

# PyQt6 imports
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QComboBox, QFrame, QMessageBox, QMenuBar,
                            QMenu, QStatusBar, QInputDialog, QLineEdit, QFileDialog, QScrollArea)
from PyQt6.QtCore import Qt, QSize, QTimer, QUrl, QObject, pyqtSignal, pyqtSlot, QEvent
from PyQt6.QtGui import QIcon, QPixmap, QAction, QFont, QPalette, QColor, QDesktopServices

# Add script directory to path for module imports
script_dir = Path(__file__).parent.absolute()
sys.path.append(str(script_dir))

# Local imports
from script.icon_utils import get_icon_image, set_offline_mode
from script.version import get_version
from script.updates import UpdateChecker
from script.about import About
from script.help import Help
from script.sponsor import Sponsor
from script.menu import create_menu_bar
from script.favorites_utils import FavoritesManager
from script.config_utils import ConfigManager
from script.translations import TRANSLATIONS
from script.translations_utils import TranslationsManager
from script.notifications import NotificationManager, check_severe_weather
from script.weather_providers import get_provider, get_available_providers
from script.ui import WeatherAppUI

# ----------- CONFIGURATION -----------
DEFAULT_CITY = 'London'

class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup config and data directories
        self.config_dir = Path.home() / '.weather_app'
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize notification system
        self.notification_manager = NotificationManager(self.config_dir)
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.units = self.config_manager.get('units', 'metric')
        self.language = self.config_manager.get('language', 'en')
        self.api_key = self.config_manager.get('api_key') or os.environ.get('OPENWEATHER_API_KEY', 'YOUR_API_KEY_HERE')
        
        # Set offline mode if no internet
        self.check_connection()
        
        # Initialize weather provider
        self.initialize_weather_provider()
        
        # Initialize translations
        self.translations_manager = TranslationsManager(TRANSLATIONS, default_lang=self.language)
        
        # Initialize UI
        self.setWindowTitle('Weather App')
        self.setMinimumSize(600, 800)
        
        # Set application icon
        self.set_application_icon()
        
        # Initialize UI
        self.ui = WeatherAppUI(
            config_manager=self.config_manager,
            translations_manager=self.translations_manager,
            weather_provider=self.weather_provider,
            notification_manager=self.notification_manager
        )
        
        # Set up signals
        self.setup_connections()
        
        # Set initial city from config or default
        self.city = self.config_manager.get('last_city', DEFAULT_CITY)
        self.ui.set_city(self.city)
        
        # Set initial units
        self.ui.set_units(self.units)
        
        # Set initial language
        self.ui.set_language(self.language)
        
        # Load favorites
        self.favorites_manager = FavoritesManager()
        self.update_favorites_menu()
        
        # Check for updates on startup
        self.check_for_updates()
        
        # Load initial weather data
        self.refresh_weather()
        
        # Set central widget
        self.setCentralWidget(self.ui)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Show the window
        self.show()
    
    def set_application_icon(self):
        """Set the application icon."""
        try:
            icon_path = Path('assets/meteo.png')
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            logging.warning(f'Could not set application icon: {e}')
    
    def check_connection(self):
        """Check internet connection and set offline mode accordingly."""
        try:
            requests.head('http://www.google.com', timeout=5)
            set_offline_mode(False)
        except requests.RequestException:
            set_offline_mode(True)
            QMessageBox.warning(
                self,
                'Offline Mode',
                'Internet connection not available. Running in offline mode with limited functionality.'
            )
    
    def initialize_weather_provider(self):
        """Initialize the weather provider with the configured settings."""
        self.weather_provider_name = self.config_manager.get('weather_provider', 'openweathermap')
        try:
            self.weather_provider = get_provider(
                self.weather_provider_name,
                api_key=self.api_key,
                units=self.units,
                language=self.language
            )
            logger.info(f"Using weather provider: {self.weather_provider_name}")
        except Exception as e:
            logger.error(f"Failed to initialize weather provider {self.weather_provider_name}: {e}")
            # Fall back to OpenWeatherMap if the configured provider fails
            from script.weather_providers.openweathermap import OpenWeatherMapProvider
            self.weather_provider = OpenWeatherMapProvider(
                api_key=self.api_key,
                units=self.units,
                language=self.language
            )
            self.weather_provider_name = 'openweathermap'
            logger.info("Falling back to OpenWeatherMap provider")
    
    def setup_connections(self):
        """Set up signal connections."""
        # Connect UI signals to slots
        self.ui.search_clicked.connect(self.on_search)
        self.ui.language_changed.connect(self.on_language_changed)
        self.ui.units_changed.connect(self.on_units_changed)
        self.ui.favorite_toggled.connect(self.on_toggle_favorite)
        self.ui.favorite_selected.connect(self.on_favorite_selected)
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        # Get translations for the current language
        translations = self.translations_manager.translations
        
        # Create the custom menu bar with translations
        menubar = create_menu_bar(self, translations=translations)
        
        # Connect signals
        menubar.refresh_triggered.connect(self.refresh_weather)
        menubar.units_changed.connect(self.on_units_changed)
        menubar.language_changed.connect(self.on_language_changed)
        menubar.theme_changed.connect(self.on_theme_changed)
        menubar.provider_changed.connect(self.update_weather_provider)
        
        # Set initial values
        menubar.set_units(self.units)
        menubar.set_languages(TRANSLATIONS.get('languages', {}), self.language)
        menubar.set_theme(self.config_manager.get('theme', 'dark'))
        
        # Set the menu bar
        self.setMenuBar(menubar)
    
    def on_search(self, city: str):
        """Handle search for a city's weather."""
        if not city or city.lower() == 'enter city name...':
            return
            
        self.city = city
        self.config_manager.set('last_city', city)
        self.refresh_weather()
    
    def refresh_weather(self):
        """Refresh the weather data for the current city."""
        if not self.city:
            return
            
        self.ui.set_status(f'Fetching weather for {self.city}...')
        self.ui.show_loading(True)
        
        # Use a thread to avoid blocking the UI
        def fetch_weather():
            try:
                weather_data = self.weather_provider.get_current_weather(self.city)
                return weather_data, None
            except requests.exceptions.HTTPError as http_err:
                error_msg = f"HTTP error occurred: {http_err}"
                if http_err.response.status_code == 404:
                    error_msg = f"City '{self.city}' not found. Please check the city name and try again."
                logging.error(error_msg)
                return None, error_msg
            except Exception as e:
                error_msg = f"Error fetching weather data: {str(e)}"
                logging.error(error_msg)
                return None, error_msg
        
        def update_ui(result):
            weather_data, error = result
            self.ui.show_loading(False)
            
            if error:
                self.ui.show_error(f"Failed to fetch weather: {error}")
                return
                
            self.update_weather_display(weather_data)
            self.ui.set_status('Ready')
        
        # Start the background task
        self._run_in_background(fetch_weather, update_ui)
    
    def update_weather_display(self, weather_data):
        """Update the UI with weather data."""
        # Clear previous weather widgets
        self.ui.clear_weather_display()
        
        # Create and add weather widgets based on the data
        if weather_data is None:
            self.ui.show_error("No weather data available")
            return
            
        # Create a widget for the current weather
        current_widget = QFrame()
        current_widget.setObjectName('currentWeather')
        current_widget.setStyleSheet('''
            QFrame#currentWeather {
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: #ecf0f1;
            }
            .temp {
                font-size: 24px;
                font-weight: bold;
            }
            .desc {
                font-size: 16px;
                color: #bdc3c7;
            }
        ''')
        
        layout = QVBoxLayout(current_widget)
        
        # City name
        city_label = QLabel(self.city.title() if hasattr(self, 'city') else 'N/A')
        city_label.setStyleSheet('font-size: 20px; font-weight: bold;')
        layout.addWidget(city_label)
        
        # Temperature
        temp = getattr(weather_data, 'temperature', 'N/A')
        temp_label = QLabel(f"{temp}°" if temp != 'N/A' else 'N/A')
        temp_label.setProperty('class', 'temp')
        layout.addWidget(temp_label)
        
        # Weather condition
        condition = getattr(weather_data, 'condition', 'N/A')
        desc_label = QLabel(condition.title() if condition != 'N/A' else 'N/A')
        desc_label.setProperty('class', 'desc')
        layout.addWidget(desc_label)
        
        # Additional weather details
        details = QFrame()
        details_layout = QHBoxLayout(details)
        
        # Humidity
        humidity = getattr(weather_data, 'humidity', 'N/A')
        humidity_widget = self._create_detail_widget("💧", f"{humidity}%" if humidity != 'N/A' else 'N/A')
        details_layout.addWidget(humidity_widget)
        
        # Wind
        wind_speed = getattr(weather_data, 'wind_speed', 'N/A')
        wind_widget = self._create_detail_widget("💨", f"{wind_speed} m/s" if wind_speed != 'N/A' else 'N/A')
        details_layout.addWidget(wind_widget)
        
        # Pressure
        pressure = getattr(weather_data, 'pressure', 'N/A')
        pressure_widget = self._create_detail_widget("📊", f"{pressure} hPa" if pressure != 'N/A' else 'N/A')
        details_layout.addWidget(pressure_widget)
        
        layout.addWidget(details)
        
        # Add to the UI
        self.ui.add_weather_widget(current_widget)
    
    def _create_detail_widget(self, icon: str, text: str) -> QWidget:
        """Create a widget for displaying a weather detail."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        
        return widget
    
    def on_language_changed(self, language: str):
        """Handle language change."""
        self.language = language
        self.config_manager.set('language', language)
        self.translations_manager.set_default_lang(language)
        self.weather_provider.language = language
        self.refresh_weather()
    
    def on_units_changed(self, units: str):
        """Handle units change."""
        self.units = units
        self.config_manager.set('units', units)
        self.weather_provider.units = units
        self.refresh_weather()
    
    def on_toggle_favorite(self, city: str):
        """Toggle a city as favorite."""
        if not city:
            return
            
        if self.favorites_manager.is_favorite(city):
            self.favorites_manager.remove_favorite(city)
            self.ui.update_favorite_button(False)
        else:
            self.favorites_manager.add_favorite(city)
            self.ui.update_favorite_button(True)
            
        self.update_favorites_menu()
    
    def on_favorite_selected(self, city: str):
        """Handle selection of a favorite city."""
        if city:
            self.city = city
            self.ui.set_city(city)
            self.refresh_weather()
    
    def update_favorites_menu(self):
        """Update the favorites dropdown in the UI."""
        favorites = self.favorites_manager.get_favorites()
        self.ui.update_favorites_list(favorites)
        
        # Update the favorite button state
        city = self.ui.search_input.text().strip()
        if city and city.lower() != 'enter city name...':
            is_favorite = self.favorites_manager.is_favorite(city)
            self.ui.update_favorite_button(is_favorite)
    
    def check_for_updates(self):
        """Check for application updates."""
        def check():
            try:
                checker = UpdateChecker(get_version())
                update_available, update_info = checker.check_for_updates(force=True)
                return update_available, update_info, None
            except Exception as e:
                logging.error(f"Error checking for updates: {e}")
                return False, None, ("Error", str(e))
        
        def update_ui(result):
            update_available, update_info, error_info = result
            
            if update_available and update_info:
                # Show update dialog
                checker = UpdateChecker(get_version())
                checker.show_update_dialog(self, update_info)
            elif error_info and error_info[0] and error_info[1]:
                QMessageBox.information(
                    self,
                    error_info[0],
                    error_info[1],
                    QMessageBox.StandardButton.Ok
                )
            else:
                QMessageBox.information(
                    self,
                    'No Updates',
                    'You are using the latest version.',
                    QMessageBox.StandardButton.Ok
                )
        
        # Start the background task
        self._run_in_background(check, update_ui)
    
    def show_about_dialog(self):
        """Show the about dialog."""
        from script.about import About
        About.show_about()
    
    def show_help_dialog(self):
        """Show the help dialog."""
        from script.help import Help
        Help.show_help(self, self.translations_manager, self.language)
    
    def _run_in_background(self, func, callback):
        """Run a function in the background and call callback with the result."""
        def run():
            result = func()
            QApplication.instance().postEvent(
                self,
                _CallbackEvent(callback, result)
            )
        
        import threading
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def event(self, event):
        """Handle custom events."""
        if isinstance(event, _CallbackEvent):
            event.callback(event.result)
            return True
        return super().event(event)

    def on_theme_changed(self, theme: str):
        """Handle theme change.
        
        Args:
            theme (str): The selected theme ('system', 'light', or 'dark')
        """
        # Save the theme preference
        self.config_manager.set('theme', theme)
        
        # Apply the theme
        if theme == 'dark':
            self.setStyleSheet('')
            app = QApplication.instance()
            app.setStyle('Fusion')
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            app.setPalette(dark_palette)
        elif theme == 'light':
            self.setStyleSheet('')
            app = QApplication.instance()
            app.setStyle('Fusion')
            light_palette = QPalette()
            light_palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            light_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            light_palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 231, 227))
            light_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
            light_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
            light_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
            light_palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            light_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
            light_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            light_palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
            light_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
            light_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
            app.setPalette(light_palette)
        else:  # system
            self.setStyleSheet('')
            app = QApplication.instance()
            app.setStyle('Windows' if sys.platform.startswith('win') else 'Fusion')
            app.setPalette(app.style().standardPalette())

    def update_weather_provider(self, provider_name: str) -> None:
        """Update the weather provider dynamically.
        
        Args:
            provider_name: Name of the weather provider to switch to
        """
        logger.info(f"Switching to weather provider: {provider_name}")
        
        try:
            # Save the new provider to config
            self.config_manager.set('weather_provider', provider_name)
            
            # Re-initialize the weather provider
            self.initialize_weather_provider()
            
            # Update the UI with the new provider
            if hasattr(self.ui, 'weather_provider'):
                self.ui.weather_provider = self.weather_provider
            
            # Refresh the weather data
            self.refresh_weather()
            
            logger.info(f"Successfully switched to {provider_name} provider")
            
        except Exception as e:
            logger.error(f"Failed to switch to {provider_name} provider: {str(e)}")
            QMessageBox.critical(
                self,
                self.tr('Provider Error'),
                self.tr(f'Failed to switch to {provider_name} provider: {str(e)}')
            )


class _CallbackEvent(QEvent):
    """Custom event for callbacks from background threads."""
    def __init__(self, callback, result):
        super().__init__(QEvent.Type.User)
        self.callback = callback
        self.result = result


def main():
    # Create the application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = WeatherApp()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
