"""
Language package for the Weather application.

This package handles internationalization and localization of the application,
including loading and managing translations for different languages.
"""

__version__ = "1.0.0"
__all__ = ['language_manager', 'translations']

# Import the main language manager to make it available at the package level
from .language_manager import LanguageManager  # noqa: F401
