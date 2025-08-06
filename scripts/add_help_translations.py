"""
Script to add missing help dialog translation keys to all language files.
"""

import json
import os
from pathlib import Path

# Define the base directory
BASE_DIR = Path(__file__).parent.parent
LANG_DIR = BASE_DIR / "lang" / "translations"

# Define the help dialog keys and their default English values
HELP_KEYS = {
    "help_title": "Help - Weather Application",
    "help_usage_tab": "Usage",
    "help_usage_text": "<h2>How to Use the Application</h2>\n<p>1. Enter a city name in the search bar and press Enter or click the search button.</p>\n<p>2. View current weather conditions in the main display.</p>\n<p>3. Use the tabs to switch between current weather, hourly forecasts, and 7-day forecasts.</p>\n<p>4. Add locations to favorites for quick access.</p>",
    "help_features_tab": "Features",
    "help_features_text": "<h2>Application Features</h2>\n<ul>\n  <li>Current weather conditions with detailed information</li>\n  <li>Hourly and 7-day forecasts</li>\n  <li>Weather maps and radar (when online)</li>\n  <li>Support for multiple locations with favorites</li>\n  <li>Customization of units and display options</li>\n  <li>Offline mode for previously viewed locations</li>\n</ul>",
    "help_tips_tab": "Tips",
    "help_tips_text": "<h2>Helpful Tips</h2>\n<ul>\n  <li>Press F5 or use the refresh button to update weather data.</li>\n  <li>Right-click on the map to add a custom location.</li>\n  <li>Use the settings menu to customize the application to your preferences.</li>\n  <li>Enable notifications to receive weather alerts for your location.</li>\n  <li>Check the log viewer if you encounter any issues.</li>\n</ul>",
    "help_close_btn": "Close",
    "select_language": "Select Language"
}

# Language-specific overrides (for non-English languages)
LANGUAGE_OVERRIDES = {
    "de": {
        "help_title": "Hilfe - Wetteranwendung",
        "help_usage_tab": "Verwendung",
        "help_features_tab": "Funktionen",
        "help_tips_tab": "Tipps",
        "help_close_btn": "Schließen",
        "select_language": "Sprache auswählen"
    },
    "es": {
        "help_title": "Ayuda - Aplicación del Tiempo",
        "help_usage_tab": "Uso",
        "help_features_tab": "Características",
        "help_tips_tab": "Consejos",
        "help_close_btn": "Cerrar",
        "select_language": "Seleccionar idioma"
    },
    "fr": {
        "help_title": "Aide - Application Météo",
        "help_usage_tab": "Utilisation",
        "help_features_tab": "Fonctionnalités",
        "help_tips_tab": "Conseils",
        "help_close_btn": "Fermer",
        "select_language": "Sélectionner la langue"
    },
    "it": {
        # Already has these translations
    },
    "ja": {
        "help_title": "ヘルプ - 天気アプリ",
        "help_usage_tab": "使い方",
        "help_features_tab": "機能",
        "help_tips_tab": "ヒント",
        "help_close_btn": "閉じる",
        "select_language": "言語を選択"
    },
    "ko": {
        "help_title": "도움말 - 날씨 앱",
        "help_usage_tab": "사용 방법",
        "help_features_tab": "기능",
        "help_tips_tab": "팁",
        "help_close_btn": "닫기",
        "select_language": "언어 선택"
    },
    "nl": {
        "help_title": "Help - Weer App",
        "help_usage_tab": "Gebruik",
        "help_features_tab": "Functies",
        "help_tips_tab": "Tips",
        "help_close_btn": "Sluiten",
        "select_language": "Taal selecteren"
    },
    "pl": {
        "help_title": "Pomoc - Aplikacja Pogodowa",
        "help_usage_tab": "Użycie",
        "help_features_tab": "Funkcje",
        "help_tips_tab": "Wskazówki",
        "help_close_btn": "Zamknij",
        "select_language": "Wybierz język"
    },
    "pt": {
        "help_title": "Ajuda - Aplicativo de Clima",
        "help_usage_tab": "Uso",
        "help_features_tab": "Recursos",
        "help_tips_tab": "Dicas",
        "help_close_btn": "Fechar",
        "select_language": "Selecionar idioma"
    },
    "ru": {
        "help_title": "Справка - Приложение Погода",
        "help_usage_tab": "Использование",
        "help_features_tab": "Функции",
        "help_tips_tab": "Советы",
        "help_close_btn": "Закрыть",
        "select_language": "Выбрать язык"
    },
    "tr": {
        "help_title": "Yardım - Hava Durumu Uygulaması",
        "help_usage_tab": "Kullanım",
        "help_features_tab": "Özellikler",
        "help_tips_tab": "İpuçları",
        "help_close_btn": "Kapat",
        "select_language": "Dil Seçin"
    },
    "zh": {
        "help_title": "帮助 - 天气应用",
        "help_usage_tab": "使用说明",
        "help_features_tab": "功能",
        "help_tips_tab": "提示",
        "help_close_btn": "关闭",
        "select_language": "选择语言"
    },
    "ar": {
        "help_title": "مساعدة - تطبيق الطقس",
        "help_usage_tab": "طريقة الاستخدام",
        "help_features_tab": "الميزات",
        "help_tips_tab": "نصائح",
        "help_close_btn": "إغلاق",
        "select_language": "اختر اللغة"
    },
    "he": {
        "help_title": "עזרה - אפליקציית מזג אוויר",
        "help_usage_tab": "שימוש",
        "help_features_tab": "תכונות",
        "help_tips_tab": "טיפים",
        "help_close_btn": "סגור",
        "select_language": "בחר שפה"
    },
    "hu": {
        "help_title": "Súgó - Időjárás alkalmazás",
        "help_usage_tab": "Használat",
        "help_features_tab": "Funkciók",
        "help_tips_tab": "Tippek",
        "help_close_btn": "Bezárás",
        "select_language": "Nyelv kiválasztása"
    }
}

def process_language_file(lang_code):
    """Process a single language file."""
    file_path = LANG_DIR / f"{lang_code}.json"
    
    # Skip if file doesn't exist (except for English which should be our base)
    if not file_path.exists():
        print(f"Skipping {file_path} - file not found")
        return
    
    print(f"Processing {file_path}...")
    
    # Load existing translations
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            translations = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  Error loading {file_path}: {e}")
            return
    
    # Track if we made any changes
    changes_made = False
    
    # Add or update each help key
    for key, default_value in HELP_KEYS.items():
        # Skip if key already exists
        if key in translations:
            continue
        
        # Check for language-specific override
        if lang_code in LANGUAGE_OVERRIDES and key in LANGUAGE_OVERRIDES[lang_code]:
            translations[key] = LANGUAGE_OVERRIDES[lang_code][key]
        else:
            # Use English as default for other languages
            translations[key] = default_value if lang_code == "en" else key
        
        changes_made = True
        print(f"  Added/updated: {key}")
    
    # Only write back if we made changes
    if changes_made:
        # Create a new ordered dict with keys in a logical order
        new_translations = {}
        
        # Add existing keys in original order, then new help keys
        help_keys_added = set()
        
        # First, add all existing keys
        for key in translations:
            if key not in HELP_KEYS:
                new_translations[key] = translations[key]
            elif key not in help_keys_added:
                help_keys_added.add(key)
        
        # Then add any new help keys that weren't in the original file
        for key in HELP_KEYS:
            if key in translations and key not in help_keys_added:
                new_translations[key] = translations[key]
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_translations, f, ensure_ascii=False, indent=2, sort_keys=False)
            f.write("\n")  # Add newline at end of file
        
        print(f"  Updated {file_path}")
    else:
        print("  No changes needed")

def main():
    """Main function to process all language files."""
    # Ensure the translations directory exists
    if not LANG_DIR.exists():
        print(f"Error: Directory not found: {LANG_DIR}")
        return
    
    # Process each language file
    for lang_file in sorted(LANG_DIR.glob("*.json")):
        lang_code = lang_file.stem
        process_language_file(lang_code)

if __name__ == "__main__":
    main()
