"""
favorites_utils.py
Utility functions and class for managing favorite cities in a modular way.
"""
import json
import os

FAV_FILE = 'favorites.json'

class FavoritesManager:
    def __init__(self, fav_file=FAV_FILE):
        self.fav_file = fav_file
        self.favorites = self.load_favorites()

    def load_favorites(self):
        if os.path.exists(self.fav_file):
            with open(self.fav_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except Exception:
                    return []
        return []

    def save_favorites(self):
        with open(self.fav_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)

    def add_favorite(self, city):
        city = city.strip()
        if city and city not in self.favorites:
            self.favorites.append(city)
            self.save_favorites()
            return True
        return False

    def remove_favorite(self, city):
        city = city.strip()
        if city in self.favorites:
            self.favorites.remove(city)
            self.save_favorites()
            return True
        return False

    def is_favorite(self, city):
        return city.strip() in self.favorites

    def get_favorites(self):
        return self.favorites[:]
