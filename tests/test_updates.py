"""
Tests for the updates module.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the module to test
from script.update import check_for_updates  # Adjust import path as needed

class TestUpdates:
    """Test cases for the updates module."""
    
    @pytest.fixture
    def mock_version_file(self, tmp_path):
        """Create a temporary version file for testing."""
        version_data = {
            "version": "1.0.0",
            "release_date": "2025-01-01",
            "changelog": "Initial release"
        }
        version_file = tmp_path / "version.json"
        version_file.write_text(json.dumps(version_data))
        return version_file
    
    @pytest.fixture
    def mock_latest_release(self):
        """Mock response for the latest GitHub release."""
        return {
            "tag_name": "v1.1.0",
            "published_at": "2025-02-01T00:00:00Z",
            "body": "New features and bug fixes"
        }
    
    @patch('script.update.requests.get')
    def test_check_for_updates_new_version(self, mock_get, mock_version_file, mock_latest_release):
        """Test that check_for_updates detects a new version."""
        # Mock the GitHub API response
        mock_response = Mock()
        mock_response.json.return_value = mock_latest_release
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the function
        result = check_for_updates(str(mock_version_file))
        
        # Verify the result
        assert result["update_available"] is True
        assert result["current_version"] == "1.0.0"
        assert result["latest_version"] == "1.1.0"
        assert "New features and bug fixes" in result["changelog"]
    
    @patch('script.update.requests.get')
    def test_check_for_updates_no_updates(self, mock_get, mock_version_file):
        """Test that check_for_updates handles no updates available."""
        # Mock the GitHub API response with the same version
        mock_response = Mock()
        mock_response.json.return_value = {
            "tag_name": "v1.0.0",
            "published_at": "2025-01-01T00:00:00Z",
            "body": "Initial release"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the function
        result = check_for_updates(str(mock_version_file))
        
        # Verify the result
        assert result["update_available"] is False
        assert result["current_version"] == "1.0.0"
        assert result["latest_version"] == "1.0.0"
    
    @patch('script.update.requests.get')
    def test_check_for_updates_network_error(self, mock_get, mock_version_file):
        """Test that check_for_updates handles network errors gracefully."""
        # Mock a network error
        mock_get.side_effect = Exception("Network error")
        
        # Call the function
        result = check_for_updates(str(mock_version_file))
        
        # Verify the result indicates an error
        assert "error" in result
        assert "Network error" in result["error"]

if __name__ == "__main__":
    pytest.main()
