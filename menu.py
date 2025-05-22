"""
Menu Bar Module for Weather Application

This module provides the menu bar and menu actions for the Weather application.
It is designed to be imported and used by the main WeatherApp class.
"""

import tkinter as tk
from tkinter import messagebox
from about import About
from help import Help
from sponsor import Sponsor
from log_viewer import LogViewer


def create_menu_bar(root, app):
    """
    Create the application menu bar and attach it to the root window.
    Args:
        root: The main Tkinter root window
        app: The WeatherApp instance (for callbacks)
    """
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)

    # View menu
    view_menu = tk.Menu(menubar, tearoff=0)
    view_menu.add_command(label="Refresh", command=app.refresh_weather)
    view_menu.add_separator()
    # Add more view options here if needed
    menubar.add_cascade(label="View", menu=view_menu)

    # Settings menu
    settings_menu = tk.Menu(menubar, tearoff=0)
    settings_menu.add_command(label="Preferences...", command=app._show_settings)
    menubar.add_cascade(label="Settings", menu=settings_menu)

    # Log menu (placeholder, implement log view if needed)
    log_menu = tk.Menu(menubar, tearoff=0)
    log_menu.add_command(label="View Log", command=lambda: LogViewer.show_log(root))
    menubar.add_cascade(label="Log", menu=log_menu)

    # API menu (placeholder, implement API insert if needed)
    api_menu = tk.Menu(menubar, tearoff=0)
    api_menu.add_command(label="Insert API Key", command=app._show_settings)
    menubar.add_cascade(label="API", menu=api_menu)

    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="Help", command=lambda: Help.show_help(root, app.translations_manager, app.language))
    help_menu.add_separator()
    help_menu.add_command(label="About", command=lambda: About.show_about(root))
    help_menu.add_command(label="Sponsor", command=lambda: Sponsor(root).show_sponsor())
    menubar.add_cascade(label="Help", menu=help_menu)

    return menubar
