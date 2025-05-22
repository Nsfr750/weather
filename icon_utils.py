"""
icon_utils.py
Utility functions for weather icon fetching and caching.
"""
import requests
from PIL import Image, ImageTk
import io
import logging

_icon_cache = {}


def get_icon_image(icon_code, size=(64, 64)):
    """
    Fetch and cache weather icon images from OpenWeatherMap.
    Returns a Tkinter-compatible PhotoImage.
    """
    cache_key = (icon_code, size)
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
    url = f'http://openweathermap.org/img/wn/{icon_code}@2x.png'
    try:
        r = requests.get(url)
        img = Image.open(io.BytesIO(r.content)).resize(size)
        tk_img = ImageTk.PhotoImage(img)
        _icon_cache[cache_key] = tk_img
        return tk_img
    except Exception as e:
        logging.error(f'Failed to fetch or process icon {icon_code}: {e}', exc_info=True)
        return None
