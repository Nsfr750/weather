"""
enhanced_notifications.py
Enhanced notification system for weather alerts with system tray integration.
"""
import json
import logging
import platform
import os
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path.home() / '.weather_app' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

# Create file handler
log_file = log_dir / 'notifications.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon, QStyle

# Import language manager
from lang.language_manager import LanguageManager

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


class WeatherAlert:
    """Data class for weather alerts with enhanced features."""

    def __init__(
        self,
        alert_id: str,
        title: str,
        message: str,
        severity: AlertSeverity,
        alert_type: AlertType,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        location: str = "",
        source: str = "",
        metadata: Optional[Dict] = None,
    ):
        self.id = alert_id
        self.title = title
        self.message = message
        self.severity = severity
        self.alert_type = alert_type
        self.start_time = start_time or datetime.utcnow()
        self.end_time = end_time or (self.start_time + timedelta(days=1))
        self.location = location
        self.source = source
        self.metadata = metadata or {}

    def is_active(self) -> bool:
        """Check if the alert is currently active based on start/end times."""
        now = datetime.utcnow()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True

    def to_dict(self) -> Dict:
        """Convert alert to dictionary for serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity.name,
            'alert_type': self.alert_type.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'location': self.location,
            'source': self.source,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'WeatherAlert':
        """Create WeatherAlert from dictionary."""
        return cls(
            alert_id=data['id'],
            title=data['title'],
            message=data['message'],
            severity=AlertSeverity[data['severity']],
            alert_type=AlertType(data['alert_type']),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            location=data.get('location', ''),
            source=data.get('source', ''),
            metadata=data.get('metadata', {})
        )


class NotificationManager(QObject):
    """
    Enhanced notification manager with system tray integration.
    """
    new_alert = pyqtSignal(WeatherAlert)  # Emitted when a new alert is received

    def __init__(self, data_dir: Path):
        """Initialize the notification manager.
        
        Args:
            data_dir: Directory to store notification data
        """
        super().__init__()
        self.data_dir = Path(data_dir)
        self.notifications_dir = self.data_dir / "config"
        self.settings_file = self.notifications_dir / "notifications.json"
        self._alerts: Dict[str, WeatherAlert] = {}
        self._muted = False
        self._tray_icon = None
        
        # Ensure directories exist
        self.notifications_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize default settings if they don't exist
        if not self.settings_file.exists():
            self._save_settings()
        
        # Load settings
        self._load_settings()
        
        # Clean up expired alerts on startup
        self._cleanup_expired_alerts()
        
        # Set up cleanup timer for expired alerts
        self._cleanup_timer = QTimer()
        self._cleanup_timer.timeout.connect(self._cleanup_expired_alerts)
        self._cleanup_timer.start(5 * 60 * 1000)  # Check every 5 minutes

    def _save_settings(self) -> None:
        """Save notification settings to disk."""
        settings = {
            "muted": self._muted,
            "last_cleanup": datetime.utcnow().isoformat()
        }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except (IOError, OSError) as e:
            logging.error(f"Failed to save notification settings: {e}")

    def _load_settings(self) -> None:
        """Load notification settings."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self._muted = settings.get('muted', False)
            except Exception as e:
                logging.error(f"Error loading notification settings: {e}")

    def show_notification(self, title: str, message: str, alert_type: str = 'info', 
                         alert_id: str = None, duration: int = None) -> Optional[str]:
        """Show a desktop notification.
        
        Args:
            title: The title of the notification
            message: The message content of the notification
            alert_type: Type of alert ('info', 'warning', 'error', 'critical')
            alert_id: Optional unique ID for the notification
            duration: How long to show the notification in milliseconds
            
        Returns:
            str: The alert ID if notification was shown, None otherwise
        """
        try:
            if not title or not message:
                logger.warning("Cannot show notification: title and message are required")
                return None
                
            if not alert_id:
                alert_id = f"notif_{int(datetime.utcnow().timestamp())}"
                
            if not self._should_show_notification(alert_id):
                logger.debug(f"Notification suppressed for alert_id: {alert_id}")
                return None
                
            # Ensure alert_type is valid
            alert_type = alert_type.lower()
            if alert_type not in ['info', 'warning', 'error', 'critical']:
                alert_type = 'info'
                
            alert = WeatherAlert(
                alert_id=alert_id,
                title=str(title)[:100],  # Limit title length
                message=str(message)[:500],  # Limit message length
                severity=getattr(AlertSeverity, alert_type.upper(), AlertSeverity.INFO),
                alert_type=AlertType.OTHER,
                metadata={
                    'type': 'notification',
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            return self._show_alert(alert, duration)
            
        except Exception as e:
            logger.error(f"Error showing notification: {e}", exc_info=True)
            return None

    def show_alert(self, alert_data: Union[WeatherAlert, Dict]) -> Optional[str]:
        """Show a weather alert notification."""
        alert = alert_data if isinstance(alert_data, WeatherAlert) else WeatherAlert.from_dict(alert_data)
        
        if not alert.is_active():
            return None
            
        return self._show_alert(alert)

    def _show_alert(self, alert: WeatherAlert, duration: int = None) -> str:
        """Internal method to show an alert.
        
        Args:
            alert: The WeatherAlert to display
            duration: How long to show the notification in milliseconds
            
        Returns:
            str: The alert ID if shown, or empty string if not
        """
        try:
            if not isinstance(alert, WeatherAlert):
                logger.error("Invalid alert type provided to _show_alert")
                return ""
                
            self._alerts[alert.id] = alert
            
            if self._muted:
                logger.debug(f"Notifications are muted, not showing alert: {alert.id}")
                return alert.id
                
            duration = duration or 5000  # Default duration 5 seconds
            
            # Ensure we have a system tray icon
            if not hasattr(self, '_tray_icon') or self._tray_icon is None:
                try:
                    self._tray_icon = QSystemTrayIcon(QIcon("assets/meteo.png"), parent=QApplication.instance())
                    self._tray_icon.show()
                except Exception as e:
                    logger.error(f"Failed to initialize system tray icon: {e}")
                    return ""
            
            try:
                # Show the notification
                self._tray_icon.showMessage(
                    alert.title,
                    alert.message,
                    QSystemTrayIcon.MessageIcon.Information,
                    duration
                )
                
                # Emit signal for new alert
                self.new_alert.emit(alert)
                logger.debug(f"Showed notification: {alert.id}")
                
            except Exception as e:
                logger.error(f"Failed to show notification: {e}")
                return ""
                
        except Exception as e:
            logger.error(f"Error in _show_alert: {e}", exc_info=True)
            return ""
            
        return alert.id

    def _should_show_notification(self, alert_id: str) -> bool:
        """Check if we should show a notification based on cooldown."""
        return True  # Add cooldown logic here
    
    def dismiss_alert(self, alert_id: str) -> None:
        """Dismiss an alert by ID."""
        if alert_id in self._alerts:
            del self._alerts[alert_id]
    
    def toggle_mute(self) -> None:
        """Toggle notification mute state."""
        self._muted = not self._muted
        self._save_settings()
    
    def show_notification_history(self) -> None:
        """Show notification history in a dialog."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Weather Alerts")
        
        if not self._alerts:
            msg.setText("No weather alerts to display.")
        else:
            alert_text = "\n\n".join(
                f"{alert.title}: {alert.message}" 
                for alert in self._alerts.values()
            )
            msg.setText("Current Weather Alerts:")
            msg.setDetailedText(alert_text)
            
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _cleanup_expired_alerts(self) -> None:
        """Remove expired alerts."""
        now = datetime.utcnow()
        expired = [
            alert_id for alert_id, alert in self._alerts.items()
            if alert.end_time and alert.end_time < now
        ]
        
        for alert_id in expired:
            self.dismiss_alert(alert_id)

    def __del__(self):
        """Cleanup resources."""
        if self._tray_icon:
            self._tray_icon.hide()
