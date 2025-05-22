"""
About Dialog Module

This module provides the About dialog for the Weather application.
It displays information about the application including version number,
copyright information, and a brief description.
"""

import tkinter as tk
from tkinter import ttk
from version import get_version

class About:
    """
    A class to display the About dialog for the Weather application.
    
    This class provides a static method to show a modal dialog with
    application information including version, description, and copyright.
    """
    
    @staticmethod
    def show_about(root):
        """
        Display the About dialog.
        
        This method creates and shows a modal dialog with application information.
        The dialog includes the application name, version, description, and
        copyright information.
        
        Args:
            root (tk.Tk): The parent window for the dialog
        """
        # Create and configure the about dialog window
        about_dialog = tk.Toplevel(root)
        about_dialog.title('About Weather')
        about_dialog.geometry('400x300')
        about_dialog.transient(root)  # Set as transient window
        about_dialog.grab_set()  # Make dialog modal
        
        # Center the dialog on screen
        window_width = 400
        window_height = 300
        screen_width = about_dialog.winfo_screenwidth()
        screen_height = about_dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        about_dialog.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Application title
        title = ttk.Label(
            about_dialog,
            text='Weather Application',
            font=('Helvetica', 16, 'bold')
        )
        title.pack(pady=20)

        # Version information (dynamically imported from version.py)
        version = ttk.Label(
            about_dialog,
            text=f'Version {get_version()}',
            font=('Helvetica', 10)
        )
        version.pack()

        # Application description
        description = ttk.Label(
            about_dialog,
            text='A weather information application\nproviding current conditions\nand forecasts.',
            justify=tk.CENTER,
            font=('Helvetica', 10)
        )
        description.pack(pady=20, padx=20)

        # Copyright information
        copyright_label = ttk.Label(
            about_dialog,
            text='© 2025 Nsfr750. All rights reserved.',
            font=('Helvetica', 9)
        )
        copyright_label.pack(pady=10)

        # Close button
        close_btn = ttk.Button(
            about_dialog,
            text='Close',
            command=about_dialog.destroy
        )
        close_btn.pack(pady=20)
