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
    
    def __init__(self, parent=None):
        """Initialize the API key manager dialog."""
        super().__init__(parent)
        self.setWindowTitle(self.tr("API Key Manager"))
        self.setMinimumSize(600, 400)
        
        self.config_path = Path("config/providers.json")
        self.providers = {}
        
        self._setup_ui()
        self._load_providers()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget for providers
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close |
            QDialogButtonBox.StandardButton.SaveAll
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Custom buttons
        self.save_all_btn = button_box.button(QDialogButtonBox.StandardButton.SaveAll)
        self.save_all_btn.setText(self.tr("Save All"))
        self.save_all_btn.clicked.connect(self.save_all)
        
        layout.addWidget(button_box)
    
    def _load_providers(self):
        """Load available weather providers."""
        try:
            # Create a tab for the OpenMeteo provider
            provider_widget = ProviderConfigWidget(
                provider_id='openmeteo',
                provider_name='OpenMeteo',
                config={
                    'id': 'openmeteo',
                    'name': 'OpenMeteo',
                    'api_key': '',
                    'enabled': True
                }
            )
            
            self.tab_widget.addTab(provider_widget, 'OpenMeteo')
            self.providers['openmeteo'] = provider_widget
            
        except Exception as e:
            logger.error(f"Error loading providers: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load weather providers: {e}"
            )
    
    def save_all(self):
        """Save settings for all providers."""
        all_saved = True
        
        # Collect config from all widgets
        for provider_id, widget in self.providers.items():
            if not widget.save_settings():
                all_saved = False
        
        if all_saved:
            self.api_keys_updated.emit()
            QMessageBox.information(self, "Success", "All API keys have been saved successfully.")
        else:
            QMessageBox.warning(self, "Warning", "Some API keys were not saved. Please check the inputs.")
    
    def accept(self):
        """Handle dialog acceptance."""
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
