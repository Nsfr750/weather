"""
Weather provider plugins for the Weather Application.

This package contains weather provider plugins that can be loaded by the application.
"""

# This file is intentionally left empty.
# It serves to mark the directory as a Python package.
# The plugin manager will discover and load plugins from this directory.

__all__ = [  # List of plugin module names can be added here if needed
    'accuweather_plugin',
    'openmeteo_plugin',
    'openweathermap_plugin',
    'example_provider',
    'example_plugin'
]