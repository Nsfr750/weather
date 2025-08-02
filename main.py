import sys
import os
import asyncio
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
from PyQt6.QtCore import Qt, QSize, QTimer, QUrl, QObject, pyqtSignal, pyqtSlot, QEvent, QThread, QMetaObject
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
from script.plugin_system.plugin_manager import PluginManager
from script.plugin_system.feature_manager import FeatureManager, BaseFeature
from script.plugin_system.weather_provider import BaseWeatherProvider

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
        
        # Initialize online status
        self.online = True  # Default to online, will be updated by check_connection()
        
        # Set offline mode if no internet
        self.check_connection()
        
        # Initialize the plugin manager with all possible plugin paths
        script_dir = Path(__file__).parent.absolute()
        plugin_paths = [
            script_dir / 'script' / 'plugins' / 'weather_providers',
            script_dir / 'script' / 'plugins' / 'features',
            script_dir / 'plugins' / 'weather_providers',
            script_dir / 'plugins' / 'features'
        ]
        
        # Filter out non-existent paths and log them
        self.plugin_manager = PluginManager([p for p in plugin_paths if p.exists()])
        
        # Set the plugin manager for the weather providers module
        from script.weather_providers import set_plugin_manager
        set_plugin_manager(self.plugin_manager)
        
        # Log the paths we're actually using
        logger.info(f"Looking for plugins in: {[str(p) for p in self.plugin_manager.plugin_dirs]}")
        
        # Log which plugin directories exist
        for path in plugin_paths:
            logger.info(f"Plugin path '{path}' exists: {path.exists()}")
        
        # Load plugins
        try:
            self.plugin_manager.load_plugins()
            logger.info(f"Successfully loaded {len(self.plugin_manager.plugins)} plugins")
            if self.plugin_manager.plugins:
                logger.info(f"Available plugins: {list(self.plugin_manager.plugins.keys())}")
        except Exception as e:
            logger.error(f"Error loading plugins: {e}", exc_info=True)
        
        # Initialize weather provider (needs plugin_manager to be initialized)
        self.initialize_weather_provider()
        
        # Initialize translations
        self.translations_manager = TranslationsManager(TRANSLATIONS, default_lang=self.language)
        
        # Initialize feature manager
        self.feature_manager = FeatureManager(self.plugin_manager)
        
        # Load features from all plugin directories
        for plugin_dir in self.plugin_manager.plugin_dirs:
            features_dir = plugin_dir / 'features'
            if features_dir.exists():
                self.feature_manager.load_features(str(features_dir))
        
        # Initialize UI
        self.setWindowTitle('Weather App')
        self.setMinimumSize(600, 800)
        
        # Set application icon
        self.set_application_icon()
        
        # Initialize the UI
        self.ui = WeatherAppUI(
            config_manager=self.config_manager,
            translations_manager=self.translations_manager,
            weather_provider=self.weather_provider,
            notification_manager=self.notification_manager,
            plugin_manager=self.plugin_manager
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
            self.online = True
        except requests.RequestException:
            set_offline_mode(True)
            self.online = False
            QMessageBox.warning(
                self,
                'Offline Mode',
                'Internet connection not available. Running in offline mode with limited functionality.'
            )
    
    def initialize_weather_provider(self):
        """Initialize the weather provider based on configuration."""
        from script.weather_providers.openmeteo import OpenMeteoProvider
        
        # Set default provider to legacy OpenMeteo
        self.weather_provider_name = 'openmeteo'
        logger.info("Initializing legacy OpenMeteo provider")
        
        try:
            # Initialize the legacy OpenMeteo provider with keyword arguments
            self.weather_provider = OpenMeteoProvider(
                api_key=self.config_manager.get('api_key', ''),
                units=self.units,
                language=self.language,
                offline_mode=not self.online
            )
            logger.info("Successfully initialized legacy OpenMeteo provider")
        except Exception as e:
            error_msg = f"Failed to initialize legacy OpenMeteo provider: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
    
    def setup_connections(self):
        """Set up signal connections."""
        # Connect UI signals to slots
        self.ui.search_clicked.connect(self.on_search)
        self.ui.language_changed.connect(self.on_language_changed)
        self.ui.units_changed.connect(self.on_units_changed)
        self.ui.favorite_toggled.connect(self.on_toggle_favorite)
        self.ui.favorite_selected.connect(self.on_favorite_selected)
    
    def update_weather_provider(self, provider_name: str):
        """Update the weather provider dynamically.
        
        Args:
            provider_name: Name of the weather provider to switch to
        """
        logger.info(f"Switching to weather provider: {provider_name}")
        
        # Show a status message
        self.statusBar().showMessage(f"Switching to {provider_name} provider...")
        
        try:
            # Save the new provider to config
            self.config_manager.set('weather_provider', provider_name)
            
            # Store the current city to restore it after provider switch
            current_city = self.city
            
            # Re-initialize the weather provider
            self.weather_provider_name = provider_name
            self.initialize_weather_provider()
            
            # Update the UI with the new provider
            if hasattr(self.ui, 'weather_provider'):
                self.ui.weather_provider = self.weather_provider
            
            # Update the provider in the menu bar if it exists
            if hasattr(self, 'menuBar') and hasattr(self.menuBar(), 'set_current_provider'):
                self.menuBar().set_current_provider(provider_name)
            
            # Restore the city and refresh weather data
            self.city = current_city
            self.refresh_weather()
            
            # Show success message
            self.statusBar().showMessage(f"Successfully switched to {provider_name}", 3000)
            logger.info(f"Successfully switched to {provider_name} provider")
            
        except Exception as e:
            error_msg = f"Failed to switch to {provider_name} provider: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Show error in status bar and message box
            self.statusBar().showMessage("Failed to switch weather provider", 3000)
            QMessageBox.critical(
                self,
                self.tr('Provider Error'),
                self.tr(error_msg)
            )
            
            # Try to revert to the previous provider
            try:
                prev_provider = self.config_manager.get('previous_provider', 'openweathermap')
                if prev_provider != provider_name:
                    self.update_weather_provider(prev_provider)
            except Exception as revert_error:
                logger.error(f"Failed to revert to previous provider: {revert_error}")
        finally:
            # Clear any status message after a delay
            QTimer.singleShot(3000, self.statusBar().clearMessage)
    
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
        async def fetch_weather_async():
            try:
                # Fetch both current weather and forecast
                current, forecast = await asyncio.gather(
                    self.weather_provider.get_current_weather(self.city),
                    self.weather_provider.get_forecast(self.city, days=5)
                )
                
                # Combine the data
                if hasattr(forecast, 'daily') and forecast.daily:
                    current.daily = forecast.daily
                
                return current, None
                
            except requests.exceptions.HTTPError as http_err:
                error_msg = f"HTTP error occurred: {http_err}"
                if hasattr(http_err, 'response') and http_err.response.status_code == 404:
                    error_msg = f"City '{self.city}' not found. Please check the city name and try again."
                logger.error(error_msg)
                return None, error_msg
            except Exception as e:
                error_msg = f"Error fetching weather data: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return None, error_msg
        
        def fetch_weather():
            loop = None
            try:
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Initialize the weather provider's session in this thread
                if hasattr(self.weather_provider, 'initialize'):
                    loop.run_until_complete(self.weather_provider.initialize())
                
                # Run the async function and get the result
                future = asyncio.ensure_future(fetch_weather_async(), loop=loop)
                result = loop.run_until_complete(asyncio.shield(future))
                return result
                
            except asyncio.CancelledError:
                logger.warning("Weather fetch was cancelled")
                return None, "Weather fetch was cancelled"
                
            except Exception as e:
                error_msg = f"Error in weather fetch thread: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return None, error_msg
                
            finally:
                # Clean up the weather provider's session
                if hasattr(self.weather_provider, 'cleanup'):
                    try:
                        loop.run_until_complete(self.weather_provider.cleanup())
                    except Exception as e:
                        logger.error(f"Error during provider cleanup: {e}", exc_info=True)
                
                # Clean up the event loop
                if loop is not None:
                    try:
                        # Cancel all pending tasks
                        pending = asyncio.all_tasks(loop)
                        for task in pending:
                            task.cancel()
                            try:
                                loop.run_until_complete(task)
                            except (asyncio.CancelledError, Exception):
                                pass
                        
                        # Run one more time to process any pending callbacks
                        loop.run_until_complete(asyncio.sleep(0))
                        
                        # Stop the loop if it's still running
                        if loop.is_running():
                            loop.stop()
                        
                        # Close the loop
                        loop.close()
                        
                    except Exception as e:
                        logger.error(f"Error cleaning up event loop: {e}", exc_info=True)
                    
                    # Set the event loop to None
                    asyncio.set_event_loop(None)
        
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
        try:
            # Ensure we're on the main thread for UI updates
            if QThread.currentThread() != self.thread():
                # If not on the main thread, use QMetaObject.invokeMethod to call this method on the main thread
                QMetaObject.invokeMethod(
                    self, 
                    'update_weather_display', 
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(object, weather_data)
                )
                return
                
            # Clear previous weather widgets on the main thread
            self.ui.clear_weather_display()
            
            # Check if we have valid weather data
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
                    padding: 20px;
                    margin: 10px 0;
                }
                QLabel {
                    color: white;
                }
                .temp {
                    font-size: 36px;
                    font-weight: bold;
                }
                .desc {
                    font-size: 16px;
                    margin: 8px 0;
                    opacity: 0.9;
                }
            ''')
            
            layout = QVBoxLayout(current_widget)
            
            # City name and date
            city = getattr(weather_data, 'city', self.city) if hasattr(weather_data, 'city') else self.city
            timestamp = getattr(weather_data, 'timestamp', None)
            date_str = timestamp.strftime('%A, %B %d, %Y') if hasattr(timestamp, 'strftime') else datetime.now().strftime('%A, %B %d, %Y')
            
            city_label = QLabel(f"{city.title()}")
            city_label.setStyleSheet('font-size: 20px; font-weight: bold;')
            city_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            city_label.setWordWrap(True)
            layout.addWidget(city_label)
            
            date_label = QLabel(date_str)
            date_label.setStyleSheet('font-size: 14px; opacity: 0.8; margin-bottom: 10px;')
            date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(date_label)
            
            # Weather icon and temperature
            weather_layout = QHBoxLayout()
            
            # Weather icon - use a placeholder first
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setMinimumSize(80, 80)  # Reduced from 100x100
            icon_label.setMaximumSize(80, 80)  # Add maximum size to maintain consistency
            weather_layout.addWidget(icon_label, 1)
            
            # Temperature and description
            temp = getattr(weather_data, 'temperature', 'N/A')
            temp_text = f"{round(float(temp))}°" if temp != 'N/A' and str(temp).replace('.', '').isdigit() else 'N/A'
            temp_label = QLabel(temp_text)
            temp_label.setProperty('class', 'temp')
            
            condition = getattr(weather_data, 'description', getattr(weather_data, 'condition', 'N/A'))
            desc_text = str(condition).title() if condition != 'N/A' else 'N/A'
            desc_label = QLabel(desc_text)
            desc_label.setProperty('class', 'desc')
            
            temp_layout = QVBoxLayout()
            temp_layout.addWidget(temp_label)
            temp_layout.addWidget(desc_label)
            temp_layout.addStretch()
            weather_layout.addLayout(temp_layout, 1)
            
            layout.addLayout(weather_layout)
            
            # Additional weather details
            details = QFrame()
            details_layout = QHBoxLayout(details)
            details_layout.setSpacing(10)
            
            # Humidity
            humidity = getattr(weather_data, 'humidity', 'N/A')
            humidity_text = f"{humidity}%" if humidity != 'N/A' and str(humidity).isdigit() else 'N/A'
            humidity_widget = self._create_detail_widget("💧", f"Humidity\n{humidity_text}")
            details_layout.addWidget(humidity_widget)
            
            # Wind
            wind_speed = getattr(weather_data, 'wind_speed', 'N/A')
            wind_text = f"{wind_speed} m/s" if wind_speed != 'N/A' and str(wind_speed).replace('.', '').isdigit() else 'N/A'
            wind_widget = self._create_detail_widget("💨", f"Wind\n{wind_text}")
            details_layout.addWidget(wind_widget)
            
            # Pressure
            pressure = getattr(weather_data, 'pressure', 'N/A')
            pressure_text = f"{pressure} hPa" if pressure != 'N/A' and str(pressure).isdigit() else 'N/A'
            pressure_widget = self._create_detail_widget("📊", f"Pressure\n{pressure_text}")
            details_layout.addWidget(pressure_widget)
            
            layout.addWidget(details)
            
            # Add current weather to the UI
            self.ui.add_weather_widget(current_widget)
            
            # Load the icon asynchronously to prevent UI freezing
            self._load_weather_icon_async(icon_label, getattr(weather_data, 'icon', None) or getattr(weather_data, 'condition', 'clear'))
            
            # Add 5-day forecast if available
            daily_forecast = getattr(weather_data, 'daily', None)
            if daily_forecast and len(daily_forecast) > 0:
                # Create forecast container
                forecast_frame = QFrame()
                forecast_frame.setObjectName('forecastFrame')
                forecast_frame.setStyleSheet('''
                    QFrame#forecastFrame {
                        background-color: rgba(44, 62, 80, 0.7);
                        border-radius: 10px;
                        padding: 15px;
                        margin: 10px 0;
                    }
                    QLabel {
                        color: white;
                    }
                ''')
                
                forecast_layout = QVBoxLayout(forecast_frame)
                forecast_layout.setContentsMargins(5, 5, 5, 5)
                forecast_layout.setSpacing(10)
                
                # Add section title
                title_label = QLabel('5-Day Forecast')
                title_font = QFont()
                title_font.setBold(True)
                title_font.setPointSize(14)
                title_label.setFont(title_font)
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                forecast_layout.addWidget(title_label)
                
                # Create scroll area for forecast days
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                scroll.setStyleSheet('''
                    QScrollArea {
                        border: none;
                        background: transparent;
                    }
                    QScrollBar:vertical {
                        border: none;
                        background: rgba(200, 200, 200, 50);
                        width: 8px;
                        margin: 0px;
                        border-radius: 4px;
                    }
                    QScrollBar::handle:vertical {
                        background: rgba(255, 255, 255, 150);
                        border-radius: 4px;
                        min-height: 20px;
                    }
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                        height: 0px;
                    }
                ''')
                
                # Container widget for forecast days
                days_container = QWidget()
                days_layout = QHBoxLayout(days_container)
                days_layout.setSpacing(15)
                days_layout.setContentsMargins(5, 5, 5, 5)
                
                # Get next 5 days (or as many as available)
                for i, day in enumerate(daily_forecast[:5]):
                    day_widget = QFrame()
                    day_widget.setObjectName('dayWidget')
                    day_widget.setStyleSheet('''
                        QFrame#dayWidget {
                            background-color: rgba(255, 255, 255, 0.1);
                            border-radius: 8px;
                            padding: 10px;
                            min-width: 100px;
                        }
                    ''')
                    
                    day_layout = QVBoxLayout(day_widget)
                    day_layout.setSpacing(8)
                    day_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                    
                    # Day of week and date
                    timestamp = getattr(day, 'timestamp', datetime.now() + timedelta(days=i+1))
                    day_name = timestamp.strftime('%A')
                    date_str = timestamp.strftime('%b %d')
                    
                    day_label = QLabel(day_name)
                    day_label.setStyleSheet('font-size: 12px; font-weight: bold;')
                    day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    date_label = QLabel(date_str)
                    date_label.setStyleSheet('font-size: 11px; opacity: 0.8;')
                    date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Weather icon
                    icon_label = QLabel()
                    condition = getattr(day, 'condition', getattr(day, 'weather', [{}])[0].get('main', 'clear') if hasattr(day, 'weather') else 'clear')
                    icon_pixmap = get_icon_image(condition, 20)  # Reduced from 48px
                    if icon_pixmap:
                        icon_label.setPixmap(icon_pixmap)
                    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    icon_label.setMinimumSize(20, 20)  # Ensure consistent icon size
                    icon_label.setMaximumSize(20, 20)
                    
                    # Temperature
                    temp_min = getattr(day, 'temperature_min', getattr(day, 'temp', {}).get('min', 'N/A'))
                    temp_max = getattr(day, 'temperature_max', getattr(day, 'temp', {}).get('max', 'N/A'))
                    
                    temp_text = 'N/A'
                    if temp_min != 'N/A' and temp_max != 'N/A':
                        temp_text = f"{round(float(temp_max))}° / {round(float(temp_min))}°"
                    
                    temp_label = QLabel(temp_text)
                    temp_label.setStyleSheet('font-size: 13px; font-weight: bold;')
                    temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Description
                    desc = getattr(day, 'description', 
                                 getattr(day, 'weather', [{}])[0].get('description', 'N/A') if hasattr(day, 'weather') else 'N/A')
                    desc_text = str(desc).capitalize() if desc != 'N/A' else 'N/A'
                    desc_label = QLabel(desc_text)
                    desc_label.setStyleSheet('font-size: 11px; opacity: 0.9;')
                    desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    desc_label.setWordWrap(True)
                    
                    # Add widgets to day layout with proper spacing
                    day_layout.addWidget(day_label)
                    day_layout.addWidget(date_label)
                    day_layout.addSpacing(2)
                    day_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
                    day_layout.addSpacing(2)
                    day_layout.addWidget(temp_label)
                    day_layout.addWidget(desc_label)
                    day_layout.addStretch()
                    
                    # Add day widget to days layout
                    days_layout.addWidget(day_widget)
                
                # Add stretch to push days to the left
                days_layout.addStretch()
                
                # Set up scroll area
                scroll.setWidget(days_container)
                forecast_layout.addWidget(scroll)
                
                # Add forecast frame to the UI
                self.ui.add_weather_widget(forecast_frame)
                
        except Exception as e:
            logger.error(f"Error updating weather display: {str(e)}", exc_info=True)
            self.ui.show_error(f"Error displaying weather: {str(e)}")
    
    def _load_weather_icon_async(self, icon_label, icon_code, size=(20, 20)):
        """Load a weather icon asynchronously to prevent UI freezing.
        
        Args:
            icon_label: The QLabel to set the icon on
            icon_code: The icon code or URL to load
            size: The size of the icon (width, height)
        """
        # Create a worker function to load the icon
        def load_icon():
            try:
                # Load the icon (this is thread-safe as it doesn't interact with the UI)
                pixmap = get_icon_image(icon_code, size)
                if not pixmap or pixmap.isNull():
                    return None
                return pixmap
            except Exception as e:
                logging.error(f"Error loading icon {icon_code}: {e}")
                return None
        
        # Create a callback function to update the UI on the main thread
        def update_ui(pixmap):
            if pixmap and not pixmap.isNull() and icon_label:
                try:
                    # This runs on the main thread
                    icon_label.setPixmap(pixmap)
                except Exception as e:
                    logging.error(f"Error updating icon UI: {e}")
        
        # Run the icon loading in a thread
        self._run_in_background(load_icon, update_ui)
    
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
        
        # Update weather provider language if supported
        if hasattr(self.weather_provider, 'language'):
            self.weather_provider.language = language
        
        # Update UI elements
        self.ui.set_language(language)
        
        # Refresh the weather to update all text
        self.refresh_weather()
        
        # Update window title
        self.setWindowTitle(self.translations_manager.t('app_title', language) or 'Weather App')
        
        # Update menu bar
        if hasattr(self, 'menu_bar'):
            self.menu_bar.set_languages(
                self.translations_manager.translations.get('languages', {}), 
                language
            )
    
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

    def update_weather_provider(self, provider_name: str):
        """Update the weather provider dynamically.
        
        Args:
            provider_name: Name of the weather provider to switch to
        """
        logger.info(f"Switching to weather provider: {provider_name}")
        
        # Show a status message
        status_message = self.statusBar().showMessage(f"Switching to {provider_name} provider...")
        
        try:
            # Save the new provider to config
            self.config_manager.set('weather_provider', provider_name)
            
            # Store the current city to restore it after provider switch
            current_city = self.city
            
            # Re-initialize the weather provider
            self.weather_provider_name = provider_name
            self.initialize_weather_provider()
            
            # Update the UI with the new provider
            if hasattr(self.ui, 'weather_provider'):
                self.ui.weather_provider = self.weather_provider
            
            # Update the provider in the menu bar if it exists
            if hasattr(self, 'menuBar') and hasattr(self.menuBar(), 'set_current_provider'):
                self.menuBar().set_current_provider(provider_name)
            
            # Restore the city and refresh weather data
            self.city = current_city
            self.refresh_weather()
            
            # Show success message
            self.statusBar().showMessage(f"Successfully switched to {provider_name}", 3000)
            logger.info(f"Successfully switched to {provider_name} provider")
            
        except Exception as e:
            error_msg = f"Failed to switch to {provider_name} provider: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Show error in status bar and message box
            self.statusBar().showMessage("Failed to switch weather provider", 3000)
            QMessageBox.critical(
                self,
                self.tr('Provider Error'),
                self.tr(error_msg)
            )
            
            # Try to revert to the previous provider
            try:
                prev_provider = self.config_manager.get('previous_provider', 'openweathermap')
                if prev_provider != provider_name:
                    self.update_weather_provider(prev_provider)
            except Exception as revert_error:
                logger.error(f"Failed to revert to previous provider: {revert_error}")
        finally:
            # Clear any status message after a delay
            QTimer.singleShot(3000, self.statusBar().clearMessage)


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
