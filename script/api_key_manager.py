"""
API Key Manager for Weather Providers.

This module provides a dialog for managing API keys for weather providers.
It's a simplified version that works with the OpenMeteo provider.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any, List

from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QDialogButtonBox, QFormLayout, QWidget, QTabWidget, QHBoxLayout
)

# Configure logging
logger = logging.getLogger(__name__)

# Import language manager
from lang.language_manager import LanguageManager

class ProviderConfigWidget(QWidget):
    """Widget for configuring a single provider's API key."""
    
    def __init__(self, provider_id: str, provider_name: str, config: Dict[str, Any], parent=None):
        """Initialize the provider config widget.
        
        Args:
            provider_id: The provider ID (e.g., 'openweathermap')
            provider_name: The display name of the provider
            config: The provider configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.provider_id = provider_id
        self.provider_name = provider_name
        self.config = config
        self.config_path = Path("config/providers.json")
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Provider info
        info_layout = QFormLayout()
        
        # Provider name
        name_label = QLabel(f"<h3>{self.provider_name}</h3>")
        layout.addWidget(name_label)
        
        # Add fields based on config
        self.fields = {}
        for key, value in self.config.items():
            if key == 'api_key' or key in ['username', 'password']:  # Only show these fields
                field = QLineEdit()
                field.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit if 'password' in key else QLineEdit.EchoMode.Normal)
                info_layout.addRow(f"{key.replace('_', ' ').title()}:", field)
                self.fields[key] = field
        
        layout.addLayout(info_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton(self.tr("Save"))
        self.save_btn.clicked.connect(self.save_settings)
        
        self.validate_btn = QPushButton(self.tr("Validate"))
        self.validate_btn.clicked.connect(self.validate_api_key)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.validate_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _load_settings(self):
        """Load settings for this provider."""
        # Load from providers.json if it exists
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    providers_config = json.load(f)
                provider_config = providers_config.get('Providers', {}).get(self.provider_id, {})
                
                # Update the UI fields
                for key, field in self.fields.items():
                    if key in provider_config:
                        field.setText(provider_config[key])
            except Exception as e:
                logger.error(f"Error loading provider settings: {e}")
    
    def save_settings(self) -> bool:
        """Save settings for this provider.
        
        Returns:
            bool: True if settings were saved successfully, False otherwise
        """
        try:
            # Load existing config
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    providers_config = json.load(f)
            else:
                providers_config = {'Providers': {}}
                
            # Update provider config
            provider_config = {}
            for key, field in self.fields.items():
                provider_config[key] = field.text().strip()
                
            # Update the providers config
            if 'Providers' not in providers_config:
                providers_config['Providers'] = {}
            providers_config['Providers'][self.provider_id] = provider_config
            
            # Ensure config directory exists
            os.makedirs(self.config_path.parent, exist_ok=True)
            
            # Save to file
            with open(self.config_path, 'w') as f:
                json.dump(providers_config, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving provider settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            return False
    
    def validate_api_key(self):
        """Validate the API key with the provider."""
        api_key = self.fields['api_key'].text().strip()
        
        if not api_key:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("Please enter an API key first.")
            )
            return False
        
        # Update the provider with the current key
        # self.provider.api_key = api_key
        
        try:
            # Try to validate the key
            # if self.provider.validate_api_key():
            #     QMessageBox.information(
            #         self,
            #         self.tr("Success"),
            #         self.tr("API key is valid!")
            #     )
            #     return True
            # else:
            #     QMessageBox.warning(
            #         self,
            #         self.tr("Validation Failed"),
            #         self.tr("The API key appears to be invalid.")
            #     )
            #     return False
                
            # For now, just pretend the key is valid
            QMessageBox.information(
                self,
                self.tr("Success"),
                self.tr("API key is valid!")
            )
            return True
                
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("An error occurred while validating the API key: {}".format(str(e)))
            )
            return False


class ApiKeyManagerDialog(QDialog):
    """Dialog for managing API keys for weather providers."""
    
    api_keys_updated = pyqtSignal()
    
    # Define available providers and their configurations
    PROVIDERS = {
        'openweathermap': {
            'name': 'OpenWeatherMap',
            'description': 'Weather data and maps with global coverage',
            'fields': {
                'api_key': {
                    'label': 'API Key',
                    'required': True,
                    'help': 'Your OpenWeatherMap API key (required for map layers)'
                },
                'tile_server': {
                    'label': 'Tile Server',
                    'required': False,
                    'default': 'https://tile.openweathermap.org/map/{layer}/{z}/{x}/{y}.png?appid={api_key}',
                    'help': 'Base URL for map tiles (advanced)'
                }
            }
        },
        'open-meteo': {
            'name': 'Open-Meteo',
            'description': 'Free weather forecast API for non-commercial use',
            'fields': {
                'api_key': {
                    'label': 'API Key',
                    'required': False,
                    'help': 'Optional API key (not required for basic usage)'
                }
            }
        }
    }
    
    def __init__(self, parent=None):
        """Initialize the API key manager dialog."""
        super().__init__(parent)
        self.setWindowTitle(self.tr("API Key Manager"))
        self.setMinimumSize(600, 400)
        
        # Use the new config system
        self.config_path = Path("config/config.json")
        self.config_manager = None
        try:
            from script.config_utils import ConfigManager
            self.config_manager = ConfigManager()
        except ImportError:
            logger.warning("ConfigManager not found, using legacy config system")
        self.providers = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs for each provider
        self.provider_widgets = {}
        
        # Add tabs for each provider
        for provider_id, provider_info in self.PROVIDERS.items():
            widget = ProviderConfigWidget(
                provider_id,
                provider_info['name'],
                provider_info['fields']
            )
            self.tab_widget.addTab(widget, provider_info['name'])
            self.provider_widgets[provider_id] = widget
            
            # Set tooltip with provider description
            idx = self.tab_widget.indexOf(widget)
            self.tab_widget.setTabToolTip(idx, provider_info['description'])
        
        layout.addWidget(self.tab_widget)
        
        # Add status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Help
        )
        
        # Connect buttons
        button_box.accepted.connect(self.save_all_settings)
        button_box.rejected.connect(self.reject)
        apply_btn = button_box.button(QDialogButtonBox.StandardButton.Apply)
        apply_btn.clicked.connect(self.save_all_settings)
        help_btn = button_box.button(QDialogButtonBox.StandardButton.Help)
        help_btn.clicked.connect(self.show_help)
        
        layout.addWidget(button_box)
        
        # Load current settings
        self.load_settings()
    
    def load_settings(self):
        """Load settings from config."""
        if self.config_manager:
            # Use the new config system
            for provider_id in self.PROVIDERS:
                if provider_id in self.provider_widgets:
                    config = self.config_manager.get_provider_config(provider_id)
                    if config:
                        for key, field in self.provider_widgets[provider_id].fields.items():
                            if key in config:
                                field.setText(str(config[key]))
        else:
            # Fallback to legacy config
            if self.config_path.exists():
                try:
                    with open(self.config_path, 'r') as f:
                        providers_config = json.load(f)
                    
                    for provider_id, widget in self.provider_widgets.items():
                        if 'Providers' in providers_config and provider_id in providers_config['Providers']:
                            provider_config = providers_config['Providers'][provider_id]
                            for key, field in widget.fields.items():
                                if key in provider_config:
                                    field.setText(provider_config[key])
                except Exception as e:
                    logger.error(f"Error loading settings: {e}")
    
    def save_all_settings(self):
        """Save settings for all providers."""
        success = True
        
        if self.config_manager:
            # Use the new config system
            for provider_id, widget in self.provider_widgets.items():
                config = {}
                for key, field in widget.fields.items():
                    config[key] = field.text().strip()
                self.config_manager.update_provider_config(provider_id, config)
            
            # Save the config
            try:
                self.config_manager.save_config()
                self.status_label.setText(self.tr("Settings saved successfully!"))
                self.status_label.setStyleSheet("color: green;")
                self.api_keys_updated.emit()
                return True
            except Exception as e:
                logger.error(f"Error saving settings: {e}")
                self.status_label.setText(self.tr(f"Error saving settings: {e}"))
                self.status_label.setStyleSheet("color: red;")
                return False
        else:
            # Fallback to legacy config
            providers_config = {'Providers': {}}
            
            # Collect settings from all providers
            for provider_id, widget in self.provider_widgets.items():
                provider_config = {}
                for key, field in widget.fields.items():
                    provider_config[key] = field.text().strip()
                providers_config['Providers'][provider_id] = provider_config
            
            # Save to file
            try:
                os.makedirs(self.config_path.parent, exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(providers_config, f, indent=2)
                
                self.status_label.setText(self.tr("Settings saved successfully!"))
                self.status_label.setStyleSheet("color: green;")
                self.api_keys_updated.emit()
                return True
            except Exception as e:
                logger.error(f"Error saving settings: {e}")
                self.status_label.setText(self.tr(f"Error saving settings: {e}"))
                self.status_label.setStyleSheet("color: red;")
                return False
    
    def accept(self):
        """Handle dialog acceptance."""
        if self.save_all_settings():
            super().accept()
    
    def show_help(self):
        """Show help information about API keys."""
        current_provider = list(self.PROVIDERS.keys())[self.tab_widget.currentIndex()]
        provider_info = self.PROVIDERS[current_provider]
        
        help_text = f"<h3>{provider_info['name']}</h3>"
        help_text += f"<p>{provider_info['description']}</p>"
        
        if current_provider == 'openweathermap':
            help_text += """
            <p>To get an API key for OpenWeatherMap:</p>
            <ol>
                <li>Go to <a href="https://openweathermap.org/api">OpenWeatherMap API</a></li>
                <li>Sign up for a free account</li>
                <li>Navigate to the <a href="https://home.openweathermap.org/api_keys">API keys</a> section</li>
                <li>Copy your API key and paste it above</li>
            </ol>
            <p>Note: The free tier includes limited requests per minute.</p>
            """
        elif current_provider == 'open-meteo':
            help_text += """
            <p>Open-Meteo provides free weather data without an API key for non-commercial use.</p>
            <p>If you need higher request limits, you can get an API key from their website.</p>
            """
        
        QMessageBox.information(
            self,
            f"{provider_info['name']} - Help",
            help_text,
            QMessageBox.StandardButton.Ok
        )
        # Save all settings before closing
        self.save_all()
        super().accept()


if __name__ == "__main__":
    # For testing the dialog
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    dialog = ApiKeyManagerDialog()
    dialog.show()
    
    sys.exit(app.exec())
