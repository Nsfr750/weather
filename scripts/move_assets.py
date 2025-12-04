#!/usr/bin/env python3
"""
Move assets folder and update file references.
"""

import os
import shutil
from pathlib import Path

def move_assets():
    """Move assets folder and update file references."""
    current_dir = Path(__file__).parent.parent
    source_dir = current_dir / 'assets'
    dest_dir = current_dir / 'script' / 'assets'
    
    # Create destination directory if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Move files from assets to script/assets
    for item in source_dir.glob('*'):
        if item.is_file():
            shutil.copy2(item, dest_dir / item.name)
        elif item.is_dir():
            dest_subdir = dest_dir / item.name
            if dest_subdir.exists():
                shutil.rmtree(dest_subdir)
            shutil.copytree(item, dest_subdir)
    
    # Update file paths in Python files
    update_file_paths(current_dir, 'script')
    
    print("Assets moved and file paths updated successfully!")

def update_file_paths(root_dir: Path, script_dir_name: str):
    """Update file paths in Python files to use the new assets location."""
    # Files that need path updates
    files_to_update = [
        'main.py',
        'script/menu.py',
        'script/maps_dialog.py',
        'script/ui.py',
        'script/notifications.py',
        'script/about.py',
        'scripts/download_weather_icons.py'
    ]
    
    replacements = {
        'assets/': f'{script_dir_name}/assets/',
        "Path('assets/": f"Path('{script_dir_name}/assets/",
        '"assets/': f'"{script_dir_name}/assets/'
    }
    
    for file_path in files_to_update:
        file_path = root_dir / file_path
        if not file_path.exists():
            print(f"Warning: File not found: {file_path}")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        updated = False
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                updated = True
                
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")

if __name__ == "__main__":
    move_assets()
