import tkinter as tk
from tkinter import ttk, scrolledtext
import os

LOG_FILE = 'weather_app.log'

class LogViewer:
    """
    A dialog to view the application log file.
    """
    @staticmethod
    def show_log(root):
        log_window = tk.Toplevel(root)
        log_window.title('Application Log')
        log_window.geometry('700x500')
        log_window.minsize(500, 300)
        
        # Log text area
        text_area = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, font=('Consolas', 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load log file content
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            text_area.insert(tk.END, content)
        else:
            text_area.insert(tk.END, 'Log file not found.')
        text_area.config(state=tk.DISABLED)
        
        # Close button
        close_btn = ttk.Button(log_window, text='Close', command=log_window.destroy)
        close_btn.pack(pady=10)
        
        log_window.transient(root)
        log_window.grab_set()
        root.wait_window(log_window)
