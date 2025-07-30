"""
icon_utils.py
Utility functions for weather icon fetching and caching with offline support.
"""
import os
import io
import logging
import requests
from wand.image import Image as WandImage
from wand.drawing import Drawing
from wand.color import Color
import tkinter as tk

_icon_cache = {}
_offline_mode = False

# Emoji fallbacks for common weather conditions
EMOJI_ICONS = {
    '01d': '☀️',  # clear sky (day)
    '01n': '🌙',  # clear sky (night)
    '02d': '⛅',  # few clouds (day)
    '02n': '☁️',  # few clouds (night)
    '03d': '☁️',  # scattered clouds
    '03n': '☁️',
    '04d': '☁️',  # broken clouds
    '04n': '☁️',
    '09d': '🌧️',  # shower rain
    '09n': '🌧️',
    '10d': '🌦️',  # rain (day)
    '10n': '🌧️',  # rain (night)
    '11d': '⛈️',  # thunderstorm
    '11n': '⛈️',
    '13d': '❄️',  # snow
    '13n': '❄️',
    '50d': '🌫️',  # mist
    '50n': '🌫️',
}

def set_offline_mode(enabled=True):
    """Enable or disable offline mode for icons"""
    global _offline_mode
    _offline_mode = enabled
    logging.info(f'Offline mode for icons: {enabled}')

def _create_emoji_icon(emoji, size):
    """Create an image from an emoji character"""
    try:
        with WandImage(width=size[0], height=size[1], background=Color('transparent')) as img:
            with Drawing() as draw:
                draw.font_size = min(size) * 0.8
                draw.text(0, int(size[1] * 0.8), emoji)
                draw(img)
            # Convert to Tkinter PhotoImage
            img_binary = img.make_blob('png')
            return tk.PhotoImage(data=img_binary)
    except Exception as e:
        logging.error(f'Failed to create emoji icon: {e}', exc_info=True)
        return None

def get_icon_image(icon_code, size=(64, 64)):
    """
    Fetch and cache weather icon images from OpenWeatherMap.
    If offline or fetch fails, falls back to emoji representation.
    Returns a Tkinter-compatible PhotoImage.
    """
    if not isinstance(size, (tuple, list)) or len(size) != 2:
        size = (64, 64)
    
    cache_key = (icon_code, size[0], size[1])
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
    
    # If in offline mode or we've had previous failures, use emoji fallback
    if _offline_mode or not _check_internet_connection():
        emoji = EMOJI_ICONS.get(icon_code, '❓')
        emoji_img = _create_emoji_icon(emoji, size)
        if emoji_img:
            _icon_cache[cache_key] = emoji_img
            return emoji_img
    
    # Try to fetch the online icon
    url = f'http://openweathermap.org/img/wn/{icon_code}@2x.png'
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        with WandImage(blob=r.content) as img:
            img.resize(size[0], size[1])
            img_binary = img.make_blob('png')
            tk_img = tk.PhotoImage(data=img_binary)
            _icon_cache[cache_key] = tk_img
            return tk_img
    except Exception as e:
        logging.warning(f'Failed to fetch online icon {icon_code}, using emoji fallback: {e}')
        set_offline_mode(True)
        emoji = EMOJI_ICONS.get(icon_code, '❓')
        emoji_img = _create_emoji_icon(emoji, size)
        if emoji_img:
            _icon_cache[cache_key] = emoji_img
            return emoji_img
        return None

def _check_internet_connection(timeout=5):
    """Check if we have an active internet connection"""
    try:
        requests.head('http://www.google.com', timeout=timeout)
        return True
    except requests.RequestException:
        return False
