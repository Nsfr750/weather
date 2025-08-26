"""
Resources module for the application.
This module handles the loading of Qt resources (icons, etc.)
"""
import os
from pathlib import Path
from PyQt6.QtCore import QFile, QIODevice
from PyQt6.QtGui import QIcon

def load_resources():
    """Load application resources."""
    # This function will be called from the main application
    # to ensure resources are loaded before they're needed
    pass

def get_icon(name: str) -> QIcon:
    """Get an icon by name from the resources.
    
    Args:
        name: Name of the icon without extension
        
    Returns:
        QIcon: The requested icon or an empty icon if not found
    """
    # First try to load from theme
    icon = QIcon.fromTheme(name)
    if not icon.isNull():
        return icon
        
    # Then try to load from resources
    icon_path = f":/menu_icons/{name}.svg"
    if QFile.exists(icon_path):
        return QIcon(icon_path)
        
    # Return empty icon if not found
    return QIcon()
