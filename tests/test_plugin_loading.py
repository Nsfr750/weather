"""
Test script to verify plugin loading functionality.
"""
import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_plugin_loading():
    """Test loading the OpenMeteo plugin."""
    # Add the script directory to the Python path
    script_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(script_dir))
    
    # Import the plugin manager
    from script.plugin_system.plugin_manager import PluginManager, BasePlugin
    from script.plugin_system.weather_provider import BaseWeatherProvider
    
    # Set up plugin paths
    plugin_paths = [
        script_dir / 'plugins' / 'weather_providers',
        script_dir / 'script' / 'plugins' / 'weather_providers'
    ]
    
    # Filter out non-existent paths
    plugin_paths = [p for p in plugin_paths if p.exists()]
    
    if not plugin_paths:
        logger.error("No valid plugin directories found")
        return False
    
    logger.info(f"Testing plugin loading with paths: {plugin_paths}")
    
    # Initialize the plugin manager
    plugin_manager = PluginManager(plugin_paths)
    
    # Load plugins
    try:
        plugin_manager.load_plugins()
        logger.info(f"Successfully loaded {len(plugin_manager.plugins)} plugins")
        
        # Check if OpenMeteo plugin was loaded
        weather_plugins = plugin_manager.get_plugins_by_type(BaseWeatherProvider)
        logger.info(f"Found {len(weather_plugins)} weather provider plugins")
        
        for name, plugin_class in weather_plugins.items():
            logger.info(f"Found weather provider: {name} (class: {plugin_class.__name__})")
            if name.lower() == 'openmeteo':
                logger.info("OpenMeteo plugin found and loaded successfully!")
                return True
        
        logger.error("OpenMeteo plugin not found in loaded plugins")
        return False
        
    except Exception as e:
        logger.error(f"Error during plugin loading: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    if test_plugin_loading():
        print("✅ Plugin loading test passed!")
        sys.exit(0)
    else:
        print("❌ Plugin loading test failed!")
        sys.exit(1)
