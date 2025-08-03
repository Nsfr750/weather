"""
Tests for the version module.
"""
import pytest
import importlib.util
from pathlib import Path

# Path to the version module
VERSION_MODULE_PATH = Path("script/version.py").resolve()

def import_version_module():
    """
    Dynamically import the version module.
    
    Returns:
        module: The imported version module
    """
    spec = importlib.util.spec_from_file_location("version", VERSION_MODULE_PATH)
    version = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version)
    return version

class TestVersion:
    """Test cases for the version module."""
    
    def test_version_format(self):
        """Test that version follows semantic versioning (semver)."""
        version = import_version_module()
        # Check that __version__ exists and is a string
        assert hasattr(version, "__version__")
        assert isinstance(version.__version__, str)
        
        # Check semver format (major.minor.patch)
        parts = version.__version__.split('.')
        assert len(parts) >= 3  # At least major.minor.patch
        
        # Check that all parts are numeric
        for part in parts:
            assert part.isdigit() or ('-' in part and part.split('-')[0].isdigit())
    
    def test_version_info(self):
        """Test that version_info exists and has the correct attributes."""
        version = import_version_module()
        # Check that version_info exists and is a namedtuple
        assert hasattr(version, "version_info")
        version_info = version.version_info
        
        # Check that all expected fields are present
        for field in ["major", "minor", "patch", "releaselevel", "serial"]:
            assert hasattr(version_info, field)
        
        # Check that the version string matches version_info
        assert version.__version__ == f"{version_info.major}.{version_info.minor}.{version_info.patch}"
    
    def test_version_file(self):
        """Test that the version file exists and has the correct format."""
        # Check that the version file exists
        assert VERSION_MODULE_PATH.exists(), f"Version file not found at {VERSION_MODULE_PATH}"
        
        # Read the file content
        content = VERSION_MODULE_PATH.read_text(encoding='utf-8')
        
        # Check for version string
        assert "__version__" in content
        
        # Check for version_info
        assert "version_info" in content
        
        # Check that it's using a namedtuple for version_info
        assert "namedtuple" in content or "collections.namedtuple" in content

if __name__ == "__main__":
    pytest.main()
