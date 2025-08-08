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
from typing import Dict, Optional, Tuple, List, Any, Union

# For geocoding
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Import config manager
from script.config_utils import ConfigManager

from PyQt6.QtCore import Qt, QUrl, QSize, QCoreApplication, QMetaObject, Q_ARG, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QComboBox, QLabel, QPushButton, QSizePolicy, QCompleter, QLineEdit
)
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QPixmap, QFont

# Import language manager
from lang.language_manager import LanguageManager

# Configure logging
logger = logging.getLogger(__name__)

# Default coordinates
DEFAULT_LATITUDE = 45.7627855
DEFAULT_LONGITUDE = 8.4451747
DEFAULT_ZOOM = 4

class MapsDialog(QDialog):
    """
    A dialog for displaying weather maps and radar data using various services.
    """
    
    # Signal for language changes
    language_changed = pyqtSignal(str)
    
    def __init__(self, parent=None, language_manager: Optional[LanguageManager] = None):
        """
        Initialize the Maps Dialog.
        
        Args:
            parent: The parent widget
            language_manager: The language manager instance for translations
        """
        super().__init__(parent)
        
        # Initialize language manager
        self.language_manager = language_manager or LanguageManager()
        
        # Set window title using translation
        self.setWindowTitle(self._tr('Weather Maps & Radar'))
        self.setMinimumSize(800, 600)
        
        # Connect to language changed signal
        self.language_manager.language_changed.connect(self.retranslate_ui)
        
        # Initialize UI
        self._init_ui()
        self._set_window_icon()
        
        # Initialize map data
        self.current_lat = DEFAULT_LATITUDE
        self.current_lon = DEFAULT_LONGITUDE
        self.current_zoom = DEFAULT_ZOOM
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
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
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)  # Ensure config directory exists
        self.geocode_cache_file = config_dir / "geocode_cache.json"
        self.geocode_cache = self._load_geocode_cache()
        
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
    
    def _update_temperature_map(self):
        """Update the temperature map based on selected unit."""
        temp_unit = self.temp_unit.currentData()
        
        # Create a map centered on current location with OpenStreetMap as base
        m = folium.Map(
            location=[self.current_lat, self.current_lon],
            zoom_start=self.current_zoom,
            tiles='OpenStreetMap',
            attr='Map data &copy; OpenStreetMap contributors',
            control_scale=True
        )
        
        # Add temperature overlay using OpenWeatherMap
        owm_api_key = self.config_manager.get_provider_api_key('openweathermap')
        if not owm_api_key:
            self._update_status(self._tr('OpenWeatherMap API key not configured. Please set it in settings.'), is_error=True)
            # Show error in web view
            self.temp_web_view.setHtml(
                "<h3 style='color: red;'>OpenWeatherMap API key not configured</h3>"
                "<p>Please set your OpenWeatherMap API key in the settings.</p>"
            )
            return
        
        # Add temperature overlay with selected unit
        unit_param = 'imperial' if temp_unit == 'fahrenheit' else 'metric'
        folium.TileLayer(
            tiles=f'https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid={owm_api_key}&units={unit_param}&opacity=0.7',
            attr='OpenWeatherMap',
            name=f'Temperature ({temp_unit})',
            overlay=True,
            show=True,
            opacity=0.7
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl(position='topright').add_to(m)
        
        # Save map to HTML and load in web view
        self._load_map_in_webview(m, self.temp_web_view)
    
    def _update_radar_map(self):
        """Update the radar map based on selected type and layer."""
        map_type = self.radar_type.currentData()
        layer = self.radar_layer.currentData()
        
        # Create a map centered on current location with a default base layer
        # We'll add the actual base layers below with proper control
        m = folium.Map(
            location=[self.current_lat, self.current_lon],
            zoom_start=self.current_zoom,
            tiles=None,  # Start with no base layer
            control_scale=True
        )
        
        # Define all base layers
        base_layers = {
            'osm': {
                'tiles': 'OpenStreetMap',
                'attr': '© OpenStreetMap contributors',
                'name': 'OpenStreetMap',
                'show': map_type == 'osm' and layer != 'satellite'
            },
            'topo': {
                'tiles': 'OpenTopoMap',
                'attr': 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)',
                'name': 'OpenTopoMap',
                'show': map_type == 'topo' and layer != 'satellite',
                'tile_url': 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png'
            },
            'stamen_terrain': {
                'tiles': 'stamenterrain',
                'attr': 'Map tiles by <a href="https://stamen.com">Stamen Design</a>, under <a href="https://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="https://openstreetmap.org">OpenStreetMap</a>, under <a href="https://www.openstreetmap.org/copyright">ODbL</a>.',
                'name': 'Stamen Terrain',
                'show': map_type == 'stamen_terrain' and layer != 'satellite'
            },
            'satellite': {
                'tiles': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                'attr': 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                'name': 'Satellite',
                'show': layer == 'satellite',
                'overlay': False
            }
        }
        
        # Add all base layers to the map
        for key, layer_config in base_layers.items():
            # Special handling for Stamen Terrain
            if key == 'stamen_terrain':
                # Use folium's built-in Stamen Terrain provider
                folium.TileLayer(
                    tiles=layer_config['tiles'],
                    attr=layer_config['attr'],
                    name=layer_config['name'],
                    overlay=layer_config.get('overlay', False),
                    control=True,
                    show=layer_config['show']
                ).add_to(m)
            else:
                # Standard tile layer for other map types
                folium.TileLayer(
                    tiles=layer_config.get('tile_url', layer_config['tiles']),
                    attr=layer_config['attr'],
                    name=layer_config['name'],
                    overlay=layer_config.get('overlay', False),
                    control=True,
                    show=layer_config['show']
                ).add_to(m)
        
        # Add weather overlay based on selection
        owm_api_key = self.config_manager.get_provider_api_key('openweathermap')
        if not owm_api_key:
            self._update_status(self._tr('OpenWeatherMap API key not configured. Please set it in settings.'), is_error=True)
            # Show error in web view
            self.radar_web_view.setHtml(
                "<h3 style='color: red;'>OpenWeatherMap API key not configured</h3>"
                "<p>Please set your OpenWeatherMap API key in the settings.</p>"
            )
            return
            
        if layer == "radar":
            # Add precipitation overlay
            folium.TileLayer(
                tiles=f'https://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={owm_api_key}',
                attr='OpenWeatherMap',
                name='Precipitation',
                overlay=True,
                show=True,
                opacity=0.7
            ).add_to(m)
        
        # Add layer control with base layers and overlays
        layer_control = folium.LayerControl(
            position='topright',
            collapsed=False,  # Keep expanded for better UX
            autoZIndex=True  # Automatically manage z-index of layers
        )
        m.add_child(layer_control)
        
        # Save map to HTML and load in web view
        self._load_map_in_webview(m, self.radar_web_view)
    
    def _update_precipitation_map(self):
        """Update the precipitation map based on selected precipitation type."""
        prec_type = self.prec_type.currentData()
        
        # Create a map centered on current location with OpenStreetMap as base
        m = folium.Map(
            location=[self.current_lat, self.current_lon],
            zoom_start=self.current_zoom,
            tiles='OpenStreetMap',
            attr='Map data &copy; OpenStreetMap contributors',
            control_scale=True
        )
        
        # Add precipitation overlay using OpenWeatherMap
        owm_api_key = self.config_manager.get_provider_api_key('openweathermap')
        if not owm_api_key:
            self._update_status(self._tr('OpenWeatherMap API key not configured. Please set it in settings.'), is_error=True)
            # Show error in web view
            self.prec_web_view.setHtml(
                "<h3 style='color: red;'>OpenWeatherMap API key not configured</h3>"
                "<p>Please set your OpenWeatherMap API key in the settings.</p>"
            )
            return
        
        # Add precipitation layer based on selection
        if prec_type == 'rain':
            # Add rain overlay
            folium.TileLayer(
                tiles=f'https://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={owm_api_key}&opacity=0.7',
                attr='OpenWeatherMap',
                name='Rain',
                overlay=True,
                show=True,
                opacity=0.7
            ).add_to(m)
        elif prec_type == 'snow':
            # Add snow overlay
            folium.TileLayer(
                tiles=f'https://tile.openweathermap.org/map/snow_new/{{z}}/{{x}}/{{y}}.png?appid={owm_api_key}&opacity=0.7',
                attr='OpenWeatherMap',
                name='Snow',
                overlay=True,
                show=True,
                opacity=0.7
            ).add_to(m)
        else:  # clouds
            # Add clouds overlay
            folium.TileLayer(
                tiles=f'https://tile.openweathermap.org/map/clouds_new/{{z}}/{{x}}/{{y}}.png?appid={owm_api_key}&opacity=0.7',
                attr='OpenWeatherMap',
                name='Clouds',
                overlay=True,
                show=True,
                opacity=0.7
            ).add_to(m)
        
        # Add layer control
        folium.LayerControl(position='topright').add_to(m)
        
        # Save map to HTML and load in web view
        self._load_map_in_webview(m, self.prec_web_view)
    
    def _update_wind_map(self):
        """Update the wind map based on selected wind layer."""
        wind_layer = self.wind_layer.currentData()
        
        # Create a map centered on current location with OpenStreetMap as base
        m = folium.Map(
            location=[self.current_lat, self.current_lon],
            zoom_start=self.current_zoom,
            tiles='OpenStreetMap',
            attr='Map data &copy; OpenStreetMap contributors',
            control_scale=True
        )
        
        # Add wind overlay using OpenWeatherMap
        owm_api_key = self.config_manager.get_provider_api_key('openweathermap')
        if not owm_api_key:
            self._update_status(self._tr('OpenWeatherMap API key not configured. Please set it in settings.'), is_error=True)
            # Show error in web view
            self.wind_web_view.setHtml(
                "<h3 style='color: red;'>OpenWeatherMap API key not configured</h3>"
                "<p>Please set your OpenWeatherMap API key in the settings.</p>"
            )
            return
        
        # Add wind layer based on selection
        if wind_layer == 'wind':
            # Add wind speed overlay
            folium.TileLayer(
                tiles=f'https://tile.openweathermap.org/map/wind_new/{{z}}/{{x}}/{{y}}.png?appid={owm_api_key}&opacity=0.7',
                attr='OpenWeatherMap',
                name='Wind Speed',
                overlay=True,
                show=True,
                opacity=0.7
            ).add_to(m)
        elif wind_layer == 'gust':
            # Add wind gusts overlay
            folium.TileLayer(
                tiles=f'https://tile.openweathermap.org/map/wind_new/{{z}}/{{x}}/{{y}}.png?appid={owm_api_key}&opacity=0.7&gust=1',
                attr='OpenWeatherMap',
                name='Wind Gusts',
                overlay=True,
                show=True,
                opacity=0.7
            ).add_to(m)
        else:  # direction
            # Add wind direction overlay
            folium.TileLayer(
                tiles=f'https://tile.openweathermap.org/map/wind_new/{{z}}/{{x}}/{{y}}.png?appid={owm_api_key}&opacity=0.7&direction=1',
                attr='OpenWeatherMap',
                name='Wind Direction',
                overlay=True,
                show=True,
                opacity=0.7
            ).add_to(m)
        
        # Add layer control
        folium.LayerControl(position='topright').add_to(m)
        
        # Save map to HTML and load in web view
        self._load_map_in_webview(m, self.wind_web_view)
    
    def _load_map_in_webview(self, folium_map, web_view):
        """
        Load a Folium map into a QWebEngineView.
        
        Args:
            folium_map: The Folium map object to display
            web_view: The QWebEngineView widget to display the map in
        """
        try:
            # Save the map to a temporary HTML file
            temp_file = Path("temp_map.html")
            folium_map.save(str(temp_file))
            
            # Read the HTML content
            with open(temp_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Configure web view settings
            web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)
            web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
            
            # Load the HTML content
            web_view.setHtml(html_content, QUrl.fromLocalFile(str(temp_file.absolute())))
            
            # Force a refresh
            web_view.reload()
            
            logger.info("Map loaded successfully")
            
        except Exception as e:
            error_msg = f"Error loading map: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._update_status(error_msg, is_error=True)
            
            # Show error in web view
            web_view.setHtml(f"<h3 style='color: red;'>{error_msg}</h3><p>Please check your internet connection and try again.</p>")
            
            # Try a fallback to OpenStreetMap if the main map fails
            try:
                web_view.setUrl(QUrl("https://www.openstreetmap.org/"))
            except Exception as fallback_error:
                logger.error(f"Fallback map also failed: {fallback_error}")
        
        # Ensure we're on the main thread when updating the web view
        if QThread.currentThread() != self.thread():
            QMetaObject.invokeMethod(self, "_load_map_in_webview",
                                   Qt.ConnectionType.QueuedConnection,
                                   Q_ARG(object, folium_map),
                                   Q_ARG(object, web_view))
            return
    
    def _get_tile_url(self, map_type: str) -> str:
        """Get the tile URL for the specified map type."""
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
        # Schedule the update on the main thread
        QMetaObject.invokeMethod(
            self.status_label, 
            'setText', 
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, message)
        )
        
        color = 'red' if is_error else 'black'
        QMetaObject.invokeMethod(
            self.status_label, 
            'setStyleSheet', 
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, f'color: {color};')
        )
    
    @pyqtSlot(object, str)
    def _handle_geocode_result(self, result: Optional[Dict[str, Any]], original_query: str):
        """Handle the result of a geocoding operation."""
        def _update_ui():
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
                
                # Update all maps on the main thread
                self._update_radar_map()
                self._update_temperature_map()
                self._update_precipitation_map()
                self._update_wind_map()
                
            except Exception as e:
                error_msg = f"{self._tr('Error processing location')}: {str(e)}"
                self._update_status(error_msg, is_error=True)
                logger.error(f"Error handling geocode result: {e}")
        
        # Ensure we're on the main thread when updating the UI
        if QThread.currentThread() != self.thread():
            QMetaObject.invokeMethod(self, "_handle_geocode_result", 
                                   Qt.ConnectionType.QueuedConnection,
                                   Q_ARG(object, result),
                                   Q_ARG(str, original_query))
        else:
            _update_ui()
    
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
        try:
            if not self.geocode_cache_file.exists():
                return {}
                
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
            # Ensure parent directory exists
            self.geocode_cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with atomic write to prevent corruption
            temp_file = self.geocode_cache_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.geocode_cache, f, ensure_ascii=False, indent=2)
            
            # On Windows, we need to remove the destination file first if it exists
            if self.geocode_cache_file.exists():
                self.geocode_cache_file.unlink()
            
            # Rename temp file to final name
            temp_file.rename(self.geocode_cache_file)
            
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

    def retranslate_ui(self, language_code: Optional[str] = None):
        """
        Update all UI text with current translations.
        
        Args:
            language_code: The language code to use for translations (optional)
        """
        # Update window title
        self.setWindowTitle(self._tr('Weather Maps & Radar'))
        
        # Update map type labels
        if hasattr(self, 'map_type_combo'):
            for i in range(self.map_type_combo.count()):
                map_type = self.map_type_combo.itemData(i)
                if map_type == 'openstreetmap':
                    self.map_type_combo.setItemText(i, self._tr('map_type_street'))
                elif map_type == 'opentopomap':
                    self.map_type_combo.setItemText(i, self._tr('map_type_topographic'))
                elif map_type == 'stamen_terrain':
                    self.map_type_combo.setItemText(i, self._tr('map_type_terrain'))
                elif map_type == 'stamen_toner':
                    self.map_type_combo.setItemText(i, self._tr('map_type_bw'))
                elif map_type == 'cartodbpositron':
                    self.map_type_combo.setItemText(i, self._tr('map_type_light'))
                elif map_type == 'cartodbdark_matter':
                    self.map_type_combo.setItemText(i, self._tr('map_type_dark'))
        
        # Update button text
        if hasattr(self, 'search_button'):
            self.search_button.setText(self._tr('search_button'))
        
        if hasattr(self, 'current_location_btn'):
            self.current_location_btn.setToolTip(self._tr('show_current_location'))
        
        # Update layer control text if it exists
        if hasattr(self, 'layer_control'):
            try:
                self.layer_control.options['collapsed'] = False
                self.layer_control.options['position'] = 'topleft'
                self.layer_control.options['autoZIndex'] = True
                self.layer_control.options['hideSingleBase'] = True
                self.layer_control.options['sortLayers'] = True
                self.layer_control.options['sortFunction'] = "function(layerA, layerB, nameA, nameB) { return nameA.localeCompare(nameB); }"
                
                # Update base map names
                for layer in self.layer_control.base_layers:
                    if layer.name == 'OpenStreetMap':
                        layer.name = self._tr('map_type_street')
                    elif layer.name == 'OpenTopoMap':
                        layer.name = self._tr('map_type_topographic')
                    elif layer.name == 'Stamen Terrain':
                        layer.name = self._tr('map_type_terrain')
                    elif layer.name == 'Stamen Toner':
                        layer.name = self._tr('map_type_bw')
                    elif layer.name == 'CartoDB Positron':
                        layer.name = self._tr('map_type_light')
                    elif layer.name == 'CartoDB Dark Matter':
                        layer.name = self._tr('map_type_dark')
            except Exception as e:
                logger.warning(f"Error updating layer control text: {e}")

    def _tr(self, text: str, default: Optional[str] = None, **kwargs) -> str:
        """
        Translate text using the language manager.
        
        Args:
            text: The text to translate (key in translations)
            default: Default text to return if translation is not found
            **kwargs: Format arguments for the translated string
            
        Returns:
            The translated text or the default/input text if not found
        """
        if default is None:
            default = text
            
        try:
            return self.language_manager.get(text, default, **kwargs)
        except Exception as e:
            logger.warning(f"Translation error for '{text}': {e}")
            return default

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

def show_maps_dialog(parent=None, language_manager: Optional[LanguageManager] = None):
    """
    Show the Maps dialog.
    
    Args:
        parent: The parent widget
        language_manager: The language manager instance for translations
    """
    dialog = MapsDialog(parent, language_manager)
    dialog.exec()
