"""
Tests for the enhanced notification system.
"""
import json
import logging
import os
import shutil
import tempfile
import time
import unittest
import logging
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon

# Import the module to test
from script.notifications import (
    AlertSeverity,
    AlertType,
    NotificationManager,
    WeatherAlert,
    logger,
)

# Suppress logging during tests
logger.setLevel(logging.CRITICAL)


class TestWeatherAlert(unittest.TestCase):
    """Test cases for the WeatherAlert class."""

    def setUp(self):
        """Set up test fixtures."""
        self.alert_data = {
            "alert_id": "test_alert_1",
            "title": "Test Alert",
            "message": "This is a test alert",
            "severity": AlertSeverity.WARNING,
            "alert_type": AlertType.WEATHER,
            "start_time": datetime.utcnow(),
            "end_time": datetime.utcnow() + timedelta(hours=1),
            "location": "Test Location",
            "source": "test_source",
            "metadata": {"key": "value"},
        }
        self.alert = WeatherAlert(**self.alert_data)

    def test_alert_initialization(self):
        """Test that a WeatherAlert is initialized correctly."""
        self.assertEqual(self.alert.id, self.alert_data["alert_id"])
        self.assertEqual(self.alert.title, self.alert_data["title"])
        self.assertEqual(self.alert.message, self.alert_data["message"])
        self.assertEqual(self.alert.severity, self.alert_data["severity"])
        self.assertEqual(self.alert.alert_type, self.alert_data["alert_type"])
        self.assertEqual(self.alert.location, self.alert_data["location"])
        self.assertEqual(self.alert.source, self.alert_data["source"])
        self.assertEqual(self.alert.metadata, self.alert_data["metadata"])

    def test_is_active(self):
        """Test the is_active method."""
        # Test active alert
        self.assertTrue(self.alert.is_active())

        # Test future alert
        future_alert = WeatherAlert(
            "future_alert",
            "Future",
            "Future alert",
            AlertSeverity.INFO,
            AlertType.OTHER,
            start_time=datetime.utcnow() + timedelta(hours=1),
        )
        self.assertFalse(future_alert.is_active())

        # Test expired alert
        past_alert = WeatherAlert(
            "past_alert",
            "Past",
            "Expired alert",
            AlertSeverity.INFO,
            AlertType.OTHER,
            start_time=datetime.utcnow() - timedelta(hours=2),
            end_time=datetime.utcnow() - timedelta(hours=1),
        )
        self.assertFalse(past_alert.is_active())

    def test_to_dict(self):
        """Test converting alert to dictionary."""
        alert_dict = self.alert.to_dict()
        self.assertEqual(alert_dict["id"], self.alert_data["alert_id"])
        self.assertEqual(alert_dict["title"], self.alert_data["title"])
        self.assertEqual(alert_dict["severity"], self.alert_data["severity"].name)
        self.assertEqual(alert_dict["alert_type"], self.alert_data["alert_type"].value)

    def test_from_dict(self):
        """Test creating alert from dictionary."""
        alert_dict = self.alert.to_dict()
        new_alert = WeatherAlert.from_dict(alert_dict)
        self.assertEqual(new_alert.id, self.alert.id)
        self.assertEqual(new_alert.title, self.alert.title)
        self.assertEqual(new_alert.severity, self.alert.severity)
        self.assertEqual(new_alert.alert_type, self.alert.alert_type)


class TestNotificationManager(unittest.TestCase):
    """Test cases for the NotificationManager class."""

    @classmethod
    def setUpClass(cls):
        """Set up the QApplication for testing."""
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.test_dir = Path(tempfile.mkdtemp())
        self.notification_manager = NotificationManager(self.test_dir)
        
        # Mock the QSystemTrayIcon to prevent actual UI interactions
        self.notification_manager._tray_icon = MagicMock(spec=QSystemTrayIcon)
        
        # Sample alert data
        self.alert_data = {
            "alert_id": "test_alert_1",
            "title": "Test Alert",
            "message": "This is a test alert",
            "severity": AlertSeverity.WARNING,
            "alert_type": AlertType.WEATHER,
        }

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up the temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            
        # Stop and delete the cleanup timer
        if hasattr(self.notification_manager, '_cleanup_timer'):
            self.notification_manager._cleanup_timer.stop()
            del self.notification_manager._cleanup_timer

    def test_initialization(self):
        """Test that NotificationManager initializes correctly."""
        self.assertTrue(self.notification_manager.notifications_dir.exists())
        self.assertTrue(self.notification_manager.settings_file.exists())
        self.assertIsInstance(self.notification_manager._cleanup_timer, QTimer)

    def test_show_notification(self):
        """Test showing a notification."""
        # Test with minimal parameters
        alert_id = self.notification_manager.show_notification(
            "Test Title", "Test Message"
        )
        self.assertIsNotNone(alert_id)
        self.assertIn(alert_id, self.notification_manager._alerts)
        
        # Test with all parameters
        custom_id = "custom_alert_123"
        alert_id = self.notification_manager.show_notification(
            "Test Title",
            "Test Message",
            alert_type="warning",
            alert_id=custom_id,
            duration=5000,
        )
        self.assertEqual(alert_id, custom_id)
        self.assertIn(custom_id, self.notification_manager._alerts)

    def test_show_alert(self):
        """Test showing an alert from a WeatherAlert object or dict."""
        # Test with WeatherAlert object
        alert = WeatherAlert(
            "test_alert_2",
            "Test Alert 2",
            "Another test alert",
            AlertSeverity.INFO,
            AlertType.TEMPERATURE,
        )
        alert_id = self.notification_manager.show_alert(alert)
        self.assertEqual(alert_id, alert.id)
        self.assertIn(alert.id, self.notification_manager._alerts)
        
        # Test with dictionary
        alert_dict = {
            "id": "test_alert_3",
            "title": "Test Alert 3",
            "message": "Alert from dict",
            "severity": "EMERGENCY",
            "alert_type": "severe",
            "start_time": datetime.utcnow().isoformat(),
            "end_time": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        alert_id = self.notification_manager.show_alert(alert_dict)
        self.assertEqual(alert_id, alert_dict["id"])
        self.assertIn(alert_dict["id"], self.notification_manager._alerts)

    def test_dismiss_alert(self):
        """Test dismissing an alert."""
        # Add an alert
        alert_id = self.notification_manager.show_notification(
            "Test Dismiss", "Dismiss me"
        )
        self.assertIn(alert_id, self.notification_manager._alerts)
        
        # Dismiss the alert
        self.notification_manager.dismiss_alert(alert_id)
        self.assertNotIn(alert_id, self.notification_manager._alerts)
        
        # Test dismissing non-existent alert (should not raise)
        self.notification_manager.dismiss_alert("non_existent_id")

    def test_toggle_mute(self):
        """Test toggling mute state."""
        initial_state = self.notification_manager._muted
        
        # Toggle mute
        self.notification_manager.toggle_mute()
        self.assertEqual(self.notification_manager._muted, not initial_state)
        
        # Toggle back
        self.notification_manager.toggle_mute()
        self.assertEqual(self.notification_manager._muted, initial_state)

    def test_cleanup_expired_alerts(self):
        """Test cleanup of expired alerts."""
        # Add an expired alert
        expired_alert = WeatherAlert(
            "expired_alert",
            "Expired",
            "This alert has expired",
            AlertSeverity.INFO,
            AlertType.OTHER,
            start_time=datetime.utcnow() - timedelta(days=2),
            end_time=datetime.utcnow() - timedelta(days=1),
        )
        self.notification_manager._alerts[expired_alert.id] = expired_alert
        
        # Add a non-expired alert
        active_alert = WeatherAlert(
            "active_alert",
            "Active",
            "This alert is active",
            AlertSeverity.INFO,
            AlertType.OTHER,
        )
        self.notification_manager._alerts[active_alert.id] = active_alert
        
        # Run cleanup
        self.notification_manager._cleanup_expired_alerts()
        
        # Verify only the active alert remains
        self.assertNotIn(expired_alert.id, self.notification_manager._alerts)
        self.assertIn(active_alert.id, self.notification_manager._alerts)

    @patch('script.notifications.QMessageBox')
    def test_show_notification_history(self, mock_message_box_class):
        """Test showing notification history."""
        # Create a mock for the QMessageBox instance
        mock_msg_box = MagicMock()
        mock_message_box_class.return_value = mock_msg_box
        
        # Add some test alerts
        for i in range(3):
            self.notification_manager.show_notification(
                f"Test {i}", f"Message {i}", alert_type="info"
            )
        
        # Show history
        self.notification_manager.show_notification_history()
        
        # Verify QMessageBox was instantiated
        mock_message_box_class.assert_called_once()
        
        # Check that the message box methods were called with expected arguments
        mock_msg_box.setIcon.assert_called_once()
        mock_msg_box.setWindowTitle.assert_called_once_with("Weather Alerts")
        
        # Get the text that was set on the message box
        set_text_call = mock_msg_box.setText.call_args[0][0]
        
        # Verify all test alerts are in the message
        for i in range(3):
            self.assertIn(f"Test {i}", set_text_call)
            self.assertIn(f"Message {i}", set_text_call)
        
        # Verify the exec method was called
        mock_msg_box.exec.assert_called_once()


if __name__ == "__main__":
    unittest.main()
