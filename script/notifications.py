"""
notifications.py
Handles desktop notifications for weather alerts and warnings.
"""
import platform
import logging
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import os
import json
from pathlib import Path

# Notification cooldown period (minutes)
NOTIFICATION_COOLDOWN = 30

class NotificationManager:
    def __init__(self, config_dir):
        # Ensure config directory exists
        self.config_dir = Path(config_dir) / 'config'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.notification_history = {}
        self.load_notification_history()
        
    def load_notification_history(self):
        """Load notification history from file"""
        history_file = self.config_dir / 'notifications.json'
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.notification_history = json.load(f)
        except Exception as e:
            logging.error(f'Failed to load notification history: {e}')
            self.notification_history = {}
    
    def save_notification_history(self):
        """Save notification history to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            history_file = self.config_dir / 'notifications.json'
            with open(history_file, 'w') as f:
                json.dump(self.notification_history, f)
        except Exception as e:
            logging.error(f'Failed to save notification history: {e}')
    
    def should_show_notification(self, alert_id):
        """Check if we should show a notification based on cooldown"""
        now = datetime.utcnow()
        last_shown = self.notification_history.get(alert_id)
        
        if not last_shown:
            return True
            
        try:
            last_shown_time = datetime.fromisoformat(last_shown)
            return (now - last_shown_time) > timedelta(minutes=NOTIFICATION_COOLDOWN)
        except (ValueError, TypeError):
            return True
    
    def update_notification_time(self, alert_id):
        """Update the last shown time for an alert"""
        now = datetime.utcnow().isoformat()
        self.notification_history[alert_id] = now
        self.save_notification_history()
    
    def show_notification(self, title, message, alert_id=None):
        """
        Show a desktop notification.
        If alert_id is provided, will respect cooldown periods.
        """
        if alert_id and not self.should_show_notification(alert_id):
            return
            
        try:
            # Try system notification first
            if platform.system() == 'Windows':
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast(title, message, duration=10, threaded=True)
                except ImportError:
                    # Fallback to Tkinter messagebox
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showwarning(title, message)
                    root.destroy()
            elif platform.system() == 'Darwin':  # macOS
                os.system(f"""osascript -e 'display notification "{message}" with title "{title}"'""")
            else:  # Linux and others
                os.system(f'notify-send "{title}" "{message}"')
                
            if alert_id:
                self.update_notification_time(alert_id)
                
        except Exception as e:
            logging.error(f'Failed to show notification: {e}')
            # Fallback to simple print
            print(f"[ALERT] {title}: {message}")

def check_severe_weather(weather_data):
    """
    Check weather data for severe conditions that warrant notifications.
    
    Args:
        weather_data (dict or list): The weather data from the API. Can be a single weather dict or a list of alerts.
        
    Returns:
        list: List of alert dictionaries with 'id', 'title', and 'message' keys.
    """
    alerts = []
    
    # Handle case where weather_data is a list of alerts (from One Call API)
    if isinstance(weather_data, list):
        for alert in weather_data:
            if not isinstance(alert, dict):
                continue
                
            # Process each alert from the One Call API
            alert_id = alert.get('event', '').lower().replace(' ', '_')
            if not alert_id:
                alert_id = f'alert_{len(alerts)}'
                
            alerts.append({
                'id': alert_id,
                'title': f"{alert.get('sender_name', 'Weather Alert')}: {alert.get('event', 'Severe Weather')}",
                'message': f"{alert.get('description', 'Severe weather alert')}\n"
                        f"Start: {alert.get('start', 'N/A')}\n"
                        f"End: {alert.get('end', 'N/A')}",
                'severity': 'high'
            })
        return alerts
    
    # Handle current weather data structure
    if not isinstance(weather_data, dict):
        return alerts
    
    # Check for extreme temperatures
    temp = weather_data.get('main', {}).get('temp')
    if temp is not None:
        if temp > 35:  # 35°C or 95°F
            alerts.append({
                'id': f'temp_high_{int(temp)}',
                'title': 'Extreme Heat Warning',
                'message': f'Extremely high temperature: {int(temp)}°C. Stay hydrated and avoid direct sun exposure.',
                'severity': 'high'
            })
        elif temp < -10:  # -10°C or 14°F
            alerts.append({
                'id': f'temp_low_{int(temp)}',
                'title': 'Extreme Cold Warning',
                'message': f'Extremely low temperature: {int(temp)}°C. Dress warmly and limit time outdoors.',
                'severity': 'high'
            })
    
    # Check for severe weather conditions
    weather_conditions = weather_data.get('weather', [])
    if not isinstance(weather_conditions, list):
        weather_conditions = [weather_conditions] if weather_conditions else []
    
    for weather in weather_conditions:
        if not isinstance(weather, dict):
            continue
            
        main = str(weather.get('main', '')).lower()
        description = str(weather.get('description', '')).lower()
        weather_id = str(weather.get('id', ''))
        
        if 'thunderstorm' in main or 'thunderstorm' in description:
            alerts.append({
                'id': f'weather_thunder_{weather_id}',
                'title': 'Thunderstorm Warning',
                'message': f'Thunderstorm detected: {description.capitalize()}. Stay indoors if possible.',
                'severity': 'high'
            })
        elif 'tornado' in description or 'tornado' in main:
            alerts.append({
                'id': 'weather_tornado',
                'title': 'Tornado Warning',
                'message': 'Tornado warning! Seek shelter immediately.',
                'severity': 'extreme'
            })
        elif 'hurricane' in description or 'typhoon' in description:
            alerts.append({
                'id': 'weather_hurricane',
                'title': 'Hurricane/Typhoon Warning',
                'message': 'Hurricane or typhoon warning! Take necessary precautions immediately.',
                'severity': 'extreme'
            })
    
    # Check wind speed (m/s)
    wind_data = weather_data.get('wind', {})
    if isinstance(wind_data, dict):
        wind_speed = wind_data.get('speed', 0)
        if isinstance(wind_speed, (int, float)) and wind_speed > 15:  # ~34 mph or 54 km/h
            alerts.append({
                'id': f'wind_high_{int(wind_speed)}',
                'title': 'High Wind Warning',
                'message': f'High winds detected: {int(wind_speed)} m/s. Secure loose objects and be cautious outdoors.',
                'severity': 'medium'
            })
    
    # Check for heavy rain or snow
    rain = weather_data.get('rain', {})
    snow = weather_data.get('snow', {})
    
    if isinstance(rain, dict) and rain.get('1h', 0) > 20:  # More than 20mm in 1 hour
        alerts.append({
            'id': 'heavy_rain',
            'title': 'Heavy Rain Warning',
            'message': 'Heavy rainfall detected. Be aware of potential flooding.',
            'severity': 'high'
        })
    
    if isinstance(snow, dict) and snow.get('1h', 0) > 5:  # More than 5cm in 1 hour
        alerts.append({
            'id': 'heavy_snow',
            'title': 'Heavy Snow Warning',
            'message': 'Heavy snowfall detected. Travel may be dangerous.',
            'severity': 'high'
        })
    
    return alerts
