"""
Sponsor Dialog Module

This module provides the Sponsor dialog for the Weather application.
It displays options for users to support the project through various
platforms like GitHub Sponsors, Patreon, PayPal, and cryptocurrency.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import platform
import logging
from datetime import datetime

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
            root: The parent window for the dialog
        """
        self.root = root
        self.style = ttk.Style()
        self._setup_styles()
    
    def _setup_styles(self) -> None:
        """Configure custom styles for the sponsor dialog."""
        # Configure button styles
        self.style.configure('Sponsor.TButton',
                           font=('Segoe UI', 10),
                           padding=8,
                           background='#1a73e8',
                           foreground='white')
        
        # Map the button state to change appearance on hover
        self.style.map('Sponsor.TButton',
                      background=[('active', '#0d5bba'), ('!disabled', '#1a73e8')],
                      foreground=[('!disabled', 'white')])
        
        # Style for crypto address buttons
        self.style.configure('Crypto.TButton',
                           font=('Consolas', 9),
                           padding=5,
                           background='#1a73e8',
                           foreground='white')
        
        # Map the crypto button state
        self.style.map('Crypto.TButton',
                      background=[('active', '#0d5bba'), ('!disabled', '#1a73e8')],
                      foreground=[('!disabled', 'white')])
        
        # Style for link labels
        self.style.configure('Link.TLabel',
                           foreground='#1a73e8',
                           font=('Segoe UI', 9, 'underline'),
                           cursor='hand2')
    
    def _open_url(self, url: str) -> None:
        """
        Open the specified URL in the default web browser.
        
        Args:
            url: The URL to open
        """
        try:
            webbrowser.open_new_tab(url)
            logging.info(f"Opened URL: {url}")
        except Exception as e:
            logging.error(f"Error opening URL {url}: {e}")
            messagebox.showerror("Error", f"Could not open URL: {e}")
    
    def _copy_to_clipboard(self, text: str, label: str = "") -> None:
        """
        Copy text to the clipboard and show a confirmation.
        
        Args:
            text: The text to copy
            label: Optional label to show in the confirmation message
        """
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()  # Required for clipboard to work
            
            msg = f"Copied {label} to clipboard!" if label else "Copied to clipboard!"
            messagebox.showinfo("Success", msg, parent=self.dialog)
            logging.info(f"Copied to clipboard: {text[:20]}...")
        except Exception as e:
            logging.error(f"Error copying to clipboard: {e}")
            messagebox.showerror("Error", "Failed to copy to clipboard", parent=self.dialog)
    
    def _create_section(self, parent: tk.Widget, title: str) -> ttk.Frame:
        """
        Create a titled section in the dialog.
        
        Args:
            parent: The parent widget
            title: The section title
            
        Returns:
            The created frame
        """
        frame = ttk.LabelFrame(
            parent,
            text=f" {title} ",
            padding=(15, 10, 15, 10),
            style='Card.TFrame'
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        return frame
    
    def _create_sponsor_button(self, parent: tk.Widget, text: str, url: str, icon: str = "") -> ttk.Button:
        """
        Create a styled sponsor button.
        
        Args:
            parent: The parent widget
            text: Button text
            url: URL to open when clicked
            icon: Optional emoji icon
            
        Returns:
            The created button
        """
        btn_text = f"{icon} {text}" if icon else text
        btn = ttk.Button(
            parent,
            text=btn_text,
            style='Sponsor.TButton',
            command=lambda: self._open_url(url)
        )
        return btn
    
    def _create_crypto_section(self, parent: tk.Widget) -> None:
        """Create the cryptocurrency donation section."""
        crypto_frame = self._create_section(parent, "Cryptocurrency")
        
        # Monero
        btc_frame = ttk.Frame(crypto_frame)
        btc_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(btc_frame, text="Monero:").pack(side=tk.LEFT, padx=5)
        
        btc_address = "47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF"
        ttk.Button(
            btc_frame,
            text=btc_address,
            style='Crypto.TButton',
            command=lambda: self._copy_to_clipboard(btc_address, "Monero address")
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
    def show_sponsor(self) -> None:
        """Display the sponsor dialog with various support options."""
        # Create and configure the dialog window
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Support the Project")
        self.dialog.geometry('800x600')
        self.dialog.minsize(700, 500)
        
        # Set application icon if available
        try:
            icon_path = Path('assets/weather.ico')
            if icon_path.exists():
                self.dialog.iconbitmap(str(icon_path))
        except Exception as e:
            logging.warning(f"Could not set window icon: {e}")
        
        # Make the dialog modal
        self.dialog.transient(self.root)
        self.dialog.grab_set()
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Main container
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.grid(row=0, column=0, sticky='nsew')
        main_frame.columnconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame,
            text="Support the Project",
            font=('Segoe UI', 18, 'bold')
        ).pack(side=tk.LEFT)
        
        # Close button in header
        close_btn = ttk.Button(
            header_frame,
            text="✕",
            width=3,
            command=self.dialog.destroy,
            style='Accent.TButton'
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Thank you message
        ttk.Label(
            main_frame,
            text=(
                "Thank you for considering to support the development of Weather App!\n"
                "Your support helps keep this project alive and evolving."
            ),
            wraplength=650,
            justify=tk.CENTER,
            font=('Segoe UI', 11)
        ).pack(pady=(0, 20))
        
        # Create notebook for different sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Sponsorship Platforms Tab
        platforms_frame = ttk.Frame(notebook, padding=10)
        notebook.add(platforms_frame, text="Sponsorship")
        
        # Sponsorship buttons
        buttons = [
            ("GitHub Sponsors", "https://github.com/sponsors/Nsfr750", "💝"),
            ("Patreon", "https://www.patreon.com/Nsfr750", "❤️"),
            ("PayPal", "https://paypal.me/3dmega", "💳"),
        ]
        
        for text, url, icon in buttons:
            btn = self._create_sponsor_button(platforms_frame, text, url, icon)
            btn.pack(fill=tk.X, pady=5, ipady=8)
        
        # Community Tab
        community_frame = ttk.Frame(notebook, padding=10)
        notebook.add(community_frame, text="Community")
        
        community_buttons = [
            ("Join Discord", "https://discord.gg/ryqNeuRYjD", "💬"),
            ("Star on GitHub", "https://github.com/Nsfr750/weather", "⭐"),
            ("Report Issues", "https://github.com/Nsfr750/weather/issues", "🐛"),
            ("Feature Request", "https://github.com/Nsfr750/weather/issues/new/choose", "✨")
        ]
        
        for text, url, icon in community_buttons:
            btn = self._create_sponsor_button(community_frame, text, url, icon)
            btn.pack(fill=tk.X, pady=5, ipady=8)
        
        # Cryptocurrency Tab
        crypto_frame = ttk.Frame(notebook, padding=10)
        notebook.add(crypto_frame, text="Crypto")
        self._create_crypto_section(crypto_frame)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(
            footer_frame,
            text=f"© {datetime.now().year} Nsfr750 • Thank you for your support! 🚀",
            font=('Segoe UI', 9),
            foreground='#666666'
        ).pack(side=tk.LEFT)
        
        # Center the dialog on screen
        self.dialog.update_idletasks()
        window_width = self.dialog.winfo_width()
        window_height = self.dialog.winfo_height()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.dialog.geometry(f'{window_width}x{window_height}+{x}+{y}')

