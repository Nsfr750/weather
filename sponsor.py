"""
Sponsor Dialog Module

This module provides the Sponsor dialog for the Weather application.
It displays options for users to support the project through various
platforms like GitHub Sponsors, Patreon, and others.
"""

import tkinter as tk
import webbrowser
from typing import List, Tuple

class Sponsor:
    """
    A class to display the Sponsor dialog for the Weather application.
    
    This class provides a method to show a dialog with various sponsorship
    options for users who want to support the development of the application.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the Sponsor dialog.
        
        Args:
            root (tk.Tk): The parent window for the dialog
        """
        self.root = root
        
    def _open_url(self, url: str) -> None:
        """
        Open the specified URL in the default web browser.
        
        Args:
            url (str): The URL to open
        """
        try:
            webbrowser.open(url)
        except Exception as e:
            # Log error if URL cannot be opened
            print(f"Error opening URL {url}: {e}")
    
    def show_sponsor(self) -> None:
        """
        Display the sponsor dialog with various support options.
        
        This method creates a modal dialog with buttons for different
        sponsorship platforms. Each button opens the corresponding URL
        in the default web browser when clicked.
        """
        # Create and configure the dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Support the Project")
        dialog.geometry('600x200')
        dialog.resizable(False, False)
        
        # Center the dialog on screen
        window_width = 700
        window_height = 200
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        dialog.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Add a thank you message
        thank_you = tk.Label(
            dialog,
            text="Thank you for considering to support the project!",
            font=('Helvetica', 12, 'bold'),
            pady=10
        )
        thank_you.pack()
        
        # Frame to hold the sponsor buttons
        btn_frame = tk.Frame(dialog, pady=20)
        btn_frame.pack(expand=True)
        
        # Define sponsorship options with their display text and URLs
        buttons: List[Tuple[str, str]] = [
            ("⭐ Sponsor on GitHub", "https://github.com/sponsors/Nsfr750"),
            ("💬 Join Discord", "https://discord.gg/BvvkUEP9"),
            ("☕ Buy Me a Coffee", "https://paypal.me/3dmega"),
            ("❤️ Join Patreon", "https://www.patreon.com/Nsfr750")
        ]
        
        # Create and pack each sponsor button
        for text, url in buttons:
            btn = tk.Button(
                btn_frame,
                text=text,
                pady=8,
                padx=15,
                relief=tk.RAISED,
                bd=2,
                command=lambda u=url: self._open_url(u)
            )
            btn.pack(side=tk.LEFT, padx=10, ipadx=5, ipady=3)
        
        # Close button at the bottom
        close_btn = tk.Button(
            dialog,
            text="Close",
            command=dialog.destroy,
            width=15,
            pady=5
        )
        close_btn.pack(pady=(0, 10))
        
        # Make the dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

