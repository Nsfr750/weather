"""
Tests for the UI module.
"""
import pytest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt

# Import the module to test
from script.ui import MainWindow  # Adjust import path as needed

class TestUI:
    """Test cases for the UI module."""
    
    @pytest.fixture
    def app(self):
        """Create a QApplication instance for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        app.quit()
    
    @pytest.fixture
    def main_window(self, app):
        """Create a main window for testing."""
        with patch('script.ui.sys') as _:
            return MainWindow()
    
    def test_initialization(self, main_window):
        """Test that the main window initializes correctly."""
        assert main_window is not None
        assert main_window.windowTitle() == "Weather App"  # Update with actual title
    
    def test_ui_elements_exist(self, main_window):
        """Test that all expected UI elements exist."""
        # This is a basic example - update with actual UI elements from your MainWindow
        assert hasattr(main_window, 'statusBar')
        assert hasattr(main_window, 'menuBar')
        
        # Example of checking for specific widgets
        # assert hasattr(main_window, 'some_widget')
    
    def test_status_bar_message(self, main_window):
        """Test that status bar messages can be set."""
        test_message = "Test message"
        main_window.statusBar().showMessage(test_message)
        assert main_window.statusBar().currentMessage() == test_message

if __name__ == "__main__":
    pytest.main()
