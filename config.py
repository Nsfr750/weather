import json
import os

CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    'units': 'metric',  # or 'imperial'
    'api_key': '1a5c879bc1d493f1458a50db471bcb2f',
    'language': 'IT',  # default language
    'theme': 'dark'    # default theme
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
