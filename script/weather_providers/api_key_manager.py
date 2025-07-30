"""
API Key Manager for Weather Providers.

This module provides a dialog for managing API keys for different weather providers.
"""

import logging
from typing import Dict, Optional, Any, List

from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox,
    QDialogButtonBox, QFormLayout, QWidget, QTabWidget
)

from script.weather_providers.base_provider import BaseProvider

# Configure logging
logger = logging.getLogger(__name__)


class ProviderConfigWidget(QWidget):
    """Widget for configuring a single provider's API key."""
    
    def __init__(self, provider_class, parent=None):
        """Initialize the provider config widget.
        
        Args:
            provider_class: The provider class to configure
            parent: Parent widget
        """
        super().__init__(parent)
        self.provider_class = provider_class
        self.provider = provider_class()
        self.settings = QSettings("WeatherApp", "WeatherProviders")
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Provider info
        info_layout = QFormLayout()
        
        # Provider name
        name_label = QLabel("<b>" + self.provider.display_name + "</b>")
        info_layout.addRow(self.tr("Provider:"), name_label)
        
        # API key field
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText(
            self.tr("Enter your {} API key").format(self.provider.display_name)
        )
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        info_layout.addRow(self.tr("API Key:"), self.api_key_edit)
        
        # Show/hide API key button
        self.toggle_visibility_btn = QPushButton(self.tr("Show"))
        self.toggle_visibility_btn.setCheckable(True)
        self.toggle_visibility_btn.toggled.connect(self._toggle_api_key_visibility)
        info_layout.addRow("", self.toggle_visibility_btn)
        
        # Status indicator
        self.status_label = QLabel()
        self._update_status()
        info_layout.addRow(self.tr("Status:"), self.status_label)
        
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
    
    def _toggle_api_key_visibility(self, checked):
        """Toggle API key visibility."""
        if checked:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_visibility_btn.setText(self.tr("Hide"))
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_visibility_btn.setText(self.tr("Show"))
    
    def _update_status(self):
        """Update the status label based on API key presence and validity."""
        if not self.api_key_edit.text():
            self.status_label.setText("<font color='orange'>" + self.tr("No API key provided") + "</font>")
            return
            
        # In a real implementation, you would validate the key here
        self.status_label.setText("<font color='green'>" + self.tr("API key saved") + "</font>")
    
    def _load_settings(self):
        """Load settings from QSettings."""
        self.settings.beginGroup(f"provider_{self.provider.name}")
        api_key = self.settings.value("api_key", "")
        self.settings.endGroup()
        
        self.api_key_edit.setText(api_key)
        self._update_status()
    
    def save_settings(self):
        """Save the API key to settings."""
        api_key = self.api_key_edit.text().strip()
        
        if not api_key:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("API key cannot be empty.")
            )
            return False
        
        self.settings.beginGroup(f"provider_{self.provider.name}")
        self.settings.setValue("api_key", api_key)
        self.settings.endGroup()
        
        # Update the provider instance
        self.provider.api_key = api_key
        
        self._update_status()
        QMessageBox.information(
            self,
            self.tr("Success"),
            self.tr("API key saved successfully!")
        )
        return True
    
    def validate_api_key(self):
        """Validate the API key with the provider."""
        api_key = self.api_key_edit.text().strip()
        
        if not api_key:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("Please enter an API key first.")
            )
            return False
        
        # Update the provider with the current key
        self.provider.api_key = api_key
        
        try:
            # Try to validate the key
            if self.provider.validate_api_key():
                QMessageBox.information(
                    self,
                    self.tr("Success"),
                    self.tr("API key is valid!")
                )
                return True
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Validation Failed"),
                    self.tr("The API key appears to be invalid.")
                )
                return False
                
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
    
    # Signal emitted when API keys are updated
    api_keys_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the API key manager dialog."""
        super().__init__(parent)
        self.setWindowTitle(self.tr("API Key Manager"))
        self.setMinimumSize(600, 400)
        
        self.settings = QSettings("WeatherApp", "WeatherProviders")
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
            # Import all provider modules to register them
            from script.weather_providers.openweathermap import OpenWeatherMapProvider
            from script.weather_providers.weatherapi import WeatherAPIProvider
            from script.weather_providers.accuweather import AccuWeatherProvider
            
            providers = [
                OpenWeatherMapProvider,
                WeatherAPIProvider,
                AccuWeatherProvider,
            ]
            
            for provider_class in providers:
                if provider_class.requires_api_key:
                    widget = ProviderConfigWidget(provider_class, self)
                    self.tab_widget.addTab(widget, provider_class.display_name)
                    self.providers[provider_class.name] = widget
            
            # Show a message if no providers are available
            if not self.providers:
                label = QLabel(self.tr("No weather providers requiring API keys were found."))
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tab_widget.addTab(label, self.tr("No Providers"))
                
        except Exception as e:
            logger.error(f"Error loading providers: {e}")
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to load weather providers: {}".format(str(e)))
            )
    
    def save_all(self):
        """Save settings for all providers."""
        success = True
        for provider_name, widget in self.providers.items():
            if not widget.save_settings():
                success = False
        
        if success:
            self.api_keys_updated.emit()
            QMessageBox.information(
                self,
                self.tr("Success"),
                self.tr("All API keys have been saved successfully!")
            )
        else:
            QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Some API keys could not be saved. Please check the input and try again.")
            )
    
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
