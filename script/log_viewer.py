import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, font as tkfont
import os
from pathlib import Path
from datetime import datetime

class LogViewer:
    """
    A dialog to view and filter application log files.
    """
    def __init__(self, root):
        self.root = root
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.current_log_file = None
        self.log_levels = ['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        self.current_level = 'ALL'
        
        self.setup_ui()
        self.apply_dark_theme()
        self.load_log_files()
        
    def apply_dark_theme(self):
        """Apply dark theme colors to the UI"""
        self.bg_color = '#1e1e1e'
        self.fg_color = '#e0e0e0'
        self.select_bg = '#3e3e3e'
        self.select_fg = '#ffffff'
        self.text_bg = '#2d2d2d'
        self.text_fg = '#e0e0e0'
        self.status_bg = '#2d2d2d'
        self.status_fg = '#a0a0a0'
        self.button_bg = '#3c3f41'
        self.button_fg = '#e0e0e0'
        self.highlight_bg = '#3c3f41'
        self.highlight_fg = '#ffffff'
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure main window
        self.window.configure(bg=self.bg_color)
        
        # Configure ttk styles
        style.configure('.', background=self.bg_color, foreground=self.fg_color)
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        style.configure('TButton', 
                       background=self.button_bg, 
                       foreground=self.button_fg,
                       bordercolor=self.highlight_bg,
                       lightcolor=self.bg_color,
                       darkcolor=self.bg_color)
        style.map('TButton',
                 background=[('active', self.highlight_bg)],
                 foreground=[('active', self.highlight_fg)])
        
        style.configure('TCombobox', 
                       fieldbackground=self.text_bg,
                       background=self.bg_color,
                       foreground=self.fg_color,
                       selectbackground=self.select_bg,
                       selectforeground=self.select_fg)
        
        # Configure text area
        self.text_area.configure(
            bg=self.text_bg,
            fg=self.text_fg,
            insertbackground=self.fg_color,
            selectbackground=self.select_bg,
            selectforeground=self.select_fg,
            inactiveselectbackground=self.select_bg
        )
        
        # Configure scrollbar
        scroll_style = ttk.Style()
        scroll_style.configure('Vertical.TScrollbar', 
                             background=self.bg_color,
                             troughcolor=self.bg_color,
                             bordercolor=self.bg_color,
                             arrowcolor=self.fg_color)
        
        # Configure status bar
        self.status_bar.configure(background=self.status_bg, foreground=self.status_fg)
    
    def setup_ui(self):
        """Initialize the user interface"""
        self.window = tk.Toplevel(self.root)
        self.window.title('Log Viewer')
        self.window.geometry('900x600')
        self.window.minsize(700, 400)
        
        # Create a custom font
        default_font = tkfont.nametofont('TkDefaultFont')
        self.custom_font = default_font.copy()
        self.custom_font.configure(size=10)
        
        # Top frame for controls
        control_frame = ttk.Frame(self.window, style='TFrame')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Log file selection
        ttk.Label(control_frame, text='Log File:').pack(side=tk.LEFT, padx=5)
        self.file_var = tk.StringVar()
        self.file_dropdown = ttk.Combobox(
            control_frame, 
            textvariable=self.file_var,
            state='readonly',
            width=40,
            style='TCombobox'
        )
        self.file_dropdown.pack(side=tk.LEFT, padx=5)
        self.file_dropdown.bind('<<ComboboxSelected>>', self.on_file_select)
        
        # Log level filter
        ttk.Label(control_frame, text='Log Level:').pack(side=tk.LEFT, padx=(20, 5))
        self.level_var = tk.StringVar(value='ALL')
        self.level_dropdown = ttk.Combobox(
            control_frame,
            textvariable=self.level_var,
            values=self.log_levels,
            state='readonly',
            width=10,
            style='TCombobox'
        )
        self.level_dropdown.pack(side=tk.LEFT, padx=5)
        self.level_dropdown.bind('<<ComboboxSelected>>', self.on_level_select)
        
        # Refresh button
        refresh_btn = ttk.Button(
            control_frame,
            text='⟳',
            width=3,
            command=self.refresh_logs,
            style='TButton'
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Log text area with scrollbar
        text_frame = ttk.Frame(self.window, style='TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=self.custom_font,
            state=tk.DISABLED,
            relief=tk.FLAT,
            bd=0,
            padx=5,
            pady=5
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value='Ready')
        self.status_bar = ttk.Label(
            self.window,
            textvariable=self.status_var,
            relief=tk.FLAT,
            anchor=tk.W,
            style='TLabel'
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)
        
        # Bottom buttons
        btn_frame = ttk.Frame(self.window, style='TFrame')
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        save_btn = ttk.Button(
            btn_frame,
            text='Save As...',
            command=self.save_log,
            style='TButton'
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = ttk.Button(
            btn_frame,
            text='Close',
            command=self.window.destroy,
            style='TButton'
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ttk.Button(
            btn_frame,
            text='Clear Log',
            command=self.clear_log
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configure tags for different log levels
        self.text_area.tag_configure('DEBUG', foreground='gray')
        self.text_area.tag_configure('INFO', foreground='black')
        self.text_area.tag_configure('WARNING', foreground='orange')
        self.text_area.tag_configure('ERROR', foreground='red')
        self.text_area.tag_configure('CRITICAL', foreground='white', background='red')
        
        # Make the window modal
        self.window.transient(self.root)
        self.window.grab_set()
    
    def load_log_files(self):
        """Load available log files from the logs directory"""
        log_files = sorted(
            [f for f in self.log_dir.glob('*.log') if f.is_file()],
            key=os.path.getmtime,
            reverse=True
        )
        
        if not log_files:
            self.status_var.set('No log files found in logs directory')
            return
            
        self.file_dropdown['values'] = [f.name for f in log_files]
        self.current_log_file = log_files[0]
        self.load_log_content()
        
    def load_log_content(self):
        """Load the content of the selected log file with the current filters"""
        if not self.current_log_file or not self.current_log_file.exists():
            self.status_var.set('Log file not found')
            return
            
        try:
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            
            with open(self.current_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    self._process_log_line(line.strip())
                    
            self.status_var.set(f'Loaded {self.current_log_file.name}')
            self.text_area.see(tk.END)
            
        except Exception as e:
            self.status_var.set(f'Error loading log file: {str(e)}')
        finally:
            self.text_area.config(state=tk.DISABLED)
            
    def _process_log_line(self, line):
        """Process a single log line and add it to the text area with appropriate formatting"""
        if not line.strip():
            return
            
        log_level = 'INFO'  # Default log level
        
        # Try to extract log level from the line
        for level in self.log_levels[1:]:  # Skip 'ALL'
            if f'[{level}]' in line:
                log_level = level
                break
                
        # Skip if not matching the selected level filter
        if self.current_level != 'ALL' and log_level != self.current_level:
            return
            
        # Add line with appropriate formatting
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, line + '\n', (log_level,))
        self.text_area.config(state=tk.DISABLED)
                
        # Skip if not matching the selected level filter
        if self.current_level != 'ALL' and log_level != self.current_level:
            return
            
        # Add line with appropriate formatting
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, line, (log_level,))
        self.text_area.config(state=tk.DISABLED)
    
    def on_file_select(self, event):
        """Handle log file selection from dropdown"""
        selected_file = self.file_var.get()
        if selected_file:
            self.current_log_file = self.log_dir / selected_file
            self.load_log_content()
    
    def on_level_select(self, event):
        """Handle log level filter selection"""
        self.current_level = self.level_var.get()
        self.load_log_content()
    
    def refresh_logs(self):
        """Refresh the log file list and content"""
        self.load_log_files()
        self.status_var.set('Logs refreshed')
    
    def save_log(self):
        """Save the current log view to a file"""
        if not self.current_log_file:
            return
            
        default_name = f"log_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
        )
        
        if file_path:
            try:
                with open(self.current_log_file, 'r', encoding='utf-8') as src, \
                     open(file_path, 'w', encoding='utf-8') as dest:
                    dest.write(src.read())
                self.status_var.set(f'Saved log to {file_path}')
            except Exception as e:
                messagebox.showerror('Save Error', f'Failed to save log: {str(e)}')
    
    def clear_log(self):
        """Clear the current log file"""
        if not self.current_log_file or not messagebox.askyesno(
            'Clear Log',
            'Are you sure you want to clear the current log file? This cannot be undone.'
        ):
            return
            
        try:
            with open(self.current_log_file, 'w', encoding='utf-8') as f:
                f.write('')
            self.load_log_content()
            self.status_var.set('Log file cleared')
        except Exception as e:
            messagebox.showerror('Clear Error', f'Failed to clear log: {str(e)}')

    @staticmethod
    def show_log(root):
        """Static method to show the log viewer dialog"""
        log_viewer = LogViewer(root)
        root.wait_window(log_viewer.window)
