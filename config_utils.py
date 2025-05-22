"""
config_utils.py
Utility class for managing application configuration in a modular way.
"""
import json
import os

CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    'units': 'metric',
    'api_key': '1a5c879bc1d493f1458a50db471bcb2f',
    'language': 'IT',
    'theme': 'dark'
}

class ConfigManager:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def update(self, **kwargs):
        self.config.update(kwargs)
        self.save_config()

    def get_config(self):
        return self.config.copy()
