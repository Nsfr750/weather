"""
favorites_dialog.py
Dialog for managing favorite cities.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                           QPushButton, QLineEdit, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt

# Import language manager
from lang.language_manager import LanguageManager

class FavoritesDialog(QDialog):
    """Dialog for managing favorite cities."""
    
    def __init__(self, favorites_manager, parent=None):
        """Initialize the favorites dialog.
        
        Args:
            favorites_manager: Instance of FavoritesManager
            parent: Parent widget
        """
        super().__init__(parent)
        self.favorites_manager = favorites_manager
        self.setWindowTitle("Manage Favorite Cities")
        self.setMinimumSize(400, 400)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # List widget to display favorites
        self.favorites_list = QListWidget()
        self.favorites_list.itemDoubleClicked.connect(self.edit_favorite)
        self.update_favorites_list()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_favorite)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_selected_favorite)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected_favorite)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        # Add widgets to layout
        layout.addWidget(self.favorites_list)
        layout.addLayout(button_layout)
        
    def update_favorites_list(self):
        """Update the list of favorites in the UI."""
        self.favorites_list.clear()
        self.favorites_list.addItems(self.favorites_manager.favorites)
        
    def add_favorite(self):
        """Add a new favorite city."""
        city, ok = QInputDialog.getText(
            self, 
            "Add Favorite", 
            "Enter city name:", 
            QLineEdit.EchoMode.Normal
        )
        
        if ok and city.strip():
            if self.favorites_manager.add_favorite(city):
                self.update_favorites_list()
                self.parent().update_status(f"Added {city} to favorites", 3000)
            else:
                QMessageBox.warning(
                    self,
                    "Duplicate Entry",
                    f"{city} is already in your favorites.",
                    QMessageBox.StandardButton.Ok
                )
    
    def edit_selected_favorite(self):
        """Edit the currently selected favorite."""
        current_item = self.favorites_list.currentItem()
        if current_item:
            self.edit_favorite(current_item)
    
    def edit_favorite(self, item):
        """Edit an existing favorite.
        
        Args:
            item: The QListWidgetItem to edit
        """
        old_city = item.text()
        new_city, ok = QInputDialog.getText(
            self,
            "Edit Favorite",
            "Edit city name:",
            QLineEdit.EchoMode.Normal,
            old_city
        )
        
        if ok and new_city.strip() and new_city != old_city:
            if new_city in self.favorites_manager.favorites:
                QMessageBox.warning(
                    self,
                    "Duplicate Entry",
                    f"{new_city} is already in your favorites.",
                    QMessageBox.StandardButton.Ok
                )
                return
                
            index = self.favorites_manager.favorites.index(old_city)
            self.favorites_manager.favorites[index] = new_city
            self.favorites_manager.save_favorites()
            self.update_favorites_list()
            self.parent().update_status(f"Updated favorite: {old_city} → {new_city}", 3000)
    
    def remove_selected_favorite(self):
        """Remove the currently selected favorite."""
        current_item = self.favorites_list.currentItem()
        if current_item:
            city = current_item.text()
            reply = QMessageBox.question(
                self,
                "Confirm Removal",
                f"Are you sure you want to remove {city} from favorites?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.favorites_manager.remove_favorite(city):
                    self.update_favorites_list()
                    self.parent().update_status(f"Removed {city} from favorites", 3000)
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Could not remove {city} from favorites.",
                        QMessageBox.StandardButton.Ok
                    )
