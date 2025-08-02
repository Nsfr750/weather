"""
Script to update import statements in legacy provider modules.

This script updates the import of WeatherData in all legacy provider modules
to use the correct path from the plugin system.
"""

import os
import re
from pathlib import Path

# Directory containing the legacy provider modules
PROVIDERS_DIR = Path("script/weather_providers")

# Pattern to find the old import statement
OLD_IMPORT_PATTERN = r'from\s+\.base_provider\s+import\s+BaseProvider(?:\s*,\s*WeatherData\s*)?'
REPLACEMENT = 'from .base_provider import BaseProvider\nfrom script.plugin_system.weather_provider import WeatherDataPoint as WeatherData'

def update_file(file_path):
    """Update the import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already updated
        if 'from script.plugin_system.weather_provider import WeatherDataPoint as WeatherData' in content:
            print(f"Skipping {file_path} - already updated")
            return False
            
        # Replace the import statement
        new_content, count = re.subn(
            OLD_IMPORT_PATTERN,
            REPLACEMENT,
            content,
            flags=re.MULTILINE
        )
        
        if count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {file_path}")
            return True
        else:
            print(f"No changes needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Update all legacy provider modules."""
    updated_count = 0
    total_files = 0
    
    # Process all Python files in the providers directory
    for file_path in PROVIDERS_DIR.glob("*.py"):
        # Skip __init__.py and base_provider.py
        if file_path.name in ("__init__.py", "base_provider.py"):
            continue
            
        total_files += 1
        if update_file(file_path):
            updated_count += 1
    
    print(f"\nUpdated {updated_count} of {total_files} provider files.")

if __name__ == "__main__":
    main()
