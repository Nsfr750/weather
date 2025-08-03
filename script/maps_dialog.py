"""
Weather Maps and Radar Dialog

This module provides a dialog for displaying weather maps and radar data
using various weather map services and OpenStreetMap.
"""

import os
import folium
import logging
import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any

# For geocoding
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

from PyQt6.QtCore import Qt, QUrl, QSize, QCoreApplication, QMetaObject
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QComboBox, QLabel, QPushButton, QSizePolicy, QCompleter, QLineEdit
)
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QPixmap, QFont

# Configure logging
logger = logging.getLogger(__name__)

# Set Qt.AA_ShareOpenGLContexts attribute if not already set
app = QCoreApplication.instance()
if app is not None and not hasattr(Qt.ApplicationAttribute, '_shareopenglcontexts_set'):
    app.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    Qt.ApplicationAttribute._shareopenglcontexts_set = True

# Default coordinates (centered on Europe)
DEFAULT_LATITUDE = 46.0
DEFAULT_LONGITUDE = 2.0
DEFAULT_ZOOM = 4

class MapsDialog(QDialog):
    """
    A dialog for displaying weather maps and radar data using various services.
    """
    
    def __init__(self, parent=None, translations: Optional[Dict[str, str]] = None):
        """
        Initialize the Maps Dialog.
        
        Args:
            parent: The parent widget
            translations: Dictionary containing translations for UI elements
        """
        super().__init__(parent, Qt.WindowType.Window)
        self.translations = translations or {}
        self.setWindowTitle(self._tr("Weather Maps & Radar"))
        self.setMinimumSize(1024, 768)
        
        # Initialize map data
        self.current_lat = DEFAULT_LATITUDE
        self.current_lon = DEFAULT_LONGITUDE
        self.current_zoom = DEFAULT_ZOOM
        
        # Initialize geocoder with rate limiting (max 1 request per second)
        self.geolocator = Nominatim(user_agent="weather_app_maps")
        self.geocode = RateLimiter(
            self.geolocator.geocode,
            min_delay_seconds=1.0,  # Respect Nominatim's rate limit
            max_retries=2,
            error_wait_seconds=5.0
        )
        self.last_geocode_time = 0
        
        # Cache for geocoding results
        self.geocode_cache_file = Path("geocode_cache.json")
        self.geocode_cache = self._load_geocode_cache()
        
        # Initialize UI
        self._init_ui()
        self._set_window_icon()
        
        # Load initial maps
        self._update_radar_map()
        self._update_temperature_map()
        self._update_precipitation_map()
        self._update_wind_map()
    
    def _init_ui(self):
        """Initialize the user interface components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create header with location search
        header_layout = QHBoxLayout()
        
        # Location search
        search_layout = QHBoxLayout()
        search_label = QLabel(self._tr("Location:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self._tr("Search location..."))
        self.search_input.setMinimumWidth(250)
        search_button = QPushButton(self._tr("Search"))
        search_button.clicked.connect(self._on_search_clicked)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        header_layout.addLayout(search_layout)
        
        # Add stretch to push controls to the left
        header_layout.addStretch()
        
        # Add header to main layout
        main_layout.addLayout(header_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self._add_radar_tab()
        self._add_temperature_map_tab()
        self._add_precipitation_map_tab()
        self._add_wind_map_tab()
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget, 1)  # 1 is stretch factor
        
        # Add status bar
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Add close button
        close_button = QPushButton(self._tr("Close"))
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(100)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
    
    def _add_radar_tab(self):
        """Add radar map tab."""
        radar_widget = QWidget()
        layout = QVBoxLayout(radar_widget)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Map type selector
        self.radar_type = QComboBox()
        self.radar_type.addItem(self._tr("OpenStreetMap"), "osm")
        self.radar_type.addItem(self._tr("OpenTopoMap"), "topo")
        self.radar_type.addItem(self._tr("Stamen Terrain"), "stamen_terrain")
        self.radar_type.currentIndexChanged.connect(self._update_radar_map)
        
        # Layer selector
        self.radar_layer = QComboBox()
        self.radar_layer.addItem(self._tr("Radar"), "radar")
        self.radar_layer.addItem(self._tr("Satellite"), "satellite")
        self.radar_layer.currentIndexChanged.connect(self._update_radar_map)
        
        # Add controls to layout
        controls_layout.addWidget(QLabel(self._tr("Map Type:")))
        controls_layout.addWidget(self.radar_type)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(QLabel(self._tr("Layer:")))
        controls_layout.addWidget(self.radar_layer)
        controls_layout.addStretch()
        
        # Web view for the map
        self.radar_web_view = QWebEngineView()
        
        # Add widgets to layout
        layout.addLayout(controls_layout)
        layout.addWidget(self.radar_web_view)
        
        # Add tab
        self.tab_widget.addTab(radar_widget, self._tr("Radar"))
    
    def _add_temperature_map_tab(self):
        """Add temperature map tab."""
        temp_widget = QWidget()
        layout = QVBoxLayout(temp_widget)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Temperature unit selector
        self.temp_unit = QComboBox()
        self.temp_unit.addItem("°C", "celsius")
        self.temp_unit.addItem("°F", "fahrenheit")
        self.temp_unit.currentIndexChanged.connect(self._update_temperature_map)
        
        # Add controls to layout
        controls_layout.addWidget(QLabel(self._tr("Temperature Unit:")))
        controls_layout.addWidget(self.temp_unit)
        controls_layout.addStretch()
        
        # Web view for temperature map
        self.temp_web_view = QWebEngineView()
        
        # Add widgets to layout
        layout.addLayout(controls_layout)
        layout.addWidget(self.temp_web_view)
        
        # Add tab
        self.tab_widget.addTab(temp_widget, self._tr("Temperature"))
    
    def _add_precipitation_map_tab(self):
        """Add precipitation map tab."""
        prec_widget = QWidget()
        layout = QVBoxLayout(prec_widget)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Precipitation type selector
        self.prec_type = QComboBox()
        self.prec_type.addItem(self._tr("Rain"), "rain")
        self.prec_type.addItem(self._tr("Snow"), "snow")
        self.prec_type.addItem(self._tr("Clouds"), "clouds")
        self.prec_type.currentIndexChanged.connect(self._update_precipitation_map)
        
        # Add controls to layout
        controls_layout.addWidget(QLabel(self._tr("Type:")))
        controls_layout.addWidget(self.prec_type)
        controls_layout.addStretch()
        
        # Web view for precipitation map
        self.prec_web_view = QWebEngineView()
        
        # Add widgets to layout
        layout.addLayout(controls_layout)
        layout.addWidget(self.prec_web_view)
        
        # Add tab
        self.tab_widget.addTab(prec_widget, self._tr("Precipitation"))
    
    def _add_wind_map_tab(self):
        """Add wind map tab."""
        wind_widget = QWidget()
        layout = QVBoxLayout(wind_widget)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Wind layer selector
        self.wind_layer = QComboBox()
        self.wind_layer.addItem(self._tr("Wind Speed"), "wind")
        self.wind_layer.addItem(self._tr("Wind Gusts"), "gust")
        self.wind_layer.addItem(self._tr("Wind Direction"), "direction")
        self.wind_layer.currentIndexChanged.connect(self._update_wind_map)
        
        # Add controls to layout
        controls_layout.addWidget(QLabel(self._tr("Layer:")))
        controls_layout.addWidget(self.wind_layer)
        controls_layout.addStretch()
        
        # Web view for wind map
        self.wind_web_view = QWebEngineView()
        
        # Add widgets to layout
        layout.addLayout(controls_layout)
        layout.addWidget(self.wind_web_view)
        
        # Add tab
        self.tab_widget.addTab(wind_widget, self._tr("Wind"))
    
    def _update_radar_map(self):
        """Update the radar map based on selected type and layer."""
        map_type = self.radar_type.currentData()
        layer = self.radar_layer.currentData()
        
        # Create a map centered on current location
        m = folium.Map(
            location=[self.current_lat, self.current_lon],
            zoom_start=self.current_zoom,
            tiles=self._get_tile_url(map_type),
            attr='Map data © OpenStreetMap contributors',
            control_scale=True
        )
        
        # Add layer based on selection
        if layer == "radar":
            # Add radar overlay (example using OpenWeatherMap)
            folium.TileLayer(
                tiles='https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY',
                attr='OpenWeatherMap',
                name='Precipitation',
                overlay=True
            ).add_to(m)
        elif layer == "satellite":
            # Add satellite layer
            folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Satellite',
                overlay=True
            ).add_to(m)
        
        # Save map to HTML and load in web view
        self._load_map_in_webview(m, self.radar_web_view)
    
    def _update_temperature_map(self):
        """Update the temperature map."""
        unit = self.temp_unit.currentData()
        
        # Create a map centered on current location
        m = folium.Map(
            location=[self.current_lat, self.current_lon],
            zoom_start=self.current_zoom,
            tiles='OpenStreetMap',
            attr='Map data © OpenStreetMap contributors',
            control_scale=True
        )
        
        # Add temperature overlay (example using OpenWeatherMap)
        folium.TileLayer(
            tiles=f'https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid=YOUR_API_KEY&units={"imperial" if unit == "fahrenheit" else "metric"}',
            attr='OpenWeatherMap',
            name='Temperature',
            overlay=True
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map to HTML and load in web view
        self._load_map_in_webview(m, self.temp_web_view)
    
    def _update_precipitation_map(self):
        """Update the precipitation map."""
        prec_type = self.prec_type.currentData()
        
        # Create a map centered on current location
        m = folium.Map(
            location=[self.current_lat, self.current_lon],
            zoom_start=self.current_zoom,
            tiles='OpenStreetMap',
            attr='Map data © OpenStreetMap contributors',
            control_scale=True
        )
        
        # Add precipitation overlay based on type
        if prec_type == "rain":
            folium.TileLayer(
                tiles='https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY',
                attr='OpenWeatherMap',
                name='Precipitation',
                overlay=True
            ).add_to(m)
        elif prec_type == "snow":
            folium.TileLayer(
                tiles='https://tile.openweathermap.org/map/snow_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY',
                attr='OpenWeatherMap',
                name='Snow',
                overlay=True
            ).add_to(m)
        else:  # clouds
            folium.TileLayer(
                tiles='https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY',
                attr='OpenWeatherMap',
                name='Clouds',
                overlay=True
            ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map to HTML and load in web view
        self._load_map_in_webview(m, self.prec_web_view)
    
    def _update_wind_map(self):
        """Update the wind map."""
        layer = self.wind_layer.currentData()
        
        # Create a map centered on current location
        m = folium.Map(
            location=[self.current_lat, self.current_lon],
            zoom_start=self.current_zoom,
            tiles='OpenStreetMap',
            attr='Map data © OpenStreetMap contributors',
            control_scale=True
        )
        
        # Add wind overlay based on layer
        if layer == "wind":
            folium.TileLayer(
                tiles='https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY',
                attr='OpenWeatherMap',
                name='Wind Speed',
                overlay=True
            ).add_to(m)
        elif layer == "gust":
            folium.TileLayer(
                tiles='https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY',
                attr='OpenWeatherMap',
                name='Wind Gusts',
                overlay=True
            ).add_to(m)
        else:  # direction
            folium.TileLayer(
                tiles='https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY',
                attr='OpenWeatherMap',
                name='Wind Direction',
                overlay=True
            ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map to HTML and load in web view
        self._load_map_in_webview(m, self.wind_web_view)
    
    def _load_map_in_webview(self, folium_map, web_view):
        """
        Load a Folium map into a QWebEngineView.
        
        Args:
            folium_map: The Folium map object
            web_view: The QWebEngineView to load the map into
        """
        # Create a temporary HTML file
        temp_file = Path("temp_map.html")
        
        try:
            # Save the map to the temporary file
            folium_map.save(str(temp_file))
            
            # Load the file into the web view
            web_view.setUrl(QUrl.fromLocalFile(str(temp_file.absolute())))
            
            # Clean up the temporary file
            # Note: We can't delete it immediately as the web view needs to load it
            # The file will be deleted when the application exits
            
        except Exception as e:
            logger.error(f"Error loading map: {e}")
            web_view.setHtml(f"<h2>Error</h2><p>Could not load map: {str(e)}</p>")
    
    def _get_tile_url(self, map_type: str) -> str:
        """
        Get the tile URL for the specified map type.
        
        Args:
            map_type: Type of map (e.g., 'osm', 'topo', 'stamen_terrain')
            
        Returns:
            str: The tile URL
        """
        tile_urls = {
            'osm': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'topo': 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            'stamen_terrain': 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
        }
        return tile_urls.get(map_type, tile_urls['osm'])
    
    def _on_search_clicked(self):
        """Handle search button click."""
        query = self.search_input.text().strip()
        if not query:
            self.status_label.setText(self._tr("Please enter a location to search"))
            return
        
        # Show searching message
        self.status_label.setText(f"{self._tr('Searching for')}: {query}...")
        
        # Use a thread to prevent UI freezing during geocoding
        import threading
        threading.Thread(
            target=self._geocode_location,
            args=(query,),
            daemon=True
        ).start()
    
    def _update_status(self, message: str, is_error: bool = False):
        """Thread-safe method to update the status label."""
        QMetaObject.invokeMethod(
            self.status_label, 'setText',
            Qt.ConnectionType.QueuedConnection,
            QMetaObject.Argument(str, message)
        )
        
        # Set text color based on error status
        color = 'red' if is_error else 'black'
        QMetaObject.invokeMethod(
            self.status_label, 'setStyleSheet',
            Qt.ConnectionType.QueuedConnection,
            QMetaObject.Argument(str, f'color: {color};')
        )
    
    def _handle_geocode_result(self, result: Optional[Dict[str, Any]], original_query: str):
        """Handle the result of a geocoding operation."""
        if not result or 'error' in result:
            error_msg = result.get('error', 'Unknown error') if result else 'No results found'
            self._update_status(f"{self._tr('Error')}: {error_msg}", is_error=True)
            logger.error(f"Geocoding error: {error_msg}")
            return

        try:
            # Update current location
            self.current_lat = result['latitude']
            self.current_lon = result['longitude']
            display_name = result.get('display_name', original_query)
            
            # Update status
            self._update_status(
                f"{self._tr('Showing')}: {display_name} ({result['latitude']:.4f}, {result['longitude']:.4f})"
            )
            
            # Update all maps
            self._update_radar_map()
            self._update_temperature_map()
            self._update_precipitation_map()
            self._update_wind_map()
            
        except Exception as e:
            error_msg = f"{self._tr('Error processing location')}: {str(e)}"
            self._update_status(error_msg, is_error=True)
            logger.error(f"Error handling geocode result: {e}")
    
    def _geocode_location(self, location: str):
        """
        Geocode a location name to get coordinates.
        
        Args:
            location: The location name to geocode
        """
        try:
            # Update status
            self._update_status(f"{self._tr('Searching for')}: {location}...")
            
            # Check cache first
            cached = self.geocode_cache.get(location.lower())
            if cached:
                # Simulate async behavior with a small delay
                import threading
                threading.Timer(0.5, lambda: self._handle_geocode_result(cached, location)).start()
                return
            
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_geocode_time
            if time_since_last < 1.0:  # Respect rate limit of 1 request per second
                time.sleep(1.0 - time_since_last)
            
            # Perform geocoding
            self.last_geocode_time = time.time()
            result = self.geocode(location, exactly_one=True)
            
            if result:
                # Cache the result
                result_data = {
                    'latitude': result.latitude,
                    'longitude': result.longitude,
                    'display_name': result.raw.get('display_name', location),
                    'timestamp': time.time()
                }
                self.geocode_cache[location.lower()] = result_data
                self._save_geocode_cache()
                
                # Update UI with the result
                self._handle_geocode_result(result_data, location)
            else:
                self._update_status(
                    f"{self._tr('Location not found')}: {location}",
                    is_error=True
                )
                
        except Exception as e:
            error_msg = f"{self._tr('Error geocoding location')}: {str(e)}"
            self._update_status(error_msg, is_error=True)
            logger.error(f"Geocoding error: {e}")
    
    def _load_geocode_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load geocoding results from cache file."""
        if not self.geocode_cache_file.exists():
            return {}
            
        try:
            with open(self.geocode_cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                # Filter out entries older than 30 days
                current_time = time.time()
                return {
                    k: v for k, v in cache.items() 
                    if current_time - v.get('timestamp', 0) < 30 * 24 * 60 * 60
                }
        except Exception as e:
            logger.error(f"Error loading geocode cache: {e}")
            return {}
    
    def _save_geocode_cache(self):
        """Save geocoding results to cache file."""
        try:
            with open(self.geocode_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.geocode_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving geocode cache: {e}")
    
    def _set_window_icon(self):
        """Set the window icon."""
        try:
            icon_path = Path('assets/map.svg')
            if not icon_path.exists():
                icon_path = Path('assets/meteo.png')  # Fallback to main app icon
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            logger.warning(f'Could not set window icon: {e}')
    
    def _tr(self, text: str) -> str:
        """
        Translate text if translations are available.
        
        Args:
            text: The text to translate
            
        Returns:
            str: The translated text or the original if no translation is available
        """
        return self.translations.get(text, text)
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Clean up any temporary files
        temp_file = Path("temp_map.html")
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception as e:
                logger.warning(f"Could not delete temporary file: {e}")
        
        # Save the geocode cache
        self._save_geocode_cache()
        
        super().closeEvent(event)


def show_maps_dialog(parent=None, translations: Optional[Dict[str, str]] = None):
    """
    Show the Maps dialog.
    
    Args:
        parent: The parent widget
        translations: Dictionary containing translations for UI elements
    """
    dialog = MapsDialog(parent, translations)
    dialog.exec()
