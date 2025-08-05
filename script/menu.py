"""
Menu Bar Module for Weather Application

This module provides the menu bar and menu actions for the Weather application.
It is designed to be imported and used by the main WeatherApp class.
"""

# Standard library imports
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Callable, Union

# Third-party imports
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QTimer
from PyQt6.QtGui import QAction, QActionGroup, QKeySequence, QIcon
from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QMessageBox, QFileDialog, QVBoxLayout, 
    QLabel, QLineEdit, QDialogButtonBox, QWidget, QStyle
)

# Local application imports
from script.about import About
from script.help import Help
from script.sponsor import Sponsor
from script.log_viewer import LogViewer
from script.api_key_manager import ApiKeyManagerDialog
from lang.language_manager import LanguageManager

# Constants
DEFAULT_LANGUAGE = 'en'
DEFAULT_THEME = 'dark'
DEFAULT_UNITS = 'metric'

# Configure logging
logger = logging.getLogger(__name__)

class MenuBar(QMenuBar):
    """
    Custom menu bar for the Weather application.
    
    Provides a fully featured menu system with support for themes, languages,
    and application settings.
    """
    
    # Signals
    refresh_triggered = pyqtSignal()
    units_changed = pyqtSignal(str)
    language_changed = pyqtSignal(str)
    toggle_history = pyqtSignal(bool)
    add_to_favorites = pyqtSignal()
    manage_favorites = pyqtSignal()
    favorite_selected = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    offline_mode_changed = pyqtSignal(bool)
    settings_updated = pyqtSignal()
    provider_changed = pyqtSignal(str)
    
    def _tr(self, text: str, default: str = None) -> str:
        """
        Translate text using the language manager.
        
        Args:
            text: The text to translate
            default: Default text if translation is not found
            
        Returns:
            str: The translated text or the original text if not found
        """
        if not text:
            return text
            
        if not hasattr(self, 'language_manager') or not self.language_manager:
            logger.warning(f"No language manager available for translation of: {text}")
            return text if default is None else default
            
        # Try to get translation, fall back to default or original text
        result = self.language_manager.get(text, default if default is not None else text)
        logger.debug(f"Translated '{text}' to '{result}' in language {self.language_manager.current_language}")
        return result
        
    def __init__(self, 
                 parent: Optional[QWidget] = None, 
                 language_manager: Optional[LanguageManager] = None,
                 config_manager=None,
                 theme: str = DEFAULT_THEME,
                 language: str = DEFAULT_LANGUAGE,
                 units: str = DEFAULT_UNITS,
                 on_refresh: Optional[Callable] = None,
                 on_units_changed: Optional[Callable] = None,
                 on_theme_changed: Optional[Callable] = None,
                 on_show_about: Optional[Callable] = None,
                 on_show_help: Optional[Callable] = None,
                 on_show_sponsor: Optional[Callable] = None,
                 on_check_updates: Optional[Callable] = None,
                 on_show_maps: Optional[Callable] = None,
                 on_show_log_viewer: Optional[Callable] = None,
                 on_show_api_key_manager: Optional[Callable] = None,
                 on_import_settings: Optional[Callable] = None,
                 on_export_settings: Optional[Callable] = None,
                 on_quit: Optional[Callable] = None) -> None:
        """
        Initialize the menu bar.
        
        Args:
            parent: The parent widget.
            language_manager: The language manager instance.
            config_manager: The configuration manager instance.
            theme: The current theme.
            language: The current language code.
            units: The current units system (metric/imperial).
            on_refresh: Callback for refresh action.
            on_units_changed: Callback when units are changed.
            on_theme_changed: Callback when theme is changed.
            on_show_about: Callback for showing about dialog.
            on_check_updates: Callback for checking updates.
            on_show_maps: Callback for showing weather maps.
            on_show_log_viewer: Callback for showing log viewer.
            on_show_api_key_manager: Callback for showing API key manager.
            on_import_settings: Callback for importing settings.
            on_export_settings: Callback for exporting settings.
            on_quit: Callback for quit action.
        """
        super().__init__(parent)
        
        # Store references
        self.language_manager = language_manager or LanguageManager()
        self.config_manager = config_manager
        self.theme = theme
        self.language = language
        self.units = units
        
        # Store callbacks
        self.on_refresh = on_refresh
        self.on_units_changed = on_units_changed
        self.on_theme_changed = on_theme_changed
        self.on_show_about = on_show_about
        self.on_show_help = on_show_help
        self.on_show_sponsor = on_show_sponsor
        self.on_check_updates = on_check_updates
        self.on_show_maps = on_show_maps
        self.on_show_log_viewer = on_show_log_viewer
        self.on_show_api_key_manager = on_show_api_key_manager
        self.on_import_settings = on_import_settings
        self.on_export_settings = on_export_settings
        self.on_quit = on_quit
        
        # Initialize mode settings
        self.offline_mode = False  # Default to online mode
        self.mode_group = QActionGroup(self)  # For radio button behavior
        
        # Initialize UI
        self._init_ui()
        self._apply_styling()
        
        logger.info("Menu bar initialized")
    
    def _init_ui(self) -> None:
        """Initialize the user interface components."""
        # Create all menu items
        self._create_file_menu()
        self._create_favorites_menu()
        self._create_settings_menu()
        self._create_view_menu()
        self._create_language_menu()
        self._create_help_menu()
    
    def _create_file_menu(self) -> None:
        """Create the File menu with common application actions."""
        file_menu = self.addMenu(self._tr('file_menu'))
        
        # Online/Offline mode
        mode_menu = file_menu.addMenu(self._tr('mode_menu'))
        
        # Online mode action
        online_action = QAction(
            self._tr('online_mode'),
            self,
            checkable=True,
            checked=not self.offline_mode,
            statusTip=self._tr('online_mode_tip')
        )
        online_action.triggered.connect(lambda: self._on_mode_changed(False))
        self.mode_group.addAction(online_action)
        mode_menu.addAction(online_action)
        
        # Offline mode action
        offline_action = QAction(
            self._tr('offline_mode'),
            self,
            checkable=True,
            checked=self.offline_mode,
            statusTip=self._tr('offline_mode_tip')
        )
        offline_action.triggered.connect(lambda: self._on_mode_changed(True))
        self.mode_group.addAction(offline_action)
        mode_menu.addAction(offline_action)
        
        # Separator
        file_menu.addSeparator()
        
        # Refresh action
        refresh_action = QAction(
            self._tr('&Refresh'),
            self,
            shortcut=QKeySequence.StandardKey.Refresh,
            statusTip=self._tr('Refresh weather data'),
            triggered=self.refresh_triggered.emit
        )
        file_menu.addAction(refresh_action)
        
        # Separator
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction(
            self._tr('E&xit'),
            self,
            shortcut=QKeySequence.StandardKey.Quit,
            statusTip=self._tr('Exit the application'),
            triggered=self.on_quit if self.on_quit else self.parent().close
        )
        file_menu.addAction(exit_action)
        
        # Store actions for later reference
        self.refresh_action = refresh_action
        self.exit_action = exit_action
    
    def _create_favorites_menu(self) -> None:
        """Create the Favorites menu with options to manage favorite cities."""
        favorites_menu = self.addMenu(self._tr('favorites_menu'))
        
        # Add to Favorites action
        self.add_to_favorites_action = QAction(
            self._tr('add_to_favorites'),
            self,
            statusTip=self._tr('add_favorite_tip'),
            triggered=self.add_to_favorites.emit
        )
        favorites_menu.addAction(self.add_to_favorites_action)
        
        # Manage Favorites action
        manage_favorites_action = QAction(
            self._tr('manage_favorites') + '...',
            self,
            statusTip=self._tr('manage_favorites_tip'),
            triggered=self.manage_favorites.emit
        )
        favorites_menu.addAction(manage_favorites_action)
        
        # Add a separator
        favorites_menu.addSeparator()
        
        # Favorites submenu
        self.favorites_submenu = favorites_menu.addMenu(self._tr('select_favorite'))
        
        # Store the menu for dynamic updates
        self.favorites_menu = favorites_menu
        self.favorites_actions = {}
        self._favorites = {}  # Store favorites for the submenu
        
        # Connect the aboutToShow signal to update the favorites list
        self.favorites_submenu.aboutToShow.connect(self._update_favorites_submenu)
        
        # Add a placeholder action (will be updated when favorites are loaded)
        no_favs = QAction(self._tr('no_favorites'), self)
        no_favs.setEnabled(False)
        self.favorites_submenu.addAction(no_favs)
        
        # Load initial favorites
        self._load_favorites()
    
        
    def _load_favorites(self) -> None:
        """Load favorites from the config/favorites.json file."""
        try:
            favorites_path = Path('config/favorites.json')
            if favorites_path.exists():
                with open(favorites_path, 'r', encoding='utf-8') as f:
                    favorites_list = json.load(f)
                    # Convert list to dict with city as both key and value for compatibility
                    self._favorites = {city: city for city in favorites_list}
            else:
                self._favorites = {}
        except Exception as e:
            logger.error(f"Error loading favorites: {e}")
            self._favorites = {}
    
    def _update_favorites_submenu(self) -> None:
        """Update the favorites submenu with the current list of favorites."""
        if not hasattr(self, 'favorites_submenu'):
            return
            
        # Reload favorites from file
        self._load_favorites()
            
        # Clear existing actions
        self.favorites_submenu.clear()
        
        # Add a disabled action if no favorites
        if not self._favorites:
            no_favs = QAction(self._tr('No favorites yet'), self)
            no_favs.setEnabled(False)
            self.favorites_submenu.addAction(no_favs)
            return
            
        # Add each favorite as a selectable action
        for name, location in self._favorites.items():
            action = QAction(
                f"{name}: {location}",
                self,
                statusTip=f"Show weather for {name} ({location})",
                triggered=lambda checked, loc=location: self.favorite_selected.emit(loc)
            )
            self.favorites_submenu.addAction(action)
    
    def _create_settings_menu(self) -> None:
        """Create the Settings menu with configuration options."""
        settings_menu = self.addMenu(self._tr('settings_menu'))
        settings_menu.setObjectName("settingsMenu")
        
        # Units submenu
        units_menu = settings_menu.addMenu(self._tr('units_menu'))
        self.unit_group = QActionGroup(self)
        
        # Metric units
        metric_action = QAction(self._tr('metric_units'), self, checkable=True)
        metric_action.setStatusTip(self._tr('metric_units_tip'))
        metric_action.setData('metric')
        metric_action.triggered.connect(lambda: self._on_units_changed('metric'))
        self.unit_group.addAction(metric_action)
        units_menu.addAction(metric_action)
        
        # Imperial units
        imperial_action = QAction(self._tr('imperial_units'), self, checkable=True)
        imperial_action.setStatusTip(self._tr('imperial_units_tip'))
        imperial_action.setData('imperial')
        imperial_action.triggered.connect(lambda: self._on_units_changed('imperial'))
        self.unit_group.addAction(imperial_action)
        units_menu.addAction(imperial_action)
        
        # Set the current units
        if self.units == 'metric':
            metric_action.setChecked(True)
        else:
            imperial_action.setChecked(True)
            
        # Theme submenu
        theme_menu = settings_menu.addMenu(self._tr('theme'))
        self.theme_group = QActionGroup(self)
        
        # Light theme
        light_theme = QAction(self._tr('light_theme'), self, checkable=True)
        light_theme.setData('light')
        light_theme.triggered.connect(lambda: self._on_theme_changed('light'))
        self.theme_group.addAction(light_theme)
        theme_menu.addAction(light_theme)
        
        # Dark theme
        dark_theme = QAction(self._tr('dark_theme'), self, checkable=True)
        dark_theme.setData('dark')
        dark_theme.triggered.connect(lambda: self._on_theme_changed('dark'))
        self.theme_group.addAction(dark_theme)
        theme_menu.addAction(dark_theme)
        
        # Set the current theme
        if self.theme == 'light':
            light_theme.setChecked(True)
        else:
            dark_theme.setChecked(True)
            
        # Separator
        settings_menu.addSeparator()
        
        # API Key Manager
        api_key_action = QAction(
            self._tr('api_key_manager'),
            self,
            statusTip=self._tr('api_key_manager_tip'),
            triggered=self._show_api_key_manager
        )
        settings_menu.addAction(api_key_action)
        
        # Application settings
        app_settings_action = QAction(
            self._tr('application_settings') + '...',
            self,
            statusTip=self._tr('app_settings_tip'),
            triggered=self._show_app_settings
        )
        settings_menu.addAction(app_settings_action)
    
    def _create_view_menu(self) -> None:
        """Create the View menu with display options."""
        view_menu = self.addMenu(self._tr('view_menu'))
        
        # Add Weather Maps & Radar action
        self.maps_action = QAction(
            QIcon(str(Path('assets/map.png'))) if Path('assets/map.png').exists() else QIcon(),
            self._tr('weather_maps'),
            self
        )
        self.maps_action.setStatusTip(self._tr('weather_maps_tip'))
        self.maps_action.triggered.connect(self._show_maps_dialog)
        view_menu.addAction(self.maps_action)
        view_menu.addSeparator()
        
        # Toggle History action
        self.toggle_history_action = QAction(
            self._tr('show_history'),
            self,
            checkable=True,
            checked=False,
            statusTip=self._tr('show_history_tip')
        )
        self.toggle_history_action.triggered.connect(self.toggle_history.emit)
        view_menu.addAction(self.toggle_history_action)
        
        # Add a separator
        view_menu.addSeparator()
        
        # Fullscreen toggle
        fullscreen_action = QAction(
            self._tr('fullscreen'),
            self,
            shortcut=QKeySequence.StandardKey.FullScreen,
            statusTip=self._tr('fullscreen_tip'),
            triggered=self._toggle_fullscreen
        )
        view_menu.addAction(fullscreen_action)
        
        # Store actions for later reference
        self.fullscreen_action = fullscreen_action
    
    def _create_language_menu(self) -> None:
        """Create the Language menu with available translations."""
        language_menu = self.addMenu(self._tr('language_menu'))
        self.language_group = QActionGroup(self)
        
        # Get available languages from the language manager
        if not hasattr(self, 'language_manager') or not self.language_manager:
            logger.warning("Language manager not available")
            # Fallback to English if there's an error
            action = language_menu.addAction(self._tr('english'))
            action.setCheckable(True)
            action.setChecked(True)
            action.setData('en')
            self.language_group.addAction(action)
            return
            
        try:
            # Get available languages from the translations directory
            available_languages = {}
            for file in self.language_manager.translations_dir.glob('*.json'):
                lang_code = file.stem.lower()
                # Get the language name from the translation file itself
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        lang_name = data.get(f'language_{lang_code}', lang_code)
                        available_languages[lang_code] = lang_name
                except Exception as e:
                    logger.error(f"Error loading language {lang_code}: {e}")
            
            # Sort languages by their display name
            sorted_languages = sorted(available_languages.items(), key=lambda x: x[1])
            
            # Add a language action for each available language
            for lang_code, lang_name in sorted_languages:
                # Skip if we don't have a display name for this language
                if not lang_name or not lang_code:
                    continue
                
                # Create the action with the language name
                action = QAction(lang_name, self, checkable=True)
                action.setData(lang_code)
                
                # Use a lambda with a default argument to capture the current lang_code
                action.triggered.connect(lambda checked, lc=lang_code: self._on_language_changed(lc))
                
                # Add to the action group and menu
                self.language_group.addAction(action)
                language_menu.addAction(action)
                
                # Check if this is the current language
                if lang_code == self.language:
                    action.setChecked(True)
                    
        except Exception as e:
            logger.error(f"Error creating language menu: {e}", exc_info=True)
            # Fallback to English if there's an error
            action = language_menu.addAction('English')
            action.setCheckable(True)
            action.setChecked(True)
            action.setData('en')
            self.language_group.addAction(action)
    
    def _create_help_menu(self) -> None:
        """Create the Help menu with support and information options."""
        help_menu = self.addMenu(self._tr('help_menu'))
        
        # Help actions with translations
        actions = [
            (self._tr('about'), 'F1', self._show_about_dialog, self._tr('about_tip')),
            (self._tr('help'), 'F1', self._show_help_dialog, self._tr('help_tip')),
            (self._tr('documentation'), 'F2', self._show_documentation, self._tr('documentation_tip')),
            (self._tr('view_logs'), 'F3', self._show_log_viewer, self._tr('view_logs_tip')),
            (self._tr('sponsor'), None, self._show_sponsor_dialog, self._tr('sponsor_tip')),
            (self._tr('check_updates'), None, self._check_for_updates, self._tr('check_updates_tip'))
        ]
        
        for i, (text, shortcut, slot, tooltip) in enumerate(actions):
            action = QAction(text, self, triggered=slot)
            action.setStatusTip(tooltip)
            if shortcut:
                action.setShortcut(shortcut)
            help_menu.addAction(action)
            
            # Add separators for better grouping
            if i in [0, 2, 3]:
                help_menu.addSeparator()
    

    
    def _apply_styling(self) -> None:
        """Apply consistent styling to the menu bar and its components.
        
        This method applies styles to the menu bar and its components. It includes
        additional safety checks to prevent QPainter warnings that can occur when
        the widget is not yet properly initialized or visible.
        """
        # Only apply styling if the widget is properly initialized and has a paint device
        if not self.isVisible() or not self.testAttribute(Qt.WidgetAttribute.WA_WState_Created):
            # Schedule restyling for when the widget is shown
            QTimer.singleShot(100, self._apply_styling)
            return
            
        try:
            # Store the current style sheet
            style_sheet = """
                QMenuBar {
                    background-color: #2c3e50;
                    padding: 2px;
                    border: none;
                    color: #ecf0f1;
                }
                
                QMenuBar::item {
                    padding: 5px 10px;
                    background: transparent;
                    border-radius: 4px;
                    color: #ecf0f1;
                }
                
                QMenuBar::item:selected {
                    background: #34495e;
                }
                
                QMenuBar::item:disabled {
                    color: #7f8c8d;
                }
                
                QMenu {
                    background-color: #2c3e50;
                    border: 1px solid #34495e;
                    padding: 5px;
                    color: #ecf0f1;
                    border-radius: 4px;
                }
                
                QMenu::item {
                    padding: 5px 25px 5px 20px;
                    background: transparent;
                }
                
                QMenu::item:selected {
                    background: #3498db;
                    color: white;
                }
                
                QMenu::item:disabled {
                    color: #7f8c8d;
                }
                
                QMenu::separator {
                    height: 1px;
                    background: #34495e;
                    margin: 5px 5px;
                }
                
                QMenu::icon {
                    left: 5px;
                }
                
                QMenu::indicator {
                    width: 13px;
                    height: 13px;
                }
                
                QMenu::indicator:checked {
                    background-color: #3498db;
                    border: 1px solid #2980b9;
                    border-radius: 3px;
                }
            """
            
            # Apply the style sheet
            self.setStyleSheet(style_sheet)
            
            # Force a style refresh
            self.style().unpolish(self)
            self.style().polish(self)
            
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                # Widget was deleted, ignore
                return
            logger.error(f"Runtime error applying menu styling: {e}")
        except Exception as e:
            logger.error(f"Error applying menu styling: {e}")
        finally:
            # Ensure we don't have a dangling reference
            if hasattr(self, '_style_timer'):
                self._style_timer = None
    
    def _tr(self, text: str, **kwargs) -> str:
        """Translate text using the current translations.
        
        Args:
            text: The text to translate
            **kwargs: Additional arguments to format the translated string
            
        Returns:
            The translated text, or the original text if no translation is found
        """
        try:
            # Use the language manager to get the translation
            return self.language_manager.get(text, text, **kwargs)
        except Exception as e:
            logger.warning(f"Translation error for '{text}': {e}")
            return text
        
    def update_translations(self) -> None:
        """Update all menu items with the current translations."""
        try:
            logger.info("Force rebuilding menu for language update...")
            
            # Store current state
            current_theme = self.theme
            current_language = self.language
            current_units = self.units
            current_provider = getattr(self, 'current_provider', None)
            
            # Clear existing menus
            self.clear()
            
            # Rebuild the menu structure
            self._init_ui()
            
            # Restore the state
            self.set_theme(current_theme)
            self.set_units(current_units)
            if current_provider:
                self.set_providers([current_provider], current_provider)
                
            # Force a complete UI update
            self.update()
            self.repaint()
            
            logger.info("Menu rebuilt successfully with new translations")
            
        except Exception as e:
            logger.error(f"Error rebuilding menu: {str(e)}", exc_info=True)
            try:
                # Fallback to the old method if rebuild fails
                self._update_translations_fallback()
            except Exception as fallback_error:
                logger.error(f"Fallback translation update failed: {str(fallback_error)}", exc_info=True)
                
    def _update_translations_fallback(self):
        """Fallback method to update translations without rebuilding the menu."""
        try:
            logger.info("Using fallback translation update method...")
            
            def update_widget_text(widget, text):
                if not text or not hasattr(widget, 'setText'):
                    return
                clean_text = text.replace('&', '')
                translated = self._tr(clean_text)
                if '&' in text:
                    widget.setText('&' + translated)
                else:
                    widget.setText(translated)
            
            # Update all menus and actions
            for widget in self.findChildren((QMenu, QAction)):
                try:
                    if isinstance(widget, QMenu):
                        update_widget_text(widget, widget.title())
                    else:  # QAction
                        update_widget_text(widget, widget.text())
                        if widget.toolTip():
                            widget.setToolTip(self._tr(widget.toolTip()))
                        if widget.statusTip():
                            widget.setStatusTip(self._tr(widget.statusTip()))
                except Exception as e:
                    logger.error(f"Error updating widget {widget}: {str(e)}", exc_info=True)
            
            # Special handling for language menu items
            if hasattr(self, 'language_menu'):
                try:
                    for action in self.language_menu.actions():
                        if action.data():
                            lang_name = self.language_manager.get(
                                f'language_{action.data()}', 
                                action.data().upper()
                            )
                            action.setText(lang_name)
                except Exception as e:
                    logger.error(f"Error updating language menu: {str(e)}", exc_info=True)
            
            self.update()
            self.repaint()
            logger.info("Fallback translation update completed")
            
        except Exception as e:
            logger.error(f"Critical error in fallback translation update: {str(e)}", exc_info=True)
    
    def set_units(self, units: str) -> None:
        """Set the currently selected units."""
        if hasattr(self, 'unit_group'):
            for action in self.unit_group.actions():
                if action.data() == units:
                    action.setChecked(True)
                    break
    
    def set_theme(self, theme: str) -> None:
        """Set the currently selected theme."""
        if hasattr(self, 'theme_group'):
            for action in self.theme_group.actions():
                if action.data() == theme:
                    action.setChecked(True)
                    break
    
    def set_providers(self, providers: List[str], current_provider: str) -> None:
        """Set the available weather providers and select the current one.
        
        Args:
            providers: List of available weather provider names
            current_provider: Name of the currently selected provider
        """
        # Find the Weather Provider submenu
        settings_menu = self.findChild(QMenu, "settingsMenu")
        if not settings_menu:
            logger.warning("Could not find settings menu")
            return
            
        # Find the provider menu
        provider_menu = None
        for action in settings_menu.actions():
            if action.text() == self._tr('Weather Provider'):
                provider_menu = action.menu()
                break
                
        if not provider_menu:
            logger.warning("Could not find Weather Provider menu")
            return
            
        # Clear existing provider actions
        for action in self.provider_group.actions():
            provider_menu.removeAction(action)
            self.provider_group.removeAction(action)
        
        # Add the new providers
        for provider in providers:
            action = QAction(provider, self, checkable=True)
            action.setChecked(provider == current_provider)
            action.triggered.connect(
                lambda checked, p=provider: self._on_provider_changed(p)
            )
            self.provider_group.addAction(action)
            provider_menu.addAction(action)
            action.setData(provider)
    
    def _on_units_changed(self, units: str) -> None:
        """Handle units change."""
        self.units_changed.emit(units)
    
    def _on_language_changed(self, action_or_lang: Union[QAction, str]) -> None:
        """Handle language change from the menu.
        
        Args:
            action_or_lang: Either a QAction with language data or a string language code
        """
        # Handle both QAction and direct string language codes
        if isinstance(action_or_lang, QAction):
            language = action_or_lang.data()
        else:
            language = action_or_lang
            
        if language and hasattr(self, 'language') and language != self.language:
            # Update the language in the language manager
            if self.language_manager.set_language(language):
                self.language = language
                
                # Save the language preference
                if self.config_manager:
                    self.config_manager.set('language', language)
                    self.config_manager.save()
                
                # Emit signal to notify the main application
                self.language_changed.emit(language)
                
                # Update the UI
                self.update_translations()
            else:
                logger.error(f"Failed to set language to {language}")
                # Revert the menu selection
                for a in self.language_group.actions():
                    if a.data() == self.language:
                        a.setChecked(True)
                        break
    
    def _on_theme_changed(self, theme: str) -> None:
        """Handle theme change."""
        self.theme_changed.emit(theme)
    
    def _show_documentation(self) -> None:
        """Show the documentation using markdown_viewer.py."""
        try:
            # Get the current language from the application
            current_lang = getattr(self, 'current_language', 'EN')
            
            # Start the markdown viewer in a separate process
            import subprocess
            import sys
            import os
            
            # Get the path to the Python interpreter and the script
            python = sys.executable
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'md_viewer.py'))
            
            # Get the project root directory (one level up from script directory)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            
            # Create a command that sets up the Python path correctly
            cmd = [
                python,
                script_path,
                current_lang
            ]
            
            # Set up the environment with the correct PYTHONPATH
            env = os.environ.copy()
            env['PYTHONPATH'] = project_root
            
            # Start the markdown viewer with the current language
            subprocess.Popen(cmd, env=env)
            
        except Exception as e:
            # Log the error
            import logging
            logging.error(f"Error opening documentation: {str(e)}")
            
            # Show error message to the user
            QMessageBox.critical(
                self,
                self._translations.get('error', 'Error'),
                self._translations.get('error_loading_file', 'Error loading file:') + f" {str(e)}"
            )
    
    def _show_maps_dialog(self):
        """Show the Weather Maps & Radar dialog."""
        try:
            from script.maps_dialog import show_maps_dialog
            # Call parent() to get the parent widget, not the parent method
            show_maps_dialog(self.parent(), self.language_manager)
        except ImportError as e:
            logger.error(f"Failed to load maps dialog: {e}")
            QMessageBox.critical(
                self,
                self._tr("error"),
                self._tr("error_loading_maps")
            )
    
    def _show_about_dialog(self):
        """Show the about dialog."""
        About.show_about(self)
    
    def _check_for_updates(self) -> None:
        """Check for application updates."""
        try:
            # Placeholder for update check logic
            update_available = False
            version = "1.0.0"
            
            if update_available:
                reply = QMessageBox.information(
                    self,
                    self._tr('Update Available'),
                    self._tr('Version {} is available. Would you like to download it now?').format(version),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
            else:
                QMessageBox.information(
                    self,
                    self._tr('No Updates'),
                    self._tr('You are using the latest version.')
                )
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Failed to check for updates: {}').format(str(e))
            )
    
    def _show_api_key_manager(self):
        """Show the API Key Manager dialog."""
        try:
            dialog = ApiKeyManagerDialog(self.parent)
            dialog.api_keys_updated.connect(self._on_api_keys_updated)
            dialog.exec()
        except Exception as e:
            logger.error(f"Error showing API key manager: {e}")
            QMessageBox.critical(
                self.parent,
                self._tr("Error"),
                self._tr("Failed to load API key manager: {}").format(str(e))
            )
    
    def _on_api_keys_updated(self):
        """Handle API keys being updated."""
        logger.info("API keys were updated")
        # Emit signal to notify other components
        self.settings_updated.emit()
    
    def _show_api_key_dialog(self) -> None:
        """Show the API key management dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle(self._tr('Manage API Keys'))
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Add form fields for API keys
        layout.addWidget(QLabel(self._tr('OpenMeteo API Key:')))
        owm_key_edit = QLineEdit()
        # Load current key from config
        # owm_key_edit.setText(self.config_manager.get('api_keys', {}).get('openmeteo', ''))
        layout.addWidget(owm_key_edit)
        
        # Add more API key fields as needed
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save API keys to config
            # self.config_manager.set('api_keys', {
            #     'openmeteo': owm_key_edit.text().strip()
            # })
            QMessageBox.information(
                self,
                self._tr('Success'),
                self._tr('API keys have been saved. Changes will take effect the next time you fetch weather data.')
            )
    
    def _show_app_settings(self) -> None:
        """Show the application settings dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle(self._tr('Application Settings'))
        dialog.setMinimumWidth(450)
        
        layout = QVBoxLayout(dialog)
        
        # Add settings widgets here
        # Example: Auto-update checkbox
        auto_update_chk = QCheckBox(self._tr('Check for updates automatically'))
        # auto_update_chk.setChecked(self.config_manager.get('auto_update', True))
        layout.addWidget(auto_update_chk)
        
        # Add more settings as needed
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save settings
            # self.config_manager.set('auto_update', auto_update_chk.isChecked())
            QMessageBox.information(
                self,
                self._tr('Settings Saved'),
                self._tr('Application settings have been saved.')
            )
    
    def _show_help_dialog(self) -> None:
        """Show the help dialog."""
        from script.help import Help
        
        # Create help dialog with the current language manager
        help_dialog = Help(self, self.language_manager, self.language)
        help_dialog.exec()
    
    def _show_sponsor_dialog(self) -> None:
        """Show the sponsor dialog."""
        sponsor = Sponsor(self)
        sponsor.exec()
    
    def _show_log_viewer(self) -> None:
        """Show the log viewer dialog."""
        try:
            from script.log_viewer import show_log
            show_log(self)
        except Exception as e:
            logger.error(f"Failed to open log viewer: {e}")
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Failed to open log viewer: {}').format(str(e))
            )
    
    def _on_provider_changed(self, provider: str) -> None:
        """Handle weather provider change.
        
        Args:
            provider: The selected weather provider
        """
        logger.info(f"Weather provider changed to: {provider}")
        
        # Save the selected provider to settings
        settings = QSettings("WeatherApp", "WeatherApp")
        settings.setValue("weather_provider", provider.lower())
        
        # Emit the provider_changed signal
        self.provider_changed.emit(provider.lower())
        
        # Show a success message
        QMessageBox.information(
            self,
            self._tr('Provider Changed'),
            self._tr(f'Weather provider changed to {provider}.')
        )
    
    def _on_mode_changed(self, offline: bool) -> None:
        """Handle online/offline mode change.
        
        Args:
            offline: True if offline mode is enabled, False for online mode
        """
        if self.offline_mode == offline:
            return
            
        self.offline_mode = offline
        logger.info(f"{'Offline' if offline else 'Online'} mode enabled")
        
        # Update UI state based on mode
        for action in self.mode_group.actions():
            if action.text().lower().startswith('offline' if offline else 'online'):
                action.setChecked(True)
        
        # Emit signal to notify other components
        self.offline_mode_changed.emit(offline)
        
        # Show status message
        QMessageBox.information(
            self,
            self._tr('Mode Changed'),
            self._tr('Now in {} mode').format(
                self._tr('Offline') if offline else self._tr('Online')
            )
        )
    
    def set_offline_mode(self, offline: bool) -> None:
        """Set the offline mode programmatically.
        
        Args:
            offline: True to enable offline mode, False for online mode
        """
        if self.offline_mode != offline:
            self._on_mode_changed(offline)
    
    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode for the main window."""
        try:
            # Get the parent widget (using callable check in case it's a method)
            parent = self.parent() if callable(self.parent) else self.parent
            
            if not parent:
                logger.warning("Cannot toggle fullscreen: No parent window found")
                return
                
            if parent.isFullScreen():
                parent.showNormal()
                if hasattr(self, 'fullscreen_action'):
                    self.fullscreen_action.setChecked(False)
                logger.debug("Exited fullscreen mode")
            else:
                parent.showFullScreen()
                if hasattr(self, 'fullscreen_action'):
                    self.fullscreen_action.setChecked(True)
                logger.debug("Entered fullscreen mode")
        except Exception as e:
            logger.error(f"Error toggling fullscreen: {e}")
    
    def _on_layout_changed(self, layout: str) -> None:
        """Handle layout change in the view menu.
        
        Args:
            layout: The selected layout name (e.g., 'standard', 'compact', 'detailed')
        """
        logger.info(f"Layout changed to: {layout}")
        self.settings.setValue("layout", layout)
        
        # Emit a signal if needed (uncomment if you want to connect this to other components)
        # if hasattr(self.parent(), 'on_layout_changed'):
        #     self.parent().on_layout_changed(layout)
    
def create_menu_bar(parent: Optional[QWidget] = None, 
                    language_manager: Optional[LanguageManager] = None) -> MenuBar:
    """
    Create and return a menu bar for the application.
    
    Args:
        parent: The parent widget (main window)
        language_manager: The language manager instance for translations
        
    Returns:
        MenuBar: The created menu bar
    """
    return MenuBar(parent=parent, language_manager=language_manager)
