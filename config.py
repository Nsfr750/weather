import json
import os

CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    'units': 'metric',  # or 'imperial'
    'api_key': 'INSERT_API_HERE',
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
