"""
Base classes for feature plugins.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
import logging

from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QObject, pyqtSignal

from ..plugin_system import BasePlugin

logger = logging.getLogger(__name__)

class BaseFeaturePlugin(BasePlugin):
    """Base class for all feature plugins.
    
    Feature plugins can extend the application with new functionality,
    such as new UI elements, background tasks, or integrations with other services.
    """
    
    # Feature metadata
    name = "Unnamed Feature"
    category = "Uncategorized"
    icon = ""  # Optional: Path to an icon for the feature
    
    # UI configuration
    add_to_toolbar = False  # Whether to add a button to the main toolbar
    add_to_menu = True      # Whether to add an entry to the main menu
    
    def __init__(self):
        super().__init__()
        self._widget = None
        self._menu_actions = []
        self._toolbar_actions = []
    
    @abstractmethod
    def initialize(self, app: Any = None) -> bool:
        """Initialize the feature.
        
        This is called when the plugin is loaded. Perform any setup here.
        
        Args:
            app: Reference to the main application instance
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
    
    def create_widget(self, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """Create and return the main widget for this feature.
        
        This widget will be displayed when the feature is activated.
        
        Args:
            parent: The parent widget
            
        Returns:
            Optional[QWidget]: The created widget, or None if not applicable
        """
        return None
    
    def get_widget(self, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """Get the main widget for this feature, creating it if necessary."""
        if self._widget is None:
            self._widget = self.create_widget(parent)
        return self._widget
    
    def get_menu_actions(self, parent: QWidget) -> List[QAction]:
        """Get menu actions to add to the main menu.
        
        Override this to add custom menu items.
        
        Args:
            parent: The parent widget for the actions
            
        Returns:
            List[QAction]: List of menu actions
        """
        if not self._menu_actions:
            action = QAction(self.name, parent)
            if self.icon:
                action.setIcon(self.icon)
            action.triggered.connect(self.on_menu_triggered)
            self._menu_actions.append(action)
        return self._menu_actions
    
    def get_toolbar_actions(self, parent: QWidget) -> List[QAction]:
        """Get toolbar actions to add to the main toolbar.
        
        Override this to add custom toolbar buttons.
        
        Args:
            parent: The parent widget for the actions
            
        Returns:
            List[QAction]: List of toolbar actions
        """
        if not self._toolbar_actions and self.add_to_toolbar:
            action = QAction(self.name, parent)
            if self.icon:
                action.setIcon(self.icon)
            action.triggered.connect(self.on_toolbar_triggered)
            self._toolbar_actions.append(action)
        return self._toolbar_actions
    
    def on_menu_triggered(self) -> None:
        """Called when the feature's menu item is triggered."""
        widget = self.get_widget()
        if widget:
            # Show the widget in the main window or a dialog
            # This is a placeholder - the actual implementation will depend on the app's UI structure
            widget.show()
    
    def on_toolbar_triggered(self) -> None:
        """Called when the feature's toolbar button is clicked."""
        self.on_menu_triggered()  # Default to same behavior as menu action
    
    def cleanup(self) -> None:
        """Clean up resources used by the feature."""
        if self._widget:
            self._widget.deleteLater()
            self._widget = None
        self._menu_actions.clear()
        self._toolbar_actions.clear()
        super().cleanup()


class FeatureManager:
    """Manager for feature plugins."""
    
    def __init__(self, plugin_manager):
        """Initialize with a plugin manager instance."""
        self.plugin_manager = plugin_manager
        self.features: Dict[str, BaseFeaturePlugin] = {}
        self.active_features: Dict[str, BaseFeaturePlugin] = {}
    
    def discover_features(self) -> None:
        """Discover all available feature plugins."""
        for plugin in self.plugin_manager.get_plugins_by_type(BaseFeaturePlugin):
            if plugin.name not in self.features:
                self.features[plugin.name] = plugin
    
    def get_available_features(self) -> List[str]:
        """Get names of all available features."""
        return list(self.features.keys())
    
    def get_feature(self, name: str) -> Optional[BaseFeaturePlugin]:
        """Get a feature by name."""
        return self.features.get(name)
    
    def activate_feature(self, name: str) -> bool:
        """Activate a feature.
        
        Args:
            name: The name of the feature to activate
            
        Returns:
            bool: True if the feature was activated successfully, False otherwise
        """
        if name in self.active_features:
            return True  # Already active
            
        feature = self.get_feature(name)
        if not feature:
            return False
            
        if feature.initialize():
            self.active_features[name] = feature
            return True
        return False
    
    def deactivate_feature(self, name: str) -> bool:
        """Deactivate a feature.
        
        Args:
            name: The name of the feature to deactivate
            
        Returns:
            bool: True if the feature was deactivated successfully, False otherwise
        """
        if name not in self.active_features:
            return True  # Already inactive
            
        feature = self.active_features.pop(name, None)
        if feature:
            feature.cleanup()
            return True
        return False
    
    def get_menu_actions(self, parent: QWidget) -> Dict[str, List[QAction]]:
        """Get all menu actions from active features, grouped by category.
        
        Args:
            parent: The parent widget for the actions
            
        Returns:
            Dict[str, List[QAction]]: Dictionary mapping category names to lists of actions
        """
        actions = {}
        for feature in self.active_features.values():
            if not feature.add_to_menu:
                continue
                
            category = feature.category
            if category not in actions:
                actions[category] = []
                
            actions[category].extend(feature.get_menu_actions(parent))
            
        return actions
    
    def get_toolbar_actions(self, parent: QWidget) -> List[QAction]:
        """Get all toolbar actions from active features.
        
        Args:
            parent: The parent widget for the actions
            
        Returns:
            List[QAction]: List of toolbar actions
        """
        actions = []
        for feature in self.active_features.values():
            if feature.add_to_toolbar:
                actions.extend(feature.get_toolbar_actions(parent))
        return actions
    
    def cleanup(self) -> None:
        """Clean up all features."""
        for name in list(self.active_features.keys()):
            self.deactivate_feature(name)
