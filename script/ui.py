from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QComboBox, QFrame, QScrollArea,
                             QStatusBar, QMenuBar, QMenu, QSizePolicy, QSpacerItem, QSizePolicy,
                             QDialog, QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QAction, QCloseEvent
from pathlib import Path
import logging
import sys
from typing import Dict, Any, List, Optional, Callable
from script.version import get_version
from script.menu import create_menu_bar

class WeatherAppUI(QMainWindow):
    # Signals for UI events
    search_clicked = pyqtSignal(str)  # Emitted when search is triggered
    language_changed = pyqtSignal(str)  # Emitted when language changes
    units_changed = pyqtSignal(str)  # Emitted when units change
    favorite_toggled = pyqtSignal(str)  # Emitted when favorite is toggled
    favorite_selected = pyqtSignal(str)  # Emitted when a favorite is selected

    def __init__(self, config_manager, translations_manager, weather_provider, notification_manager):
        super().__init__()
        self.config_manager = config_manager
        self.translations_manager = translations_manager
        self.weather_provider = weather_provider
        self.notification_manager = notification_manager
        
        # Initialize UI
        self._setup_window()
        self._init_ui()
        self.apply_theme()
    
    def _setup_window(self):
        """Set up the main window properties."""
        self.setWindowTitle('Weather v. ' + get_version())
        self.setMinimumSize(800, 800)
        
        # Set application icon
        try:
            icon_path = Path('assets/meteo.png')
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            logging.warning(f'Could not set application icon: {e}')
            
        # Create menu bar
        self._create_menu_bar()
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        # Create the menu bar using the menu module
        # The menu bar is already created in the MenuBar class
        # and set as the main window's menu bar there
        pass
    
    def _init_ui(self):
        """Initialize the main UI components."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_layout.setSpacing(10)
        scroll_area.setWidget(scroll_content)
        
        # Header with search and settings
        self._create_header()
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Ready')
        
        # Initialize weather display area
        self._init_weather_display()
    
    def _create_header(self):
        """Create the header with search and settings."""
        # Search bar frame
        search_frame = QFrame()
        search_frame.setObjectName('searchFrame')
        search_frame.setFrameShape(QFrame.Shape.StyledPanel)
        search_frame.setStyleSheet('''
            QFrame#searchFrame {
                background-color: #2c3e50;
                border-radius: 5px;
                padding: 5px;
            }
        ''')
        
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(5, 5, 5, 5)
        
        # Search icon
        search_icon = QLabel('🔍')
        search_icon.setStyleSheet('font-size: 16px;')
        search_layout.addWidget(search_icon)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Enter city name...')
        self.search_input.setStyleSheet('''
            QLineEdit {
                border: none;
                background: transparent;
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                border-radius: 3px;
            }
        ''')
        self.search_input.returnPressed.connect(self._on_search_clicked)
        search_layout.addWidget(self.search_input)
        
        # Search button
        self.search_btn = QPushButton('Search')
        self.search_btn.clicked.connect(self._on_search_clicked)
        self.search_btn.setStyleSheet('''
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 3px 0 0 3px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
        ''')
        search_layout.addWidget(self.search_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton('🔄')
        self.refresh_btn.setToolTip('Aggiorna')
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        self.refresh_btn.setStyleSheet('''
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 0 3px 3px 0;
                padding: 5px 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        ''')
        search_layout.addWidget(self.refresh_btn)
        
        # Settings frame
        settings_frame = QFrame()
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(10)
        
        # Units selector
        units_frame = QFrame()
        units_layout = QHBoxLayout(units_frame)
        units_layout.setContentsMargins(0, 0, 0, 0)
        
        units_icon = QLabel('📏')
        units_icon.setStyleSheet('font-size: 16px;')
        units_layout.addWidget(units_icon)
        
        self.units_combo = QComboBox()
        self.units_combo.addItem('°C, m/s', 'metric')
        self.units_combo.addItem('°F, mph', 'imperial')
        self.units_combo.currentIndexChanged.connect(self._on_units_changed)
        self.units_combo.setStyleSheet('''
            QComboBox {
                padding: 3px;
                border: 1px solid #3d4f5e;
                border-radius: 3px;
                background: #2c3e50;
                color: white;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid white;
            }
        ''')
        units_layout.addWidget(self.units_combo)
        
        # Favorites
        fav_frame = QFrame()
        fav_layout = QHBoxLayout(fav_frame)
        fav_layout.setContentsMargins(0, 0, 0, 0)
        
        fav_icon = QLabel('⭐')
        fav_icon.setStyleSheet('font-size: 16px;')
        fav_layout.addWidget(fav_icon)
        
        self.favorites_combo = QComboBox()
        self.favorites_combo.setObjectName('favoritesCombo')
        self.favorites_combo.setPlaceholderText('Favorites')
        self.favorites_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.favorites_combo.setEditable(False)
        self.favorites_combo.setMaxVisibleItems(10)
        self.favorites_combo.currentTextChanged.connect(self._on_favorite_selected)
        self.favorites_combo.setStyleSheet('''
            QComboBox#favoritesCombo {
                padding: 3px 6px;
                border: 1px solid #3d4f5e;
                border-radius: 3px;
                background: #2c3e50;
                color: white;
                min-width: 150px;
                max-width: 200px;
            }
            QComboBox#favoritesCombo::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox#favoritesCombo::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #95a5a6;
            }
            QComboBox#favoritesCombo:hover::down-arrow {
                border-top-color: #f1c40f;
            }
            QComboBox#favoritesCombo QAbstractItemView {
                background: #2c3e50;
                color: white;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #3d4e5d;
                border-radius: 3px;
                padding: 5px 0;
                outline: none;
            }
            QComboBox#favoritesCombo QAbstractItemView::item {
                padding: 3px 8px;
                border-radius: 2px;
                margin: 1px 5px;
            }
            QComboBox#favoritesCombo QAbstractItemView::item:hover {
                background-color: #3d4e5d;
            }
        ''')
        fav_layout.addWidget(self.favorites_combo)
        
        self.fav_btn = QPushButton('⭐')
        self.fav_btn.setToolTip('Add to favorites')
        self.fav_btn.clicked.connect(self._on_toggle_favorite)
        self.fav_btn.setStyleSheet('''
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                padding: 0 5px;
            }
            QPushButton:hover {
                color: #f1c40f;
            }
        ''')
        fav_layout.addWidget(self.fav_btn)
        
        # Add widgets to settings layout
        settings_layout.addWidget(units_frame)
        settings_layout.addWidget(fav_frame)
        settings_layout.addStretch()
        
        # Add header widgets to scroll layout
        self.scroll_layout.addWidget(search_frame)
        self.scroll_layout.addWidget(settings_frame)
        
        # Add stretch to push content to the top
        self.scroll_layout.addStretch()
    
    def _init_weather_display(self):
        """Initialize the weather display area."""
        self.weather_frame = QFrame()
        self.weather_frame.setObjectName('weatherFrame')
        self.weather_frame.setStyleSheet('''
            QFrame#weatherFrame {
                background-color: #2c3e50;
                border-radius: 5px;
                padding: 15px;
            }
        ''')
        
        self.weather_layout = QVBoxLayout(self.weather_frame)
        self.weather_layout.setSpacing(10)
        
        # Add a placeholder for weather content
        placeholder = QLabel('Search for a city to see weather information')
        placeholder.setStyleSheet('color: #95a5a6; font-style: italic;')
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weather_layout.addWidget(placeholder)
        
        # Add the weather frame to the scroll layout
        self.scroll_layout.insertWidget(2, self.weather_frame)
    
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        current_city = self.search_input.text().strip()
        if current_city:
            self.search_clicked.emit(current_city)
            self.set_status(f"Aggiornamento meteo per {current_city}...")
        else:
            self.set_status("Inserisci una città per aggiornare il meteo")
    
    def _on_search_clicked(self):
        """Handle search button click."""
        city = self.search_input.text().strip()
        if city:
            self.search_clicked.emit(city)
    
    def _on_language_changed(self, language):
        """Handle language change."""
        self.language_changed.emit(language)
    
    def _on_units_changed(self, index):
        """Handle units change."""
        units = self.units_combo.itemData(index)
        self.units_changed.emit(units)
    
    def _on_toggle_favorite(self):
        """Handle toggle favorite button click.
        
        Emits the favorite_toggled signal with the current city name and updates the UI
        to reflect the new favorite state.
        """
        city = self.search_input.text().strip()
        if city:
            # Visual feedback
            current_icon = self.fav_btn.text()
            if current_icon == '☆':
                self.fav_btn.setText('★')
                self.fav_btn.setToolTip('Remove from favorites')
                self.status_bar.showMessage(f'Added {city} to favorites', 3000)
            else:
                self.fav_btn.setText('☆')
                self.fav_btn.setToolTip('Add to favorites')
                self.status_bar.showMessage(f'Removed {city} from favorites', 3000)
            
            # Emit the signal
            self.favorite_toggled.emit(city)
    
    def _on_favorite_selected(self, value):
        """Handle favorite selection from the dropdown.
        
        Args:
            value (str): The selected favorite city name
        """
        if value and value != self.search_input.text().strip():
            self.search_input.setText(value)
            self.favorite_selected.emit(value)
    
    def update_favorite_button(self, is_favorite):
        """Update the favorite button state based on whether the current city is a favorite.
        
        Args:
            is_favorite (bool): Whether the current city is in favorites
        """
        if is_favorite:
            self.fav_btn.setText('★')
            self.fav_btn.setStyleSheet('''
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 16px;
                    padding: 0 5px;
                    color: #f1c40f;
                }
                QPushButton:hover {
                    color: #f39c12;
                }
            ''')
            self.fav_btn.setToolTip('Remove from favorites')
        else:
            self.fav_btn.setText('☆')
            self.fav_btn.setStyleSheet('''
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 16px;
                    padding: 0 5px;
                    color: #95a5a6;
                }
                QPushButton:hover {
                    color: #f1c40f;
                }
            ''')
            self.fav_btn.setToolTip('Add to favorites')
    
    def update_favorites_list(self, favorites):
        """Update the favorites dropdown list with the latest favorites.
        
        Args:
            favorites (list): List of favorite city names
        """
        if not isinstance(favorites, list):
            favorites = []
            
        # Sort favorites alphabetically
        favorites = sorted(favorites, key=str.lower)
        
        # Store current selection
        current = self.favorites_combo.currentText()
        
        # Block signals to prevent triggering selection change
        self.favorites_combo.blockSignals(True)
        
        try:
            self.favorites_combo.clear()
            
            # Add a placeholder if no favorites
            if not favorites:
                self.favorites_combo.addItem('No favorites yet')
                self.favorites_combo.setEnabled(False)
                return
                
            # Add favorites to the combo box
            self.favorites_combo.addItems(favorites)
            self.favorites_combo.setEnabled(True)
            
            # Try to restore previous selection if it still exists
            if current in favorites:
                self.favorites_combo.setCurrentText(current)
            elif favorites:  # Select first item if previous selection is gone
                self.favorites_combo.setCurrentIndex(0)
                
            # Update tooltip with count
            self.favorites_combo.setToolTip(f"{len(favorites)} favorite{'s' if len(favorites) != 1 else ''} saved")
            
        finally:
            # Always unblock signals when done
            self.favorites_combo.blockSignals(False)
    
    def set_city(self, city):
        """Set the current city in the search input."""
        self.search_input.setText(city)
    
    def set_units(self, units):
        """Set the current units in the units combo box."""
        index = self.units_combo.findData(units)
        if index >= 0:
            self.units_combo.setCurrentIndex(index)
    
    def set_language(self, language):
        """Set the current language and update all UI text."""
        # Update all UI text using translations
        if hasattr(self, 'search_button'):
            self.search_button.setText(self.translations_manager.t('search', language))
        
        if hasattr(self, 'favorites_combo'):
            self.favorites_combo.setPlaceholderText(self.translations_manager.t('favorites', language))
        
        if hasattr(self, 'current_weather_label'):
            self.current_weather_label.setText(self.translations_manager.t('current_weather', language))
        
        if hasattr(self, 'forecast_label'):
            self.forecast_label.setText(self.translations_manager.t('forecast', language))
        
        # Update window title
        self.setWindowTitle(f"{self.translations_manager.t('app_title', language)} v{get_version()}")
        
        # Update status bar
        self.set_status(self.translations_manager.t('ready', language) or 'Ready')
    
    def set_status(self, message):
        """Set the status bar message."""
        self.status_bar.showMessage(message)
    
    def show_error(self, message):
        """Show an error message to the user."""
        self.status_bar.showMessage(f"Error: {message}", 5000)  # Show for 5 seconds
    
    def apply_theme(self):
        """Apply the dark theme to the application."""
        # Set the application style
        self.setStyleSheet('''
            QMainWindow {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QLabel {
                color: #ecf0f1;
            }
            QStatusBar {
                background-color: #34495e;
                color: #ecf0f1;
                border-top: 1px solid #3d4f5e;
            }
        ''')
        
        # Apply dark palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(44, 62, 80))  # #2c3e50
        palette.setColor(QPalette.ColorRole.WindowText, QColor(236, 240, 241))  # #ecf0f1
        palette.setColor(QPalette.ColorRole.Base, QColor(52, 73, 94))  # #34495e
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(44, 62, 80))  # #2c3e50
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(236, 240, 241))  # #ecf0f1
        palette.setColor(QPalette.ColorRole.Button, QColor(52, 73, 94))  # #34495e
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(236, 240, 241))  # #ecf0f1
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(52, 152, 219))  # #3498db
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
    
    def clear_weather_display(self):
        """Clear the weather display area."""
        # Remove all widgets except the first one (placeholder)
        while self.weather_layout.count() > 1:
            item = self.weather_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
    
    def add_weather_widget(self, widget):
        """Add a widget to the weather display area."""
        # Remove the placeholder if it exists
        if self.weather_layout.count() == 1 and \
           isinstance(self.weather_layout.itemAt(0).widget(), QLabel) and \
           self.weather_layout.itemAt(0).widget().text() == 'Search for a city to see weather information':
            self.weather_layout.takeAt(0).widget().deleteLater()
        
        # Add the new widget
        self.weather_layout.addWidget(widget)
    
    def show_loading(self, show=True):
        """Show or hide loading state."""
        self.search_btn.setEnabled(not show)
        self.search_btn.setText('Loading...' if show else 'Search')
