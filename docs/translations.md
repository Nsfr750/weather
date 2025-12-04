# Translation Guide

This guide explains how to add or modify translations in the Weather App. The application uses a comprehensive translation system that supports multiple languages and right-to-left (RTL) text direction.

## Available Languages

The Weather App currently supports the following languages:

| Language | Code | Native Name | RTL | Status |
|----------|------|-------------|-----|--------|
| English | en   | English     | No  | Complete |
| Spanish | es   | Español     | No  | Complete |
| French  | fr   | Français    | No  | Complete |
| German  | de   | Deutsch     | No  | Complete |
| Italian | it   | Italiano    | No  | Complete |
| Portuguese | pt   | Português   | No  | Complete |
| Russian | ru   | Русский     | No  | Complete |
| Japanese | ja   | 日本語      | No  | Complete |
| Korean  | ko   | 한국어      | No  | Complete |
| Arabic  | ar   | اَلْعَرَبِيَّةُ | Yes | Complete |
| Hebrew  | he   | עברית      | Yes | Complete |
| Hungarian | hu  | Magyar      | No  | Complete |
| Polish  | pl   | Polski      | No  | Complete |
| Turkish | tr   | Türkçe      | No  | Complete |
| Dutch   | nl   | Nederlands  | No  | Complete |
| Chinese (Simplified) | zh | 简体中文   | No  | Complete |

## Language Menu Implementation

The language menu automatically displays available languages using the following logic:

1. It first tries to load language names from the current UI language's translation file
2. If not found, it falls back to English names
3. As a last resort, it uses a built-in dictionary of common language names

### Language Name Keys

Each translation file should include language names for all supported languages using the pattern `language_XX` where `XX` is the language code. For example:

- `language_en`: "English"
- `language_es": "Español"
- `language_fr": "Français"

### Menu Text

Each translation file should also include these UI-specific keys:

- `language_menu`: The menu title (e.g., "Language")
- `language_tip`: Tooltip text for the language menu

## Translation System

The translation system is based on JSON files and includes these features:

- String interpolation with variables
- Right-to-left (RTL) language support
- Fallback to English for missing translations
- Dynamic language switching without app restart
- Optimized loading with translation memory

### File Structure

```text
lang/
├── __init__.py
├── language_manager.py    # Core translation management
└── translations/
    ├── en.json           # English (base language)
    ├── it.json           # Italian
    ├── es.json           # Spanish
    ├── fr.json           # French
    ├── de.json           # German
    ├── pt.json           # Portuguese
    ├── ru.json           # Russian
    ├── ja.json           # Japanese
    ├── ko.json           # Korean
    ├── zh.json           # Chinese (Simplified)
    ├── ar.json           # Arabic (RTL)
    ├── he.json           # Hebrew (RTL)
    ├── hu.json           # Hungarian
    ├── pl.json           # Polish
    ├── tr.json           # Turkish
    └── nl.json           # Dutch
```

## Adding a New Language

To add a new language:

1. Add a new JSON file in `lang/translations/` with the language code (e.g., `fr.json` for French)
2. Copy all keys from `en.json`
3. Translate all values to the target language
4. Add the language name in its own language (e.g., `"language_fr": "Français"`)
5. Add the language to the language menu by including these keys:
   - `language_menu`: The menu title (e.g., "Language")
   - `language_tip`: Tooltip text for the language menu (e.g., "Select application language")

Example for French (`fr.json`):

```json
{
  "language_menu": "&Langue",
  "language_tip": "Sélectionner la langue de l'application",
  "language_fr": "Français",
  "language_en": "Anglais",
  "language_es": "Espagnol"
  // ... other translations
}
```

## Best Practices

1. **Consistency**
   - Use consistent terminology throughout the app
   - Maintain the same tone and style
   - Follow the language's standard date/time/number formats

2. **Variables**
   - Use `{variable}` syntax for dynamic content
   - Keep variables in the same position as the source language when possible
   - Document expected variable types and formats

3. **Pluralization**
   - Use the `_plural` key for plural forms
   - Follow the language's plural rules

   ```python
   {
       'hour': '{count} hour',
       'hour_plural': '{count} hours',
       'minute': '{count} minute',
       'minute_plural': '{count} minutes',
   }
   ```

4. **Special Characters**
   - Use proper Unicode characters for accented letters and symbols
   - Ensure proper encoding (UTF-8)
   - Test special characters on all platforms

5. **Length Considerations**
   - Account for text expansion (some languages are 30-40% longer than English)
   - Keep UI elements flexible to accommodate different text lengths
   - Test UI with the longest translations

## Right-to-Left (RTL) Support

For RTL languages like Arabic and Hebrew:

1. Set `is_rtl = True` in the language configuration
2. The application will automatically:
   - Mirror the UI layout
   - Set text alignment to right
   - Adjust scrollbars and other UI elements

## Testing Translations

1. **Visual Testing**
   - Check for text overflow
   - Verify proper alignment
   - Test with different font sizes

2. **Functional Testing**
   - Test all UI elements with the target language
   - Verify date, time, and number formatting
   - Check RTL support if applicable

3. **Automated Tests**
   - Run the test suite with the new language
   - Check for missing translations
   - Verify variable substitution

## Contributing Translations

1. Fork the repository
2. Create a new branch for your translation
3. Add or update the translation files
4. Submit a pull request with a clear description

## Troubleshooting

### Common Issues

- **Missing Translations**: Fall back to English
- **Text Overflow**: Adjust UI elements or shorten translations
- **Special Characters**: Ensure proper encoding and font support

## Getting Help

For translation issues, please open an issue on our [GitHub repository](https://github.com/yourusername/weather-app/issues).
