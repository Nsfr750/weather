"""
Sponsor Dialog Module

This module provides the Sponsor dialog for the Weather application.
It displays options for users to support the project through various
platforms like GitHub Sponsors, Patreon, PayPal, and cryptocurrency.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
    QFrame, QApplication, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QFont, QIcon
import webbrowser
from pathlib import Path
import logging
from typing import Optional, Dict, List

class Sponsor(QDialog):
    """
    A class to display the Sponsor dialog for the Weather application.
    
    This class provides a method to show a dialog with various sponsorship
    options for users who want to support the development of the application.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the Sponsor dialog.
        
        Args:
            parent: The parent widget for the dialog
        """
        super().__init__(parent)
        self.setWindowTitle("Support Weather App Development")
        self.setMinimumSize(500, 400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Support Weather App Development")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        description = QLabel(
            "If you find this application useful, please consider supporting its development.\n"
            "Your support helps cover development costs and encourages future improvements."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add title and description
        layout.addWidget(title)
        layout.addWidget(description)
        
        # Add a horizontal line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Sponsorship options
        self._add_sponsor_buttons(layout)
        
        # Add stretch to push everything up
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedWidth(100)
        
        # Center the close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
    
    def _add_sponsor_buttons(self, parent_layout):
        """Add sponsor platform buttons to the layout."""
        # List of sponsor options
        sponsor_options = [
            {
                'name': 'GitHub Sponsors',
                'description': 'Support through GitHub Sponsors',
                'url': 'https://github.com/sponsors/Nsfr750',
                'icon': 'github'
            },
            {
                'name': 'Patreon',
                'description': 'Become a patron on Patreon',
                'url': 'https://www.patreon.com/Nsfr750',
                'icon': 'patreon'
            },
            {
                'name': 'PayPal',
                'description': 'Make a one-time donation via PayPal',
                'url': 'https://paypal.me/3dmega',
                'icon': 'paypal'
            },
            {
                'name': 'Monero (XMR)',
                'description': 'Donate cryptocurrency (Monero)',
                'url': '',
                'address': '47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF',
                'icon': 'crypto'
            }
        ]
        
        # Add each sponsor option
        for option in sponsor_options:
            btn = QPushButton(option['name'])
            btn.setToolTip(option['description'])
            btn.setProperty('url', option.get('url', ''))
            btn.setProperty('address', option.get('address', ''))
            
            # Style the button
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px;
                    font-weight: bold;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: left;
                    background-color: #3ea86e;
                }
                QPushButton:hover {
                    background-color: #3e78a8;
                }
                QPushButton:pressed {
                    background-color: #71a88a;
                }
            """)
            
            # Set icon if available
            # Note: You'll need to add appropriate icons to your resources
            # For now, we'll use text as a fallback
            
            # Connect the button
            if option.get('url'):
                btn.clicked.connect(lambda checked, url=option['url']: self._open_url(url))
            elif option.get('address'):
                btn.clicked.connect(lambda checked, addr=option['address']: self._copy_address(addr))
            
            parent_layout.addWidget(btn)
    
    def _open_url(self, url):
        """Open the specified URL in the default web browser."""
        try:
            QDesktopServices.openUrl(QUrl(url))
        except Exception as e:
            logging.error(f"Failed to open URL {url}: {e}")
            try:
                webbrowser.open(url)
            except Exception as e:
                logging.error(f"Failed to open URL with webbrowser: {e}")
    
    def _copy_address(self, address):
        """Copy the cryptocurrency address to the clipboard."""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(address)
            
            # Show a message that the address was copied
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Address Copied",
                f"Monero address has been copied to clipboard.\n\n{address}",
                QMessageBox.StandardButton.Ok
            )
        except Exception as e:
            logging.error(f"Failed to copy address to clipboard: {e}")

    @staticmethod
    def show_sponsor_dialog(parent=None):
        """
        Show the sponsor dialog.
        
        Args:
            parent: The parent widget for the dialog
            
        Returns:
            The dialog result (accepted/rejected)
        """
        dialog = Sponsor(parent)
        return dialog.exec()
