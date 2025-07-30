"""
Update checking functionality for the Weather application.
"""
import logging
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Tuple, Callable
import requests
import json
from pathlib import Path
import os

# Get the application directory
APP_DIR = Path(__file__).parent.parent

# Ensure config directory exists
CONFIG_DIR = APP_DIR / 'config'
CONFIG_DIR.mkdir(exist_ok=True)
UPDATES_FILE = CONFIG_DIR / 'updates.json'

# Configure logger
logger = logging.getLogger(__name__)

class UpdateChecker:
    """Handles checking for application updates."""
    
    def __init__(self, current_version: str, config_path: Optional[Path] = None):
        """Initialize the update checker.
        
        Args:
            current_version: The current version of the application.
            config_path: Path to the configuration file (optional).
        """
        self.current_version = current_version
        self.config_path = config_path or UPDATES_FILE
        self.config = self._load_config()
        self.update_url = "https://api.github.com/repos/Nsfr750/weather/releases/latest"
    
    def _load_config(self) -> dict:
        """Load the update configuration."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading update config: {e}")
        return {
            'last_checked': None,
            'last_version': None,
            'dont_ask_until': None
        }
    
    def _save_config(self) -> None:
        """Save the update configuration."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving update config: {e}")
    
    def check_for_updates(self, parent: Optional[tk.Tk] = None, force_check: bool = False) -> Tuple[bool, Optional[dict]]:
        """Check for available updates.
        
        Args:
            parent: Parent window for dialogs.
            force_check: If True, skip the cache and force a check.
            
        Returns:
            Tuple of (update_available, update_info, error_message)
            where error_message is None if no error, or a tuple of (title, message) if there was an error
        """
        try:
            logger.info("Checking for updates...")
            response = requests.get(self.update_url, timeout=10)
            response.raise_for_status()
            release = response.json()
            
            latest_version = release['tag_name'].lstrip('v')
            self.config['last_checked'] = release['published_at']
            self.config['last_version'] = latest_version
            self._save_config()
            
            if self._version_compare(latest_version, self.current_version) > 0:
                logger.info(f"Update available: {latest_version}")
                return True, {
                    'version': latest_version,
                    'url': release['html_url'],
                    'notes': release['body'],
                    'published_at': release['published_at']
                }, None
            else:
                logger.info("No updates available")
                return False, None, ('No Updates', 'You are using the latest version.')
                
        except requests.RequestException as e:
            error_msg = f'Failed to check for updates: {str(e)}'
            logger.error(error_msg)
            return False, None, ('Update Error', error_msg)
        except Exception as e:
            error_msg = f'An unexpected error occurred: {str(e)}'
            logger.exception("Unexpected error during update check")
            return False, None, ('Update Error', error_msg)
    
    def _version_compare(self, v1: str, v2: str) -> int:
        """Compare two version strings.
        
        Returns:
            1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        def parse_version(v: str) -> list:
            return [int(x) for x in v.split('.')]
            
        try:
            v1_parts = parse_version(v1)
            v2_parts = parse_version(v2)
            
            # Pad with zeros if versions have different lengths
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts += [0] * (max_len - len(v1_parts))
            v2_parts += [0] * (max_len - len(v2_parts))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            return 0
            
        except (ValueError, AttributeError):
            # Fallback to string comparison if version format is invalid
            return (v1 > v2) - (v1 < v2)
    
    def show_update_dialog(self, parent: tk.Tk, update_info: dict) -> None:
        """Show a dialog with update information."""
        from tkinter import ttk
        
        dialog = tk.Toplevel(parent)
        dialog.title("Update Available")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = 500
        height = 300
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Update info
        ttk.Label(
            main_frame,
            text=f"Version {update_info['version']} is available!",
            font=('TkDefaultFont', 12, 'bold')
        ).pack(pady=(0, 10))
        
        # Release notes
        notes_frame = ttk.LabelFrame(main_frame, text="Release Notes", padding=5)
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        text = tk.Text(
            notes_frame,
            wrap=tk.WORD,
            width=60,
            height=10,
            font=('TkDefaultFont', 9)
        )
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text.insert('1.0', update_info['notes'])
        text.config(state='disabled')
        
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        ttk.Button(
            btn_frame,
            text="Download Now",
            command=lambda: self._open_download(update_info['url'])
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Remind Me Later",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Make the dialog modal
        dialog.wait_window()
    
    def _open_download(self, url: str) -> None:
        """Open the download URL in the default browser."""
        import webbrowser
        webbrowser.open(url)
        self.dialog.destroy()


def check_for_updates(parent: Optional[tk.Tk] = None, current_version: str = "__version__", force_check: bool = False) -> None:
    """Check for application updates and show a dialog if an update is available.
    
    Args:
        parent: Parent window for dialogs.
        current_version: Current application version.
        force_check: If True, skip the cache and force a check.
    """
    def show_message(title: str, message: str, is_error: bool = False) -> None:
        """Helper to show a message box in the main thread."""
        if parent and parent.winfo_exists():
            try:
                if is_error or title == 'No Updates':
                    parent.after(0, lambda t=title, m=message: messagebox.showinfo(t, m, parent=parent))
                else:
                    parent.after(0, lambda t=title, m=message: messagebox.showerror(t, m, parent=parent))
            except RuntimeError as e:
                logging.error(f"Failed to show message: {e}")
    
    def perform_check():
        try:
            checker = UpdateChecker(current_version)
            update_available, update_info, error_info = None, None, None
            
            try:
                update_available, update_info, error_info = checker.check_for_updates(parent, force_check=force_check)
            except Exception as e:
                error_msg = f"Error checking for updates: {e}"
                logging.exception(error_msg)
                show_message("Update Error", error_msg, is_error=True)
                return
            
            if not parent or not parent.winfo_exists():
                return
                
            if update_available and update_info:
                try:
                    parent.after(0, lambda: checker.show_update_dialog(parent, update_info))
                except Exception as e:
                    logging.exception("Failed to show update dialog")
            elif error_info:
                show_message(error_info[0], error_info[1], is_error=True)
                
        except Exception as e:
            error_msg = f"An unexpected error occurred while checking for updates: {e}"
            logging.exception(error_msg)
            if parent and parent.winfo_exists():
                parent.after(0, lambda: show_message("Update Error", error_msg, is_error=True))
    
    # Only start the thread if we have a parent window
    if parent and parent.winfo_exists():
        import threading
        try:
            thread = threading.Thread(target=perform_check, daemon=True, name="UpdateCheckThread")
            thread.start()
        except Exception as e:
            logging.exception("Failed to start update check thread")
