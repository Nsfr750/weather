"""
Test script for the API Key Manager with the plugin system.

This script tests the API key manager's integration with the plugin system
by loading all weather provider plugins and displaying the API key manager dialog.
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the script directory to the Python path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

def test_api_key_manager():
    """Test the API key manager with the plugin system."""
    try:
        from PyQt6.QtWidgets import QApplication
        from script.plugin_system.plugin_manager import PluginManager
        from script.plugin_system.weather_provider import BaseWeatherProvider
        from plugins.features.api_key_manager import ApiKeyManagerDialog
        
        # Initialize the application
        app = QApplication(sys.argv)
        
        # Initialize the plugin manager
        plugin_manager = PluginManager()
        plugin_manager.plugin_paths = [Path("plugins/weather_providers")]
        
        # Load plugins
        logger.info("Loading weather provider plugins...")
        plugin_manager.load_plugins()
        
        # Get all weather provider plugins
        providers = plugin_manager.get_plugins(BaseWeatherProvider)
        
        if not providers:
            logger.warning("No weather provider plugins found!")
            return 1
            
        logger.info(f"Found {len(providers)} weather provider(s): {', '.join(providers.keys())}")
        
        # Show the API key manager dialog
        logger.info("Opening API Key Manager...")
        dialog = ApiKeyManagerDialog()
        dialog.show()
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Error testing API key manager: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    test_api_key_manager()
