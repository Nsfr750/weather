"""
About Dialog Module

This module provides the About dialog for the Weather application.
It displays information about the application including version number,
copyright information, dependencies, and system information.
"""

import os
import platform
import sys
import webbrowser
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QWidget, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QFont, QDesktopServices, QIcon, QPixmap

from script.version import get_version

class AboutDialog(QDialog):
    """
    A dialog to display information about the Weather application.
    
    This class provides a static method to show a modal dialog with
    application information including version, description, copyright,
    dependencies, and system information.
    """
    
    @staticmethod
    def open_url(url):
        """Open a URL in the default web browser."""
        try:
            QDesktopServices.openUrl(QUrl(url))
        except Exception as e:
            print(f"Error opening URL: {e}")
    
    @classmethod
    def get_system_info(cls):
        """Get system information."""
        return {
            'Python Version': f"{sys.version.split()[0]} ({platform.architecture()[0]})",
            'Operating System': f"{platform.system()} {platform.release()} ({platform.version()})",
            'Processor': platform.processor() or "Unknown",
            'Machine': platform.machine(),
            'Platform': platform.platform()
        }
    
    @classmethod
    def get_app_info(cls):
        """Get application information."""
        return {
            'Version': get_version(),
            'Build Date': datetime.fromtimestamp(
                Path(__file__).parent.parent.resolve().stat().st_mtime
            ).strftime('%Y-%m-%d %H:%M:%S'),
            'Author': 'Nsfr750',
            'GitHub': 'https://github.com/Nsfr750/weather',
            'License': 'GNU General Public License v3.0',
            'Copyright': f'© 2023-{datetime.now().year} Nsfr750. All rights reserved.'
        }
    
    @classmethod
    def show_about(cls, parent=None):
        """
        Display the About dialog.
        
        Args:
            parent: The parent widget (main window)
        """
        dialog = cls(parent)
        dialog.exec()
    
    def __init__(self, parent=None):
        """Initialize the About dialog."""
        super().__init__(parent)
        
        self.setWindowTitle('About Weather')
        self.setMinimumSize(500, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Get application and system information
        self.app_info = self.get_app_info()
        self.sys_info = self.get_system_info()
        
        # Set up the UI
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Application header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # App icon
        icon_label = QLabel()
        # Try multiple possible paths for the logo
        logo_paths = [
            'assets/meteo.png',  # Development path
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'meteo.png'),  # Installed path
            'meteo.png'  # Fallback if in same directory
        ]
        
        pixmap = None
        for path in logo_paths:
            if os.path.exists(path):
                try:
                    pixmap = QPixmap(path)
                    if not pixmap.isNull():
                        break
                except:
                    continue
        
        if pixmap and not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(96, 96, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # App title and version
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title_label = QLabel('Weather Application')
        title_label.setObjectName('titleLabel')
        
        version_label = QLabel(f'Version {self.app_info["Version"]}')
        version_label.setObjectName('versionLabel')
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(version_label)
        title_layout.addStretch()
        
        header_layout.addLayout(title_layout)
        content_layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(
            'A feature-rich weather application providing current conditions, '
            'forecasts, and weather alerts.'
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(desc_label)
        
        # System information section
        sys_group = QFrame()
        sys_group.setObjectName('sysGroup')
        sys_layout = QVBoxLayout(sys_group)
        sys_layout.setContentsMargins(15, 10, 15, 10)
        sys_layout.setSpacing(8)
        
        sys_title = QLabel('System Information')
        sys_title.setObjectName('sectionTitle')
        sys_layout.addWidget(sys_title)
        
        # Add system info items
        for key, value in self.sys_info.items():
            item_layout = QHBoxLayout()
            
            key_label = QLabel(f"{key}:")
            key_label.setObjectName('infoKey')
            
            value_label = QLabel(value)
            value_label.setObjectName('infoValue')
            value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            
            item_layout.addWidget(key_label, 1)
            item_layout.addWidget(value_label, 2)
            sys_layout.addLayout(item_layout)
        
        content_layout.addWidget(sys_group)
        
        # Links
        links_layout = QHBoxLayout()
        links_layout.setSpacing(15)
        links_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Documentation button
        docs_btn = QPushButton('Documentation')
        docs_btn.setObjectName('linkButton')
        docs_btn.clicked.connect(lambda: self.open_url('https://github.com/Nsfr750/weather/wiki'))
        links_layout.addWidget(docs_btn)
        
        # GitHub button
        github_btn = QPushButton('GitHub Repository')
        github_btn.setObjectName('linkButton')
        github_btn.clicked.connect(lambda: self.open_url(self.app_info['GitHub']))
        links_layout.addWidget(github_btn)
        
        content_layout.addLayout(links_layout)
        
        # Spacer to push content up
        content_layout.addStretch()
        
        # Copyright
        copyright_label = QLabel(self.app_info['Copyright'])
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setObjectName('copyrightLabel')
        content_layout.addWidget(copyright_label)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 15, 0, 0)
        
        close_btn = QPushButton('Close')
        close_btn.setFixedWidth(120)
        close_btn.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)
    
    def _apply_styling(self):
        """Apply styling to the dialog and its components."""
        self.setStyleSheet("""
            QDialog {
                background-color: #aad8ff;
            }
            
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #3498db;
            }
            
            QLabel#versionLabel {
                font-size: 12px;
                color: #ffa162;
            }
            
            QFrame#sysGroup {
                background-color: #f6caa5;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            
            QLabel#sectionTitle {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                padding-bottom: 5px;
                border-bottom: 1px solid #e0e0e0;
                margin-bottom: 5px;
            }
            
            QLabel#infoKey {
                font-weight: bold;
                color: #2c3e50;
            }
            
            QLabel#infoValue {
                color: #34495e;
            }
            
            QPushButton {
                background-color: #3498db;  
                color: white;  
                border: 1px solid #2980b9;  
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #5dade2;  
            }
            
            QPushButton:pressed {
                background-color: #2980b9;  
            }
            
            QPushButton#linkButton {
                background-color: transparent;
                border: none;
                color: #3498db;
                text-decoration: underline;
                padding: 2px 5px;
                min-width: 0;
            }
            
            QPushButton#linkButton:hover {
                color: #2980b9;
                background-color: transparent;
            }
            
            QLabel#copyrightLabel {
                color: #7f8c8d;
                font-size: 11px;
                margin-top: 10px;
            }
            
            QScrollArea, QWidget#scrollAreaWidgetContents {
                background-color: transparent;
                border: none;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #c4c4c4;
                border-radius: 6px;
                min-height: 20px;
                margin: 3px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Set font for better readability
        font = self.font()
        font.setFamily('Segoe UI')
        font.setPointSize(10)
        self.setFont(font)


# Alias for backward compatibility
About = AboutDialog
