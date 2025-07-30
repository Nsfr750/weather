"""
Menu Bar Module for Weather Application

This module provides the menu bar and menu actions for the Weather application.
It is designed to be imported and used by the main WeatherApp class.
"""

# Debug imports
import sys
import importlib
import os

def check_pyqt6_installation():
    """Check PyQt6 installation and available modules."""
    print("\n=== PyQt6 Installation Check ===")
    
    # Check if PyQt6 is installed
    try:
        import PyQt6
        print(f"PyQt6 version: {PyQt6.QtCore.PYQT_VERSION_STR}")
        print(f"Qt version: {PyQt6.QtCore.QT_VERSION_STR}")
        
        # List available PyQt6 modules
        print("\nAvailable PyQt6 modules:")
        modules = [
            'QtCore', 'QtGui', 'QtWidgets', 'QtNetwork', 'QtPrintSupport',
            'QtSvg', 'QtTest', 'QtWebEngineWidgets', 'QtWebEngineCore'
        ]
        for module in modules:
            try:
                mod = importlib.import_module(f'PyQt6.{module}')
                print(f"- {module}: {mod.__file__}")
            except ImportError:
                print(f"- {module}: Not available")
                
    except ImportError as e:
        print(f"Error importing PyQt6: {e}")
        print("Please make sure PyQt6 is installed in your virtual environment.")
        print("You can install it with: pip install PyQt6")
    
    print("=" * 30 + "\n")

# Run the check when this module is imported
check_pyqt6_installation()

from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QMessageBox, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDialogButtonBox
)
from PyQt6.QtGui import QAction, QKeySequence, QActionGroup
from PyQt6.QtCore import Qt, QObject, pyqtSignal

from script.about import About
from script.help import Help
from script.sponsor import Sponsor
from script.log_viewer import LogViewer


class MenuBar(QMenuBar):
    """Custom menu bar for the Weather application."""
    
    # Signals
    refresh_triggered = pyqtSignal()
    units_changed = pyqtSignal(str)
    language_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None, translations=None):
        """Initialize the menu bar.
        
        Args:
            parent: The parent widget
            translations: Dictionary containing translations for menu items
        """
        super().__init__(parent)
        self.setObjectName("menuBar")
        
        # Store translations
        self.translations = translations or {}
        
        # Store references to actions that need to be updated
        self.units_group = QActionGroup(self)
        self.lang_group = QActionGroup(self)
        self.theme_group = QActionGroup(self)
        self.lang_actions = {}  # Initialize empty dictionary for language actions
        
        # Create menus
        self._create_file_menu()
        self._create_view_menu()
        self._create_settings_menu()
        self._create_language_menu()
        self._create_help_menu()
        
        # Apply styling
        self._apply_styling()
    
    def _create_file_menu(self):
        """Create the File menu."""
        file_menu = self.addMenu("&File")
        
        # Refresh action
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self.refresh_triggered.emit)
        file_menu.addAction(refresh_action)
        
        # Separator
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.parent().close)
        file_menu.addAction(exit_action)
    
    def _create_settings_menu(self):
        """Create the Settings menu."""
        settings_menu = self.addMenu("&Settings")
        
        # API Key management
        api_key_action = QAction("Manage API Keys...", self)
        api_key_action.triggered.connect(self._show_api_key_dialog)
        settings_menu.addAction(api_key_action)
        
        # Provider selection
        provider_menu = settings_menu.addMenu("Weather Provider")
        self.provider_group = QActionGroup(self)
        
        # Add available providers
        providers = ["OpenWeatherMap", "WeatherAPI", "AccuWeather"]  # Example providers
        current_provider = "OpenWeatherMap"  # Get this from config in real implementation
        
        for provider in providers:
            action = QAction(provider, self)
            action.setCheckable(True)
            action.setChecked(provider == current_provider)
            action.triggered.connect(lambda checked, p=provider: self._on_provider_changed(p))
            self.provider_group.addAction(action)
            provider_menu.addAction(action)
        
        # Separator
        settings_menu.addSeparator()
        
        # Application settings
        app_settings_action = QAction("Application Settings...", self)
        app_settings_action.triggered.connect(self._show_app_settings)
        settings_menu.addAction(app_settings_action)
    
    def _create_view_menu(self):
        """Create the View menu with units and theme options."""
        view_menu = self.addMenu("&View")
        
        # Units submenu
        units_menu = view_menu.addMenu("&Units")
        
        # Unit actions
        metric_action = QAction("&Metric (°C, m/s, mm)", self)
        metric_action.setCheckable(True)
        metric_action.setData("metric")
        metric_action.triggered.connect(lambda: self._on_units_changed("metric"))
        
        imperial_action = QAction("&Imperial (°F, mph, in)", self)
        imperial_action.setCheckable(True)
        imperial_action.setData("imperial")
        imperial_action.triggered.connect(lambda: self._on_units_changed("imperial"))
        
        # Add to group for mutual exclusivity
        self.units_group.addAction(metric_action)
        self.units_group.addAction(imperial_action)
        
        # Add to menu
        units_menu.addAction(metric_action)
        units_menu.addAction(imperial_action)
        
        # Theme submenu
        theme_menu = view_menu.addMenu("&Theme")
        
        # Theme actions
        system_action = QAction("System Default", self)
        system_action.setCheckable(True)
        system_action.setData("system")
        system_action.triggered.connect(lambda: self._on_theme_changed("system"))
        
        light_action = QAction("Light", self)
        light_action.setCheckable(True)
        light_action.setData("light")
        light_action.triggered.connect(lambda: self._on_theme_changed("light"))
        
        dark_action = QAction("Dark", self)
        dark_action.setCheckable(True)
        dark_action.setData("dark")
        dark_action.triggered.connect(lambda: self._on_theme_changed("dark"))
        
        # Add to group for mutual exclusivity
        self.theme_group.addAction(system_action)
        self.theme_group.addAction(light_action)
        self.theme_group.addAction(dark_action)
        
        # Add to menu
        theme_menu.addAction(system_action)
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)
        
        # Set current theme from config or use dark as default
        current_theme = getattr(self, 'current_theme', 'dark')
        if current_theme == 'system':
            system_action.setChecked(True)
        elif current_theme == 'light':
            light_action.setChecked(True)
        else:
            dark_action.setChecked(True)
    
    def _create_language_menu(self):
        """Create the Language menu with available languages."""
        # Create Language menu
        lang_menu = self.addMenu("&Language")
        
        # Language actions group
        self.lang_group = QActionGroup(self)
        self.lang_actions = {}
        
        # Get available languages from translations
        try:
            from script.translations import TRANSLATIONS
            
            # Define language display names (lowercase keys for matching)
            language_names = {
                'en': 'English',
                'it': 'Italiano',
                'es': 'Español',
                'pt': 'Português',
                'fr': 'Français',
                'de': 'Deutsch',
                'ru': 'Русский',
                'zh': '中文',
                'ja': '日本語',
                'ar': 'العربية'
            }
            
            # Get available languages from TRANSLATIONS dictionary (convert to lowercase for consistency)
            available_langs = {}
            for lang_code in TRANSLATIONS.keys():
                # Convert to lowercase for internal use, but keep original for display
                lc_code = lang_code.lower()
                available_langs[lc_code] = language_names.get(lc_code, lang_code)
            
            # Get current language from config or use default
            current_lang = getattr(self, 'current_language', 'en')
            
            # Add language actions
            for lang_code, lang_name in available_langs.items():
                action = QAction(lang_name, self)
                action.setCheckable(True)
                action.setChecked(lang_code == current_lang)
                action.setData(lang_code)
                action.triggered.connect(
                    lambda checked, lc=lang_code: self._on_language_changed(lc)
                )
                self.lang_group.addAction(action)
                self.lang_actions[lang_code] = action
                lang_menu.addAction(action)  # Add action to the menu
                
        except Exception as e:
            import logging
            logging.error(f"Error loading languages: {str(e)}")
            # Add a disabled action to show error
            error_action = QAction("Error loading languages", self)
            error_action.setEnabled(False)
            lang_menu.addAction(error_action)
    
    def _create_help_menu(self):
        """Create the Help menu."""
        help_menu = self.addMenu(self.translations.get('help', '&Help'))

        # About action
        about_action = QAction(self.translations.get('about', '&About'), self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
        
        # Separator
        help_menu.addSeparator()
        
        # Help action
        help_action = QAction(self.translations.get('help', '&Help'), self)
        help_action.triggered.connect(self._show_help_dialog)
        help_menu.addAction(help_action)
        
        # Documentation action
        docs_action = QAction(self.translations.get('documentation', '&Documentation'), self)
        docs_action.triggered.connect(self._show_documentation)
        help_menu.addAction(docs_action)
        
        # Separator
        help_menu.addSeparator()
        
        # Log viewer action
        log_action = QAction(self.translations.get('view_log', 'View &Logs'), self)
        log_action.triggered.connect(self._show_log_viewer)
        help_menu.addAction(log_action)
        
        # Separator
        help_menu.addSeparator()
        
        # Sponsor action
        sponsor_action = QAction(self.translations.get('sponsor', '&Sponsor'), self)
        sponsor_action.triggered.connect(self._show_sponsor_dialog)
        help_menu.addAction(sponsor_action)
        
        # Separator
        help_menu.addSeparator()
        
        # Check for updates action
        update_action = QAction(self.translations.get('check_updates', 'Check for &Updates'), self)
        update_action.triggered.connect(self._check_for_updates)
        help_menu.addAction(update_action)
    
    def _apply_styling(self):
        """Apply styling to the menu bar."""
        self.setStyleSheet("""
            QMenuBar {
                background-color: #b3d9ff;  /* Dark blue background */
                padding: 2px;
                border: none;
                border-bottom: 1px solid #b3d9ff;  /* Slightly darker blue border */
            }
            
            QMenuBar::item {
                padding: 5px 10px;
                background: transparent;
                border-radius: 4px;
                color: #000  /* Black text */
            }
            
            QMenuBar::item:selected {
                background: #cce6ff;  /* Lighter blue when selected */
            }
            
            QMenuBar::item:pressed {
                background: #99ccff;  /* Medium blue when pressed */
            }
            
            QMenu {
                background-color: #e6f3ff;  /* Light blue background */
                border: 1px solid #b3d9ff;
                padding: 5px;
                border-radius: 4px;
            }
            
            QMenu::item {
                padding: 5px 25px 5px 20px;
                margin: 2px;
                border-radius: 3px;
                color: #0066cc;  /* Darker blue text */
            }
            
            QMenu::item:selected {
                background-color: #cce6ff;  /* Lighter blue when selected */
            }
            
            QMenu::item:disabled {
                color: #99c2ff;  /* Lighter blue for disabled items */
            }
            
            QMenu::separator {
                height: 1px;
                background: #b3d9ff;  /* Border color */
                margin: 5px 0;
            }
            
            QMenu::indicator {
                width: 13px;
                height: 13px;
            }
            
            QMenu::indicator:unchecked {
                border: 1px solid #99c2ff;  /* Lighter blue border */
                border-radius: 3px;
                background: white;
            }
            
            QMenu::indicator:checked {
                border: 1px solid #0066cc;  /* Darker blue border */
                border-radius: 3px;
                background: #4da6ff;  /* Medium blue background */
            }
        """)
    
    def set_units(self, units):
        """Set the currently selected units."""
        for action in self.units_group.actions():
            if action.data() == units:
                action.setChecked(True)
                break
    
    def set_languages(self, languages, current_lang):
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
                trans_lang = self.translations.get('language', 'Language').replace('&', '')
                
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
    
    def set_theme(self, theme):
        """Set the currently selected theme."""
        for action in self.theme_group.actions():
            if action.data() == theme:
                action.setChecked(True)
                break
    
    def _on_units_changed(self, units):
        """Handle units change."""
        self.units_changed.emit(units)
    
    def _on_language_changed(self, lang_code):
        """Handle language change."""
        # Save the selected language to config
        # self.config_manager.set('language', lang_code)
        self.language_changed.emit(lang_code)
    
    def _on_theme_changed(self, theme):
        """Handle theme change."""
        self.theme_changed.emit(theme)
    
    def _show_documentation(self):
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
                self.translations.get('error', 'Error'),
                self.translations.get('error_loading_file', 'Error loading file:') + f" {str(e)}"
            )
    
    def _show_about_dialog(self):
        """Show the about dialog."""
        from script.about import AboutDialog
        AboutDialog.show_about(self.parent())            
    
    def _check_for_updates(self):
        """Check for application updates."""
        from script.updates import check_for_updates
        check_for_updates(self.parent())
    
    def _show_sponsor_dialog(self):
        """Show the sponsor dialog."""
        from script.sponsor import Sponsor
        Sponsor.show_sponsor_dialog(self.parent())
    
    def _show_api_key_dialog(self):
        """Show the API key management dialog."""
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
            QLineEdit, QDialogButtonBox
        )
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage API Keys")
        layout = QVBoxLayout(dialog)
        
        # Add widgets for API key management
        layout.addWidget(QLabel("Enter your API keys:"))
        
        # Example for OpenWeatherMap API key
        owm_layout = QHBoxLayout()
        owm_layout.addWidget(QLabel("OpenWeatherMap:"))
        owm_key = QLineEdit()
        owm_key.setPlaceholderText("Enter OpenWeatherMap API key")
        owm_key.setEchoMode(QLineEdit.EchoMode.Password)
        owm_layout.addWidget(owm_key)
        layout.addLayout(owm_layout)
        
        # Add more API key fields as needed
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Show the dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save the API keys
            # You would typically save these to a config file or secure storage
            pass
    
    def _on_provider_changed(self, provider):
        """Handle weather provider change."""
        # Save the selected provider to config
        # self.config_manager.set('provider', provider.lower())
        QMessageBox.information(
            self,
            "Provider Changed",
            f"Weather provider changed to {provider}"
        )
    
    def _show_app_settings(self):
        """Show the application settings dialog."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Application Settings")
        layout = QVBoxLayout(dialog)
        
        # Add settings widgets
        startup_chk = QCheckBox("Start with system")
        notifications_chk = QCheckBox("Enable notifications")
        auto_update_chk = QCheckBox("Check for updates automatically")
        
        layout.addWidget(startup_chk)
        layout.addWidget(notifications_chk)
        layout.addWidget(auto_update_chk)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Show the dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save settings
            # self.config_manager.set('start_with_system', startup_chk.isChecked())
            # self.config_manager.set('enable_notifications', notifications_chk.isChecked())
            # self.config_manager.set('auto_update', auto_update_chk.isChecked())
            pass
    
    def _show_log_viewer(self):
        """Show the log viewer dialog."""
        try:
            from script.log_viewer import LogViewer
            log_viewer = LogViewer()
            log_viewer.exec()
        except ImportError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not load log viewer: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open log viewer: {str(e)}"
            )
    
    def _show_help_dialog(self):
        """Show the help dialog."""
        try:
            from script.about import AboutDialog
            from script.help import HelpDialog
            from script.translations_utils import TranslationsManager
            from script.translations import TRANSLATIONS
            
            # Get the current language (default to 'en' if not available)
            current_lang = getattr(self, 'current_language', 'en')
            
            # Create and show the help dialog
            help_dialog = HelpDialog(self, TranslationsManager(TRANSLATIONS), current_lang)
            help_dialog.exec()
            
        except ImportError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not load help dialog: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open help: {str(e)}"
            )


def create_menu_bar(parent, translations=None):
    """
    Create and return a menu bar for the application.
    
    Args:
        parent: The parent widget (main window)
        translations: Dictionary containing translations for menu items
        
    Returns:
        MenuBar: The created menu bar
    """
    return MenuBar(parent, translations=translations)
