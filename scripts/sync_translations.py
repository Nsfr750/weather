#!/usr/bin/env python3
"""
Sync translation files using it.json as the reference.

This script ensures all language files have the same keys as it.json,
adding any missing keys with empty strings as placeholders.
"""
import json
import os
from pathlib import Path

# Path to the translations directory
TRANSLATIONS_DIR = Path(__file__).parent.parent / 'lang' / 'translations'
REFERENCE_LANG = 'it.json'
TARGET_LANGUAGES = [
    'ar.json',  # Arabic
    'de.json',  # German
    'en.json',  # English
    'es.json',  # Spanish
    'fr.json',  # French
    'ja.json',  # Japanese
    'pt.json',  # Portuguese
    'ru.json'   # Russian
]

def load_json_file(file_path):
    """Load a JSON file and return its content as a dictionary."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def save_json_file(file_path, data):
    """Save data to a JSON file with proper formatting."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write('\n')  # Add newline at end of file
        print(f"Updated {file_path}")
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

def sync_translations():
    """Sync all language files with the reference language file."""
    # Load reference file
    ref_path = TRANSLATIONS_DIR / REFERENCE_LANG
    if not ref_path.exists():
        print(f"Error: Reference file {ref_path} not found")
        return False
    
    reference = load_json_file(ref_path)
    if not reference:
        print("Error: Could not load reference translations")
        return False
    
    print(f"Loaded reference: {REFERENCE_LANG} ({len(reference)} keys)")
    
    # Process each target language file
    for lang_file in TARGET_LANGUAGES:
        if lang_file == REFERENCE_LANG:
            continue  # Skip the reference file
            
        lang_path = TRANSLATIONS_DIR / lang_file
        
        # Load existing translations if file exists
        if lang_path.exists():
            translations = load_json_file(lang_path)
            if translations is None:
                print(f"Skipping {lang_file} due to load error")
                continue
            print(f"Processing {lang_file} (has {len(translations)} keys)")
        else:
            print(f"Creating new translation file: {lang_file}")
            translations = {}
        
        # Add missing keys from reference
        updated = False
        for key, value in reference.items():
            if key not in translations:
                translations[key] = ""  # Add empty string as placeholder
                updated = True
        
        # Save updated translations if there were changes
        if updated:
            save_json_file(lang_path, translations)
        else:
            print(f"No updates needed for {lang_file}")
    
    print("\nTranslation sync complete!")
    return True

if __name__ == "__main__":
    sync_translations()
