#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown Viewer

A simple markdown viewer for the project documentation.
"""

import os
import sys
import markdown
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget, QFileDialog,
    QMenuBar, QMenu, QStatusBar, QMessageBox, QPushButton, QHBoxLayout, QLabel, QComboBox
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QFont, QTextCursor
from PyQt6.QtGui import QDesktopServices

# Import translations
from translations import TRANSLATIONS

class MarkdownViewer(QMainWindow):
    def __init__(self, file_path=None, language='EN'):
        super().__init__()
        self.language = language
        self.translations = TRANSLATIONS.get(language, TRANSLATIONS['EN'])
        self.zoom_level = 0
        self.init_ui()
        
        # Open default file if none provided
        if file_path is None:
            default_file = os.path.join('docs', 'index.md')
            if os.path.exists(default_file):
                self.load_file(default_file)
        else:
            self.load_file(file_path)
    
    def init_ui(self):
        self.setWindowTitle(self.translations.get('documentation', 'Documentation'))
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create top bar for controls
        top_bar = QHBoxLayout()
        
        # Left side: Document selection
        left_controls = QHBoxLayout()
        
        # Add label for dropdown
        label = QLabel(self.translations.get('select_document', 'Select Document:'))
        left_controls.addWidget(label)
        
        # Create dropdown for markdown files
        self.file_dropdown = QComboBox()
        self.file_dropdown.setMinimumWidth(200)
        self.file_dropdown.setToolTip(self.translations.get('select_document_tooltip', 'Select a document to view'))
        self.file_dropdown.currentTextChanged.connect(self.on_document_selected)
        left_controls.addWidget(self.file_dropdown)
        
        # Add left controls to top bar
        top_bar.addLayout(left_controls)
        
        # Add stretch to push zoom controls to the right
        top_bar.addStretch()
        
        # Right side: Zoom controls and About button
        right_controls = QHBoxLayout()
        
        # Zoom out button
        self.zoom_out_btn = QPushButton('−')  # Minus sign
        self.zoom_out_btn.setToolTip(self.translations.get('zoom_out', 'Zoom Out (Ctrl+-)'))
        self.zoom_out_btn.setFixedSize(30, 30)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        right_controls.addWidget(self.zoom_out_btn)
        
        # Zoom reset button
        self.zoom_reset_btn = QPushButton('100%')
        self.zoom_reset_btn.setToolTip(self.translations.get('reset_zoom', 'Reset Zoom (Ctrl+0)'))
        self.zoom_reset_btn.setFixedSize(50, 30)
        self.zoom_reset_btn.clicked.connect(self.reset_zoom)
        right_controls.addWidget(self.zoom_reset_btn)
        
        # Zoom in button
        self.zoom_in_btn = QPushButton('+')
        self.zoom_in_btn.setToolTip(self.translations.get('zoom_in', 'Zoom In (Ctrl++)'))
        self.zoom_in_btn.setFixedSize(30, 30)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        right_controls.addWidget(self.zoom_in_btn)
        
        # Add a separator
        separator = QLabel('|')
        separator.setStyleSheet('color: #999; margin: 0 5px;')
        right_controls.addWidget(separator)
        
        # About button
        self.about_btn = QPushButton(self.translations.get('about', 'About'))
        self.about_btn.setToolTip(self.translations.get('about_tooltip', 'Show information about this application'))
        self.about_btn.clicked.connect(self.show_about)
        self.about_btn.setFixedHeight(30)
        right_controls.addWidget(self.about_btn)
        
        # Add right controls to top bar
        top_bar.addLayout(right_controls)
        
        # Add top bar to main layout
        layout.addLayout(top_bar)
        
        # Create text browser for markdown content
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)  # We'll handle links manually
        self.text_browser.setReadOnly(True)
        self.text_browser.anchorClicked.connect(self.on_link_clicked)  # Handle link clicks
        layout.addWidget(self.text_browser)
        
        # Add close button
        close_button = QPushButton(self.translations.get('close', 'Close'))
        close_button.clicked.connect(self.close)
        close_button.setFixedWidth(100)
        close_button.setToolTip(self.translations.get('close_tooltip', 'Close this window'))
        
        # Create a horizontal layout for the button to center it
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Apply styling
        self.apply_styling(close_button)
        
        # Create menu bar (moved after UI setup to ensure all widgets exist)
        self.create_menus()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Set default font
        self.default_font = QFont()
        self.default_font.setPointSize(10)
        self.text_browser.setFont(self.default_font)
        
        # Load available markdown files
        self.load_available_documents()
    
    def create_menus(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(self.translations.get('file', 'File'))
        
        open_action = QAction(self.translations.get('open', 'Open'), self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(self.translations.get('exit', 'Exit'), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu(self.translations.get('view', 'View'))
        
        zoom_in_action = QAction(self.translations.get('zoom_in', 'Zoom In'), self)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction(self.translations.get('zoom_out', 'Zoom Out'), self)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction(self.translations.get('reset_zoom', 'Reset Zoom'), self)
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        # Help menu
        help_menu = menubar.addMenu(self.translations.get('help', 'Help'))
        
        about_action = QAction(self.translations.get('about', 'About'), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def load_available_documents(self):
        """Load all markdown files from the docs directory."""
        self.file_dropdown.clear()
        self.document_paths = {}
        
        if not os.path.exists('docs'):
            os.makedirs('docs')
            return
        
        # Get all markdown files in the docs directory
        for root, _, files in os.walk('docs'):
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    display_name = os.path.splitext(file)[0].replace('_', ' ').title()
                    self.document_paths[display_name] = full_path
                    self.file_dropdown.addItem(display_name)
        
        # Sort documents alphabetically
        self.file_dropdown.model().sort(0)

    def on_document_selected(self, display_name):
        """Handle document selection from dropdown."""
        if display_name and display_name in self.document_paths:
            self.load_file(self.document_paths[display_name])

    def ensure_docs_directory(self):
        """Ensure the docs directory exists and has basic structure."""
        docs_dir = os.path.join(os.getcwd(), 'docs')
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            
            # Create a basic README.md if it doesn't exist
            readme_path = os.path.join(docs_dir, 'README.md')
            if not os.path.exists(readme_path):
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write("# Weather App Documentation\n\n"
                           "Welcome to the Weather App documentation.\n\n"
                           "## Available Documentation\n\n"
                           "- [Main](index.md)\n"
                           "- [Installation](installation.md)\n"
                           "- [Troubleshooting](troubleshooting.md)\n"
                           "- [Usage](usage.md)\n"
                           "- [Development](development.md)\n"
                           "- [Translations](translations.md)\n"
                    )
            
            # Create other basic documentation files
            self.create_default_doc('index.md', "# Index\n\nIndex information goes here.")
            self.create_default_doc('installation.md', "# Installation\n\nInstallation instructions go here.")
            self.create_default_doc('troubleshooting.md', "# Troubleshooting\n\nTroubleshooting information goes here.")
            self.create_default_doc('usage.md', "# Usage\n\nUsage information goes here.")
            self.create_default_doc('development.md', "# Development\n\nDevelopment information goes here.")
            self.create_default_doc('translations.md', "# Translations\n\nTranslations information goes here.")
            
            return True
        return False
    
    def create_default_doc(self, filename, content):
        """Create a default documentation file if it doesn't exist."""
        filepath = os.path.join('docs', filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

    def on_link_clicked(self, url):
        """Handle clicks on markdown links."""
        if url.isLocalFile() or url.scheme() in ['file', '']:
            try:
                # Ensure docs directory exists
                docs_created = self.ensure_docs_directory()
                if docs_created:
                    self.load_available_documents()  # Refresh the dropdown
                
                # Handle local file links
                file_path = url.toLocalFile() if url.isLocalFile() else url.toString().replace('file:///', '')
                
                # Handle Windows paths with drive letters
                if ':/' in file_path and not file_path.startswith('file:'):
                    file_path = file_path.replace(':/', ':/', 1)
                
                # Normalize path and handle URL encoding
                file_path = os.path.normpath(file_path.replace('file:', ''))
                
                # If it's just a filename, look in the docs directory
                if not os.path.dirname(file_path) and not file_path.startswith('docs'):
                    file_path = os.path.join('docs', file_path)
                
                # Check if file exists directly
                if os.path.exists(file_path) and file_path.endswith('.md'):
                    self.load_file(file_path)
                    self._update_dropdown_selection(file_path)
                    return
                
                # If we get here, the file wasn't found
                reply = QMessageBox.question(
                    self,
                    self.translations.get('file_not_found', 'File Not Found'),
                    f"{self.translations.get('could_not_find', 'Could not find:')} {os.path.basename(file_path)}\n\n"
                    f"{self.translations.get('create_file', 'Would you like to create this file?')}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.create_default_doc(
                        os.path.basename(file_path),
                        f"# {os.path.splitext(os.path.basename(file_path))[0].replace('_', ' ').title()}\n\n"
                        "Documentation content goes here."
                    )
                    self.load_available_documents()
                    self.load_file(os.path.join('docs', os.path.basename(file_path)))
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.translations.get('error', 'Error'),
                    f"{self.translations.get('error_loading', 'Error loading file:')} {str(e)}"
                )
        else:
            # For external links, open in default application
            QDesktopServices.openUrl(url)

    def _update_dropdown_selection(self, file_path):
        """Update the dropdown to show the current document."""
        filename = os.path.splitext(os.path.basename(file_path))[0]
        display_name = filename.replace('_', ' ').title()
        index = self.file_dropdown.findText(display_name, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.file_dropdown.setCurrentIndex(index)
        else:
            # If not found in dropdown, add it
            self.document_paths[display_name] = file_path
            self.file_dropdown.addItem(display_name)
            self.file_dropdown.model().sort(0)
            # Find the index after sorting
            index = self.file_dropdown.findText(display_name, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.file_dropdown.setCurrentIndex(index)

    def load_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                QMessageBox.warning(
                    self,
                    self.translations.get('error', 'Error'),
                    f"{self.translations.get('file_not_found', 'File not found:')} {file_path}"
                )
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_text = f.read()
            
            # Convert markdown to HTML
            html = markdown.markdown(
                markdown_text,
                extensions=['extra', 'tables', 'codehilite', 'fenced_code', 'toc']
            )
            
            # Get directory of the current file for relative links
            base_dir = os.path.dirname(os.path.abspath(file_path))
            
            # Add some basic styling
            styled_html = """
            <html>
            <head>
                <base href="{1}" />
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        line-height: 1.6;
                        padding: 20px;
                        max-width: 1200px;
                        margin: 0 auto;
                        color: #ffffff;
                        background-color: #2c3e50;
                    }}
                    h1, h2, h3, h4, h5, h6 {{ 
                        color: #d0bbab;
                        margin-top: 1.5em;
                    }}
                    pre, code {{
                        background-color: #aad8ff;
                        border-radius: 4px;
                        padding: 0.2em 0.4em;
                        color: black;
                    }}
                    pre {{
                        padding: 1em;
                        overflow-x: auto;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 1em 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #aad8ff;
                        color: black;
                    }}
                    a {{ 
                        color: #3498db; 
                        text-decoration: none;
                    }}
                    a:hover {{ text-decoration: underline; }}
                </style>
            </head>
            <body>
                {0}
            </body>
            </html>
            """.format(html, QUrl.fromLocalFile(base_dir + '/').toString())
            
            self.text_browser.setHtml(styled_html)
            self.setWindowTitle(f"{self.translations.get('documentation', 'Documentation')} - {os.path.basename(file_path)}")
            self.status_bar.showMessage(f"{self.translations.get('loaded', 'Loaded:')} {file_path}")
            
            # Store current file path
            self.current_file = file_path
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translations.get('error', 'Error'),
                f"{self.translations.get('error_loading_file', 'Error loading file:')} {str(e)}"
            )
            return False

    def apply_styling(self, close_button):
        """Apply styling to the UI components."""
        # Style for close button
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                border-radius: 4px;
                padding: 6px 12px;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
        """)
        
        # Style for dropdown
        self.file_dropdown.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #3498db;
                border-radius: 4px;
                background: #2c3e50;
                color: white;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox QAbstractItemView {
                background: #2c3e50;
                color: white;
                selection-background-color: #3498db;
            }
        """)
        
        # Style for label
        for widget in self.findChildren(QLabel):
            widget.setStyleSheet("color: white;")

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translations.get('open_file', 'Open Markdown File'),
            '',
            self.translations.get('md_files', 'Markdown Files (*.md)')
        )
        
        if file_path:
            self.load_file(file_path)
    
    def zoom_in(self):
        self.zoom_level += 1
        self.update_font_size()
    
    def zoom_out(self):
        self.zoom_level -= 1
        self.update_font_size()
    
    def reset_zoom(self):
        self.zoom_level = 0
        self.update_font_size()
    
    def update_font_size(self):
        font = self.text_browser.font()
        base_size = 10  # Default font size
        font.setPointSize(base_size + self.zoom_level)
        self.text_browser.setFont(font)
    
    def show_about(self):
        QMessageBox.about(
            self,
            self.translations.get('about', 'About'),
            self.translations.get('about_text', 'Markdown Viewer\nVersion 1.2.0\n\nA markdown documentation viewer.')
        )


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Get language from command line or use default
    language = 'EN'  # Default language
    if len(sys.argv) > 1:
        language = sys.argv[1].upper()
    
    # Create and show the main window
    viewer = MarkdownViewer(language=language)
    viewer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
