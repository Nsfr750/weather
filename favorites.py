import json
import os

FAV_FILE = 'favorites.json'

def load_favorites():
    if os.path.exists(FAV_FILE):
        with open(FAV_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_favorites(favorites):
    with open(FAV_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)
