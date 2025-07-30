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
    QMenuBar, QMenu, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QFont, QTextCursor

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
        
        # Create text browser for markdown content
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setReadOnly(True)
        layout.addWidget(self.text_browser)
        
        # Create menu bar
        self.create_menus()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Set default font
        font = QFont()
        font.setPointSize(10)
        self.text_browser.setFont(font)
    
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
                    }}
                    h1, h2, h3, h4, h5, h6 {{ 
                        color: #2c3e50;
                        margin-top: 1.5em;
                    }}
                    pre, code {{
                        background-color: #f5f5f5;
                        border-radius: 4px;
                        padding: 0.2em 0.4em;
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
                        background-color: #f2f2f2;
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
            """.format(html, QUrl.fromLocalFile(os.path.dirname(os.path.abspath(file_path)) + '/').toString())
            
            self.text_browser.setHtml(styled_html)
            self.setWindowTitle(f"{self.translations.get('documentation', 'Documentation')} - {os.path.basename(file_path)}")
            self.status_bar.showMessage(f"{self.translations.get('loaded', 'Loaded:')} {file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translations.get('error', 'Error'),
                f"{self.translations.get('error_loading_file', 'Error loading file:')} {str(e)}"
            )
            return False
    
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
            self.translations.get('about_text', 'Markdown Viewer\nVersion 1.0.0\n\nA simple markdown documentation viewer.')
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
