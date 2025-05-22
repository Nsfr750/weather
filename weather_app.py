import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
import io
import os
import logging

from version import get_version
from about import About
from help import Help
from sponsor import Sponsor
from menu import create_menu_bar
from favorites import load_favorites, save_favorites
from config import load_config, save_config
from translations import t, TRANSLATIONS

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
LIGHT_THEME = {
    'bg': '#f4f4f4',
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

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Weather App')
        self.root.geometry('500x600')
        self.root.resizable(False, False)

        self.config = load_config()
        self.units = self.config.get('units', 'metric')
        self.language = self.config.get('language', 'en')
        self.api_key = self.config.get('api_key') or os.environ.get('OPENWEATHER_API_KEY', 'YOUR_API_KEY_HERE')
        self.theme = self.config.get('theme', 'dark')
        self.city_var = tk.StringVar(value=DEFAULT_CITY)

        # Menu bar
        create_menu_bar(self.root, self)

        self._build_ui()
        self.apply_theme()
        self.refresh_weather()
        self.city_var.trace_add('write', lambda *args: self._update_fav_btn())

    def _build_ui(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # City input
        city_frame = ttk.Frame(self.main_frame)
        city_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(city_frame, text=t('city', self.language)).pack(side=tk.LEFT)
        self.city_entry = ttk.Entry(city_frame, textvariable=self.city_var, width=20)
        self.city_entry.pack(side=tk.LEFT, padx=5)

        # Language dropdown
        self.language_var = tk.StringVar(value=self.language)
        langs = list(TRANSLATIONS.keys())
        self.lang_menu = ttk.OptionMenu(city_frame, self.language_var, self.language, *langs, command=self._change_language)
        self.lang_menu.pack(side=tk.LEFT, padx=5)

        # Units dropdown
        self.units_var = tk.StringVar(value=self.units)
        self.units_menu = ttk.OptionMenu(city_frame, self.units_var, self.units, 'metric', 'imperial', command=self._change_units)
        self.units_menu.pack(side=tk.LEFT, padx=5)

        # Favorites dropdown
        self.favorites = load_favorites()
        self.favorite_var = tk.StringVar(value='Favorites')
        self.fav_menu = ttk.OptionMenu(city_frame, self.favorite_var, t('favorites', self.language), *self.favorites, command=self._select_favorite)
        self.fav_menu.pack(side=tk.LEFT, padx=5)

        # Add/Remove Favorite button
        self.fav_btn = ttk.Button(city_frame, text=t('remove_favorite', self.language), width=3, command=self._toggle_favorite)
        self.fav_btn.pack(side=tk.LEFT, padx=2)
        self._update_fav_btn()

        ttk.Button(city_frame, text=t('search', self.language), command=self.refresh_weather).pack(side=tk.LEFT)
        ttk.Button(city_frame, text=t('theme', self.language), command=self.toggle_theme).pack(side=tk.RIGHT)

        # Current weather panel
        self.current_panel = ttk.LabelFrame(self.main_frame, text=t('current_weather', self.language))
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
        self.forecast_panel = ttk.LabelFrame(self.main_frame, text=t('forecast', self.language))
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
        # self.main_frame.configure(bg=theme['bg'])  # Do NOT set bg for ttk.Frame
        # Removed call to self._set_widget_theme; rely on ttk.Style for theming
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        style.configure('TFrame', background=theme['bg'])
        style.configure('Main.TFrame', background=theme['bg'])
        style.configure('TButton', background=theme['accent'], foreground=theme['fg'])
        style.configure('TLabelframe', background=theme['panel'], foreground=theme['fg'])
        style.configure('TLabelframe.Label', background=theme['panel'], foreground=theme['fg'])
        style.configure('TEntry', fieldbackground=theme['panel'], foreground=theme['fg'])

    def toggle_theme(self):
        self.theme = 'dark' if getattr(self, 'theme', 'light') == 'light' else 'light'
        self.config['theme'] = self.theme
        save_config(self.config)
        self.apply_theme()
        try:
            city = self.city_var.get()
            weather, forecast = self._fetch_weather(city)
            self._update_current_weather(weather)
            self._update_forecast(forecast)
            self._update_fav_btn()
        except Exception as e:
            logging.error(f'Could not fetch weather for city {city}: {e}', exc_info=True)
            messagebox.showerror('Error', f'Could not fetch weather: {e}')

    def refresh_weather(self):
        city = self.city_var.get()
        try:
            weather, forecast = self._fetch_weather(city)
            self._update_current_weather(weather)
            self._update_forecast(forecast)
            self._update_fav_btn()
        except Exception as e:
            logging.error(f'Could not fetch weather for city {city}: {e}', exc_info=True)
            messagebox.showerror('Error', f'Could not fetch weather: {e}')

    def _change_units(self, value):
        self.units = value
        self.config['units'] = value
        save_config(self.config)
        self.refresh_weather()

    def _change_language(self, value):
        self.language = value
        self.config['language'] = value
        save_config(self.config)
        # Rebuild UI to update all labels
        for widget in self.root.winfo_children():
            widget.destroy()
        self._build_ui()
        self.apply_theme()
        self.refresh_weather()

    def _fetch_weather(self, city):
        params = {'q': city, 'appid': self.api_key, 'units': self.units, 'lang': self.language}
        # Current weather
        r = requests.get(BASE_URL + 'weather', params=params)
        if r.status_code != 200:
            raise Exception(r.json().get('message', 'API error'))
        weather = r.json()
        # Forecast (5 day, 3-hour intervals)
        r2 = requests.get(BASE_URL + 'forecast', params=params)
        if r2.status_code != 200:
            raise Exception(r2.json().get('message', 'API error'))
        forecast = r2.json()
        return weather, forecast

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
        self.meta_label.config(text=f"{t('humidity', self.language)}: {humidity}%   {t('wind', self.language)}: {wind} {wind_unit}")
        # Icon
        icon_img = self._get_icon_image(icon_code)
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
            icon_img = self._get_icon_image(icon_code, size=(40, 40))
            frame = self.forecast_frames[i]
            frame['icon'].config(image=icon_img)
            frame['icon'].image = icon_img
            frame['day'].config(text=weekday)
            frame['temp'].config(text=f'{temp}{temp_unit}')
            frame['desc'].config(text=desc)

    def _get_icon_image(self, icon_code, size=(64, 64)):
        url = f'http://openweathermap.org/img/wn/{icon_code}@2x.png'
        try:
            r = requests.get(url)
            img = Image.open(io.BytesIO(r.content)).resize(size)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            logging.error(f'Failed to fetch or process icon {icon_code}: {e}', exc_info=True)
            return None

    def _toggle_favorite(self):
        city = self.city_var.get().strip()
        if not city:
            return
        if city in self.favorites:
            self.favorites.remove(city)
        else:
            self.favorites.append(city)
        save_favorites(self.favorites)
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
            menu.add_command(label=t('no_favorites', self.language), command=lambda: None)

    def _update_fav_btn(self):
        city = self.city_var.get().strip()
        if city in self.favorites:
            self.fav_btn.config(text=t('remove_favorite', self.language))
        else:
            self.fav_btn.config(text=t('add_favorite', self.language))
        self._update_fav_menu()


    def _show_settings(self):
        # Settings dialog for API key
        settings = tk.Toplevel(self.root)
        settings.title(t('settings', self.language))
        settings.geometry('350x180')
        tk.Label(settings, text=t('api_key', self.language)).pack(pady=10)
        api_var = tk.StringVar(value=self.api_key)
        entry = tk.Entry(settings, textvariable=api_var, width=40)
        entry.pack(pady=5)
        def save_key():
            self.api_key = api_var.get()
            self.config['api_key'] = self.api_key
            save_config(self.config)
            settings.destroy()
        tk.Button(settings, text=t('save', self.language), command=save_key).pack(pady=10)


if __name__ == '__main__':
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
