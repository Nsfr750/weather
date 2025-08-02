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
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QFontMetrics
from PyQt6.QtCore import QByteArray, QIODevice, QBuffer, Qt

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
    """Create a QPixmap from an emoji character"""
    try:
        width, height = size
        
        # Create a transparent pixmap
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Set up painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Set font (use system emoji font if available)
        try:
            font_size = int(min(width, height) * 0.8)
            font = QFont()
            font.setFamily("Segoe UI Emoji")
            font.setPointSize(font_size)
            painter.setFont(font)
        except Exception as e:
            logging.warning(f"Failed to set emoji font: {e}")
            # Fallback to default font if emoji font fails
            font = painter.font()
            font.setPointSize(int(min(width, height) * 0.6))
            painter.setFont(font)
        
        # Draw emoji centered
        font_metrics = QFontMetrics(font)
        text_rect = font_metrics.boundingRect(emoji)
        x = (width - text_rect.width()) / 2
        y = (height + text_rect.height()) / 2 - font_metrics.descent()
        
        painter.drawText(int(x), int(y), emoji)
        painter.end()
        
        return pixmap
    except Exception as e:
        logging.error(f'Failed to create emoji icon: {e}', exc_info=True)
        return QPixmap()

def get_icon_image(icon_code, size=(64, 64)):
    """
    Fetch and cache weather icon images from OpenWeatherMap.
    If offline or fetch fails, falls back to emoji representation.
    Returns a QPixmap.
    """
    if not isinstance(size, (tuple, list)) or len(size) != 2:
        size = (64, 64)
    
    cache_key = (icon_code, size[0], size[1])
    if cache_key in _icon_cache:
        # Return a copy to avoid issues with pixmap modification
        return _icon_cache[cache_key].copy()
    
    # If in offline mode or we've had previous failures, use emoji fallback
    if _offline_mode or not _check_internet_connection():
        emoji = EMOJI_ICONS.get(icon_code, '')
        emoji_pixmap = _create_emoji_icon(emoji, size)
        if not emoji_pixmap.isNull():
            _icon_cache[cache_key] = emoji_pixmap
            return emoji_pixmap.copy()
    
    # Try to fetch the online icon
    url = f'http://openweathermap.org/img/wn/{icon_code}@2x.png'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        # Load image data into QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        
        # Resize if needed
        if pixmap.size() != size:
            pixmap = pixmap.scaled(
                size[0], size[1],
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        
        if not pixmap.isNull():
            _icon_cache[cache_key] = pixmap
            return pixmap.copy()
        
    except Exception as e:
        logging.warning(f'Failed to fetch online icon {icon_code}, using emoji fallback: {e}')
        set_offline_mode(True)
    
    # Fallback to emoji if anything went wrong
    emoji = EMOJI_ICONS.get(icon_code, '')
    emoji_pixmap = _create_emoji_icon(emoji, size)
    if not emoji_pixmap.isNull():
        _icon_cache[cache_key] = emoji_pixmap
        return emoji_pixmap.copy()
    
    # Return empty QPixmap as last resort
    return QPixmap()

def _check_internet_connection(timeout=5):
    """Check if we have an active internet connection"""
    try:
        requests.head('http://www.google.com', timeout=timeout)
        return True
    except requests.RequestException:
        return False
