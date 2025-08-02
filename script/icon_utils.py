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
    Fetch and cache weather icon images. Handles both local icon codes and full URLs.
    If offline or fetch fails, falls back to emoji representation.
    Returns a QPixmap.
    
    Args:
        icon_code: Either a local icon code (e.g., '01d') or a full URL to an icon
        size: Tuple of (width, height) for the output pixmap
        
    Returns:
        QPixmap containing the weather icon or an emoji fallback
    """
    if not icon_code:
        return QPixmap()
        
    if not isinstance(size, (tuple, list)) or len(size) != 2:
        size = (64, 64)
    
    # Create a cache key that includes both the icon_code and size
    cache_key = (str(icon_code), size[0], size[1])
    
    # Check cache first
    if cache_key in _icon_cache:
        cached = _icon_cache[cache_key]
        if not cached.isNull():
            return cached.copy()
    
    # If in offline mode, try to use emoji fallback immediately
    if _offline_mode:
        return _get_fallback_icon(icon_code, size, cache_key)
    
    # Determine if we have a URL or a local icon code
    is_url = (isinstance(icon_code, str) and 
             (icon_code.startswith('http://') or icon_code.startswith('https://')))
    
    # If we have a URL, try to fetch it
    if is_url:
        try:
            # Check cache with URL as key
            if cache_key in _icon_cache:
                return _icon_cache[cache_key].copy()
                
            # Check internet connection
            if not _check_internet_connection():
                set_offline_mode(True)
                return _get_fallback_icon(icon_code, size, cache_key)
                
            # Fetch the remote icon
            response = requests.get(icon_code, timeout=5)
            response.raise_for_status()
            
            # Load and cache the pixmap
            return _process_icon_data(response.content, size, cache_key)
            
        except Exception as e:
            logging.warning(f'Failed to fetch remote icon {icon_code}: {e}')
            return _get_fallback_icon(icon_code, size, cache_key)

def _process_icon_data(icon_data, size, cache_key):
    """Process icon data into a QPixmap and cache it."""
    try:
        pixmap = QPixmap()
        if not pixmap.loadFromData(icon_data):
            return QPixmap()
            
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
        logging.error(f'Error processing icon data: {e}')
        
    return QPixmap()

def _get_fallback_icon(icon_code, size, cache_key):
    """Get a fallback emoji icon for the given icon code."""
    # Try to extract the base icon code if it's a URL
    if isinstance(icon_code, str) and '/' in icon_code:
        # Extract the base filename without extension
        base_name = os.path.basename(icon_code).split('.')[0]
        # Remove any @2x suffix
        base_name = base_name.replace('@2x', '')
        emoji = EMOJI_ICONS.get(base_name, '☀️')  # Default to sun emoji
    else:
        emoji = EMOJI_ICONS.get(str(icon_code), '☀️')  # Default to sun emoji
    
    emoji_pixmap = _create_emoji_icon(emoji, size)
    if not emoji_pixmap.isNull():
        _icon_cache[cache_key] = emoji_pixmap
        return emoji_pixmap.copy()
    
    return QPixmap()

def _check_internet_connection(timeout=5):
    """Check if we have an active internet connection"""
    try:
        requests.head('http://www.google.com', timeout=timeout)
        return True
    except requests.RequestException:
        return False
