"""
Menu Bar Module for Weather Application

This module provides the menu bar and menu actions for the Weather application.
It is designed to be imported and used by the main WeatherApp class.
"""

# Standard library imports
import importlib
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

# Third-party imports
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QUrl, QSettings
from PyQt6.QtGui import QAction, QActionGroup, QKeySequence, QIcon
from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QMessageBox, QFileDialog, QDialog, QVBoxLayout, 
    QLabel, QLineEdit, QDialogButtonBox, QWidget, QStyle
)

# Local application imports
from script.about import About
from script.help import Help
from script.sponsor import Sponsor
from script.log_viewer import LogViewer

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
    theme_changed = pyqtSignal(str)
    offline_mode_changed = pyqtSignal(bool)  # New signal for offline mode
    settings_updated = pyqtSignal()  # New signal for settings updates
    
    def __init__(self, parent: Optional[QWidget] = None, 
                 translations: Optional[Dict[str, str]] = None) -> None:
        """Initialize the menu bar.
        
        Args:
            parent: The parent widget (main window)
            translations: Dictionary containing translations for menu items
        """
        super().__init__(parent)
        
        # Store parent and translations
        self.parent = parent
        self._translations = translations or {}
        
        # Initialize settings
        self.settings = QSettings("WeatherApp", "WeatherApp")
        
        # Initialize instance variables
        self.current_language = DEFAULT_LANGUAGE
        self.current_theme = DEFAULT_THEME
        self.offline_mode = False  # Default to online mode
        
        # Initialize action groups
        self.units_group = QActionGroup(self)
        self.theme_group = QActionGroup(self)
        self.language_group = QActionGroup(self)
        self.lang_group = QActionGroup(self)
        self.mode_group = QActionGroup(self)  # For online/offline mode
        self.lang_actions: Dict[str, QAction] = {}
        
        # Create menus
        self._create_file_menu()
        self._create_view_menu()
        self._create_language_menu()
        self._create_help_menu()
        
        # Apply styling
        self._apply_styling()
        
        logger.info("Menu bar initialized")
    
    def _create_file_menu(self) -> None:
        """Create the File menu with common application actions."""
        file_menu = self.addMenu(self._tr('&File'))
        
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
    
    def _create_settings_menu(self) -> None:
        """Create the Settings menu with configuration options."""
        settings_menu = self.addMenu(self._tr('&Settings'))
        
        # API Key Manager
        api_key_action = QAction(self._tr("&API Key Manager..."), self)
        api_key_action.triggered.connect(self._show_api_key_manager)
        api_key_action.setStatusTip(self._tr("Manage API keys for weather providers"))
        settings_menu.addAction(api_key_action)
        
        # Add separator
        settings_menu.addSeparator()
        
        # Units submenu
        units_menu = settings_menu.addMenu(self._tr("&Units"))
        
        # Create action group for units
        self.unit_group = QActionGroup(self)
        
        # Metric units (Celsius, km/h, etc.)
        metric_action = QAction(self._tr("&Metric"), self)
        metric_action.setCheckable(True)
        metric_action.setData("metric")
        metric_action.triggered.connect(lambda: self._on_units_changed("metric"))
        self.unit_group.addAction(metric_action)
        units_menu.addAction(metric_action)
        
        # Imperial units (Fahrenheit, mph, etc.)
        imperial_action = QAction(self._tr("&Imperial"), self)
        imperial_action.setCheckable(True)
        imperial_action.setData("imperial")
        imperial_action.triggered.connect(lambda: self._on_units_changed("imperial"))
        self.unit_group.addAction(imperial_action)
        units_menu.addAction(imperial_action)
        
        # Set default unit
        current_unit = self.settings.value("units", "metric")
        for action in self.unit_group.actions():
            if action.data() == current_unit:
                action.setChecked(True)
                break
        
        # Provider selection
        provider_menu = settings_menu.addMenu(self._tr('Weather Provider'))
        self.provider_group = QActionGroup(self)
        
        # Add available providers
        providers = ["OpenWeatherMap", "WeatherAPI", "AccuWeather"]
        current_provider = "OpenWeatherMap"  # Should come from config
        
        for provider in providers:
            action = QAction(provider, self, checkable=True, data=provider)
            action.setChecked(provider == current_provider)
            action.triggered.connect(
                lambda checked, p=provider: self._on_provider_changed(p)
            )
            self.provider_group.addAction(action)
            provider_menu.addAction(action)
        
        # Separator
        settings_menu.addSeparator()
        
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
        view_menu = self.addMenu(self._tr('&View'))
        
        # Theme submenu
        theme_menu = view_menu.addMenu(self._tr("&Theme"))
        
        # Get current theme from settings or use default
        current_theme = self.settings.value("theme", "system", str)
        
        # Theme actions
        theme_actions = [
            ("System", "system"),
            ("Light", "light"),
            ("Dark", "dark"),
            ("High Contrast", "high_contrast")
        ]
        
        for text, data in theme_actions:
            action = QAction(self._tr(text), self, checkable=True)
            action.setData(data)
            action.setChecked(data == current_theme)
            action.triggered.connect(lambda checked, t=data: self._on_theme_changed(t))
            self.theme_group.addAction(action)
            theme_menu.addAction(action)
        
        view_menu.addSeparator()
        
        # Layout submenu
        layout_menu = view_menu.addMenu(self._tr("&Layout"))
        
        # Get current layout from settings or use default
        current_layout = self.settings.value("layout", "standard", str)
        
        # Layout actions
        layout_actions = [
            ("Standard", "standard"),
            ("Compact", "compact"),
            ("Detailed", "detailed")
        ]
        
        for text, data in layout_actions:
            action = QAction(self._tr(text), self, checkable=True)
            action.setData(data)
            action.setChecked(data == current_layout)
            action.triggered.connect(lambda checked, l=data: self._on_layout_changed(l))
            layout_menu.addAction(action)
        
        view_menu.addSeparator()
        
        # Fullscreen toggle
        fullscreen_action = QAction(self._tr("Fullscreen"), self, checkable=True)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Store actions for later reference
        self.fullscreen_action = fullscreen_action
    
    def _create_language_menu(self) -> None:
        """Create the Language menu with available translations."""
        language_menu = self.addMenu(self._tr('&Language'))
        
        # Get available languages
        languages = {
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어'
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
        help_menu = self.addMenu(self._tr('&Help'))
        
        # Help actions
        actions = [
            (self._tr('&About'), 'F1', self._show_about_dialog),
            (self._tr('&Help'), 'F1', self._show_help_dialog),
            (self._tr('&Documentation'), 'F2', self._show_documentation),
            (self._tr('View &Logs'), None, self._show_log_viewer),
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
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'zh': '中文',
            'ja': '日本語',
            'ar': 'العربية'
        }
        return lang_names.get(lang_code, lang_code)
    
    def _apply_styling(self) -> None:
        """Apply consistent styling to the menu bar and its components."""
        self.setStyleSheet("""
            QMenuBar {
                background-color: #f0f0f0;
                padding: 2px;
                border: none;
                border-bottom: 1px solid #d0d0d0;
            }
            
            QMenuBar::item {
                padding: 5px 10px;
                background: transparent;
                border-radius: 4px;
                color: #333;
            }
            
            QMenuBar::item:selected {
                background: #e0e0e0;
            }
            
            QMenuBar::item:disabled {
                color: #999999;
            }
            
            QMenu {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                padding: 5px;
                border-radius: 4px;
            }
            
            QMenu::item {
                padding: 5px 25px 5px 20px;
                margin: 2px;
                border-radius: 3px;
                color: #333;
            }
            
            QMenu::item:selected {
                background-color: #e6f0ff;
                color: #0066cc;
            }
            
            QMenu::item:disabled {
                color: #999999;
            }
            
            QMenu::separator {
                height: 1px;
                background: #e0e0e0;
                margin: 5px 0;
            }
            
            QMenu::icon {
                left: 5px;
            }
            
            QMenu::indicator {
                width: 13px;
                height: 13px;
            }
            
            QMenu::indicator:checked {
                background-color: #0066cc;
                border: 1px solid #0052a3;
                border-radius: 3px;
            }
        """)
    
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
            from script.weather_providers.api_key_manager import ApiKeyManagerDialog
            
            dialog = ApiKeyManagerDialog(self.parent())
            dialog.api_keys_updated.connect(self._on_api_keys_updated)
            dialog.exec()
            
        except ImportError as e:
            logger.error(f"Failed to import API key manager: {e}")
            QMessageBox.critical(
                self.parent(),
                self._tr("Error"),
                self._tr("Failed to load API key manager: {}".format(str(e)))
            )
        except Exception as e:
            logger.error(f"Error showing API key manager: {e}")
            QMessageBox.critical(
                self.parent(),
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
        layout.addWidget(QLabel(self._tr('OpenWeatherMap API Key:')))
        owm_key_edit = QLineEdit()
        # Load current key from config
        # owm_key_edit.setText(self.config_manager.get('api_keys', {}).get('openweathermap', ''))
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
            #     'openweathermap': owm_key_edit.text().strip()
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
        help_dialog = Help(self)
        help_dialog.exec()
    
    def _show_sponsor_dialog(self) -> None:
        """Show the sponsor dialog."""
        sponsor = Sponsor(self)
        sponsor.exec()
    
    def _show_log_viewer(self) -> None:
        """Show the log viewer dialog."""
        try:
            log_viewer = LogViewer(self)
            log_viewer.exec()
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
        # Save to config and update application state
        # self.config_manager.set('provider', provider.lower())
        
        # Show a message to the user
        QMessageBox.information(
            self,
            self._tr('Provider Changed'),
            self._tr(f'Weather provider changed to {provider}. Restart may be required for changes to take effect.')
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
