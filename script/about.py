"""
About Dialog Module

This module provides the About dialog for the Weather application.
It displays information about the application including version number,
copyright information, dependencies, and system information.
"""

import tkinter as tk
from tkinter import ttk
import platform
import sys
import webbrowser
from pathlib import Path
from datetime import datetime
from script.version import get_version
from script.icon_utils import get_icon_image

class About:
    """
    A class to display the About dialog for the Weather application.
    
    This class provides a static method to show a modal dialog with
    application information including version, description, copyright,
    dependencies, and system information.
    """
    
    @staticmethod
    def open_url(url):
        """Open a URL in the default web browser."""
        try:
            webbrowser.open_new_tab(url)
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
    def show_about(cls, root):
        """
        Display the About dialog.
        
        Args:
            root: The parent window for the dialog
        """
        # Create and configure the about dialog window
        about_dialog = tk.Toplevel(root)
        about_dialog.title('About Weather')
        about_dialog.geometry('500x600')
        about_dialog.transient(root)
        about_dialog.grab_set()
        about_dialog.resizable(False, False)
        
        # Center the dialog on screen
        window_width = 500
        window_height = 600
        screen_width = about_dialog.winfo_screenwidth()
        screen_height = about_dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        about_dialog.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Apply theme colors
        bg_color = '#f0f0f0' if 'light' in root.tk.call('ttk::style', 'theme', 'use') else '#2c3e50'
        fg_color = '#000000' if 'light' in root.tk.call('ttk::style', 'theme', 'use') else '#ffffff'
        about_dialog.configure(bg=bg_color)
        
        # Main container
        container = ttk.Frame(about_dialog, style='Card.TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Application icon
        try:
            icon_path = Path('assets/weather.ico')
            if icon_path.exists():
                about_dialog.iconbitmap(str(icon_path))
        except Exception as e:
            print(f"Error loading icon: {e}")
        
        # Application title
        title_frame = ttk.Frame(container)
        title_frame.pack(fill=tk.X, pady=(20, 10))
        
        app_icon = ttk.Label(
            title_frame,
            text='🌤️',
            font=('Segoe UI', 24)
        )
        app_icon.pack(side=tk.LEFT, padx=10)
        
        title = ttk.Label(
            title_frame,
            text='Weather Application',
            font=('Segoe UI', 18, 'bold')
        )
        title.pack(side=tk.LEFT, pady=5)
        
        # Version info
        app_info = cls.get_app_info()
        version = ttk.Label(
            container,
            text=f"Version: {app_info['Version']}",
            font=('Segoe UI', 10)
        )
        version.pack(pady=(0, 20))
        
        # Description
        desc_frame = ttk.LabelFrame(
            container,
            text='About',
            padding=10
        )
        desc_frame.pack(fill=tk.X, padx=20, pady=5)
        
        description = ttk.Label(
            desc_frame,
            text=(
                'A feature-rich weather application providing current conditions, '
                'forecasts, and weather alerts. Built with Python and Tkinter.'
            ),
            wraplength=400,
            justify=tk.CENTER
        )
        description.pack(pady=5)
        
        # System information
        sys_frame = ttk.LabelFrame(
            container,
            text='System Information',
            padding=10
        )
        sys_frame.pack(fill=tk.X, padx=20, pady=5)
        
        for key, value in cls.get_system_info().items():
            frame = ttk.Frame(sys_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(
                frame,
                text=f"{key}:",
                font=('Segoe UI', 9, 'bold'),
                width=20,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            ttk.Label(
                frame,
                text=value,
                font=('Segoe UI', 9)
            ).pack(side=tk.LEFT)
        
        # Links
        links_frame = ttk.Frame(container)
        links_frame.pack(pady=15)
        
        github_btn = ttk.Button(
            links_frame,
            text='GitHub Repository',
            command=lambda: cls.open_url(app_info['GitHub']),
            style='Link.TButton'
        )
        github_btn.pack(side=tk.LEFT, padx=5)
        
        # Copyright
        copyright_frame = ttk.Frame(container)
        copyright_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(
            copyright_frame,
            text=app_info['Copyright'],
            font=('Segoe UI', 8),
            foreground='#666666'
        ).pack()
        
        # Close button
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        close_btn = ttk.Button(
            btn_frame,
            text='Close',
            command=about_dialog.destroy,
            width=15
        )
        close_btn.pack(pady=10)
        
        # Make the dialog modal
        about_dialog.transient(root)
        about_dialog.grab_set()
        root.wait_window(about_dialog)
