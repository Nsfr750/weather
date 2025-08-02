"""
Plugin Configuration Dialog

This module provides a dialog for configuring plugins in the Weather Application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QLabel,
    QPushButton, QFormLayout, QLineEdit, QCheckBox, QMessageBox, QSpinBox,
    QDoubleSpinBox, QComboBox, QWidget, QGroupBox, QScrollArea, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import logging
from typing import Dict, Any, List, Optional, Type, get_type_hints

from .plugin_system.plugin_manager import PluginManager
from .plugin_system.plugin_manager import BasePlugin

logger = logging.getLogger(__name__)

class PluginConfigWidget(QWidget):
    """Widget for displaying and editing a plugin's configuration."""
    
    config_changed = pyqtSignal(dict)  # Emitted when config changes
    
    def __init__(self, plugin: Type[BasePlugin], current_config: Dict[str, Any] = None, is_enabled: bool = True, parent=None):
        super().__init__(parent)
        self.plugin_class = plugin
        self.current_config = current_config or {}
        self.is_enabled = is_enabled
        self.widgets = {}
        self.enabled_checkbox = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Plugin info with enable/disable toggle
        info_layout = QHBoxLayout()
        
        # Enable/disable checkbox
        self.enabled_checkbox = QCheckBox()
        self.enabled_checkbox.setChecked(self.is_enabled)
        self.enabled_checkbox.stateChanged.connect(self._on_enabled_changed)
        info_layout.addWidget(self.enabled_checkbox)
        
        # Plugin name and version
        info_layout.addWidget(QLabel(f"<h2>{self.plugin_class.name}</h2>"))
        info_layout.addStretch()
        info_layout.addWidget(QLabel(f"Version: {self.plugin_class.version}"))
        layout.addLayout(info_layout)
        
        # Disable all child widgets if plugin is disabled
        self._set_widgets_enabled(self.is_enabled)
        
        # Plugin description
        desc_label = QLabel(self.plugin_class.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-style: italic;")
        layout.addWidget(desc_label)
        
        # Author
        author_label = QLabel(f"<b>Author:</b> {self.plugin_class.author}")
        layout.addWidget(author_label)
        
        # Configuration form
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Add configuration fields based on plugin's config_schema
        if hasattr(self.plugin_class, 'config_schema'):
            for field, field_info in self.plugin_class.config_schema.items():
                field_type = field_info.get('type', str)
                default = field_info.get('default')
                current_value = self.current_config.get(field, default)
                
                # Create appropriate widget based on field type
                if field_type == bool:
                    widget = QCheckBox()
                    widget.setChecked(bool(current_value))
                    widget.toggled.connect(self._on_config_changed)
                elif field_type == int:
                    widget = QSpinBox()
                    widget.setMinimum(field_info.get('min', -2**31))
                    widget.setMaximum(field_info.get('max', 2**31-1))
                    widget.setValue(int(current_value) if current_value is not None else 0)
                    widget.valueChanged.connect(self._on_config_changed)
                elif field_type == float:
                    widget = QDoubleSpinBox()
                    widget.setMinimum(field_info.get('min', float('-inf')))
                    widget.setMaximum(field_info.get('max', float('inf')))
                    widget.setSingleStep(field_info.get('step', 1.0))
                    widget.setValue(float(current_value) if current_value is not None else 0.0)
                    widget.valueChanged.connect(self._on_config_changed)
                elif 'options' in field_info and isinstance(field_info['options'], (list, tuple)):
                    widget = QComboBox()
                    for option in field_info['options']:
                        if isinstance(option, (list, tuple)) and len(option) == 2:
                            widget.addItem(str(option[1]), option[0])
                        else:
                            widget.addItem(str(option), option)
                    
                    # Try to find the current value in options
                    if current_value is not None:
                        index = widget.findData(current_value)
                        if index >= 0:
                            widget.setCurrentIndex(index)
                    widget.currentIndexChanged.connect(self._on_config_changed)
                else:  # Default to QLineEdit for strings and unknown types
                    widget = QLineEdit(str(current_value) if current_value is not None else '')
                    widget.textChanged.connect(self._on_config_changed)
                
                # Set tooltip if description is provided
                if 'description' in field_info:
                    widget.setToolTip(field_info['description'])
                
                # Store widget reference for later access
                self.widgets[field] = widget
                
                # Add to form
                label = QLabel(field_info.get('label', field.replace('_', ' ').title()))
                form_layout.addRow(label, widget)
        else:
            # No configuration schema defined for this plugin
            no_config_label = QLabel("This plugin has no configurable options.")
            no_config_label.setStyleSheet("font-style: italic;")
            form_layout.addRow(no_config_label)
        
        # Add stretch to push everything to the top
        layout.addLayout(form_layout)
        layout.addStretch()
    
    def _on_enabled_changed(self, state):
        """Handle enable/disable toggle."""
        self.is_enabled = state == Qt.CheckState.Checked.value
        self._set_widgets_enabled(self.is_enabled)
        # Emit the enabled state as part of the config
        config = self._get_current_config()
        config['_enabled'] = self.is_enabled
        self.config_changed.emit(config)
    
    def _set_widgets_enabled(self, enabled):
        """Enable or disable all configuration widgets."""
        for widget in self.widgets.values():
            widget.setEnabled(enabled)
    
    def _get_current_config(self):
        """Get the current configuration from the UI."""
        config = {}
        for field in getattr(self.plugin_class, 'config_schema', {}).keys():
            if field in self.widgets:
                widget = self.widgets[field]
                if isinstance(widget, QCheckBox):
                    config[field] = widget.isChecked()
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    config[field] = widget.value()
                elif isinstance(widget, QComboBox):
                    config[field] = widget.currentData()
                else:  # QLineEdit and others
                    config[field] = widget.text()
        return config
        
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration from the UI."""
        config = self._get_current_config()
        if self.enabled_checkbox:
            config['_enabled'] = self.enabled_checkbox.isChecked()
        return config
    
    def _on_config_changed(self, _=None):
        """Eit config_changed signal when any config value changes."""
        self.config_changed.emit(self.get_config())


class PluginConfigDialog(QDialog):
    """Dialog for configuring plugins."""
    
    def __init__(self, plugin_manager: PluginManager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.plugin_widgets = {}
        self.current_plugin = None
        
        self.setWindowTitle("Plugin Configuration")
        self.setMinimumSize(700, 500)
        
        self._init_ui()
        self._load_plugins()
    
    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QHBoxLayout(self)
        
        # Left panel - Plugin list
        left_panel = QWidget()
        left_panel.setMaximumWidth(200)
        left_layout = QVBoxLayout(left_panel)
        
        self.plugin_list = QListWidget()
        self.plugin_list.currentItemChanged.connect(self._on_plugin_selected)
        left_layout.addWidget(QLabel("<b>Available Plugins</b>"))
        left_layout.addWidget(self.plugin_list)
        
        main_layout.addWidget(left_panel)
        
        # Right panel - Plugin configuration
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.stacked_widget = QStackedWidget()
        right_layout.addWidget(self.stacked_widget)
        
        # Add a placeholder widget for when no plugin is selected
        self.placeholder_widget = QLabel("Select a plugin to configure its settings.")
        self.placeholder_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_widget.setStyleSheet("color: gray; font-style: italic;")
        self.stacked_widget.addWidget(self.placeholder_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Apply | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Reset
        )
        
        self.apply_button = button_box.button(QDialogButtonBox.StandardButton.Apply)
        self.apply_button.clicked.connect(self.apply_changes)
        self.apply_button.setEnabled(False)
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        right_layout.addWidget(button_box)
        
        main_layout.addWidget(right_panel, 1)  # Make right panel take more space

    def _load_plugins(self):
        """Load available plugins into the list."""
        self.plugin_list.clear()
        
        # Clear the stacked widget by removing all widgets
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
            
        self.plugin_widgets.clear()

        # Group plugins by category
        plugins_by_category = {}
        for plugin_class in self.plugin_manager.get_all_plugins():
            category = getattr(plugin_class, 'category', 'Other')
            if category not in plugins_by_category:
                plugins_by_category[category] = []
            plugins_by_category[category].append(plugin_class)

        # Add plugins to the list, grouped by category
        for category, plugins in sorted(plugins_by_category.items()):
            # Add category header
            category_item = QListWidgetItem(category)
            category_item.setFlags(Qt.ItemFlag.NoItemFlags)
            category_item.setBackground(Qt.GlobalColor.lightGray)
            self.plugin_list.addItem(category_item)

            # Add plugins in this category
            for plugin_class in sorted(plugins, key=lambda p: p.name):
                item = QListWidgetItem(plugin_class.name)
                item.setData(Qt.ItemDataRole.UserRole, plugin_class)

                # Check if plugin is enabled
                plugin_id = f"{plugin_class.__module__}.{plugin_class.__name__}"
                config = self.plugin_manager.get_plugin_config(plugin_id)
                is_enabled = config.get('_enabled', True)

                # Set item appearance based on enabled state
                font = item.font()
                font.setStrikeOut(not is_enabled)
                item.setFont(font)

                self.plugin_list.addItem(item)

                # Create and store the config widget
                widget = PluginConfigWidget(plugin_class, config, is_enabled)
                self.stacked_widget.addWidget(widget)
                self.plugin_widgets[plugin_class] = widget

                # Connect config changes
                widget.config_changed.connect(
                    lambda cfg, p=plugin_class: self._on_config_changed(p, cfg)
                )

        # Select the first plugin if available
        if self.plugin_list.count() > 0:
            self.plugin_list.setCurrentRow(1 if len(plugins_by_category) > 0 else 0)

    def _on_plugin_selected(self, current, _):
        """Handle plugin selection change."""
        if not current:
            self.stacked_widget.setCurrentWidget(self.placeholder_widget)
            self.current_plugin = None
            return

        # Find the plugin class for the selected item
        plugin_name = current.text()
        for plugin_id, widget in self.plugin_widgets.items():
            if widget.plugin_class.name == plugin_name:
                self.current_plugin = plugin_id
                self.stacked_widget.setCurrentWidget(widget)
                break

    def _on_config_changed(self, plugin_class, config):
        """Handle configuration changes in a plugin's widget."""
        # Store the updated config in the plugin manager
        plugin_id = f"{plugin_class.__module__}.{plugin_class.__name__}"
        self.plugin_manager.set_plugin_config(plugin_id, config)

        # Update the plugin item appearance based on enabled state
        is_enabled = config.get('_enabled', True)
        for i in range(self.plugin_list.count()):
            item = self.plugin_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == plugin_class:
                font = item.font()
                font.setStrikeOut(not is_enabled)
                item.setFont(font)
                break

        # Mark the plugin as having unsaved changes
        if not hasattr(self, 'dirty_plugins'):
            self.dirty_plugins = set()
        self.dirty_plugins.add(plugin_class)
        self.apply_button.setEnabled(True)

    def apply_changes(self):
        """Apply configuration changes for all dirty plugins."""
        if not hasattr(self, 'dirty_plugins') or not self.dirty_plugins:
            return False
            
        for plugin_class in self.dirty_plugins:
            plugin_id = f"{plugin_class.__module__}.{plugin_class.__name__}"
            config = self.plugin_manager.get_plugin_config(plugin_id)
            is_enabled = config.get('_enabled', True)
            
            # Update the plugin's configuration
            self.plugin_manager.set_plugin_config(plugin_id, config)
            
            # Handle enable/disable state
            if plugin_id in self.plugin_manager.plugin_instances:
                plugin = self.plugin_manager.plugin_instances[plugin_id]
                if not is_enabled:
                    # Unload disabled plugins
                    self.plugin_manager.unload_plugin(plugin_id)
                else:
                    # Reinitialize enabled plugins with new config
                    plugin.config = config
                    plugin.initialize()
            elif is_enabled and plugin_id not in self.plugin_manager.plugin_instances:
                # Load newly enabled plugins
                try:
                    self.plugin_manager.load_plugin(plugin_id)
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_id}: {e}")
        
        # Clear the dirty set and update UI
        self.dirty_plugins.clear()
        self.apply_button.setEnabled(False)
        
        # Reload the plugin list to reflect changes
        self._load_plugins()
        
        QMessageBox.information(self, "Success", "Plugin configurations have been saved.")
        return True

    def accept(self):
        """Handle OK button click."""
        if self.apply_button.isEnabled():
            self.apply_changes()
        super().accept()
    
    def reject(self):
        """Handle Cancel button click."""
        if self.apply_button.isEnabled():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        super().reject()
