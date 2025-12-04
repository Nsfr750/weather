"""
Help Dialog Module

This module provides the Help dialog for the Weather application.
It displays a tabbed interface with usage instructions, features,
and tips in a dark-themed interface with language selection.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QWidget, QScrollArea, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/help_dialog.log')
    ]
)
logger = logging.getLogger(__name__)

class HelpDialog(QDialog):
    """
    A dialog to display help information for the Weather application.
    
    Features:
    - Dark theme
    - Three tabs: Usage, Features, and Tips
    - Language selection dropdown
    - Close button with blue background and white text
    """
    
    @classmethod
    def show_help(cls, parent, translations_manager, language):
        """
        Display the Help dialog.
        
        Args:
            parent: The parent widget (main window)
            translations_manager: The translations manager instance
            language: The current language code
        """
        # Create and show the dialog
        dialog = cls(parent, translations_manager, language)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.show()
        return dialog
    
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
        
        # Store references to labels for updates
        self.usage_label = None
        self.features_label = None
        self.tips_label = None
        
        # Set window properties
        self.setWindowTitle(self.translations_manager.get('help_title', 'Help'))
        self.setMinimumSize(800, 600)
        
        # Set window flags to make it a dialog
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Set up the UI
        self._setup_ui()
        self._apply_styling()
        
        # Connect language change signal
        self.translations_manager.language_changed.connect(self._on_language_code_changed)
    
    def _setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a container for the tab widget and language selector
        tab_container = QWidget()
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)
        
        # Add tabs
        self._create_usage_tab()
        self._create_features_tab()
        self._create_tips_tab()
        
        # Add tab widget to the container
        tab_layout.addWidget(self.tab_widget, 1)  # Add stretch to push language selector to the right
        
        # Create language selector
        self.language_combo = QComboBox()
        self.language_combo.setFixedWidth(150)
        self.language_combo.setToolTip(self.translations_manager.tr('select_language'))
        
        # Add available languages to the combo box
        for lang_code in sorted(self.translations_manager.available_languages):
            lang_name = self.translations_manager.get_language_name(lang_code)
            self.language_combo.addItem(lang_name, lang_code)
        
        # Set current language
        current_index = self.language_combo.findData(self.language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        
        # Connect signal
        self.language_combo.currentIndexChanged.connect(self._on_combo_language_changed)
        
        # Add language selector to the tab bar area
        tab_layout.addWidget(self.language_combo)
        
        # Add container to main layout
        main_layout.addWidget(tab_container, 1)  # Add stretch to push button to the bottom
        
        # Add close button
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(15, 10, 15, 15)
        
        self.close_button = QPushButton(self.translations_manager.tr('help_close_btn'))
        self.close_button.setFixedSize(120, 32)
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        main_layout.addWidget(button_container)
    
    def _create_scrollable_tab_content(self, text_key):
        """
        Create a scrollable widget with the given text content.
        
        Args:
            text_key: The translation key for the tab content
            
        Returns:
            QWidget, QLabel: The scrollable widget and the label
        """
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add label with content
        label = QLabel()
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setOpenExternalLinks(True)
        label.setProperty('text_key', text_key)  # Store the key for updates
        
        # Set initial text
        translated_text = self.translations_manager.get(text_key, f"[Missing: {text_key}]")
        label.setText(translated_text)
        
        layout.addWidget(label)
        
        # Add stretch to push content to top
        layout.addStretch()
        
        # Set content to scroll area
        scroll.setWidget(content)
        
        return scroll, label
    
    def _create_usage_tab(self):
        """Create the Usage tab with instructions."""
        self.usage_widget, self.usage_label = self._create_scrollable_tab_content('help_usage_text')
        self.usage_tab_index = self.tab_widget.count()
        self.tab_widget.addTab(self.usage_widget, self.translations_manager.tr('help_usage_tab'))
    
    def _create_features_tab(self):
        """Create the Features tab with application features."""
        self.features_widget, self.features_label = self._create_scrollable_tab_content('help_features_text')
        self.features_tab_index = self.tab_widget.count()
        self.tab_widget.addTab(self.features_widget, self.translations_manager.tr('help_features_tab'))
    
    def _create_tips_tab(self):
        """Create the Tips tab with usage tips."""
        self.tips_widget, self.tips_label = self._create_scrollable_tab_content('help_tips_text')
        self.tips_tab_index = self.tab_widget.count()
        self.tab_widget.addTab(self.tips_widget, self.translations_manager.tr('help_tips_tab'))
    
    def _on_language_code_changed(self, language_code):
        """Handle language change from the translations manager.
        
        Args:
            language_code: The new language code
        """
        logger.debug(f"Language changed to: {language_code}")
        
        if language_code and language_code != self.language:
            self.language = language_code
            
            # Update the combo box selection without triggering the signal
            if hasattr(self, 'language_combo'):
                index = self.language_combo.findData(language_code)
                if index >= 0:
                    self.language_combo.blockSignals(True)
                    self.language_combo.setCurrentIndex(index)
                    self.language_combo.blockSignals(False)
            
            # Update the UI with the new language
            self.retranslate_ui()
            logger.debug(f"UI updated to language: {language_code}")
    
    def _on_combo_language_changed(self, index):
        """Handle language change from the combo box.
        
        Args:
            index: The index of the selected item in the combo box
        """
        # Get the language code from the combo box data
        language_code = self.language_combo.itemData(index)
        logger.debug(f"Combo language changed to: {language_code}")
        
        if language_code and language_code != self.language:
            # Update the translations manager's language
            if not self.translations_manager.set_language(language_code):
                logger.error(f"Failed to set language to: {language_code}")
    
    def retranslate_ui(self):
        """Update all text in the UI with the current language."""
        logger.debug(f"Retranslating UI to language: {self.language}")
        
        # Block signals to prevent recursive calls during updates
        if hasattr(self, 'language_combo'):
            self.language_combo.blockSignals(True)
        
        try:
            # Update window title
            title = self.translations_manager.get('help_title', 'Help')
            self.setWindowTitle(title)
            
            # Update tab titles if they exist
            if hasattr(self, 'usage_tab_index'):
                self.tab_widget.setTabText(
                    self.usage_tab_index,
                    self.translations_manager.get('help_usage_tab', 'Usage')
                )
                
            if hasattr(self, 'features_tab_index'):
                self.tab_widget.setTabText(
                    self.features_tab_index,
                    self.translations_manager.get('help_features_tab', 'Features')
                )
                
            if hasattr(self, 'tips_tab_index'):
                self.tab_widget.setTabText(
                    self.tips_tab_index,
                    self.translations_manager.get('help_tips_tab', 'Tips')
                )
            
            # Update tab contents
            if hasattr(self, 'usage_label') and self.usage_label:
                self._update_tab_content('help_usage_text')
                
            if hasattr(self, 'features_label') and self.features_label:
                self._update_tab_content('help_features_text')
                
            if hasattr(self, 'tips_label') and self.tips_label:
                self._update_tab_content('help_tips_text')
            
            # Update close button if it exists
            if hasattr(self, 'close_button'):
                self.close_button.setText(
                    self.translations_manager.get('help_close_btn', 'Close')
                )
            
            # Update language selector tooltip if it exists
            if hasattr(self, 'language_combo'):
                self.language_combo.setToolTip(
                    self.translations_manager.get('select_language', 'Select language')
                )
            
            logger.debug("UI retranslation completed successfully")
            
        except Exception as e:
            logger.error(f"Error during UI retranslation: {e}", exc_info=True)
            
        finally:
            # Always restore signals if we blocked them
            if hasattr(self, 'language_combo'):
                self.language_combo.blockSignals(False)
    
    def _update_tab_content(self, text_key):
        """
        Update the content of a tab widget with the given translation key.
        
        Args:
            text_key: The translation key for the content
        """
        # Find the appropriate label based on the text_key
        if text_key == 'help_usage_text' and hasattr(self, 'usage_label'):
            label = self.usage_label
        elif text_key == 'help_features_text' and hasattr(self, 'features_label'):
            label = self.features_label
        elif text_key == 'help_tips_text' and hasattr(self, 'tips_label'):
            label = self.tips_label
        else:
            logger.warning(f"Could not find label for text key: {text_key}")
            return
            
        # Update the label text with the translated text
        translated_text = self.translations_manager.get(text_key, f"[Missing: {text_key}]")
        label.setText(translated_text)
    
    def _apply_styling(self):
        """Apply styling to the dialog and its components."""
        # Set the style sheet for the entire dialog
        self.setStyleSheet("""
            /* Main dialog */
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            /* Tab widget */
            QTabWidget::pane {
                border: 1px solid #34495e;
                border-top: none;
                border-radius: 0 0 4px 4px;
                background: #34495e;
                padding: 0;
            }
            
            QTabBar::tab {
                background: #2c3e50;
                color: #bdc3c7;
                border: 1px solid #34495e;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: 500;
            }
            
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
                border-color: #2980b9;
            }
            
            QTabBar::tab:hover:!selected {
                background: #34495e;
                color: #ecf0f1;
            }
            
            /* Scroll area */
            QScrollArea {
                background: transparent;
                border: none;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #2c3e50;
                width: 10px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background: #7f8c8d;
                min-height: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            /* Language selector */
            QComboBox {
                background: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 120px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: url(down-arrow.png);
            }
            
            QComboBox QAbstractItemView {
                background: #2c3e50;
                color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 4px;
            }
            
            /* Close button */
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #2472a4;
            }
            
            /* Text content */
            QLabel {
                color: #ecf0f1;
                line-height: 1.5;
            }
            
            QLabel a {
                color: #3498db;
                text-decoration: none;
            }
            
            QLabel a:hover {
                text-decoration: underline;
            }
            
            /* Headers */
            h1, h2, h3, h4, h5, h6 {
                color: #3498db;
                margin-top: 0.5em;
                margin-bottom: 0.5em;
            }
            
            /* Lists */
            ul, ol {
                margin: 0.5em 0;
                padding-left: 2em;
            }
            
            li {
                margin: 0.25em 0;
            }
        """)


# Alias for backward compatibility
Help = HelpDialog
