"""
Tests for the Maps Dialog functionality.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the script directory to the path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'script'))

# Import the dialog after setting up the path
from maps_dialog import MapsDialog, DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_ZOOM

# Test coordinates for Paris, France
TEST_LATITUDE = 48.8566
TEST_LONGITUDE = 2.3522

# Mock geocoding response
MOCK_GEOCODE_RESPONSE = MagicMock()
MOCK_GEOCODE_RESPONSE.latitude = TEST_LATITUDE
MOCK_GEOCODE_RESPONSE.longitude = TEST_LONGITUDE
MOCK_GEOCODE_RESPONSE.raw = {'display_name': 'Paris, France'}

class TestMapsDialog:
    """Test cases for the MapsDialog class."""
    
    @pytest.fixture
    def dialog(self, qtbot):
        """Create and return a MapsDialog instance for testing."""
        dialog = MapsDialog()
        qtbot.addWidget(dialog)
        return dialog
    
    def test_initialization(self, dialog):
        """Test that the dialog initializes correctly."""
        assert dialog is not None
        assert dialog.windowTitle() == "Weather Maps & Radar"
        assert dialog.current_lat == DEFAULT_LATITUDE
        assert dialog.current_lon == DEFAULT_LONGITUDE
        assert dialog.current_zoom == DEFAULT_ZOOM
    
    @patch('maps_dialog.Nominatim')
    def test_geocode_location_success(self, mock_nominatim, dialog, qtbot):
        """Test successful geocoding of a location."""
        # Setup mock
        mock_geolocator = MagicMock()
        mock_nominatim.return_value = mock_geolocator
        mock_geolocator.geocode.return_value = MOCK_GEOCODE_RESPONSE
        
        # Reset the geolocator in the dialog
        dialog.geolocator = mock_geolocator
        
        # Test geocoding
        with qtbot.waitSignal(dialog.status_label.textChanged, timeout=5000):
            dialog._geocode_location("Paris, France")
        
        # Check that the location was updated
        assert dialog.current_lat == TEST_LATITUDE
        assert dialog.current_lon == TEST_LONGITUDE
        assert dialog.current_zoom == 10  # Should zoom in on the location
    
    @patch('maps_dialog.Nominatim')
    def test_geocode_location_not_found(self, mock_nominatim, dialog, qtbot):
        """Test geocoding when location is not found."""
        # Setup mock to return None (location not found)
        mock_geolocator = MagicMock()
        mock_nominatim.return_value = mock_geolocator
        mock_geolocator.geocode.return_value = None
        
        # Reset the geolocator in the dialog
        dialog.geolocator = mock_geolocator
        
        # Test geocoding
        with qtbot.waitSignal(dialog.status_label.textChanged, timeout=5000):
            dialog._geocode_location("Nonexistent Place")
        
        # Check that the status shows location not found
        assert "not found" in dialog.status_label.text().lower()
    
    def test_geocode_cache(self, dialog, tmp_path):
        """Test that geocoding results are cached correctly."""
        # Set a temporary cache file
        dialog.geocode_cache_file = tmp_path / "test_geocode_cache.json"
        
        # Test data
        location = "Test Location"
        result_data = {
            'latitude': 12.34,
            'longitude': 56.78,
            'display_name': 'Test Location, Test Country',
            'timestamp': 1234567890.0
        }
        
        # Test saving to cache
        dialog.geocode_cache[location.lower()] = result_data
        dialog._save_geocode_cache()
        
        # Clear the in-memory cache
        dialog.geocode_cache = {}
        
        # Test loading from cache
        dialog._load_geocode_cache()
        assert location.lower() in dialog.geocode_cache
        assert dialog.geocode_cache[location.lower()] == result_data
    
    def test_map_initialization(self, dialog):
        """Test that all map views are initialized."""
        # Check that all web views are created
        assert hasattr(dialog, 'radar_web_view')
        assert hasattr(dialog, 'temp_web_view')
        assert hasattr(dialog, 'prec_web_view')
        assert hasattr(dialog, 'wind_web_view')
        
        # Check that all combo boxes are created
        assert hasattr(dialog, 'radar_type')
        assert hasattr(dialog, 'radar_layer')
        assert hasattr(dialog, 'temp_unit')
        assert hasattr(dialog, 'prec_type')
        assert hasattr(dialog, 'wind_layer')
    
    @patch('maps_dialog.folium.Map')
    def test_map_updates(self, mock_folium_map, dialog):
        """Test that map updates are triggered correctly."""
        # Setup mock
        mock_map = MagicMock()
        mock_folium_map.return_value = mock_map
        
        # Test radar map update
        dialog._update_radar_map()
        mock_folium_map.assert_called()
        
        # Test temperature map update
        dialog._update_temperature_map()
        
        # Test precipitation map update
        dialog._update_precipitation_map()
        
        # Test wind map update
        dialog._update_wind_map()
        
        # Check that the map was created with the correct parameters
        args, kwargs = mock_folium_map.call_args
        assert kwargs['location'] == [DEFAULT_LATITUDE, DEFAULT_LONGITUDE]
        assert kwargs['zoom_start'] == DEFAULT_ZOOM
