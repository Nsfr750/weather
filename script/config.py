"""
config.py
Legacy configuration module for backward compatibility.
New code should use config_utils.py instead.
"""
import json
import os
from pathlib import Path
from .config_utils import ConfigManager

# For backward compatibility
CONFIG_DIR = Path('config')
CONFIG_FILE = CONFIG_DIR / 'config.json'

# Create a config manager instance
_config_manager = ConfigManager()

# Backward compatible functions
def load_config():
    """Load the configuration (legacy function).
    
    Returns:
        dict: The configuration dictionary.
    """
    # Get the current provider's config
    current_provider = _config_manager.get_current_provider()
    provider_config = _config_manager.get_provider_config(current_provider)
    
    # Return a backward-compatible config
    return {
        'units': _config_manager.get('units', 'metric'),
        'api_key': provider_config.get('api_key', ''),
        'language': _config_manager.get('language', 'en'),
        'theme': _config_manager.get('theme', 'dark'),
        'provider': current_provider,
        'providers': _config_manager.get('providers', {})
    }

def save_config(config):
    """Save the configuration (legacy function).
    
    Args:
        config (dict): The configuration dictionary to save.
    """
    # Update the config manager with the legacy config
    if 'provider' in config:
        _config_manager.set_current_provider(config['provider'])
    
    # Update provider config if provided
    if 'api_key' in config:
        current_provider = _config_manager.get_current_provider()
        _config_manager.set_provider_api_key(current_provider, config['api_key'])
    
    # Update other settings
    update_keys = ['units', 'language', 'theme']
    updates = {k: config[k] for k in update_keys if k in config}
    if updates:
        _config_manager.update(**updates)
    
    # Save provider configs if provided
    if 'providers' in config and isinstance(config['providers'], dict):
        for provider, provider_config in config['providers'].items():
            _config_manager.update_provider_config(provider, provider_config)

# Backward compatible constants
DEFAULT_CONFIG = {
    'units': 'metric',
    'api_key': '',
    'language': 'en',
    'theme': 'dark',
    'provider': 'openmeteo',
    'providers': {}
}
