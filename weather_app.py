import tkinter as tk
from tkinter import ttk, messagebox
import requests
from weather_api import WeatherAPI
from PIL import Image, ImageTk
from icon_utils import get_icon_image
import io
import os
import logging
import threading

from version import get_version
from updates import check_for_updates
from about import About
from help import Help
from sponsor import Sponsor
from menu import create_menu_bar
from favorites_utils import FavoritesManager
from config_utils import ConfigManager
from translations import TRANSLATIONS
from translations_utils import TranslationsManager

# ----------- LOGGING SETUP -----------
LOG_FILE = 'weather_app.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ----------- CONFIGURATION -----------
# API key will be loaded from config in __init__
API_KEY = None
BASE_URL = 'https://api.openweathermap.org/data/2.5/'
DEFAULT_CITY = 'London'

# ----------- THEMES -----------
from themes import LIGHT_THEME, DARK_THEME, apply_ttk_theme

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Weather App')
        self.root.geometry('800x600')
        self.root.resizable(True, True)

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
        self.weather_api = WeatherAPI(
            api_key=self.api_key,
            units=self.units,
            language=self.language
        )

        # Initialize UI
        self._build_ui()
        
        # Initialize menu bar
        self.menu_bar = create_menu_bar(self.root, self)
        
        # Apply theme and initial data
        self.apply_theme()
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

    def _build_ui(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # City input
        city_frame = ttk.Frame(self.main_frame)
        city_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(city_frame, text=self.translations_manager.t('city', self.language)).pack(side=tk.LEFT)
        self.city_entry = ttk.Entry(city_frame, textvariable=self.city_var, width=20)
        self.city_entry.pack(side=tk.LEFT, padx=5)

        # Language dropdown
        self.language_var = tk.StringVar(value=self.language)
        langs = self.translations_manager.available_languages()
        self.lang_menu = ttk.OptionMenu(city_frame, self.language_var, self.language, *langs, command=self._change_language)
        self.lang_menu.pack(side=tk.LEFT, padx=5)

        # Units dropdown
        self.units_var = tk.StringVar(value=self.units)
        self.units_menu = ttk.OptionMenu(city_frame, self.units_var, self.units, 'metric', 'imperial', command=self._change_units)
        self.units_menu.pack(side=tk.LEFT, padx=5)

        # Favorites dropdown
        self.favorites_manager = FavoritesManager()
        self.favorites = self.favorites_manager.get_favorites()
        self.favorite_var = tk.StringVar(value='Favorites')
        self.fav_menu = ttk.OptionMenu(city_frame, self.favorite_var, self.translations_manager.t('favorites', self.language), *self.favorites, command=self._select_favorite)
        self.fav_menu.pack(side=tk.LEFT, padx=5)

        # Add/Remove Favorite button
        self.fav_btn = ttk.Button(city_frame, text=self.translations_manager.t('remove_favorite', self.language), width=3, command=self._toggle_favorite)
        self.fav_btn.pack(side=tk.LEFT, padx=2)
        self._update_fav_btn()

        ttk.Button(city_frame, text=self.translations_manager.t('search', self.language), command=self.refresh_weather).pack(side=tk.LEFT)
        ttk.Button(city_frame, text=self.translations_manager.t('theme', self.language), command=self.toggle_theme).pack(side=tk.RIGHT)

        # Current weather panel
        self.current_panel = ttk.LabelFrame(self.main_frame, text=self.translations_manager.t('current_weather', self.language))
        self.current_panel.pack(fill=tk.X, pady=5)
        self.weather_icon_label = ttk.Label(self.current_panel)
        self.weather_icon_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)
        self.temp_label = ttk.Label(self.current_panel, font=('Segoe UI', 22, 'bold'))
        self.temp_label.grid(row=0, column=1, sticky='w')
        self.desc_label = ttk.Label(self.current_panel, font=('Segoe UI', 12))
        self.desc_label.grid(row=1, column=1, sticky='w')
        self.meta_label = ttk.Label(self.current_panel, font=('Segoe UI', 10))
        self.meta_label.grid(row=2, column=1, sticky='w')

        # Forecast panel
        self.forecast_panel = ttk.LabelFrame(self.main_frame, text=self.translations_manager.t('forecast', self.language))
        self.forecast_panel.pack(fill=tk.BOTH, expand=True, pady=5)
        self.forecast_frames = []
        for i in range(5):
            frame = ttk.Frame(self.forecast_panel, borderwidth=1, relief='solid', padding=5)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
            icon = ttk.Label(frame)
            icon.pack()
            day = ttk.Label(frame, font=('Segoe UI', 11, 'bold'))
            day.pack()
            temp = ttk.Label(frame, font=('Segoe UI', 10))
            temp.pack()
            desc = ttk.Label(frame, font=('Segoe UI', 9))
            desc.pack()
            self.forecast_frames.append({'frame': frame, 'icon': icon, 'day': day, 'temp': temp, 'desc': desc})

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

    def toggle_theme(self):
        self.theme = 'dark' if getattr(self, 'theme', 'light') == 'light' else 'light'
        self.config_manager.set('theme', self.theme)
        self.config_manager.save_config()
        self.apply_theme()
        try:
            city = self.city_var.get()
            weather, forecast = self.weather_api.fetch_weather(city)
            self._update_current_weather(weather)
            self._update_forecast(forecast)
            self._update_fav_btn()
        except Exception as e:
            logging.error(f'Could not fetch weather for city {city}: {e}', exc_info=True)
            messagebox.showerror('Error', f'Could not fetch weather: {e}')

    def refresh_weather(self):
        city = self.city_var.get()
        try:
            weather, forecast = self.weather_api.fetch_weather(city)
            self._update_current_weather(weather)
            self._update_forecast(forecast)
            self._update_fav_btn()
        except Exception as e:
            logging.error(f'Could not fetch weather for city {city}: {e}', exc_info=True)
            messagebox.showerror('Error', f'Could not fetch weather: {e}')

    def _change_units(self, value):
        self.units = value
        self.config_manager.set('units', value)
        self.config_manager.save_config()
        self.weather_api.update_config(units=value)
        self.refresh_weather()

    def _change_language(self, value):
        self.language = value
        self.config_manager.set('language', value)
        self.config_manager.save_config()
        self.weather_api.update_config(language=value)
        
        # Store the current city and theme before rebuilding
        current_city = self.city_var.get()
        
        # Rebuild UI to update all labels
        for widget in self.root.winfo_children():
            if widget != self.menu_bar:  # Don't destroy the menu bar
                widget.destroy()
        
        # Rebuild the UI
        self._build_ui()
        
        # Restore the city and refresh
        self.city_var.set(current_city)
        self.apply_theme()
        self.refresh_weather()


    def _update_current_weather(self, data):
        temp = int(round(data['main']['temp']))
        desc = data['weather'][0]['description'].capitalize()
        icon_code = data['weather'][0]['icon']
        humidity = data['main']['humidity']
        wind = data['wind']['speed']
        temp_unit = '°C' if self.units == 'metric' else '°F'
        wind_unit = 'm/s' if self.units == 'metric' else 'mph'
        self.temp_label.config(text=f'{temp}{temp_unit}')
        self.desc_label.config(text=desc)
        self.meta_label.config(text=f"{self.translations_manager.t('humidity', self.language)}: {humidity}%   {self.translations_manager.t('wind', self.language)}: {wind} {wind_unit}")
        # Icon
        icon_img = get_icon_image(icon_code)
        self.weather_icon_label.config(image=icon_img)
        self.weather_icon_label.image = icon_img

    def _update_forecast(self, data):
        # Get one forecast per day (at 12:00)
        from datetime import datetime
        days = {}
        for entry in data['list']:
            dt = datetime.fromtimestamp(entry['dt'])
            if dt.hour == 12 and len(days) < 5:
                days[dt.date()] = entry
        # Fill up to 5 days
        while len(days) < 5 and data['list']:
            entry = data['list'].pop(0)
            dt = datetime.fromtimestamp(entry['dt'])
            days[dt.date()] = entry
        temp_unit = '°C' if self.units == 'metric' else '°F'
        for i, (day, entry) in enumerate(list(days.items())[:5]):
            temp = int(round(entry['main']['temp']))
            desc = entry['weather'][0]['description'].capitalize()
            icon_code = entry['weather'][0]['icon']
            weekday = day.strftime('%A')
            icon_img = get_icon_image(icon_code, size=(40, 40))
            frame = self.forecast_frames[i]
            frame['icon'].config(image=icon_img)
            frame['icon'].image = icon_img
            frame['day'].config(text=weekday)
            frame['temp'].config(text=f'{temp}{temp_unit}')
            frame['desc'].config(text=desc)


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
        settings.geometry('400x200')
        settings.resizable(False, False)
        
        # Make the settings window modal
        settings.transient(self.root)
        settings.grab_set()
        
        # API Key Frame
        api_frame = ttk.Frame(settings, padding="10 10 10 10")
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # API Key Label and Entry
        ttk.Label(api_frame, text=self.translations_manager.t('api_key', self.language)).pack(anchor='w')
        api_key_var = tk.StringVar(value=self.api_key)
        api_entry = ttk.Entry(api_frame, textvariable=api_key_var, width=40, show="*" if api_key_var.get() != 'YOUR_API_KEY_HERE' else "")
        api_entry.pack(fill=tk.X, pady=5)
        
        # Show/Hide API Key Checkbutton
        def toggle_api_key_visibility():
            if show_var.get():
                api_entry.config(show="")
            else:
                api_entry.config(show="*" if api_key_var.get() != 'YOUR_API_KEY_HERE' else "")
        
        show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(api_frame, 
                       text=self.translations_manager.t('show_api_key', self.language),
                       variable=show_var,
                       command=toggle_api_key_visibility).pack(anchor='w', pady=5)
        
        # Buttons Frame
        btn_frame = ttk.Frame(settings, padding="10 10 10 10")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_settings():
            new_api_key = api_key_var.get().strip()
            if new_api_key and new_api_key != 'YOUR_API_KEY_HERE':
                self.api_key = new_api_key
                self.config_manager.set('api_key', new_api_key)
                self.config_manager.save_config()
                self.weather_api.update_config(api_key=new_api_key)
                messagebox.showinfo(
                    self.translations_manager.t('success', self.language),
                    self.translations_manager.t('settings_saved', self.language),
                    parent=settings
                )
                settings.destroy()
                self.refresh_weather()
            else:
                messagebox.showerror(
                    self.translations_manager.t('error', self.language),
                    self.translations_manager.t('invalid_api_key', self.language),
                    parent=settings
                )
        
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
