import json
import os
from pathlib import Path

# Define the directory containing translation files
TRANSLATIONS_DIR = Path(__file__).parent.parent / 'lang' / 'translations'

# Define the reference language (Italian)
REF_LANG = 'it'

# Menu-related keys that should exist in all language files
MENU_KEYS = [
    "file_menu", "favorites_menu", "settings_menu", "view_menu", "language_menu",
    "help_menu", "mode_menu", "units_menu", "about_menu", "add_favorite_menu",
    "manage_favorites_menu", "api_key_manager_menu", "app_settings_menu",
    "check_updates_menu", "documentation_menu", "view_logs_menu", "sponsor_menu",
    "exit_menu"
]

def load_translations(lang_code):
    """Load translations for a specific language."""
    file_path = TRANSLATIONS_DIR / f"{lang_code}.json"
    if not file_path.exists():
        print(f"Warning: {file_path} does not exist")
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def save_translations(lang_code, data):
    """Save translations back to file."""
    file_path = TRANSLATIONS_DIR / f"{lang_code}.json"
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write('\n')  # Add newline at end of file
        print(f"Updated {file_path}")
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

def get_reference_translations():
    """Get reference translations from Italian file."""
    ref_translations = {}
    ref_data = load_translations(REF_LANG)
    
    for key in MENU_KEYS:
        if key in ref_data:
            ref_translations[key] = ref_data[key]
    
    return ref_translations

def update_language_file(lang_code, ref_translations):
    """Update a single language file with missing menu translations."""
    if lang_code == REF_LANG:
        print(f"Skipping reference language: {lang_code}")
        return False
    
    translations = load_translations(lang_code)
    if not translations:
        print(f"Skipping empty or invalid file: {lang_code}.json")
        return False
    
    updated = False
    for key, value in ref_translations.items():
        if key not in translations:
            # For non-English files, add the key with an empty string
            # The user can fill in the translations later
            translations[key] = "" if lang_code != 'en' else key.replace('_', ' ').title()
            updated = True
            print(f"  Added missing key: {key}")
    
    if updated:
        return save_translations(lang_code, translations)
    
    print(f"No updates needed for {lang_code}.json")
    return False

def main():
    print("Adding missing menu translations...")
    
    # Get reference translations from Italian file
    ref_translations = get_reference_translations()
    if not ref_translations:
        print(f"Error: Could not load reference translations from {REF_LANG}.json")
        return
    
    print(f"Using reference translations from {REF_LANG}.json")
    
    # Process all language files
    for file_path in TRANSLATIONS_DIR.glob("*.json"):
        lang_code = file_path.stem
        print(f"\nProcessing {lang_code}.json:")
        update_language_file(lang_code, ref_translations)
    
    print("\nDone! Please review the changes and add translations for the empty strings.")

if __name__ == "__main__":
    main()
