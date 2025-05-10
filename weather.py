import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel
import json
import requests
from datetime import datetime
import matplotlib.pyplot as plt

GEOLOCATION_URL = "http://ipinfo.io/json"  # Geolocation API
CONFIG_FILE = "config.json"


# Sponsor Class
class Sponsor:
    def show_sponsor_window(self):
        sponsor_root = Toplevel()
        sponsor_root.geometry("300x200")
        sponsor_root.title("Sponsor")

        title_label = tk.Label(sponsor_root, text="Support Us", font=("Arial", 16))
        title_label.pack(pady=10)

        def open_patreon():
            import webbrowser
            webbrowser.open("https://www.patreon.com/Nsfr750")

        def open_github():
            import webbrowser
            webbrowser.open("https://github.com/sponsors/Nsfr750")

        def open_discord():
            import webbrowser
            webbrowser.open("https://discord.gg/q5Pcgrju")

        def open_paypal():
            import webbrowser
            webbrowser.open("https://paypal.me/3dmga")    

        # Create and place buttons
        patreon_button = tk.Button(sponsor_root, text="Join the Patreon!", command=open_patreon)
        patreon_button.pack(pady=5)

        github_button = tk.Button(sponsor_root, text="GitHub", command=open_github)
        github_button.pack(pady=5)

        discord_button = tk.Button(sponsor_root, text="Join Discord", command=open_discord)
        discord_button.pack(pady=5)

        paypal_button = tk.Button(sponsor_root, text="Pay me a Coffee", command=open_paypal)    
        paypal_button.pack(pady=5)

        sponsor_root.mainloop()


# Load API Key
def load_api_key():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            return config.get("API_KEY", "")
    except FileNotFoundError:
        return ""


# Save API Key
def save_api_key(api_key):
    with open(CONFIG_FILE, "w") as file:
        json.dump({"API_KEY": api_key}, file)
    messagebox.showinfo("API Key Saved", "Your API key has been saved successfully!")


# Set API Key Dialog
def set_api_key():
    api_key = simpledialog.askstring("Set API Key", "Enter your OpenWeatherMap API Key:")
    if api_key:
        save_api_key(api_key)


# Fetch current location using IP address
def fetch_current_location():
    try:
        response = requests.get(GEOLOCATION_URL, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        city = data.get('city', None)
        if city:
            city_combobox.set(city)
            result_label.config(text=f"Detected current location: {city}")
        else:
            result_label.config(text="Unable to detect location!")
    except requests.RequestException as e:
        result_label.config(text=f"Error fetching location: {str(e)}")


# Fetch weather for the selected city
def fetch_weather():
    city = city_combobox.get()
    if not city:
        result_label.config(text="Please select a city!")
        return
    api_key = load_api_key()
    if not api_key:
        messagebox.showerror("API Key Missing", "Please set your API key in the 'Settings' menu before proceeding.")
        return
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        weather = f"Temperature: {data['main']['temp']}°C\n"
        weather += f"Humidity: {data['main']['humidity']}%\n"
        weather += f"Wind Speed: {data['wind']['speed']} m/s\n"
        weather += f"Description: {data['weather'][0]['description']}\n"
        weather += f"Sunrise: {datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S')}\n"
        weather += f"Sunset: {datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S')}"
        result_label.config(text=weather)
    except requests.RequestException as e:
        result_label.config(text=f"Error fetching weather: {str(e)}")


# Fetch weather forecast and visualize data
def fetch_forecast():
    city = city_combobox.get()
    if not city:
        forecast_label.config(text="Please select a city!")
        return
    api_key = load_api_key()
    if not api_key:
        messagebox.showerror("API Key Missing", "Please set your API key in the 'Settings' menu before proceeding.")
        return
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        forecast_data = ""
        dates = []
        temps = []  # Temperature for plotting
        winds = []  # Wind speed for plotting
        humids = []  # Humidity for plotting
        for i in range(0, 40, 8):  # Every 8th entry is roughly 24 hours apart
            timestamp = data['list'][i]['dt']
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            temp = data['list'][i]['main']['temp']
            wind_speed = data['list'][i]['wind']['speed']
            humidity = data['list'][i]['main']['humidity']
            description = data['list'][i]['weather'][0]['description']
            forecast_data += f"{date}: {temp}°C, {description}\n"
            dates.append(date)
            temps.append(temp)
            winds.append(wind_speed)
            humids.append(humidity)
        forecast_label.config(text=forecast_data)
        plot_forecast(dates, temps, winds, humids)
    except requests.RequestException as e:
        forecast_label.config(text=f"Error fetching forecast: {str(e)}")


# Plot temperature, wind speed, and humidity
def plot_forecast(dates, temps, winds, humids):
    plt.figure(figsize=(10, 8))

    # Temperature Plot
    plt.subplot(3, 1, 1)
    plt.plot(dates, temps, marker='o', linestyle='-', color='b')
    plt.title('5-Day Temperature Trend')
    plt.ylabel('Temperature (°C)')
    plt.grid(True)

    # Wind Speed Plot
    plt.subplot(3, 1, 2)
    plt.bar(dates, winds, color='g')
    plt.title('5-Day Wind Speed')
    plt.ylabel('Wind Speed (m/s)')
    plt.grid(True)

    # Humidity Plot
    plt.subplot(3, 1, 3)
    plt.plot(dates, humids, marker='o', linestyle='-', color='r')
    plt.title('5-Day Humidity Levels')
    plt.ylabel('Humidity (%)')
    plt.xlabel('Date')
    plt.grid(True)

    plt.tight_layout()
    plt.show(block=False)  # Non-blocking


# About Menu Callback
def show_about():
    messagebox.showinfo("About", "Weather App\nVersion 1.3\nAuthor: Nsfr750\n\nThis app provides current and forecasted weather details, graphical visualizations, and supports detecting your location using your IP address.")


# Help Menu Callback
def show_help():
    messagebox.showinfo("Help", "How to use this app:\n\n1. Select a city from the dropdown or detect your location.\n2. Click 'Get Weather' for current weather details.\n3. Click 'Get 5-Day Forecast' to see the weather forecast and graphical visualizations.\n\nEnjoy the app!")


# GUI Setup
root = tk.Tk()
root.title("Weather")
root.geometry("300x300")  # Set the start dialog size to 300x300

# Add Menu
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Menu
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=show_about)
help_menu.add_command(label="Help", command=show_help)
menu_bar.add_cascade(label="Help", menu=help_menu)

settings_menu = tk.Menu(menu_bar, tearoff=0)
settings_menu.add_command(label="Set API Key", command=set_api_key)
menu_bar.add_cascade(label="Settings", menu=settings_menu)

sponsor_menu = tk.Menu(menu_bar, tearoff=0)
sponsor = Sponsor()
sponsor_menu.add_command(label="Sponsor Us", command=sponsor.show_sponsor_window)
menu_bar.add_cascade(label="Sponsor", menu=sponsor_menu)

# Label for City Selection
city_label = tk.Label(root, text="Select City:")
city_label.pack()

# Dropdown list for cities
cities = ["New York", "London", "Tokyo", "Paris", "Milan", "Rome", "Mumbai", "Sydney", "Dubai", "Berlin", "Moscow", "Beijing"]
city_combobox = ttk.Combobox(root, values=cities)
city_combobox.pack()
city_combobox.set("Select a city")  # Set default placeholder text

# Buttons for Actions
detect_location_button = tk.Button(root, text="Detect Current Location", command=fetch_current_location)
detect_location_button.pack()

fetch_button = tk.Button(root, text="Get Weather", command=fetch_weather)
fetch_button.pack()

forecast_button = tk.Button(root, text="Get 5-Day Forecast", command=fetch_forecast)
forecast_button.pack()

# Result Labels
result_label = tk.Label(root, text="", justify="left")
result_label.pack()

forecast_label = tk.Label(root, text="", justify="left")
forecast_label.pack()

root.mainloop()