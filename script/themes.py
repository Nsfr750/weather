# themes.py
"""
Centralized theme definitions and theming utilities for the Weather App.
"""

LIGHT_THEME = {
    'bg': '#f6caa5',
    'fg': '#222',
    'accent': '#1976d2',
    'panel': '#ffffff',
}

DARK_THEME = {
    'bg': '#23272f',
    'fg': '#f4f4f4',
    'accent': '#90caf9',
    'panel': '#2c313a',
}

def apply_ttk_theme(style, theme):
    """
    Apply the theme dictionary to ttk widgets using the given style object.
    """
    style.theme_use('clam')
    style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
    style.configure('TFrame', background=theme['bg'])
    style.configure('Main.TFrame', background=theme['bg'])
    style.configure('TButton', background=theme['accent'], foreground=theme['fg'])
    style.configure('TLabelframe', background=theme['panel'], foreground=theme['fg'])
    style.configure('TLabelframe.Label', background=theme['panel'], foreground=theme['fg'])
    style.configure('TEntry', fieldbackground=theme['panel'], foreground=theme['fg'])
