import tkinter as tk
from tkinter import ttk, messagebox
import requests
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import importlib
import sys
from pathlib import Path
import os
import logging
import threading
from datetime import datetime, timedelta
import json

# Add script directory to path for module imports
script_dir = Path(__file__).parent.absolute()
sys.path.append(str(script_dir))

from script.icon_utils import get_icon_image, set_offline_mode
from script.version import get_version
from script.updates import check_for_updates
from script.about import About
from script.help import Help
from script.sponsor import Sponsor
from script.menu import create_menu_bar
from script.favorites_utils import FavoritesManager
from script.config_utils import ConfigManager
from script.translations import TRANSLATIONS
from script.translations_utils import TranslationsManager
from script.notifications import NotificationManager, check_severe_weather

# Import weather providers
from script.weather_providers import get_provider, get_available_providers

# ----------- LOGGING SETUP -----------
# Ensure logs directory exists
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True, parents=True)

# Create log file with timestamp
log_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = LOG_DIR / f'weather_app_{log_timestamp}.log'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logging.info(f'Logging to file: {LOG_FILE}')

# ----------- CONFIGURATION -----------
# API key will be loaded from config in __init__
API_KEY = None
BASE_URL = 'https://api.openweathermap.org/data/2.5/'
DEFAULT_CITY = 'London'

# ----------- THEMES -----------
from script.themes import LIGHT_THEME, DARK_THEME, apply_ttk_theme

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Weather App')
        self.root.geometry('600x800')  # Slightly larger for better layout
        self.root.resizable(True, True)
        
        # Set application icon
        try:
            icon_path = Path('assets/meteo.png')
            if icon_path.exists():
                self.root.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
        except Exception as e:
            logging.warning(f'Could not set application icon: {e}')

        # Setup config and data directories
        self.config_dir = Path.home() / '.weather_app'
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize notification system
        self.notification_manager = NotificationManager(self.config_dir)
        
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.units = self.config_manager.get('units', 'metric')
        
        # Check for updates on startup (in a separate thread to avoid blocking the UI)
        self.check_updates_on_startup()
        
        self.language = self.config_manager.get('language', 'en')
        self.api_key = self.config_manager.get('api_key') or os.environ.get('OPENWEATHER_API_KEY', 'YOUR_API_KEY_HERE')
        self.theme = self.config_manager.get('theme', 'dark')
        self.city_var = tk.StringVar(value=DEFAULT_CITY)
        self.translations_manager = TranslationsManager(TRANSLATIONS, default_lang=self.language)
        
        # Set offline mode if no internet
        try:
            requests.head('http://www.google.com', timeout=5)
            set_offline_mode(False)
        except requests.RequestException:
            set_offline_mode(True)
            messagebox.showwarning(
                'Offline Mode',
                'Internet connection not available. Running in offline mode with limited functionality.'
            )
        
        # Initialize weather provider
        self.weather_provider_name = self.config_manager.get('weather_provider', 'openweathermap')
        try:
            self.weather_provider = get_provider(
                self.weather_provider_name,
                api_key=self.api_key,
                units=self.units,
                language=self.language
            )
            logging.info(f"Using weather provider: {self.weather_provider_name}")
        except Exception as e:
            logging.error(f"Failed to initialize weather provider {self.weather_provider_name}: {e}")
            # Fall back to OpenWeatherMap if the configured provider fails
            self.weather_provider = OpenWeatherMapProvider(
                api_key=self.api_key,
                units=self.units,
                language=self.language
            )
            self.weather_provider_name = 'openweathermap'
            logging.info("Falling back to OpenWeatherMap provider")
        
        # Initialize alerts data
        self.alerts = []

        # Initialize UI
        self._build_ui()
        
        # Initialize menu bar
        self.menu_bar = create_menu_bar(self.root, self)
        
        # Apply theme to all widgets
        self.apply_theme()
        
        # Configure alert styles
        style = ttk.Style()
        style.configure('Alert.TFrame', background='#fff3cd' if self.theme == 'light' else '#856404')
        style.configure('Alert.TLabel', background='#fff3cd' if self.theme == 'light' else '#856404',
                      foreground='#000' if self.theme == 'light' else '#fff')
        self.refresh_weather()
        self.city_var.trace_add('write', lambda *args: self._update_fav_btn())

    def check_updates_on_startup(self):
        """Check for updates when the app starts."""
        def check():
            try:
                check_for_updates(self.root, get_version())
            except Exception as e:
                logging.error(f"Error checking for updates: {e}")
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=check, daemon=True).start()
    
    def check_for_updates(self):
        """Manually check for updates from the menu."""
        def check():
            try:
                check_for_updates(self.root, get_version(), force_check=True)
            except Exception as e:
                logging.error(f"Error checking for updates: {e}")
                messagebox.showerror("Update Error", f"Failed to check for updates: {e}", parent=self.root)
        
        threading.Thread(target=check, daemon=True).start()

    def _change_language(self, language):
        """Change the application language"""
        if language != self.language:
            self.language = language
            # Update translations
            self._update_ui_texts()
            # Save preference
            self.config_manager.set('language', language)
            self.config_manager.save()
            logging.info(f'Language changed to: {language}')
    
    def _update_ui_texts(self):
        """Update all UI texts based on current language"""
        _ = self.translations_manager.t
        
        # Update window title
        self.root.title(_('Weather App', self.language))
        
        # Update search placeholder
        if hasattr(self, 'city_entry'):
            current_text = self.city_entry.get()
            if current_text in ['Enter city name...', _('Enter city name...', self.language)]:
                self.city_entry.delete(0, 'end')
                self.city_entry.insert(0, _('Enter city name...', self.language))
        
        # Update button texts, labels, etc.
        if hasattr(self, 'search_btn'):
            self.search_btn.config(text=f"🔍 {_('Search', self.language)}")
        
        # Update status bar if needed
        if hasattr(self, 'status_var'):
            current_status = self.status_var.get()
            if current_status in ['Ready', _('Ready', self.language)]:
                self.status_var.set(_('Ready', self.language))
            elif current_status in ['Loading...', _('Loading...', self.language)]:
                self.status_var.set(_('Loading...', self.language))
            
    def _build_ui(self):
        # Configure styles
        style = ttk.Style()
        
        # Theme colors
        bg_color = '#f0f0f0' if self.theme == 'light' else '#2c3e50'
        fg_color = '#000000' if self.theme == 'light' else '#ffffff'
        accent_color = '#3498db'
        
        # Base styles
        style.configure('.', background=bg_color, foreground=fg_color, font=('Segoe UI', 10))
        
        # Alert styles
        style.configure('Alert.TFrame', 
                       background='#fff3cd' if self.theme == 'light' else '#856404',
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Alert.TLabel', 
                       background='#fff3cd' if self.theme == 'light' else '#856404',
                       foreground='#000' if self.theme == 'light' else '#fff')
        
        # Card styles
        style.configure('Card.TLabelframe', 
                       borderwidth=1, 
                       relief='solid', 
                       padding=10,
                       background=bg_color)
        
        style.configure('Card.TLabelframe.Label', 
                       font=('Segoe UI', 10, 'bold'),
                       background=bg_color,
                       foreground=fg_color)
        
        # Button styles
        style.configure('Accent.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       background=accent_color,
                       foreground='white',
                       borderwidth=0,
                       padding=5)
        
        style.map('Accent.TButton',
                 background=[('active', '#2980b9'), ('pressed', '#2472a4')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        
        # Link button style
        style.configure('Link.TButton',
                      font=('Segoe UI', 9, 'underline'),
                      foreground=accent_color,
                      borderwidth=0,
                      padding=0)
        
        style.map('Link.TButton',
                 foreground=[('active', '#2980b9'), ('pressed', '#2472a4')])
        
        # Configure root window background
        self.root.configure(background=bg_color)
        
        # Main frame with scrollbar
        main_canvas = tk.Canvas(self.root)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        main_canvas.configure(yscrollcommand=scrollbar.set)
        main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox('all')))
        
        self.main_frame = ttk.Frame(main_canvas, padding="10")
        main_canvas.create_window((0, 0), window=self.main_frame, anchor='nw')
        
        # Configure mouse wheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Search frame with improved styling
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # City input with search button
        self.city_var = tk.StringVar()
        
        # Create a frame for the search bar with rounded corners
        search_bar_frame = ttk.Frame(header_frame, style='Card.TLabelframe')
        search_bar_frame.pack(fill=tk.X, pady=5)
        
        # Search icon and entry frame
        search_entry_frame = ttk.Frame(search_bar_frame)
        search_entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        # Search icon
        search_icon = ttk.Label(search_entry_frame, text='🔍', font=('Segoe UI', 12))
        search_icon.pack(side=tk.LEFT, padx=(5, 5))
        
        # Configure style for the entry
        style.configure('Search.TEntry', padding=5)
        
        # Search button with improved styling
        search_btn = ttk.Button(
            search_bar_frame,
            text='Search',
            style='Accent.TButton',
            command=self.refresh_weather
        )
        search_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # City entry with placeholder
        city_entry = ttk.Entry(
            search_bar_frame,
            textvariable=self.city_var,
            font=('Segoe UI', 12),
            style='Search.TEntry'
        )
        city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        city_entry.bind('<Return>', lambda e: self.refresh_weather())
        
        # Add placeholder text functionality
        def on_entry_click(event):
            if city_entry.get() == 'Enter city name...':
                city_entry.delete(0, 'end')
                city_entry.config(foreground='black')
        
        def on_focus_out(event):
            if city_entry.get() == '':
                city_entry.insert(0, 'Enter city name...')
                city_entry.config(foreground='grey')
        
        city_entry.insert(0, 'Enter city name...')
        city_entry.config(foreground='grey')
        city_entry.bind('<FocusIn>', on_entry_click)
        city_entry.bind('<FocusOut>', on_focus_out)
        
        # Store the entry widget for later use
        self.city_entry = city_entry
        
        # Store the search button for later reference
        self.search_btn = search_btn
        
        # Add status bar at the bottom
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5,
            style='Status.TLabel'
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure status bar style
        style.configure('Status.TLabel',
                      background='#e0e0e0' if self.theme == 'light' else '#34495e',
                      foreground='#000000' if self.theme == 'light' else '#ffffff',
                      relief=tk.SUNKEN,
                      anchor=tk.W,
                      padding=5)
        
        # Pack the entry after the search button
        city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Define entry styles
        style.configure('Custom.TEntry', 
                      fieldbackground='white' if self.theme == 'light' else '#2c3e50',
                      foreground='black' if self.theme == 'light' else 'white',
                      borderwidth=1,
                      relief='solid')
        style.map('Focused.TEntry',
                 fieldbackground=[('focus', 'white' if self.theme == 'light' else '#34495e')])

        # Right side - Settings and actions
        settings_frame = ttk.Frame(header_frame)
        settings_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Theme toggle button with icon
        theme_btn = ttk.Button(settings_frame, text='🌓', 
                             command=self.toggle_theme,
                             style='Toolbutton',
                             width=3)
        theme_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Configure style for dropdowns
        style.configure('TMenubutton', 
                      padding=(10, 4),
                      font=('Segoe UI', 9))
        
        # Language dropdown with icon
        lang_frame = ttk.Frame(settings_frame)
        lang_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(lang_frame, text='🌐', 
                 font=('Segoe UI', 12)).pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value=self.language)
        langs = self.translations_manager.available_languages()
        self.lang_menu = ttk.OptionMenu(lang_frame, self.language_var, self.language, 
                                      *langs, command=self._change_language)
        self.lang_menu.pack(side=tk.LEFT)
        
        # Units dropdown with icon
        units_frame = ttk.Frame(settings_frame)
        units_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(units_frame, text='📏', 
                 font=('Segoe UI', 12)).pack(side=tk.LEFT)
        self.units_var = tk.StringVar(value=self.units)
        unit_display = {'metric': '°C, m/s', 'imperial': '°F, mph'}
        self.units_menu = ttk.OptionMenu(units_frame, self.units_var, 
                                       unit_display[self.units], 
                                       *[(unit_display[u], u) for u in ['metric', 'imperial']],
                                       command=lambda x, u=self.units_var: self._change_units(u.get()))
        self.units_menu.pack(side=tk.LEFT)
        
        # Favorites section
        fav_frame = ttk.Frame(settings_frame)
        fav_frame.pack(side=tk.RIGHT, padx=5)
        
        # Favorites dropdown with icon
        fav_dropdown_frame = ttk.Frame(fav_frame)
        fav_dropdown_frame.pack(side=tk.LEFT)
        ttk.Label(fav_dropdown_frame, text='⭐', 
                 font=('Segoe UI', 12)).pack(side=tk.LEFT)
        self.favorites_manager = FavoritesManager()
        self.favorites = self.favorites_manager.get_favorites()
        self.favorite_var = tk.StringVar(value='Favorites')
        self.fav_menu = ttk.OptionMenu(fav_dropdown_frame, self.favorite_var, 
                                     self.translations_manager.t('favorites', self.language), 
                                     *self.favorites, command=self._select_favorite)
        self.fav_menu.pack(side=tk.LEFT)
        
        # Add/Remove Favorite button with icon
        self.fav_btn = ttk.Button(fav_frame, text='', width=3, 
                                command=self._toggle_favorite,
                                style='Toolbutton')
        self.fav_btn.pack(side=tk.LEFT, padx=(5, 0))
        self._update_fav_btn()
        
        # Search button with icon
        search_btn = ttk.Button(search_entry_frame, 
                              text=f"🔍 {self.translations_manager.t('search', self.language)}", 
                              command=self.refresh_weather, 
                              style='Accent.TButton')
        search_btn.pack(side=tk.RIGHT, padx=(0, 5))

        # Current weather panel with improved styling
        self.current_panel = ttk.LabelFrame(
            self.main_frame, 
            text=f" {self.translations_manager.t('current_weather', self.language).upper()} ",
            padding=15,
            style='Card.TLabelframe'
        )
        self.current_panel.pack(fill=tk.X, pady=(0, 20))
        
        # Main weather info
        main_info_frame = ttk.Frame(self.current_panel)
        main_info_frame.pack(fill=tk.X, pady=5)
        
        # Weather icon (larger)
        icon_frame = ttk.Frame(main_info_frame)
        icon_frame.pack(side=tk.LEFT, padx=(0, 20))
        self.weather_icon_label = ttk.Label(icon_frame)
        self.weather_icon_label.pack()
        
        # Temperature and description
        text_frame = ttk.Frame(main_info_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Temperature with unit
        temp_frame = ttk.Frame(text_frame)
        temp_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.temp_label = ttk.Label(
            temp_frame, 
            font=('Segoe UI', 48, 'bold'),
            foreground='#2c3e50'
        )
        self.temp_label.pack(side=tk.LEFT)
        
        # Weather description
        self.desc_label = ttk.Label(
            text_frame,
            font=('Segoe UI', 18),
            foreground='#34495e'
        )
        self.desc_label.pack(anchor='w', pady=(0, 10))
        
        # Location and date
        self.location_label = ttk.Label(
            text_frame,
            font=('Segoe UI', 12, 'bold'),
            foreground='#7f8c8d'
        )
        self.location_label.pack(anchor='w')
        
        # Additional weather info in a frame
        metrics_frame = ttk.Frame(self.current_panel)
        metrics_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Create styled frames for each metric
        def create_metric_frame(parent, icon, value, unit, label):
            frame = ttk.Frame(parent, style='Metric.TFrame')
            
            # Icon
            icon_label = ttk.Label(
                frame, 
                text=icon, 
                font=('Segoe UI', 14),
                foreground='#3498db'
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 8))
            
            # Value and unit
            value_frame = ttk.Frame(frame)
            value_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            value_label = ttk.Label(
                value_frame, 
                text=f"{value}{unit}",
                font=('Segoe UI', 16, 'bold'),
                foreground='#2c3e50'
            )
            value_label.pack(anchor='w')
            
            # Label
            label_label = ttk.Label(
                value_frame,
                text=label,
                font=('Segoe UI', 9),
                foreground='#7f8c8d'
            )
            label_label.pack(anchor='w')
            
            return frame
            
        # These will be updated in _update_current_weather
        self.humidity_metric = create_metric_frame(metrics_frame, '💧', '--', '%', 'Humidity')
        self.humidity_metric.pack(side=tk.LEFT, padx=(0, 20))
        
        self.wind_metric = create_metric_frame(metrics_frame, '💨', '--', ' m/s', 'Wind')
        self.wind_metric.pack(side=tk.LEFT, padx=(0, 20))
        
        self.pressure_metric = create_metric_frame(metrics_frame, '📊', '--', ' hPa', 'Pressure')
        self.pressure_metric.pack(side=tk.LEFT, padx=(0, 20))
        
        self.feels_like_metric = create_metric_frame(metrics_frame, '🌡️', '--', '°', 'Feels Like')
        self.feels_like_metric.pack(side=tk.LEFT)

        # Forecast panel with improved styling
        self.forecast_panel = ttk.LabelFrame(
            self.main_frame, 
            text=f" {self.translations_manager.t('forecast', self.language).upper()} ",
            padding=15,
            style='Card.TLabelframe'
        )
        self.forecast_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Container for forecast cards
        forecast_container = ttk.Frame(self.forecast_panel)
        forecast_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create forecast cards
        self.forecast_frames = []
        for i in range(5):
            # Card frame
            card = ttk.Frame(
                forecast_container, 
                style='ForecastCard.TFrame',
                padding=12
            )
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Day of week
            day_frame = ttk.Frame(card)
            day_frame.pack(fill=tk.X, pady=(0, 10))
            
            day_label = ttk.Label(
                day_frame,
                text='--',
                font=('Segoe UI', 11, 'bold'),
                foreground='#2c3e50'
            )
            day_label.pack(side=tk.LEFT)
            
            # Date
            date_label = ttk.Label(
                day_frame,
                text='',
                font=('Segoe UI', 9),
                foreground='#7f8c8d'
            )
            date_label.pack(side=tk.RIGHT)
            
            # Weather icon
            icon_label = ttk.Label(card)
            icon_label.pack(pady=5)
            
            # Temperature range
            temp_frame = ttk.Frame(card)
            temp_frame.pack(fill=tk.X, pady=(5, 0))
            
            temp_high = ttk.Label(
                temp_frame,
                text='--°',
                font=('Segoe UI', 14, 'bold'),
                foreground='#e74c3c'  # Red for high temp
            )
            temp_high.pack(side=tk.LEFT, expand=True)
            
            temp_low = ttk.Label(
                temp_frame,
                text='--°',
                font=('Segoe UI', 14, 'bold'),
                foreground='#3498db'  # Blue for low temp
            )
            temp_low.pack(side=tk.RIGHT, expand=True)
            
            # Weather description
            desc_label = ttk.Label(
                card,
                text='--',
                font=('Segoe UI', 9),
                foreground='#7f8c8d',
                wraplength=100,
                justify='center'
            )
            desc_label.pack(pady=(5, 0))
            
            # Additional info (humidity, wind, etc.)
            details_frame = ttk.Frame(card)
            details_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Humidity
            humidity_frame = ttk.Frame(details_frame)
            humidity_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(
                humidity_frame,
                text='💧',
                font=('Segoe UI', 9)
            ).pack(side=tk.LEFT, padx=(0, 5))
            
            humidity_value = ttk.Label(
                humidity_frame,
                text='--%',
                font=('Segoe UI', 8),
                foreground='#7f8c8d'
            )
            humidity_value.pack(side=tk.LEFT)
            
            # Wind
            wind_frame = ttk.Frame(details_frame)
            wind_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(
                wind_frame,
                text='💨',
                font=('Segoe UI', 9)
            ).pack(side=tk.LEFT, padx=(0, 5))
            
            wind_value = ttk.Label(
                wind_frame,
                text='-- m/s',
                font=('Segoe UI', 8),
                foreground='#7f8c8d'
            )
            wind_value.pack(side=tk.LEFT)
            
            self.forecast_frames.append({
                'frame': card,
                'day': day_label,
                'date': date_label,
                'icon': icon_label,
                'temp_high': temp_high,
                'temp_low': temp_low,
                'desc': desc_label,
                'humidity': humidity_value,
                'wind': wind_value
            })

        # Responsive resizing
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

    def apply_theme(self):
        theme = DARK_THEME if getattr(self, 'theme', 'dark') == 'dark' else LIGHT_THEME
        self.root.configure(bg=theme['bg'])
        style = ttk.Style()
        apply_ttk_theme(style, theme)
        
        # Configure additional styles based on theme
        bg_color = theme['bg']
        fg_color = theme['fg']
        accent_color = '#3498db' if theme == LIGHT_THEME else '#5dade2'
        entry_bg = '#ffffff' if theme == LIGHT_THEME else '#2c3e50'
        entry_fg = '#000000' if theme == LIGHT_THEME else '#ffffff'
        card_bg = '#ffffff' if theme == LIGHT_THEME else '#2c3e50'
        card_border = '#e0e0e0' if theme == LIGHT_THEME else '#3d4f5e'
        
        # Configure card style
        style.configure('Card.TLabelframe', 
                      background=card_bg,
                      borderwidth=1,
                      relief='solid',
                      borderradius=8)
        style.configure('Card.TLabelframe.Label', 
                      background=card_bg, 
                      foreground=fg_color,
                      font=('Segoe UI', 9, 'bold'))
        
        # Configure accent button style
        style.configure('Accent.TButton', 
                      background=accent_color, 
                      foreground='white',
                      font=('Segoe UI', 9, 'bold'),
                      borderwidth=0,
                      padding=8)
        style.map('Accent.TButton',
                background=[('active', '#2980b9' if theme == LIGHT_THEME else '#7fb3d5')])
        
        # Entry styles
        style.configure('Custom.TEntry', 
                      fieldbackground=entry_bg,
                      foreground=entry_fg,
                      borderwidth=1,
                      relief='solid',
                      padding=5)
        style.map('Focused.TEntry',
                fieldbackground=[('focus', '#ffffff' if theme == LIGHT_THEME else '#34495e')])
        
        # Metric frame style
        style.configure('Metric.TFrame', 
                      background=card_bg,
                      borderwidth=0,
                      padding=(10, 8))
        
        # Configure toolbutton style
        style.configure('Toolbutton',
                      padding=5,
                      borderwidth=0)
                      
        # Forecast card style
        style.configure('ForecastCard.TFrame',
                      background=card_bg,
                      borderwidth=1,
                      relief='solid',
                      borderradius=6)
                      
        # Hover effect for forecast cards
        if theme == LIGHT_THEME:
            style.map('ForecastCard.TFrame', background=[('active', '#f8f9fa')])
        else:
            style.map('ForecastCard.TFrame', background=[('active', '#34495e')])
        
        # Apply theme to existing widgets if they exist
        if hasattr(self, 'city_entry'):
            self.city_entry.configure(style='Custom.TEntry')
            if self.city_entry == self.root.focus_get():
                self.city_entry.configure(style='Focused.TEntry')
        
        # Update metric widgets if they exist
        if hasattr(self, 'humidity_metric'):
            for widget in [self.humidity_metric, self.wind_metric, 
                         self.pressure_metric, self.feels_like_metric]:
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        # Handle font configuration safely
                        font = child.cget('font')
                        # Handle different font formats (string or font object)
                        if isinstance(font, str):
                            is_bold = 'bold' in font.lower()
                        else:
                            # For font objects, we'll assume it's not bold for theming
                            is_bold = False
                        
                        if is_bold:
                            child.config(foreground=fg_color)
                        else:
                            child.config(foreground='#7f8c8d')

    def toggle_theme(self):
        self.theme = 'dark' if getattr(self, 'theme', 'light') == 'light' else 'light'
        self.config_manager.set('theme', self.theme)
        self.config_manager.save()
        self.apply_theme()
        try:
            city = self.city_var.get()
            current_weather, forecast = self._fetch_weather_data(city)
            if current_weather and forecast:
                self._update_current_weather(current_weather)
                self._update_forecast(forecast)
                self._update_fav_btn()
        except Exception as e:
            logging.error(f'Could not fetch weather for city {city}: {e}', exc_info=True)
            messagebox.showerror('Error', f'Could not fetch weather: {e}')

    def refresh_weather(self, event=None):
        """Refresh weather data for the current city"""
        city = self.city_var.get().strip()
        _ = self.translations_manager.t  # Shortcut for translation function
        
        # Check for empty or placeholder text
        placeholder_texts = [
            'Enter city name...',
            _('enter_city_name'),  # Uses default language from translations_manager
            _('enter_city_name', 'en')  # Fallback to English
        ]
        
        if not city or city in placeholder_texts:
            messagebox.showwarning(
                _('warning'),
                _('enter_city_warning')
            )
            return
            
        # Additional validation for city name (basic check for alphabetic characters and spaces)
        if not all(c.isalpha() or c.isspace() or c in "-'" for c in city):
            messagebox.showwarning(
                _('warning'),
                _('invalid_city_warning')
            )
            return

        # Initialize status_var if it doesn't exist
        if not hasattr(self, 'status_var'):
            self.status_var = tk.StringVar(value=_('Loading weather data...', self.language))
        else:
            self.status_var.set(_('Loading weather data...', self.language))
        
        self.root.update_idletasks()  # Force UI update

        try:
            # Get weather data and alerts in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                # Get both current weather and forecast in one call
                weather_future = executor.submit(self._fetch_weather_data, city)
                # Get alerts in parallel if supported
                alerts_future = None
                if hasattr(self.weather_provider, 'get_alerts'):
                    alerts_future = executor.submit(self.weather_provider.get_alerts, city)

                # Get weather data
                weather_data = weather_future.result()
                current_weather, forecast_data = weather_data if weather_data else (None, None)
                
                # Get alerts if supported
                alerts_data = alerts_future.result() if alerts_future else []

            if current_weather is None or forecast_data is None:
                raise Exception('Failed to fetch weather data')

            # Update UI with the new data
            self._update_current_weather(current_weather)
            self._update_forecast(forecast_data)
            self._update_alerts(alerts_data)

            # Check for severe conditions that should trigger notifications
            self._check_severe_conditions()
            
            # Update status with last updated time
            now = datetime.now().strftime("%H:%M:%S")
            self.status_var.set(_('Ready - Last updated: {time}', self.language).format(time=now))

        except Exception as e:
            logging.error(f'Error refreshing weather: {e}')
            messagebox.showerror(
                _('error'),
                f"{_('fetch_error')}: {str(e)}"
            )
            self.status_var.set(_('Error: Failed to fetch weather data', self.language))
        
        # Removed settings.wait_window() as it was causing an error

    def _fetch_weather_data(self, location):
        """Fetch both current weather and forecast data for a location.
        
        Args:
            location (str): City name or coordinates (lat,lon)
            
        Returns:
            tuple: (current_data, forecast_data) or (None, None) on error
        """
        try:
            # Fetch current weather
            current_data = self.weather_provider.get_current_weather(location)
            
            # Fetch forecast (5 days)
            forecast_data = self.weather_provider.get_forecast(location, days=5)
            
            return current_data, forecast_data
        except Exception as e:
            logging.error(f"Error fetching weather data from {self.weather_provider_name}: {e}")
            # Try to show a translated error message
            error_msg = self.translations_manager.t('api_error', self.language) or str(e)
            messagebox.showerror(
                self.translations_manager.t('error', self.language) or "Error",
                f"{self.translations_manager.t('api_error', self.language)}: {str(e)}"
            )
            return None, None

    def _fetch_alerts(self, location):
        """Fetch weather alerts for a location.
        
        Args:
            location (str): City name or coordinates (lat,lon)
        """
        try:
            if hasattr(self.weather_provider, 'get_alerts'):
                alerts = self.weather_provider.get_alerts(location)
                logging.info(f"Fetched {len(alerts) if alerts else 0} alerts from {self.weather_provider_name}")
                self._update_alerts(alerts or [])
            else:
                logging.info(f"Provider {self.weather_provider_name} does not support alerts")
                self._update_alerts([])
        except Exception as e:
            logging.error(f'Error fetching alerts from {self.weather_provider_name}: {e}', exc_info=True)
            self._update_alerts([])

    def _update_current_weather(self, data):
        try:
            # Store for later use (e.g., notifications)
            self.current_weather_data = data
            
            # Extract weather data
            temp = int(round(data['main']['temp']))
            description = data['weather'][0]['description'].capitalize()
            icon_code = data['weather'][0]['icon']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            pressure = data['main']['pressure']
            feels_like = int(round(data['main']['feels_like']))
            visibility = data.get('visibility', 0) / 1000  # Convert meters to km
            city = data['name']
            country = data['sys'].get('country', '')
            
            # Get weather icon
            icon_img = get_icon_image(icon_code, size=(128, 128))
            
            # Update UI
            self.temp_label.config(text=f"{temp}°")
            self.desc_label.config(text=description)
            
            if icon_img:
                self.weather_icon_label.config(image=icon_img)
                self.weather_icon_label.image = icon_img
                
            # Update location label with city and country
            location_text = f"{city}"
            if country:
                location_text += f", {country}"
            self.location_label.config(text=location_text)
            
            # Update metrics using the helper method
            self._update_metric(self.humidity_metric, f"{humidity}%", 'Humidity')
            self._update_metric(self.wind_metric, f"{wind_speed} {'m/s' if self.units == 'metric' else 'mph'}", 'Wind')
            self._update_metric(self.pressure_metric, f"{pressure} hPa", 'Pressure')
            self._update_metric(self.feels_like_metric, f"{feels_like}°", 'Feels Like')
            
            # Last updated time is now handled in refresh_weather
            
            # Check for severe weather conditions
            self._check_severe_weather()
            
        except Exception as e:
            logging.error(f'Error updating current weather: {e}', exc_info=True)

    def _update_metric(self, metric_frame, value, label):
        """Helper method to update a metric frame with new values"""
        # Find the value label (first label in the value frame)
        for child in metric_frame.winfo_children():
            if isinstance(child, ttk.Frame):  # This is the value frame
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Label):
                        try:
                            # Safely get font info and check if it's bold
                            font_info = subchild.cget('font')
                            is_bold = False
                            
                            # Handle different font formats
                            if hasattr(font_info, 'cget'):  # It's a Font object
                                is_bold = 'bold' in font_info.cget('weight').lower()
                            elif isinstance(font_info, str):  # It's a font string
                                is_bold = 'bold' in font_info.lower()
                            # For Tcl_Obj or other types, we'll skip the bold check
                            
                            if is_bold:
                                subchild.config(text=value)
                            else:
                                subchild.config(text=label)
                        except Exception as e:
                            # Fallback: update the text based on the label's current text
                            current_text = subchild.cget('text')
                            if current_text and len(current_text) < 5:  # Likely the value (short text)
                                subchild.config(text=value)
                            else:  # Likely the label
                                subchild.config(text=label)

    def _update_forecast(self, data):
        try:
            # Get daily forecasts (one per day at 12:00)
            daily_forecasts = [f for f in data['list'] if f['dt_txt'].endswith('12:00')]
            
            for i, forecast in enumerate(daily_forecasts[:5]):  # Show next 5 days
                if i >= len(self.forecast_frames):
                    break
                    
                dt = datetime.fromtimestamp(forecast['dt'])
                day_name = dt.strftime('%A')
                date_str = dt.strftime('%b %d')
                
                temp_max = int(round(forecast['main']['temp_max']))
                temp_min = int(round(forecast['main']['temp_min']))
                humidity = forecast['main']['humidity']
                wind_speed = forecast['wind']['speed']
                wind_unit = 'm/s' if self.units == 'metric' else 'mph'
                
                weather_desc = forecast['weather'][0]['description'].capitalize()
                icon_code = forecast['weather'][0]['icon']
                
                # Get weather icon
                icon_img = get_icon_image(icon_code, size=(64, 64))
                
                # Update UI
                day_info = self.forecast_frames[i]
                day_info['day'].config(text=day_name)
                day_info['date'].config(text=date_str)
                
                # Update the icon if available
                if icon_img:
                    day_info['icon'].config(image=icon_img)
                    day_info['icon'].image = icon_img
                    
                # Update other weather info
                day_info['temp_high'].config(text=f"{temp_max}°")
                day_info['temp_low'].config(text=f"{temp_min}°")
                day_info['desc'].config(text=weather_desc)
                day_info['humidity'].config(text=f"{humidity}%")
                day_info['wind'].config(text=f"{wind_speed} {wind_unit}")
                    
        except Exception as e:
            logging.error(f'Error updating forecast: {e}', exc_info=True)

    def _update_alerts(self, data):
        try:
            # Extract alert data
            alerts = data['alerts']
            
            # Update alert UI
            alert_frame = ttk.Frame(self.main_frame, style='Alert.TFrame')
            alert_frame.pack(fill=tk.X, pady=(10, 0))
            
            for alert in alerts:
                alert_label = ttk.Label(alert_frame, text=alert['description'], style='Alert.TLabel')
                alert_label.pack(fill=tk.X, padx=10, pady=5)
                
        except Exception as e:
            logging.error(f'Error updating alerts: {e}', exc_info=True)

    def _check_severe_conditions(self):
        try:
            # Check for severe weather conditions
            severe_conditions = check_severe_weather(self.alerts)
            
            # Show notification if severe conditions are found
            if severe_conditions:
                self.notification_manager.show_notification(
                    title=self.translations_manager.t('severe_weather', self.language),
                    message=severe_conditions
                )
        except Exception as e:
            logging.error(f'Error checking for severe conditions: {e}', exc_info=True)

    def _toggle_favorite(self):
        city = self.city_var.get().strip()
        if not city:
            return
        if self.favorites_manager.is_favorite(city):
            self.favorites_manager.remove_favorite(city)
        else:
            self.favorites_manager.add_favorite(city)
        self.favorites = self.favorites_manager.get_favorites()
        self._update_fav_menu()
        self._update_fav_btn()

    def _select_favorite(self, value):
        if value and value != 'Favorites':
            self.city_var.set(value)

    def _update_fav_menu(self):
        menu = self.fav_menu['menu']
        menu.delete(0, 'end')
        for fav in self.favorites:
            menu.add_command(label=fav, command=lambda v=fav: self._select_favorite(v))
        if not self.favorites:
            menu.add_command(label=self.translations_manager.t('no_favorites', self.language), command=lambda: None)

    def _update_fav_btn(self):
        city = self.city_var.get().strip()
        if self.favorites_manager.is_favorite(city):
            self.fav_btn.config(text=self.translations_manager.t('remove_favorite', self.language))
        else:
            self.fav_btn.config(text=self.translations_manager.t('add_favorite', self.language))


    def _show_settings(self):
        # Settings dialog for API key
        settings = tk.Toplevel(self.root)
        settings.title(self.translations_manager.t('settings', self.language))
        settings.geometry('500x600')
        settings.resizable(True, True)
        
        # Make the settings window modal
        settings.transient(self.root)
        settings.grab_set()
        
        # Main container with padding
        main_frame = ttk.Frame(settings, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas and a scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Weather Provider Frame
        provider_frame = ttk.LabelFrame(scrollable_frame, text="Weather Provider", padding="10 10 10 10")
        provider_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
        
        # Provider selection
        ttk.Label(provider_frame, text="Weather Data Source:").pack(anchor='w')
        
        # Get available providers
        available_providers = get_available_providers()
        provider_names = {
            'openweathermap': 'OpenWeatherMap',
            # Add more providers here as they're implemented
        }
        
        # Create a dropdown for provider selection
        self.provider_var = tk.StringVar(value=f"{self.weather_provider_name} - {provider_names.get(self.weather_provider_name, self.weather_provider_name.title())}")
        provider_menu = ttk.Combobox(
            provider_frame, 
            textvariable=self.provider_var,
            values=[f"{provider} - {provider_names.get(provider, provider.title())}" 
                   for provider in available_providers],
            state='readonly'
        )
        provider_menu.pack(fill=tk.X, pady=5)
        
        # API Key Frame
        api_frame = ttk.LabelFrame(scrollable_frame, text="API Settings", padding="10 10 10 10")
        api_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
        
        # API Key Entry
        api_key_frame = ttk.Frame(api_frame)
        api_key_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(api_key_frame, text="API Key:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.api_key_var = tk.StringVar(value=self.api_key if self.api_key != 'YOUR_API_KEY_HERE' else '')
        self.api_entry = ttk.Entry(
            api_key_frame,
            textvariable=self.api_key_var,
            width=40,
            show='*' if not hasattr(self, 'show_api_key') or not self.show_api_key.get() else ''
        )
        self.api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Toggle API key visibility
        if not hasattr(self, 'show_api_key'):
            self.show_api_key = tk.BooleanVar(value=False)
            
        def toggle_api_key_visibility():
            show = self.show_api_key.get()
            self.api_entry.config(show='' if show else '*')
        
        ttk.Checkbutton(
            api_key_frame,
            text="Show",
            variable=self.show_api_key,
            command=toggle_api_key_visibility
        ).pack(side=tk.LEFT, padx=5)
        
        # Validation status label
        self.validation_status = ttk.Label(api_frame, text="", foreground="red")
        self.validation_status.pack(anchor='w', pady=5)
        
        # Validate API Key Button
        def validate_api_key():
            api_key = self.api_key_var.get().strip()
            if not api_key or api_key == 'YOUR_API_KEY_HERE':
                self.validation_status.config(text="Please enter an API key", foreground="red")
                return
                
            self.validation_status.config(text="Validating API key...", foreground="blue")
            settings.update_idletasks()  # Force UI update
            
            def validate():
                try:
                    is_valid, message = self.weather_provider.validate_api_key(api_key)
                    if is_valid:
                        self.validation_status.after(0, lambda m=message: self.validation_status.config(
                            text=m or "API key is valid!",
                            foreground="green"
                        ))
                        self.api_key = api_key
                        self.weather_provider.update_config(api_key=api_key)
                        self.config_manager.set('api_key', api_key)
                        self.config_manager.write_config()  # Use write_config instead of save
                        save_btn.config(state=tk.NORMAL)
                    else:
                        self.validation_status.after(0, lambda m=message: self.validation_status.config(
                            text=m or "Invalid API key",
                            foreground="red"
                        ))
                except Exception as e:
                    error_msg = str(e)
                    logging.error(f"Error validating API key: {error_msg}")
                    self.validation_status.after(0, lambda msg=error_msg: self.validation_status.config(
                        text=f"Error: {msg}",
                        foreground="red"
                    ))
            
            threading.Thread(target=validate, daemon=True).start()
        
        ttk.Button(
            api_frame,
            text="Validate API Key",
            command=validate_api_key
        ).pack(anchor='w', pady=5)
        
        # Buttons Frame
        btn_frame = ttk.Frame(scrollable_frame, padding="10 10 10 10")
        btn_frame.pack(fill=tk.X, padx=5, pady=10)
        
        def save_settings():
            # Save weather provider if changed
            new_provider = self.provider_var.get().split(' - ')[0]
            if new_provider != self.weather_provider_name:
                try:
                    self.weather_provider = get_provider(
                        new_provider,
                        api_key=self.api_key_var.get().strip() or self.api_key,
                        units=self.units,
                        language=self.language
                    )
                    self.weather_provider_name = new_provider
                    self.config_manager.set('weather_provider', new_provider)
                    logging.info(f"Switched to weather provider: {new_provider}")
                except Exception as e:
                    logging.error(f"Failed to switch to provider {new_provider}: {e}")
                    messagebox.showerror("Error", f"Failed to switch weather provider: {e}")
                    return
            
            # Save API key if changed
            new_api_key = self.api_key_var.get().strip()
            if new_api_key and new_api_key != self.api_key:
                try:
                    is_valid, message = self.weather_provider.validate_api_key(new_api_key)
                    if not is_valid:
                        messagebox.showerror("Invalid API Key", message)
                        messagebox.showinfo("No Changes", "No changes were made.")
                        return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save settings: {e}")
                    return
                
                # Save the API key and update config
                self.api_key = new_api_key
                self.weather_provider.update_config(api_key=new_api_key)
                self.config_manager.set('api_key', new_api_key)
                
                # Update the API key in the config file
                self.config_manager.save()
                
                # Refresh weather data with new API key
                self.refresh_weather()
                
                # Update the save button state
                save_btn.config(state=tk.DISABLED)
                
                messagebox.showinfo("Success", "Settings saved successfully!")
            else:
                messagebox.showinfo("No Changes", "No changes were made.")
        
        # Save button (initially disabled until validation)
        save_btn = ttk.Button(btn_frame, 
                            text=self.translations_manager.t('save_settings', self.language),
                            command=save_settings,
                            state=tk.NORMAL)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Validate the current API key on startup if it exists
        if self.api_key and self.api_key != 'YOUR_API_KEY_HERE':
            settings.after(100, lambda: validate_api_key())
            
        # Language Selection Frame
        lang_frame = ttk.LabelFrame(scrollable_frame, text="Language", padding="10 10 10 10")
        lang_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
        
        # Get available languages from translations
        available_languages = self.translations_manager.available_languages()
        language_names = {
            'en': 'English',
            'it': 'Italiano',
            'es': 'Español',
            'pt': 'Português',
            'de': 'Deutsch',
            'fr': 'Français',
            'ru': 'Русский',
            'ar': 'العربية',
            'ja': '日本語'
        }
        
        # Current language
        current_lang = self.language
        
        # Language selection dropdown
        lang_var = tk.StringVar(value=current_lang)
        lang_menu = ttk.Combobox(lang_frame, textvariable=lang_var, state='readonly')
        lang_menu['values'] = [(f"{lang} - {language_names.get(lang, lang)}") for lang in available_languages]
        lang_menu.set(f"{current_lang} - {language_names.get(current_lang, current_lang)}")
        lang_menu.pack(fill=tk.X, pady=5)
        
        # Save button (initially disabled until validation)
        save_btn = ttk.Button(btn_frame, 
                            text=self.translations_manager.t('save_settings', self.language),
                            command=save_settings,
                            state=tk.NORMAL)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Validate the current API key on startup if it exists
        if self.api_key and self.api_key != 'YOUR_API_KEY_HERE':
            settings.after(100, lambda: validate_api_key())
            
        # Update save_settings to handle language change
        original_save_settings = save_settings
        def save_settings_with_lang():
            # Save language preference if changed
            selected_lang = lang_var.get().split(' - ')[0]
            if selected_lang != self.language:
                self._change_language(selected_lang)
                # Update provider language
                self.weather_provider.update_config(language=selected_lang)
                # Refresh weather data with new language
                self.refresh_weather()
            # Call original save_settings
            original_save_settings()
            
        # Replace the save_settings function
        save_settings = save_settings_with_lang
        
        # Cancel button
        ttk.Button(btn_frame, 
                  text="Cancel",
                  command=settings.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Center the window
        settings.update_idletasks()
        width = settings.winfo_width()
        height = settings.winfo_height()
        x = (settings.winfo_screenwidth() // 2) - (width // 2)
        y = (settings.winfo_screenheight() // 2) - (height // 2)
        settings.geometry(f'400x400+{x}+{y}')
        
        # Set focus to the API key entry
        api_entry.focus_set()
        
        ttk.Button(btn_frame, 
                  text=self.translations_manager.t('save', self.language),
                  command=save_settings).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(btn_frame, 
                  text=self.translations_manager.t('cancel', self.language),
                  command=settings.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Set focus to API key entry
        api_entry.focus_set()
        
        # Make the dialog modal
        settings.wait_window()


if __name__ == '__main__':
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
