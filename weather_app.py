import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
import io
import os

from version import get_version
from about import About
from help import Help
from sponsor import Sponsor
from menu import create_menu_bar

# ----------- CONFIGURATION -----------
API_KEY = os.environ.get('OPENWEATHER_API_KEY', 'YOUR_API_KEY_HERE')  # Replace with your actual API key or set as env var
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
        self.theme = 'light'
        self.theme_colors = LIGHT_THEME.copy()
        self.city_var = tk.StringVar(value=DEFAULT_CITY)

        # Menu bar
        create_menu_bar(self.root, self)

        self._build_ui()
        self.apply_theme()
        self.refresh_weather()

    def _build_ui(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # City input
        city_frame = ttk.Frame(self.main_frame)
        city_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(city_frame, text='City:').pack(side=tk.LEFT)
        self.city_entry = ttk.Entry(city_frame, textvariable=self.city_var, width=20)
        self.city_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(city_frame, text='Search', command=self.refresh_weather).pack(side=tk.LEFT)
        ttk.Button(city_frame, text='Theme', command=self.toggle_theme).pack(side=tk.RIGHT)

        # Current weather panel
        self.current_panel = ttk.LabelFrame(self.main_frame, text='Current Weather')
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
        self.forecast_panel = ttk.LabelFrame(self.main_frame, text='5-Day Forecast')
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
        colors = LIGHT_THEME if self.theme == 'light' else DARK_THEME
        self.theme_colors = colors.copy()
        self.root.configure(bg=colors['bg'])
        self.main_frame.configure(style='Main.TFrame')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        style.configure('TFrame', background=colors['bg'])
        style.configure('Main.TFrame', background=colors['bg'])
        style.configure('TButton', background=colors['accent'], foreground=colors['fg'])
        style.configure('TLabelframe', background=colors['panel'], foreground=colors['fg'])
        style.configure('TLabelframe.Label', background=colors['panel'], foreground=colors['fg'])
        style.configure('TEntry', fieldbackground=colors['panel'], foreground=colors['fg'])

    def toggle_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.apply_theme()

    def refresh_weather(self):
        city = self.city_var.get()
        try:
            weather, forecast = self._fetch_weather(city)
            self._update_current_weather(weather)
            self._update_forecast(forecast)
        except Exception as e:
            messagebox.showerror('Error', f'Could not fetch weather: {e}')

    def _fetch_weather(self, city):
        params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
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
        self.temp_label.config(text=f'{temp}°C')
        self.desc_label.config(text=desc)
        self.meta_label.config(text=f'Humidity: {humidity}%   Wind: {wind} m/s')
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
            frame['temp'].config(text=f'{temp}°C')
            frame['desc'].config(text=desc)

    def _get_icon_image(self, icon_code, size=(64, 64)):
        url = f'http://openweathermap.org/img/wn/{icon_code}@2x.png'
        try:
            r = requests.get(url)
            img = Image.open(io.BytesIO(r.content)).resize(size)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _show_settings(self):
        # Simple settings dialog for API key
        settings = tk.Toplevel(self.root)
        settings.title('Settings')
        settings.geometry('350x150')
        tk.Label(settings, text='OpenWeatherMap API Key:').pack(pady=10)
        api_var = tk.StringVar(value=os.environ.get('OPENWEATHER_API_KEY', API_KEY))
        entry = tk.Entry(settings, textvariable=api_var, width=40)
        entry.pack(pady=5)
        def save_key():
            global API_KEY
            API_KEY = api_var.get()
            settings.destroy()
        tk.Button(settings, text='Save', command=save_key).pack(pady=10)

if __name__ == '__main__':
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
