"""
Help Dialog Module

This module provides the Help dialog for the Weather application.
It displays a tabbed interface with usage instructions, features,
and tips for using the application effectively.
"""

import tkinter as tk
from tkinter import ttk, messagebox

class Help:
    """
    A class to display the Help dialog for the Weather application.
    
    This class provides a static method to show a modal dialog with
    help information organized in tabs for different topics.
    """
    
    @staticmethod
    def show_help(parent, translations_manager, language):
        """
        Display the Help dialog.
        
        This method creates and shows a modal dialog with help information
        organized in tabs. The dialog includes sections for usage instructions,
        features, and tips.
        
        Args:
            parent (tk.Tk): The parent window for the dialog
        """
        # Create and configure the help window
        help_window = tk.Toplevel(parent)
        help_window.title(translations_manager.t('help_title', language))
        help_window.geometry("700x500")
        help_window.minsize(600, 400)
        
        # Center the window on screen
        window_width = 700
        window_height = 500
        screen_width = help_window.winfo_screenwidth()
        screen_height = help_window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        help_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Create a notebook (tabbed interface)
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== USAGE TAB =====
        usage_frame = ttk.Frame(notebook, padding=10)
        notebook.add(usage_frame, text=translations_manager.t('help_usage_tab', language))
        
        usage_text = translations_manager.t('help_usage_text', language)
        
        # Create a scrollable text area for usage instructions
        usage_canvas = tk.Canvas(usage_frame)
        scrollbar = ttk.Scrollbar(usage_frame, orient="vertical", command=usage_canvas.yview)
        scrollable_frame = ttk.Frame(usage_canvas)
        
        # Configure the canvas scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: usage_canvas.configure(
                scrollregion=usage_canvas.bbox("all")
            )
        )
        
        usage_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        usage_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add usage text
        usage_label = ttk.Label(
            scrollable_frame,
            text=usage_text,
            justify=tk.LEFT,
            wraplength=600,
            padding=10
        )
        usage_label.pack(anchor="w", fill=tk.X)
        
        # Pack the scrollable area
        usage_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ===== FEATURES TAB =====
        features_frame = ttk.Frame(notebook, padding=10)
        notebook.add(features_frame, text=translations_manager.t('help_features_tab', language))
        
        features_text = translations_manager.t('help_features_text', language)
        
        features_label = ttk.Label(
            features_frame,
            text=features_text,
            justify=tk.LEFT,
            wraplength=600
        )
        features_label.pack(anchor="w", fill=tk.BOTH, expand=True)
        
        # ===== TIPS TAB =====
        tips_frame = ttk.Frame(notebook, padding=10)
        notebook.add(tips_frame, text=translations_manager.t('help_tips_tab', language))
        
        tips_text = translations_manager.t('help_tips_text', language)
        
        tips_label = ttk.Label(
            tips_frame,
            text=tips_text,
            justify=tk.LEFT,
            wraplength=600
        )
        tips_label.pack(anchor="w", fill=tk.BOTH, expand=True)
        
        # Add close button at the bottom
        button_frame = ttk.Frame(help_window)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        close_button = ttk.Button(
            button_frame,
            text=translations_manager.t('help_close_btn', language),
            command=help_window.destroy,
            width=15
        )
        close_button.pack(side=tk.RIGHT, padx=10)
        
        # Make the window modal
        help_window.transient(parent)
        help_window.grab_set()
        parent.wait_window(help_window)
