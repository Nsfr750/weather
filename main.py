#!/usr/bin/env python3
"""
Weather Application - 1.6.0

A modern weather application that displays current weather, 7-day forecast,
and historical weather data using the Open-Meteo.com API.
"""

import sys
import os
import json
import webbrowser
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable

# Import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QSplitter, QStatusBar,
    QMessageBox, QDialog, QMenuBar, QMenu, QComboBox, QSystemTrayIcon, 
    QStyle, QGridLayout, QTabWidget, QFrame, QSizePolicy, QSpacerItem,
    QScrollArea, QStackedWidget, QInputDialog, QFileDialog, QDialogButtonBox
)
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtCore import Qt, QSize, QTimer, QUrl, QObject, pyqtSignal, pyqtSlot, QEvent, QThread, QMetaObject
from PyQt6.QtGui import QIcon, QPixmap, QAction, QFont, QPalette, QColor, QDesktopServices

# Import translations
from script.translations import TRANSLATIONS

# Import logger
from script.logger import setup_logging, logger

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
from script.history_utils import HistoryManager
from script.config_utils import ConfigManager
from script.translations import TRANSLATIONS
from script.translations_utils import TranslationsManager
from script.notifications import NotificationManager
from script.weather_providers.openmeteo import OpenMeteoProvider

# Constants
DEFAULT_CITY = "Rome, IT"
REFRESH_INTERVAL = 30 * 60 * 1000  # 30 minutes in milliseconds

# Configure logging
logger = setup_logging()
logger = logger.getChild('main')

class WeatherApp(QMainWindow):
    """Main application window for the Weather application."""
    
    def __init__(self):
        """Initialize the weather application."""
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
        
        # Initialize online status
        self.online = True  # Default to online, will be updated by check_connection()
        self.check_connection()
        
        # Initialize translations
        self.translations_manager = TranslationsManager(TRANSLATIONS, default_lang=self.language)
        
        # Initialize weather provider
        self.weather_provider = OpenMeteoProvider(units=self.units)
        
        # Initialize UI
        self.setWindowTitle(f'Weather v{get_version()}')
        self.setMinimumSize(800, 800)
        
        # Set application icon
        self.set_application_icon()
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar first to ensure it's at the bottom
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("Ready")
        
        # Create main content area
        self.create_main_content()
        
        # Set initial city from config or default
        self.city = self.config_manager.get('last_city', DEFAULT_CITY)
        
        # Load favorites and history
        self.favorites_manager = FavoritesManager()
        self.history_manager = HistoryManager()
        self.update_favorites_menu()
        
        # Set up refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_weather)
        self.refresh_timer.start(REFRESH_INTERVAL)
        
        # Initial weather update
        self.refresh_weather()
        
    def update_status(self, message: str, timeout: int = 0) -> None:
        """Update the status bar with a message.
        
        Args:
            message: The message to display
            timeout: Time in milliseconds to display the message (0 = show until next message)
        """
        if hasattr(self, 'status_bar') and self.status_bar is not None:
            self.status_bar.showMessage(message, timeout)
            self.status_bar.repaint()  # Force immediate update
    
    def create_menu_bar(self):
        """Create and set up the menu bar."""
        from script.menu import MenuBar
        
        # Create the menu bar
        self.menu_bar = MenuBar(
            parent=self,
            translations_manager=self.translations_manager,
            current_language=self.language,
            current_units=self.units
        )
        
        # Connect signals
        self.menu_bar.refresh_triggered.connect(self.refresh_weather)
        self.menu_bar.units_changed.connect(self.set_units)
        self.menu_bar.language_changed.connect(self.set_language)
        self.menu_bar.toggle_history.connect(self.toggle_history)
        self.menu_bar.add_to_favorites.connect(self.add_current_to_favorites)
        self.menu_bar.manage_favorites.connect(self.manage_favorites)
        self.menu_bar.favorite_selected.connect(self.set_location)
        self.menu_bar.show_about.connect(self.show_about)
        self.menu_bar.show_help.connect(self.show_help)
        self.menu_bar.show_md_viewer.connect(self.show_md_viewer)
        self.menu_bar.show_log_viewer.connect(self.show_log_viewer)
        self.menu_bar.show_sponsor.connect(self.show_sponsor)
        self.menu_bar.check_updates.connect(self.check_for_updates)
        self.menu_bar.exit_triggered.connect(self.close)
        
        # Set the menu bar
        self.setMenuBar(self.menu_bar)
        
        # Set the menu bar
        self.setMenuBar(self.menu_bar)
        
        # Update favorites menu state
        self.update_favorites_menu()
    
    def create_main_content(self):
        """Create the main content area with current weather, forecast, and history."""
        # Create main splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Current weather
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        # Search box
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search location...")
        self.search_input.returnPressed.connect(self.on_search)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_search)
        
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)
        
        # Current weather widget
        self.current_weather_widget = QWidget()
        self.current_weather_layout = QVBoxLayout(self.current_weather_widget)
        
        # Location and date
        self.location_label = QLabel("Location")
        self.location_label.setObjectName("locationLabel")
        self.date_label = QLabel("Date")
        self.date_label.setObjectName("dateLabel")
        
        # Current weather icon and temperature
        self.weather_icon = QLabel()
        self.weather_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temperature_label = QLabel("--°C")
        self.temperature_label.setObjectName("temperatureLabel")
        self.weather_description = QLabel("Weather description")
        self.weather_description.setObjectName("weatherDescription")
        
        # Weather details
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        
        self.feels_like_label = QLabel("Feels like: --°C")
        self.humidity_label = QLabel("Humidity: --%")
        self.wind_label = QLabel("Wind: -- km/h")
        self.pressure_label = QLabel("Pressure: -- hPa")
        self.visibility_label = QLabel("Visibility: -- km")
        
        for label in [self.feels_like_label, self.humidity_label, self.wind_label, 
                     self.pressure_label, self.visibility_label]:
            self.details_layout.addWidget(label)
        
        # Add widgets to current weather layout
        self.current_weather_layout.addWidget(self.location_label)
        self.current_weather_layout.addWidget(self.date_label)
        self.current_weather_layout.addStretch()
        self.current_weather_layout.addWidget(self.weather_icon)
        self.current_weather_layout.addWidget(self.temperature_label)
        self.current_weather_layout.addWidget(self.weather_description)
        self.current_weather_layout.addStretch()
        self.current_weather_layout.addWidget(self.details_widget)
        self.current_weather_layout.addStretch()
        
        # Forecast widget
        self.forecast_widget = QWidget()
        self.forecast_layout = QHBoxLayout(self.forecast_widget)
        self.forecast_layout.setSpacing(10)
        
        # Add widgets to left layout
        self.left_layout.addLayout(self.search_layout)
        self.left_layout.addWidget(self.current_weather_widget)
        self.left_layout.addWidget(QLabel("7-Day Forecast:"))
        self.left_layout.addWidget(self.forecast_widget)
        
        # Right panel - History (initially hidden)
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        
        self.history_title = QLabel("History")
        self.history_title.setObjectName("historyTitle")
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.clicked.connect(self.clear_history)
        
        self.history_layout.addWidget(self.history_title)
        self.history_layout.addWidget(self.history_list)
        self.history_layout.addWidget(self.clear_history_button)
        
        # Add widgets to splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.history_widget)
        self.history_widget.hide()  # Hide history by default
        
        # Set initial sizes (convert to integers)
        self.splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.splitter)
    
    def set_application_icon(self):
        """Set the application icon."""
        try:
            icon_path = Path('assets/meteo.png')
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            logger.warning(f'Could not set application icon: {e}')
    
    def check_connection(self):
        """Check internet connection and set offline mode accordingly."""
        try:
            requests.head('http://www.google.com', timeout=5)
            set_offline_mode(False)
            self.online = True
        except requests.RequestException:
            set_offline_mode(True)
            self.online = False
            QMessageBox.warning(
                self,
                'Offline Mode',
                'Internet connection not available. Running in offline mode with limited functionality.'
            )
    
    def refresh_weather(self):
        """Refresh weather data for the current location."""
        if not self.city:
            return
            
        self.update_status(f"Fetching weather data for {self.city}...")
        
        try:
            # Get current weather
            current_weather = self.weather_provider.get_weather(self.city)
            
            if "error" in current_weather:
                self.status_bar.showMessage(f"Error: {current_weather['error']}")
                return
            
            # Update UI with current weather
            self.update_current_weather(current_weather)
            
            # Get 7-day forecast
            forecast = self.weather_provider.get_forecast(self.city, days=7)
            
            if "error" not in forecast:
                self.update_forecast(forecast)
            
            # Update status bar
            self.update_status(f"Weather data for {self.city} updated at {datetime.now().strftime('%H:%M:%S')}", 5000)
            
            # Save last city to config
            self.config_manager.set('last_city', self.city)
            
        except Exception as e:
            logger.error(f"Error refreshing weather: {e}")
            self.update_status(f"Error: {str(e)}", 0)
    
    def update_current_weather(self, weather_data: Dict[str, Any]):
        """Update the UI with current weather data.
        
        Args:
            weather_data: Dictionary containing current weather data
        """
        try:
            # Update location and date
            location = weather_data.get("location", "--")
            self.location_label.setText(location)
            self.date_label.setText(datetime.now().strftime("%A, %B %d, %Y"))
            
            # Update temperature and description
            temp = weather_data.get("temperature", "--")
            unit = "°C" if self.units == "metric" else "°F"
            self.temperature_label.setText(f"{temp}{unit}" if temp != "--" else "--")
            
            # Update history entry with actual weather data if this was a new search
            if hasattr(self, 'city') and temp != "--":
                history = self.history_manager.get_history()
                for entry in history:
                    if entry.get("location") == self.city and (entry.get("temperature") == 0 or entry.get("temperature") == "--"):
                        feels_like = weather_data.get("feels_like", "--")
                        humidity = weather_data.get("humidity", "--")
                        wind_speed = weather_data.get("wind_speed", "--")
                        pressure = weather_data.get("pressure", "--")
                        visibility = weather_data.get("visibility", "--")
                        
                        entry.update({
                            "temperature": temp,
                            "feels_like": feels_like if feels_like != "--" else 0,
                            "humidity": humidity if humidity != "--" else 0,
                            "wind_speed": wind_speed if wind_speed != "--" else 0,
                            "pressure": pressure if pressure != "--" else 0,
                            "visibility": visibility if visibility != "--" else 0,
                            "timestamp": datetime.now()
                        })
                        self.history_manager.save_history()
                        self.update_history_list()
                        break
            
            self.weather_description.setText(weather_data.get("description", "--"))
            
            # Update weather icon
            icon_name = weather_data.get("icon", "01d")
            icon_path = Path(f"assets/weather_icons/{icon_name}.png")
            if icon_path.exists():
                pixmap = QPixmap(str(icon_path)).scaled(100, 100, 
                                                       Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation)
                self.weather_icon.setPixmap(pixmap)
            
            # Get weather details
            feels_like = weather_data.get("feels_like", "--")
            humidity = weather_data.get("humidity", "--")
            wind_speed = weather_data.get("wind_speed", "--")
            pressure = weather_data.get("pressure", "--")
            visibility = weather_data.get("visibility", "--")
            
            # Set units based on current unit system
            wind_unit = "km/h" if self.units == "metric" else "mph"
            visibility_unit = "km" if self.units == "metric" else "miles"
            
            # Update UI with weather details
            self.feels_like_label.setText(f"Feels like: {feels_like}{unit}" if feels_like != "--" else "Feels like: --")
            self.humidity_label.setText(f"Humidity: {humidity}%" if humidity != "--" else "Humidity: --")
            self.wind_label.setText(f"Wind: {wind_speed} {wind_unit}" if wind_speed != "--" else "Wind: --")
            self.pressure_label.setText(f"Pressure: {pressure} hPa" if pressure != "--" else "Pressure: --")
            self.visibility_label.setText(f"Visibility: {visibility} {visibility_unit}" if visibility != "--" else "Visibility: --")
            
        except Exception as e:
            logger.error(f"Error updating current weather: {e}")
    
    def update_forecast(self, forecast_data: Dict[str, Any]):
        """Update the UI with forecast data.
        
        Args:
            forecast_data: Dictionary containing forecast data
        """
        try:
            # Clear existing forecast widgets
            while self.forecast_layout.count():
                item = self.forecast_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Add forecast days
            days = forecast_data.get("days", [])
            unit = "°C" if self.units == "metric" else "°F"
            
            for day in days[:7]:  # Show next 7 days
                day_widget = QWidget()
                day_layout = QVBoxLayout(day_widget)
                day_layout.setContentsMargins(5, 5, 5, 5)
                
                # Day name and date
                date = datetime.strptime(day.get("date", ""), "%Y-%m-%d")
                day_name = date.strftime("%A")
                date_str = date.strftime("%b %d")
                day_label = QLabel(f"{day_name}\n{date_str}")
                day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Weather icon
                icon_label = QLabel()
                icon_path = Path(f"assets/weather_icons/{day.get('icon', '01d')}.png")
                if icon_path.exists():
                    pixmap = QPixmap(str(icon_path)).scaled(64, 64, 
                                                          Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation)
                    icon_label.setPixmap(pixmap)
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Temperature range
                temp_max = day.get("temp_max", "--")
                temp_min = day.get("temp_min", "--")
                temp_text = f"{temp_max}{unit} / {temp_min}{unit}" if temp_max != "--" and temp_min != "--" else "--"
                temp_label = QLabel(temp_text)
                temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Description
                desc_label = QLabel(day.get("description", "--"))
                desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                desc_label.setWordWrap(True)
                
                # Add widgets to day layout
                day_layout.addWidget(day_label)
                day_layout.addWidget(icon_label)
                day_layout.addWidget(temp_label)
                day_layout.addWidget(desc_label)
                
                # Add day widget to forecast layout
                self.forecast_layout.addWidget(day_widget)
            
            # Add stretch to push content to the top
            self.forecast_layout.addStretch()
            
        except Exception as e:
            logger.error(f"Error updating forecast: {e}")
            logger.exception("Forecast update error:")
    
    def update_history_list(self):
        """Update the history list with recent searches."""
        try:
            self.history_list.clear()
            history = self.history_manager.get_history()
            
            for item in history:
                location = item.get("location", "Unknown Location")
                temp = item.get("temperature", "--")
                unit = "°C" if self.units == "metric" else "°F"
                
                # Handle both string and datetime timestamps
                timestamp = item.get("timestamp")
                if isinstance(timestamp, str):
                    try:
                        # Try to parse the timestamp string
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        timestamp = datetime.now()
                elif not isinstance(timestamp, datetime):
                    timestamp = datetime.now()
                
                date_str = timestamp.strftime("%Y-%m-%d %H:%M")
                
                list_item = QListWidgetItem(f"{location}: {temp}{unit} on {date_str}")
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.history_list.addItem(list_item)
                
        except Exception as e:
            logger.error(f"Error updating history list: {e}")
            logger.exception("Full exception:")
    
    def on_search(self):
        """Handle search button click or Enter key press."""
        city = self.search_input.text().strip()
        if city:
            # Add to history before setting location
            # We'll update the weather details after we get the weather data
            self.history_manager.add_entry(
                location=city,
                temperature=0,  # Will be updated after we get the weather data
                timestamp=datetime.now(),
                feels_like=0,
                humidity=0,
                wind_speed=0,
                pressure=0,
                visibility=0
            )
            self.update_history_list()
            self.city = city
            self.update_status(f"Searching for {city}...")
            self.refresh_weather()
    
    def on_history_item_clicked(self, item):
        """Handle history item click to load that weather data."""
        weather_data = item.data(Qt.ItemDataRole.UserRole)
        if weather_data:
            self.city = weather_data.get("location", self.city)
            self.update_current_weather(weather_data)
            
            # Get forecast for this location
            forecast = self.weather_provider.get_forecast(self.city, days=7)
            if "error" not in forecast:
                self.update_forecast(forecast)
    
    def clear_history(self):
        """Clear the search history."""
        reply = QMessageBox.question(
            self, 
            'Clear History',
            'Are you sure you want to clear your search history?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.history_manager.clear_history():
                self.update_history_list()
                self.update_status("History cleared", 3000)
            else:
                self.update_status("Failed to clear history", 3000)
    
    def toggle_history(self, checked: bool):
        """Toggle the visibility of the history panel."""
        self.history_widget.setVisible(checked)
        
        # Update the menu bar's toggle action text
        if hasattr(self, 'menu_bar') and hasattr(self.menu_bar, 'toggle_history_action'):
            self.menu_bar.toggle_history_action.setText("Hide History" if checked else "Show History")
        
        # Update window size if showing history
        if checked:
            self.update_history_list()
            self.resize(self.width() + 300, self.height())
            self.update_status("History panel shown", 3000)
    
    def set_units(self, units: str):
        """Set the units system and refresh weather data."""
        if units not in ["metric", "imperial"]:
            logger.warning(f"Invalid units: {units}")
            return
            
        self.units = units
        self.config_manager.set('units', units)
        self.weather_provider.set_units(units)
        self.update_status(f"Units changed to {units}", 3000)
        self.refresh_weather()
        
    def set_language(self, language: str):
        """Set the application language."""
        try:
            logger.info(f"Attempting to change language to: {language}")
            
            # Convert to uppercase for consistency
            language = language.upper()
            
            # Get available languages in uppercase for comparison
            available_languages = [lang.upper() for lang in self.translations_manager.available_languages()]
            logger.debug(f"Available languages: {available_languages}")
            
            if language not in available_languages:
                logger.warning(f"Unsupported language: {language}")
                return
                
            logger.info(f"Setting language to: {language}")
            self.language = language
            self.config_manager.set('language', language)
            
            # Update the translations manager with the new language
            self.translations_manager.set_language(language)
            
            # Update status bar with translated message
            self.update_status(f"Language changed to {language}", 3000)
            
            # Update all UI elements with new translations
            self.retranslate_ui()
            
            # Refresh weather data to get updates in the new language
            logger.info("Refreshing weather data with new language...")
            self.refresh_weather()
            
            logger.info(f"Successfully changed language to {language}")
        except Exception as e:
            logger.error(f"Error changing language: {str(e)}", exc_info=True)
            self.update_status(f"Error changing language: {str(e)}", 5000)
        
    def retranslate_ui(self):
        """Update all UI text elements with the current language."""
        try:
            logger.info("Updating UI translations...")
            
            # Get translations manager
            t = self.translations_manager.t
            
            # Update window title
            self.setWindowTitle(f'{t("Weather")} v{get_version()}')
            
            # Update search box
            if hasattr(self, 'search_input'):
                self.search_input.setPlaceholderText(t("search"))
            
            if hasattr(self, 'search_button'):
                self.search_button.setText(t("search"))
            
            # Update status bar
            self.update_status(t("Ready"))
            
            # Update menu bar translations
            if hasattr(self, 'menu_bar') and hasattr(self.menu_bar, 'update_translations'):
                translations = {
                    'Search': t('search'),
                    'Refresh': t('refresh'),
                    'View': t('view'),
                    'History': t('history'),
                    'Favorites': t('favorites'),
                    'Add to Favorites': t('add_favorite'),
                    'Manage Favorites': t('manage_favorites'),
                    'Settings': t('settings'),
                    'Units': t('units'),
                    'Language': t('language'),
                    'Help': t('help'),
                    'About': t('about'),
                    'Check for Updates': t('check_updates'),
                    'Exit': t('exit'),
                    'Metric': t('units_metric'),
                    'Imperial': t('units_imperial'),
                    'File': t('file'),
                    'Open': t('open'),
                    'Close': t('close'),
                    'Zoom In': t('zoom_in'),
                    'Zoom Out': t('zoom_out'),
                    'Reset Zoom': t('reset_zoom'),
                    'Documentation': t('documentation'),
                    'Open Documentation': t('open_documentation'),
                    'Sponsor': t('sponsor')
                }
                logger.debug(f"Updating menu translations: {translations}")
                self.menu_bar.update_translations(translations)
            
            # Update section headers
            if hasattr(self, 'current_weather_label'):
                self.current_weather_label.setText(t('current_weather'))
                
            if hasattr(self, 'forecast_label'):
                self.forecast_label.setText(t('forecast'))
                
            if hasattr(self, 'history_label'):
                self.history_label.setText(t('recent_searches'))
                
            # Update other UI elements
            if hasattr(self, 'clear_history_btn'):
                self.clear_history_btn.setText(t('clear_history'))
                
            if hasattr(self, 'temperature_label'):
                self.temperature_label.setText(f"{t('temperature')}:")
                
            if hasattr(self, 'humidity_label'):
                self.humidity_label.setText(f"{t('humidity')}:")
                
            if hasattr(self, 'wind_label'):
                self.wind_label.setText(f"{t('wind')}:")
                
            logger.info("UI translations updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating UI translations: {str(e)}", exc_info=True)
    
    def update_favorites_menu(self):
        """Update the favorites menu with current favorites."""
        if not hasattr(self, 'menu_bar'):
            return
            
        # Update the favorites menu in the menu bar if it exists
        if hasattr(self.menu_bar, 'update_favorites_menu'):
            favorites = self.favorites_manager.get_favorites()
            self.menu_bar.update_favorites_menu(has_favorites=bool(favorites))
    
    def add_current_to_favorites(self):
        """Add the current location to favorites."""
        if not self.city:
            return
            
        name, ok = QInputDialog.getText(
            self,
            'Add to Favorites',
            'Enter a name for this location:',
            QLineEdit.EchoMode.Normal,
            self.city
        )
        
        if ok and name:
            self.favorites_manager.add_favorite(name, self.city)
            self.update_favorites_menu()
            self.update_status(f"Added {name} to favorites")
    
    def manage_favorites(self):
        """Open the favorites management dialog."""
        from script.favorites_dialog import FavoritesDialog
        from PyQt6.QtWidgets import QDialog
        
        # Create and show the favorites dialog
        dialog = FavoritesDialog(self.favorites_manager, self)
        result = dialog.exec()
        
        # Update the favorites menu if the dialog was accepted
        if result == QDialog.DialogCode.Accepted:
            self.update_favorites_menu()
            
            # If the current city is in favorites, update the UI
            if self.favorites_manager.is_favorite(self.city):
                self.update_favorites_menu()
    
    def set_location(self, location: str):
        """Set the current location and refresh weather data."""
        if location:
            self.city = location
            self.search_input.setText(location)
            self.refresh_weather()
    
    def show_about(self):
        """Show the About dialog."""
        about = About(self)
        about.exec()
    
    def show_help(self):
        """Show the Help dialog."""
        help_dialog = Help(self, self.translations_manager, self.language)
        help_dialog.exec()
    
    def check_for_updates(self):
        """Check for application updates."""
        self.status_bar.showMessage("Checking for updates...")
        
        try:
            update_checker = UpdateChecker()
            update_available, version, url = update_checker.check_for_updates()
            
            if update_available:
                reply = QMessageBox.information(
                    self,
                    'Update Available',
                    f'Version {version} is available. Would you like to download it now?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes and url:
                    QDesktopServices.openUrl(QUrl(url))
            else:
                QMessageBox.information(
                    self,
                    'No Updates',
                    'You are using the latest version of Weather App.'
                )
                
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            QMessageBox.critical(
                self,
                'Update Error',
                f'An error occurred while checking for updates: {str(e)}'
            )
        finally:
            self.status_bar.clearMessage()
    
    def show_md_viewer(self):
        """Show the Markdown documentation viewer."""
        try:
            from script.md_viewer import MarkdownViewer
            self.md_viewer = MarkdownViewer(language=self.language.upper())
            self.md_viewer.show()
        except Exception as e:
            logger.error(f"Error showing markdown viewer: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open documentation: {str(e)}",
                QMessageBox.StandardButton.Ok
            )
    
    def show_log_viewer(self):
        """Show the application log viewer."""
        try:
            from script.log_viewer import LogViewer  # Assuming this exists
            self.log_viewer = LogViewer()
            self.log_viewer.show()
        except Exception as e:
            logger.error(f"Error showing log viewer: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open log viewer: {str(e)}",
                QMessageBox.StandardButton.Ok
            )
    
    def show_sponsor(self):
        """Show the Sponsor dialog."""
        from script.sponsor import Sponsor
        sponsor_dialog = Sponsor(self)
        sponsor_dialog.exec()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window size and position
        self.config_manager.set('window/geometry', self.saveGeometry().data().hex())
        self.config_manager.set('window/state', self.saveState().data().hex())
        
        # Save history visibility
        self.config_manager.set('ui/show_history', self.history_widget.isVisible())
        
        event.accept()


def main():
    """Main function to run the application."""
    # Create application instance
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set application info
    app.setApplicationName("Weather App")
    app.setApplicationVersion(get_version())
    app.setOrganizationName("Nsfr750")
    
    # Create and show main window
    window = WeatherApp()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
