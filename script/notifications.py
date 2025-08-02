"""
notifications.py
Handles desktop notifications for weather alerts and warnings.
"""
import logging
from datetime import datetime, timedelta
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json

from PyQt6.QtWidgets import QMessageBox, QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QAction

# Default settings
DEFAULT_ALERT_COOLDOWN = 30  # minutes
DEFAULT_ALERT_EXPIRY_DAYS = 7

class AlertSeverity(Enum):
    """Severity levels for weather alerts."""
    INFO = auto()
    ADVISORY = auto()
    WATCH = auto()
    WARNING = auto()
    EMERGENCY = auto()

class AlertType(Enum):
    """Types of weather alerts."""
    WEATHER = "weather"
    TEMPERATURE = "temperature"
    WIND = "wind"
    PRECIPITATION = "precipitation"
    SEVERE = "severe"
    OTHER = "other"

@dataclass
class WeatherAlert:
    """Data class for weather alerts."""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    alert_type: AlertType
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: str = ""
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """Check if the alert is currently active based on start/end times."""
        now = datetime.utcnow()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary for serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity.name,
            'alert_type': self.alert_type.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location': self.location,
            'source': self.source,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherAlert':
        """Create WeatherAlert from dictionary."""
        return cls(
            id=data['id'],
            title=data['title'],
            message=data['message'],
            severity=AlertSeverity[data['severity']],
            alert_type=AlertType(data['alert_type']),
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            location=data.get('location', ''),
            source=data.get('source', ''),
            metadata=data.get('metadata', {})
        )


class NotificationManager(QObject):
    """Manages weather alerts and notifications."""
    
    # Signal emitted when new alerts are received
    new_alerts = pyqtSignal(list)  # List[WeatherAlert]
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
            
        last_shown_time = datetime.fromisoformat(last_shown)
        time_since_last = now - last_shown_time
        return time_since_last > timedelta(minutes=NOTIFICATION_COOLDOWN)
    
    def show_notification(self, title, message, alert_id=None, parent=None):
        """
        Show a desktop notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            alert_id (str, optional): Unique ID for this alert to prevent duplicates
            parent (QWidget, optional): Parent widget for the message box
        """
        if alert_id and not self.should_show_notification(alert_id):
            return
            
        try:
            # Show a message box
            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            
            # Update notification history
            if alert_id:
                self.notification_history[alert_id] = datetime.utcnow().isoformat()
                self.save_notification_history()
                
        except Exception as e:
            logging.error(f'Failed to show notification: {e}')
    
    def show_alert(self, title, message, alert_id=None, parent=None):
        """
        Show an alert dialog.
        
        Args:
            title (str): Alert title
            message (str): Alert message
            alert_id (str, optional): Unique ID for this alert to prevent duplicates
            parent (QWidget, optional): Parent widget for the message box
        """
        if alert_id and not self.should_show_notification(alert_id):
            return
            
        try:
            # Show a warning message box
            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            
            # Update notification history
            if alert_id:
                self.notification_history[alert_id] = datetime.utcnow().isoformat()
                self.save_notification_history()
                
        except Exception as e:
            logging.error(f'Failed to show alert: {e}')

def check_severe_weather(weather_data):
    """
    Check weather data for severe conditions that warrant notifications.
    
    Args:
        weather_data (dict, list, or WeatherData): The weather data. Can be a dictionary, list of alerts, or WeatherData object.
        
    Returns:
        list: List of alert dictionaries with 'id', 'title', and 'message' keys.
    """
    alerts = []
    
    if not weather_data:
        return alerts
    
    # Convert WeatherData object to dictionary if needed
    if hasattr(weather_data, 'to_dict'):
        weather_data = weather_data.to_dict()
    
    # Handle case where weather_data is a list of alerts
    if isinstance(weather_data, list):
        for alert in weather_data:
            if isinstance(alert, dict):
                alert_id = alert.get('id', str(hash(str(alert))))
                alerts.append({
                    'id': alert_id,
                    'title': alert.get('event', 'Weather Alert'),
                    'message': f"{alert.get('description', 'No description')}"
                })
        return alerts
    
    # Handle current weather data
    if isinstance(weather_data, dict):
        # Check for weather conditions
        if 'weather' in weather_data and isinstance(weather_data['weather'], list):
            for condition in weather_data.get('weather', []):
                if not isinstance(condition, dict):
                    continue
                    
                condition_id = condition.get('id', 0)
                
                # Thunderstorm
                if 200 <= condition_id < 300:
                    alerts.append({
                        'id': f'thunder_{condition_id}',
                        'title': 'Thunderstorm Alert',
                        'message': f"Thunderstorm detected: {condition.get('description', '')}"
                    })
                
                # Heavy rain
                elif condition_id in [500, 501, 502, 503, 504, 511, 520, 521, 522]:
                    alerts.append({
                        'id': f'rain_{condition_id}',
                        'title': 'Heavy Rain Alert',
                        'message': f"Heavy rain expected: {condition.get('description', '')}"
                    })
                
                # Snow
                elif 600 <= condition_id < 700:
                    alerts.append({
                        'id': f'snow_{condition_id}',
                        'title': 'Snow Alert',
                        'message': f"Snow expected: {condition.get('description', '')}"
                    })
        
        # Handle alerts if present
        if 'alerts' in weather_data and isinstance(weather_data['alerts'], list):
            for alert in weather_data['alerts']:
                if not isinstance(alert, dict):
                    continue
                    
                alert_id = alert.get('id', str(hash(str(alert))))
                alerts.append({
                    'id': alert_id,
                    'title': alert.get('event', 'Weather Alert'),
                    'message': f"{alert.get('description', 'No description')}"
                })
    
    return alerts
