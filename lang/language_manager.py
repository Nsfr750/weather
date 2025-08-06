"""
Language Manager Module

This module provides a centralized way to manage translations for the Weather application.
It handles loading translation files, switching between languages, and providing
translated strings to the application.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Set, Any, Union, List
import os
from PyQt6.QtCore import QObject, pyqtSignal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageManager(QObject):
    """
    Manages language translations for the application.
    
    Signals:
        language_changed: Emitted when the language is changed
    
    Attributes:
        translations_dir (Path): Directory containing translation files
        translations (Dict[str, Dict[str, str]]): Loaded translations by language code
        available_languages (Set[str]): Set of available language codes
        current_language (str): Currently selected language code (default: 'en')
    """
    # Signal emitted when the language is changed
    language_changed = pyqtSignal(str)
    
    def __init__(self, translations_dir: Union[str, Path] = None):
        """
        Initialize the language manager with translations directory.
        
        Args:
            translations_dir: Path to directory containing translation files.
                            Defaults to 'lang/translations' relative to the script.
        """
        # Initialize QObject parent class
        super().__init__()
        
        # Set up translations directory
        if translations_dir is None:
            # Default to lang/translations relative to the script location
            base_dir = Path(__file__).parent.parent
            self.translations_dir = base_dir / "lang" / "translations"
        else:
            self.translations_dir = Path(translations_dir)
            
        # Ensure directory exists
        self.translations_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize instance variables
        self.translations: Dict[str, Dict[str, str]] = {}
        self.available_languages: Set[str] = set()
        self.current_language: str = "it"  # Default to Italian
        
        # Load available languages
        self._discover_languages()
        
        # Load default language if available
        if self.current_language in self.available_languages:
            self._load_language(self.current_language)
    
    def _discover_languages(self) -> None:
        """
        Discover available language files in the translations directory.
        
        Updates self.available_languages with found language codes.
        """
        try:
            # Clear existing languages
            self.available_languages.clear()
            
            # Find all JSON files in the translations directory
            for file in sorted(self.translations_dir.glob("*.json")):
                try:
                    # Validate the file is valid JSON
                    with open(file, 'r', encoding='utf-8') as f:
                        json.load(f)  # Validate JSON
                    
                    # Add the language code (filename without extension, lowercased)
                    lang_code = file.stem.lower()
                    self.available_languages.add(lang_code)
                    logger.debug(f"Discovered language: {lang_code}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in {file.name}: {e}")
                except Exception as e:
                    logger.error(f"Error processing {file.name}: {e}")
                    
            logger.info(f"Discovered {len(self.available_languages)} languages: {', '.join(sorted(self.available_languages))}")
            
        except Exception as e:
            logger.error(f"Error discovering languages: {e}", exc_info=True)
    
    def _load_language(self, lang_code: str) -> bool:
        """
        Load translations for a specific language.
        
        Args:
            lang_code: Language code to load (e.g., 'en', 'it')
            
        Returns:
            bool: True if language was loaded successfully, False otherwise
        """
        if not lang_code:
            logger.error("No language code provided")
            return False
            
        lang_code = lang_code.lower()
        file_path = self.translations_dir / f"{lang_code}.json"
        
        try:
            if not file_path.exists():
                logger.error(f"Translation file not found: {file_path}")
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                
            if not isinstance(translations, dict):
                logger.error(f"Invalid translation format in {file_path}: expected dict, got {type(translations)}")
                return False
                
            # Store the translations
            self.translations[lang_code] = translations
            logger.info(f"Loaded {len(translations)} translations for language: {lang_code}")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading language {lang_code}: {e}", exc_info=True)
            
        return False
    
    def set_language(self, lang_code: str) -> bool:
        """
        Set the current application language.
        
        Args:
            lang_code: Language code to set (e.g., 'en', 'it')
            
        Returns:
            bool: True if language was set successfully, False otherwise
            
        Emits:
            language_changed: Signal with the new language code when language is changed
        """
        if not lang_code:
            logger.error("No language code provided")
            return False
            
        lang_code = lang_code.lower()
        
        # Check if language is available
        if lang_code not in self.available_languages:
            logger.warning(f"Language not available: {lang_code}")
            return False
        
        # Load the language if not already loaded
        if lang_code not in self.translations:
            if not self._load_language(lang_code):
                return False
        
        # Set the current language
        self.current_language = lang_code
        logger.info(f"Language set to: {lang_code}")
        
        # Emit signal that language has changed
        self.language_changed.emit(lang_code)
        
        return True
    
    def get(self, key: str, default: str = None, **kwargs) -> str:
        """
        Get a translated string for the current language.
        
        Args:
            key: Translation key to look up
            default: Default value to return if key is not found
            **kwargs: Format arguments for string formatting
            
        Returns:
            str: The translated string, or the key if not found
        """
        if not key:
            logger.warning("Empty translation key provided")
            return ""
        
        # Ensure current language is loaded
        if self.current_language not in self.translations:
            if not self._load_language(self.current_language):
                logger.warning(f"Failed to load language: {self.current_language}")
                return default or key
        
        # Get the translation
        translations = self.translations.get(self.current_language, {})
        text = translations.get(key, default)
        
        # Return key if translation not found
        if text is None:
            logger.debug(f"Translation not found for key: {key} in language: {self.current_language}")
            return key
        
        # Format the string if there are format arguments
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError) as e:
                logger.warning(f"Error formatting string for key '{key}': {e}")
                return text
                
        return text
    
    def get_available_languages(self) -> List[str]:
        """
        Get a list of available language codes.
        
        Returns:
            List[str]: Sorted list of available language codes
        """
        return sorted(self.available_languages)
    
    def __call__(self, key: str, default: str = None, **kwargs) -> str:
        """
        Allow the instance to be called directly to get translations.
        
        Example:
            _ = language_manager
            greeting = _("welcome_message")
        """
        return self.get(key, default, **kwargs)
    
    def get_current_language(self) -> str:
        """Get current language code."""
        return self.current_language
    
    # Make the instance callable as a shortcut for get()
    __call__ = get

# Global instance
language_manager = LanguageManager()

def get_language_manager() -> LanguageManager:
    """Get the global language manager instance."""
    return language_manager
