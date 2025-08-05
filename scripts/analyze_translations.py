"""
Script to analyze Python files for translatable strings and update language files.
"""

import json
import re
from pathlib import Path
from typing import Dict, Set, List, Tuple

# Configuration
SCRIPT_DIR = Path(__file__).parent / "script"
LANG_DIR = Path(__file__).parent / "lang"
TRANSLATIONS_DIR = LANG_DIR / "translations"
REFERENCE_LANG = "it"

# Regular expression to find translation patterns
translation_patterns = [
    # Matches: _tr("string")
    re.compile(r'_tr\(["\'](.*?)["\']\)'),
    # Matches: self.tr("string")
    re.compile(r'self\.tr\(["\'](.*?)["\']\)'),
    # Matches: QApplication.translate("context", "string")
    re.compile(r'QApplication\.translate\([\w"]+\s*,\s*["\'](.*?)["\']\)'),
]

def load_translations(lang_code: str) -> Dict[str, str]:
    """Load translations for a specific language."""
    file_path = TRANSLATIONS_DIR / f"{lang_code}.json"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_translations(lang_code: str, data: Dict[str, str]):
    """Save translations back to file with proper formatting."""
    file_path = TRANSLATIONS_DIR / f"{lang_code}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def find_translatable_strings() -> Set[str]:
    """Find all potentially translatable strings in Python files."""
    strings = set()
    
    for py_file in SCRIPT_DIR.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # Skip files that are part of the standard library or virtual environment
            if 'site-packages' in str(py_file) or 'venv' in str(py_file):
                continue
                
            for pattern in translation_patterns:
                for match in pattern.finditer(content):
                    # Get the first group which contains the actual string
                    string = match.group(1)
                    # Clean up the string (remove escaped quotes)
                    string = string.replace('\\"', '"').replace("\\'", "'")
                    if string:  # Only add non-empty strings
                        strings.add(string)
                        
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
    
    return strings

def update_translations():
    """Update all translation files with missing keys."""
    # Find all translatable strings in the codebase
    code_strings = find_translatable_strings()
    print(f"Found {len(code_strings)} potentially translatable strings in the codebase.")
    
    # Get all available language files
    lang_files = list(TRANSLATIONS_DIR.glob("*.json"))
    print(f"Found {len(lang_files)} language files.")
    
    # Process each language file
    for lang_file in lang_files:
        lang_code = lang_file.stem
        print(f"\nProcessing language: {lang_code}")
        
        # Load existing translations
        translations = load_translations(lang_code)
        original_count = len(translations)
        
        # Add any missing strings
        for string in code_strings:
            if string not in translations:
                # For non-reference languages, use the string as is (can be translated later)
                # For the reference language, use the string as both key and value
                translations[string] = string if lang_code == REFERENCE_LANG else ""
        
        # Only save if there were changes
        if len(translations) > original_count:
            save_translations(lang_code, translations)
            print(f"  - Added {len(translations) - original_count} new strings to {lang_code}.json")
        else:
            print(f"  - No new strings to add to {lang_code}.json")

if __name__ == "__main__":
    print("Starting translation analysis...")
    update_translations()
    print("\nTranslation analysis complete!")
