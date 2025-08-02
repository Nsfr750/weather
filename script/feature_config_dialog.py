"""
Feature Configuration Dialog

Provides a user interface for configuring feature plugins.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget,
    QLabel, QPushButton, QFormLayout, QLineEdit, QCheckBox, QMessageBox, QSpinBox,
    QDoubleSpinBox, QComboBox, QWidget, QGroupBox, QScrollArea, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import logging
from typing import Dict, Any, List, Optional, Type, get_type_hints

from .plugin_system.plugin_manager import PluginManager
from .plugin_system.feature_manager import FeatureManager, BaseFeature

logger = logging.getLogger(__name__)

class FeatureConfigWidget(QWidget):
    """Widget for displaying and editing a feature's configuration."""
    
    config_changed = pyqtSignal(dict)  # Emitted when config changes
    
    def __init__(self, feature: Type[BaseFeature], current_config: Dict[str, Any] = None, is_enabled: bool = True, parent=None):
        super().__init__(parent)
        self.feature_class = feature
        self.current_config = current_config or {}
        self.is_enabled = is_enabled
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Enable/disable checkbox
        self.enabled_checkbox = QCheckBox("Enable this feature")
        self.enabled_checkbox.setChecked(self.is_enabled)
        self.enabled_checkbox.toggled.connect(self.on_enabled_changed)
        layout.addWidget(self.enabled_checkbox)
        
        # Create a scroll area for the form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.form_layout = QFormLayout(scroll_content)
        
        # Get the feature's config schema if available
        config_schema = getattr(self.feature_class, 'CONFIG_SCHEMA', {})
        
        # Create form fields based on the config schema
        self.fields = {}
        for field_name, field_info in config_schema.items():
            field_type = field_info.get('type', str)
            field_label = field_info.get('label', field_name.replace('_', ' ').title())
            field_default = field_info.get('default', '')
            field_value = self.current_config.get(field_name, field_default)
            
            # Create appropriate input widget based on type
            if field_type == bool:
                widget = QCheckBox()
                widget.setChecked(bool(field_value))
            elif field_type == int:
                widget = QSpinBox()
                widget.setRange(-999999, 999999)
                widget.setValue(int(field_value))
            elif field_type == float:
                widget = QDoubleSpinBox()
                widget.setRange(-999999, 999999)
                widget.setValue(float(field_value))
            elif isinstance(field_type, list):
                widget = QComboBox()
                widget.addItems(field_type)
                if field_value in field_type:
                    widget.setCurrentText(field_value)
            else:  # Default to QLineEdit for strings
                widget = QLineEdit(str(field_value))
            
            # Store widget reference
            self.fields[field_name] = widget
            self.form_layout.addRow(field_label, widget)
        
        # Add stretch to push everything to the top
        self.form_layout.addRow(QLabel(""))
        self.form_layout.setRowStretch(self.form_layout.rowCount(), 1)
        
        # Set up the scroll area
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
    
    def on_enabled_changed(self, enabled: bool):
        """Handle enable/disable toggle."""
        self.is_enabled = enabled
        self.config_changed.emit(self.get_config())
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration from the form."""
        config = {}
        for field_name, widget in self.fields.items():
            if isinstance(widget, QCheckBox):
                config[field_name] = widget.isChecked()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                config[field_name] = widget.value()
            elif isinstance(widget, QComboBox):
                config[field_name] = widget.currentText()
            else:  # QLineEdit
                config[field_name] = widget.text()
        return config


class FeatureConfigDialog(QDialog):
    """Dialog for configuring feature plugins."""
    
    def __init__(self, feature_manager: FeatureManager, parent=None):
        super().__init__(parent)
        self.feature_manager = feature_manager
        self.setWindowTitle("Configure Features")
        self.setMinimumSize(600, 400)
        
        self.setup_ui()
        self.load_features()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        
        # Left side: List of features
        self.feature_list = QListWidget()
        self.feature_list.setMaximumWidth(200)
        self.feature_list.currentItemChanged.connect(self.on_feature_selected)
        layout.addWidget(self.feature_list)
        
        # Right side: Configuration form
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget, 1)
        
        # Add a default empty widget
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.addWidget(QLabel("Select a feature to configure"))
        empty_layout.addStretch()
        self.stacked_widget.addWidget(empty_widget)
        
        # Add OK/Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_features(self):
        """Load available features into the list."""
        self.feature_list.clear()
        self.config_widgets = {}
        
        # Add a default empty widget at index 0
        self.stacked_widget.setCurrentIndex(0)
        
        # Add each feature to the list
        for i, (feature_name, feature) in enumerate(self.feature_manager.get_features().items(), 1):
            # Create list item
            item = QListWidgetItem(feature_name)
            item.setData(Qt.ItemDataRole.UserRole, feature_name)
            self.feature_list.addItem(item)
            
            # Create config widget
            config_widget = FeatureConfigWidget(
                feature.__class__,
                feature.__dict__,
                feature.initialized
            )
            config_widget.config_changed.connect(
                lambda config, f=feature_name: self.on_config_changed(f, config)
            )
            
            # Add to stacked widget
            self.stacked_widget.addWidget(config_widget)
            self.config_widgets[feature_name] = config_widget
    
    def on_feature_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle feature selection change."""
        if not current:
            self.stacked_widget.setCurrentIndex(0)
            return
            
        feature_name = current.data(Qt.ItemDataRole.UserRole)
        if feature_name in self.config_widgets:
            index = self.stacked_widget.indexOf(self.config_widgets[feature_name])
            self.stacked_widget.setCurrentIndex(index)
    
    def on_config_changed(self, feature_name: str, config: Dict[str, Any]):
        """Handle configuration changes."""
        # Update the feature's configuration
        if feature_name in self.config_widgets:
            widget = self.config_widgets[feature_name]
            if widget.is_enabled:
                self.feature_manager.update_feature_config(feature_name, config)
    
    def accept(self):
        """Save all configurations and close the dialog."""
        # Save all configurations
        for feature_name, widget in self.config_widgets.items():
            config = widget.get_config()
            self.feature_manager.update_feature_config(feature_name, config)
        
        super().accept()
