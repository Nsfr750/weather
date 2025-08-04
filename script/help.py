"""
Help Dialog Module

This module provides the Help dialog for the Weather application.
It displays a tabbed interface with usage instructions, features,
and tips for using the application effectively.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QWidget, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

# Import language manager
from lang.language_manager import LanguageManager

class HelpDialog(QDialog):
    """
    A dialog to display help information for the Weather application.
    
    This class provides a tabbed interface with help information organized
    into different sections such as usage, features, and tips.
    """
    
    @staticmethod
    def show_help(parent, translations_manager, language):
        """
        Display the Help dialog.
        
        This method creates and shows a modal dialog with help information
        organized in tabs. The dialog includes sections for usage instructions,
        features, and tips.
        
        Args:
            parent: The parent widget (main window)
            translations_manager: The translations manager instance
            language: The current language code
        """
        dialog = HelpDialog(parent, translations_manager, language)
        dialog.exec()
    
    def __init__(self, parent, translations_manager, language):
        """
        Initialize the Help dialog.
        
        Args:
            parent: The parent widget
            translations_manager: The translations manager instance
            language: The current language code
        """
        super().__init__(parent)
        self.translations_manager = translations_manager
        self.language = language
        
        self.setWindowTitle(self.translations_manager.t('help_title', self.language))
        self.setMinimumSize(700, 500)
        
        # Set window flags to make it a dialog
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Set up the UI
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)
        
        # Add tabs
        self._create_usage_tab()
        self._create_features_tab()
        self._create_tips_tab()
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget, 1)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 0, 10, 10)
        
        close_button = QPushButton(self.translations_manager.t('help_close_btn', self.language))
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(120)
        
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
    
    def _create_scrollable_tab_content(self, text):
        """
        Create a scrollable widget with the given text content.
        
        Args:
            text: The text to display in the scrollable area
            
        Returns:
            QWidget: The scrollable widget
        """
        # Create the scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create the content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)
        
        # Create the label with the text
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setOpenExternalLinks(True)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        
        # Add label to layout with stretch to push content to the top
        content_layout.addWidget(label)
        content_layout.addStretch()
        
        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        
        # Create a container widget to hold the scroll area
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
        
        return container
    
    def _create_usage_tab(self):
        """Create the Usage tab with instructions."""
        usage_text = self.translations_manager.t('help_usage_text', self.language)
        usage_widget = self._create_scrollable_tab_content(usage_text)
        self.tab_widget.addTab(usage_widget, self.translations_manager.t('help_usage_tab', self.language))
    
    def _create_features_tab(self):
        """Create the Features tab with application features."""
        features_text = self.translations_manager.t('help_features_text', self.language)
        features_widget = self._create_scrollable_tab_content(features_text)
        self.tab_widget.addTab(features_widget, self.translations_manager.t('help_features_tab', self.language))
    
    def _create_tips_tab(self):
        """Create the Tips tab with usage tips."""
        tips_text = self.translations_manager.t('help_tips_text', self.language)
        tips_widget = self._create_scrollable_tab_content(tips_text)
        self.tab_widget.addTab(tips_widget, self.translations_manager.t('help_tips_tab', self.language))
    
    def _apply_styling(self):
        """Apply styling to the dialog and its components."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ffffff;
            }
            
            QTabWidget::pane {
                border: 1px solid #1a2634;
                border-top: none;
                border-radius: 0 0 6px 6px;
                background: #34495e;
                padding: 15px;
            }
            
            QTabBar::tab {
                background: #3498db;
                color: #ffffff;
                border: 1px solid #2980b9;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 20px;
                margin-right: 4px;
                font-weight: 500;
            }
            
            QTabBar::tab:selected {
                background: #2980b9;
                color: #ffffff;
                border-color: #1a2634 #1a2634 #34495e;
                margin-bottom: -1px;
            }
            
            QTabBar::tab:!selected {
                margin-top: 2px;
                border-bottom: 1px solid #1a2634;
            }
            
            QTabBar::tab:hover:!selected {
                background: #3fa7f0;
            }
            
            QLabel {
                color: #ffffff;
                line-height: 1.6;
                padding: 4px 0;
            }
            
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: 1px solid #2980b9;
                border-radius: 6px;
                padding: 8px 20px;
                min-width: 100px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
                border-color: #2472a4;
            }
            
            QPushButton:pressed {
                background-color: #2472a4;
                border-color: #1c5d84;
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #2c3e50;
                width: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #7f8c8d;
                border-radius: 5px;
                min-height: 30px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
            
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, 
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Set font for better readability
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        # Set tab bar font to be slightly larger and bold
        tab_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        self.tab_widget.setFont(tab_font)


# Alias for backward compatibility
Help = HelpDialog
