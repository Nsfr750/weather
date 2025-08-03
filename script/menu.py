"""
Menu Bar Module for Weather Application

This module provides the menu bar and menu actions for the Weather application.
It is designed to be imported and used by the main WeatherApp class.
"""

# Standard library imports
import importlib
import logging
import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

# Third-party imports
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QUrl, QSettings
from PyQt6.QtGui import QAction, QActionGroup, QKeySequence, QIcon
from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QMessageBox, QFileDialog, QDialog, QVBoxLayout, 
    QLabel, QLineEdit, QDialogButtonBox, QWidget, QStyle, QCheckBox
)

# Local application imports
from script.about import About
from script.help import Help
from script.sponsor import Sponsor
from script.log_viewer import LogViewer
from script.api_key_manager import ApiKeyManagerDialog

# Constants
DEFAULT_LANGUAGE = 'it'
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
    favorite_selected = pyqtSignal(str)  # Signal emitted when a favorite is selected
    show_about = pyqtSignal()
    show_help = pyqtSignal()
    check_updates = pyqtSignal()
    show_sponsor = pyqtSignal()
    exit_triggered = pyqtSignal()
    
    theme_changed = pyqtSignal(str)
    offline_mode_changed = pyqtSignal(bool)
    settings_updated = pyqtSignal()
    provider_changed = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None, 
                 translations: Optional[Dict[str, str]] = None,
                 translations_manager=None,
                 current_language: str = 'en',
                 current_units: str = 'metric') -> None:
        """Initialize the menu bar.
        
        Args:
            parent: The parent widget (main window)
            translations: Dictionary containing translations for menu items
            translations_manager: The translations manager instance
            current_language: The current language code (e.g., 'en', 'it')
            current_units: The current units system ('metric' or 'imperial')
        """
        super().__init__(parent)
        
        # Store parent and translations
        self.parent = parent
        self._translations = translations or {}
        self.translations_manager = translations_manager
        self.current_language = current_language
        self.current_units = current_units
        
        # Initialize settings
        self.settings = QSettings("WeatherApp", "WeatherApp")
        
        # Initialize theme and mode
        self.current_theme = DEFAULT_THEME
        self.offline_mode = False  # Default to online mode
        
        # Initialize action groups
        self.units_group = QActionGroup(self)
        self.theme_group = QActionGroup(self)
        self.language_group = QActionGroup(self)
        self.lang_group = QActionGroup(self)
        self.mode_group = QActionGroup(self)  # For online/offline mode
        self.lang_actions: Dict[str, QAction] = {}
        
        # Set up the UI
        self.setup_ui()
        
        # Create menus
        self._create_file_menu()
        self._create_view_menu()
        self._create_favorites_menu()
        self._create_settings_menu()
        self._create_language_menu()
        self._create_help_menu()
    
    def setup_ui(self):
        """Set up the menu bar UI components."""
        # This method is intentionally left empty as the UI setup is handled
        # by the individual _create_*_menu methods called in __init__
        
        # Apply styling
        self._apply_styling()
        
        logger.info("Menu bar initialized")
    
    def _create_file_menu(self) -> None:
        """Create the File menu with common application actions."""
        file_menu = self.addMenu(self._tr('🗃️ &File'))
        
        # Online/Offline mode
        mode_menu = file_menu.addMenu(self._tr('&Mode'))
        
        # Online mode action
        online_action = QAction(
            self._tr('&Online Mode'),
            self,
            checkable=True,
            checked=not self.offline_mode,
            statusTip=self._tr('Connect to the internet for weather data')
        )
        online_action.triggered.connect(lambda: self._on_mode_changed(False))
        self.mode_group.addAction(online_action)
        mode_menu.addAction(online_action)
        
        # Offline mode action
        offline_action = QAction(
            self._tr('O&ffline Mode'),
            self,
            checkable=True,
            checked=self.offline_mode,
            statusTip=self._tr('Work with cached data only')
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
            triggered=self.parent.close
        )
        file_menu.addAction(exit_action)
        
        # Store actions for later reference
        self.refresh_action = refresh_action
        self.exit_action = exit_action
    
    def _create_favorites_menu(self) -> None:
        """Create the Favorites menu with options to manage favorite cities."""
        favorites_menu = self.addMenu(self._tr('⭐ &Favorites'))
        
        # Add to Favorites action
        self.add_to_favorites_action = QAction(
            self._tr('&Add Current Location'),
            self,
            statusTip=self._tr('Add current location to favorites'),
            triggered=self.add_to_favorites.emit
        )
        favorites_menu.addAction(self.add_to_favorites_action)
        
        # Manage Favorites action
        manage_favorites_action = QAction(
            self._tr('&Manage Favorites...'),
            self,
            statusTip=self._tr('Add, edit, or remove favorite locations'),
            triggered=self.manage_favorites.emit
        )
        favorites_menu.addAction(manage_favorites_action)
        
        # Separator
        favorites_menu.addSeparator()
        
        # Favorites list submenu
        self.favorites_submenu = QMenu(self._tr('Select Favorite'), self)
        self.favorites_submenu.setStatusTip(self._tr('Select a favorite location to display'))
        favorites_menu.addMenu(self.favorites_submenu)
        
        # Store the menu for dynamic updates
        self.favorites_menu = favorites_menu
        self.favorites_actions = {}
        self._favorites = {}  # Store favorites for the submenu
        
        # Connect the aboutToShow signal to update the favorites list
        self.favorites_submenu.aboutToShow.connect(self._update_favorites_submenu)
        
        # Add a placeholder action (will be updated when favorites are loaded)
        no_favs = QAction(self._tr('No favorites yet'), self)
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
        settings_menu = self.addMenu(self._tr('⚙️ &Settings'))
        settings_menu.setObjectName("settingsMenu")  # Add this line
        
        # Units submenu
        units_menu = settings_menu.addMenu(self._tr('&Units'))
        self.unit_group = QActionGroup(self)
        
        # Metric units
        metric_action = QAction(self._tr('&Metric (C, m/s)'), self, checkable=True)
        metric_action.setData('metric')
        metric_action.triggered.connect(lambda: self._on_units_changed('metric'))
        self.unit_group.addAction(metric_action)
        units_menu.addAction(metric_action)
        
        # Imperial units
        imperial_action = QAction(self._tr('&Imperial (F, mph)'), self, checkable=True)
        imperial_action.setData('imperial')
        imperial_action.triggered.connect(lambda: self._on_units_changed('imperial'))
        self.unit_group.addAction(imperial_action)
        units_menu.addAction(imperial_action)
        
        # Set default unit
        current_unit = self.settings.value("units", "metric")
        for action in self.unit_group.actions():
            if action.data() == current_unit:
                action.setChecked(True)
                break
                
        # Separator
        settings_menu.addSeparator()
        
        # API Key Manager
        api_key_action = QAction(self._tr("&API Key Manager..."), self)
        api_key_action.triggered.connect(self._show_api_key_manager)
        api_key_action.setStatusTip(self._tr("Manage API keys for weather providers"))
        settings_menu.addAction(api_key_action)
        
        # Application settings
        app_settings_action = QAction(
            self._tr('Application Settings...'),
            self,
            statusTip=self._tr('Configure application settings'),
            triggered=self._show_app_settings
        )
        settings_menu.addAction(app_settings_action)
    
    def _create_view_menu(self) -> None:
        """Create the View menu with display options."""
        view_menu = self.addMenu(self._tr('👁️ &View'))
        
        # Toggle History action
        self.toggle_history_action = QAction(
            self._tr('Show &History'),
            self,
            checkable=True,
            checked=False,
            statusTip=self._tr('Show or hide the history panel')
        )
        self.toggle_history_action.triggered.connect(self.toggle_history.emit)
        view_menu.addAction(self.toggle_history_action)
        
        # Add a separator
        view_menu.addSeparator()
        
        # Fullscreen toggle
        fullscreen_action = QAction(
            self._tr('&Fullscreen'),
            self,
            shortcut=QKeySequence.StandardKey.FullScreen,
            statusTip=self._tr('Toggle fullscreen mode'),
            triggered=self._toggle_fullscreen
        )
        view_menu.addAction(fullscreen_action)
        
        # Store actions for later reference
        self.fullscreen_action = fullscreen_action
    
    def _create_language_menu(self) -> None:
        """Create the Language menu with available translations."""
        language_menu = self.addMenu(self._tr('🌐 &Language'))
        
        # Get available languages
        languages = {
            'en': 'English',
            'it': 'Italiano',
            'es': 'Español',
            'pt': 'Português',
            'fr': 'Français',
            'de': 'Deutsch',
            'ru': 'Русский',
            'ar': 'العربية',
            'ja': '日本語'
        }
        
        # Add language actions
        for code, name in languages.items():
            action = QAction(name, self, checkable=True)
            action.setData(code)  # Set data after creating the action
            action.triggered.connect(lambda checked, c=code: self._on_language_changed(c))
            self.language_group.addAction(action)
            language_menu.addAction(action)
        
        # Set current language
        current_lang = self.settings.value('language', 'en', str)
        for action in self.language_group.actions():
            if action.data() == current_lang:
                action.setChecked(True)
                break
    
    def _create_help_menu(self) -> None:
        """Create the Help menu with support and information options."""
        help_menu = self.addMenu(self._tr('❓ &Help'))
        
        # Help actions
        actions = [
            (self._tr('&About'), None, self._show_about_dialog),
            (self._tr('&Help'), 'F1', self._show_help_dialog),
            (self._tr('&Documentation'), 'F2', self._show_documentation),
            (self._tr('View &Logs'), 'F3', self._show_log_viewer),
            (self._tr('&Sponsor'), None, self._show_sponsor_dialog),
            (self._tr('Check for &Updates'), None, self._check_for_updates)
        ]
        
        for i, (text, shortcut, slot) in enumerate(actions):
            action = QAction(text, self, triggered=slot)
            if shortcut:
                action.setShortcut(shortcut)
            help_menu.addAction(action)
            
            # Add separators for better grouping
            if i in [0, 2, 3]:
                help_menu.addSeparator()
    
    def _get_language_name(self, lang_code: str) -> str:
        """Get the display name for a language code.
        
        Args:
            lang_code: ISO 639-1 language code (e.g., 'en', 'es')
            
        Returns:
            str: The display name of the language
        """
        lang_names = {
            'en': 'English',
            'it': 'Italiano',
            'es': 'Español',
            'pt': 'Português',
            'fr': 'Français',
            'de': 'Deutsch',
            'ru': 'Русский',
            'ar': 'العربية',
            'ja': '日本語'
        }
        return lang_names.get(lang_code, lang_code)
    
    def _apply_styling(self) -> None:
        """Apply consistent styling to the menu bar and its components."""
        # Only apply styling if the widget is properly initialized
        if not self.isVisible():
            return
            
        # Use a more robust approach to styling
        try:
            self.setStyleSheet("""
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
            """)
        except Exception as e:
            logger.error(f"Error applying menu styling: {e}")
    
    def _tr(self, text: str) -> str:
        """Translate text using the current translations.
        
        Args:
            text: The text to translate
            
        Returns:
            The translated text or the original if no translation is found
        """
        return self._translations.get(text, text)
    
    def update_translations(self, translations: Dict[str, str]) -> None:
        """Update the translations for the menu bar.
        
        Args:
            translations: Dictionary of translations
        """
        self._translations = translations or {}
        self.set_languages({}, self.current_language)  # Refresh language menu
        
        # Update menu titles
        for menu in self.findChildren(QMenu):
            menu_title = menu.title()
            if menu_title.startswith('&') and menu_title[1:] in self._translations:
                menu.setTitle('&' + self._translations[menu_title[1:]])
            elif menu_title in self._translations:
                menu.setTitle(self._translations[menu_title])
        
        # Update action texts
        for action in self.actions():
            if not action.text():
                continue
                
            # Remove '&' for translation lookup
            text = action.text().replace('&', '')
            if text in self._translations:
                translated = self._translations[text]
                # Preserve the original mnemonic if it had one
                if '&' in action.text():
                    translated = '&' + translated
                action.setText(translated)
            
            # Update tooltips and status tips
            if action.toolTip() and action.toolTip() in self._translations:
                action.setToolTip(self._translations[action.toolTip()])
            if action.statusTip() and action.statusTip() in self._translations:
                action.setStatusTip(self._translations[action.statusTip()])
    
    def set_units(self, units: str) -> None:
        """Set the currently selected units."""
        for action in self.units_group.actions():
            if action.data() == units:
                action.setChecked(True)
                break
    
    def set_languages(self, languages: Dict[str, str], current_lang: str) -> None:
        """Set the available languages and current language."""
        if not languages:
            return
            
        try:
            # Clear existing language actions
            for action in list(self.lang_actions.values()):
                if action in self.lang_group.actions():
                    self.lang_group.removeAction(action)
            self.lang_actions.clear()
            
            # Store current language
            self.current_language = current_lang.lower() if current_lang else 'en'
            
            # Find the language menu by iterating through all menus and their actions
            for menu in self.findChildren(QMenu):
                menu_title = menu.title().replace('&', '')  # Remove ampersand for comparison
                trans_lang = self._translations.get('language', 'Language').replace('&', '')
                
                if menu_title in ['Language', trans_lang]:
                    # Clear the existing menu in a safe way
                    menu.clear()
                    
                    # Add language actions
                    for code, name in languages.items():
                        if not code or not name:
                            continue
                            
                        action = QAction(name, self)
                        action.setCheckable(True)
                        action.setChecked(str(code).lower() == self.current_language)
                        action.setData(code)
                        action.triggered.connect(
                            lambda checked, c=code: self._on_language_changed(c)
                        )
                        
                        self.lang_group.addAction(action)
                        menu.addAction(action)
                        self.lang_actions[code] = action
                    
                    # Force update the menu
                    menu.update()
                    menu.repaint()
                    break
                    
        except Exception as e:
            import logging
            logging.error(f"Error in set_languages: {str(e)}")
    
    def set_theme(self, theme: str) -> None:
        """Set the currently selected theme."""
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
    
    def _on_language_changed(self, lang_code: str) -> None:
        """Handle language change."""
        # Save the selected language to config
        # self.config_manager.set('language', lang_code)
        self.language_changed.emit(lang_code)
    
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
    
    def _show_about_dialog(self) -> None:
        """Show the about dialog."""
        about = About(self)
        about.exec()
    
    def _check_for_updates(self) -> None:
        """Check for application updates."""
        try:
            # This would call your update checking logic
            # update_available, version = check_for_updates()
            update_available = False
            version = "1.0.0"
            
            if update_available:
                reply = QMessageBox.information(
                    self,
                    self._tr('Update Available'),
                    self._tr(f'Version {version} is available. Would you like to download it now?'),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    # self._download_update(version)
                    pass
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
            from script.api_key_manager import ApiKeyManagerDialog
            
            dialog = ApiKeyManagerDialog(self.parent)  # Use self.parent directly instead of self.parent()
            dialog.api_keys_updated.connect(self._on_api_keys_updated)
            dialog.exec()
            
        except ImportError as e:
            logger.error(f"Failed to import API key manager: {e}")
            QMessageBox.critical(
                self.parent,
                self._tr("Error"),
                self._tr("Failed to load API key manager: {}".format(str(e)))
            )
        except Exception as e:
            logger.error(f"Error showing API key manager: {e}")
            QMessageBox.critical(
                self.parent,
                self._tr("Error"),
                self._tr("An error occurred while opening the API key manager: {}".format(str(e)))
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
        from script.translations_utils import TranslationsManager
        from script.translations import TRANSLATIONS
        
        # Get the translations manager and current language
        translations_manager = TranslationsManager(TRANSLATIONS)
        current_language = self.current_language  # Assuming this is stored in the class
        
        help_dialog = Help(self, translations_manager, current_language)
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
        if not hasattr(self, 'parent') or not self.parent:
            logger.warning("Cannot toggle fullscreen: No parent window found")
            return
            
        if self.parent.isFullScreen():
            self.parent.showNormal()
            if hasattr(self, 'fullscreen_action'):
                self.fullscreen_action.setChecked(False)
            logger.debug("Exited fullscreen mode")
        else:
            self.parent.showFullScreen()
            if hasattr(self, 'fullscreen_action'):
                self.fullscreen_action.setChecked(True)
            logger.debug("Entered fullscreen mode")
    
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
                    translations: Optional[Dict[str, str]] = None) -> MenuBar:
    """
    Create and return a menu bar for the application.
    
    Args:
        parent: The parent widget (main window)
        translations: Dictionary containing translations for menu items
        
    Returns:
        MenuBar: The created menu bar
    """
    return MenuBar(parent, translations=translations)
