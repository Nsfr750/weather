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
| Portuguese | pt   | Português | No  | Complete |
| Russian | ru   | Русский     | No  | Complete |
| Japanese | ja   | 日本語      | No  | Complete |
| Chinese (Simplified) | zh-CN | 简体中文 | No  | In Progress  |
| Arabic  | ar   | اَلْعَرَبِيَّةُ | Yes | Complete |
| Hindi   | hi   | हिन्दी      | No  | In Progress |
| Korean  | ko   | 한국어      | No  | In Progress |
| Turkish | tr   | Türkçe      | No  | In Progress |
| Dutch   | nl   | Nederlands  | No  | In Progress |
| Polish  | pl   | Polski      | No  | In Progress |

## Translation System (v1.7.0+)

The translation system is now based on JSON files and includes these features:
- String interpolation with variables
- Right-to-left (RTL) language support
- Fallback to English for missing translations
- Dynamic language switching without app restart
- Optimized loading with translation memory

### File Structure (New)

```
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
    └── ar.json           # Arabic (RTL)
```

## Adding a New Language

1. **Add Language Code**
   - Add a new language code to the `LANGUAGES` dictionary in `script/lang/__init__.py`
   - Specify if the language is RTL

2. **Create Translations**
   - Add a new language dictionary in `script/lang/translations.py`
   - Copy all keys from the English dictionary
   - Translate all values to the target language

3. **Register the Language**
   - Add the language to the `available_languages` list in the `LanguageManager` class

### Example: Adding German

```python
# In script/lang/translations.py

translations = {
    # ... other languages
    
    'de': {  # German
        'app_name': 'Wetter App',
        'search': 'Suchen',
        'current_weather': 'Aktuelles Wetter',
        'forecast': 'Vorhersage',
        'temperature': 'Temperatur',
        'humidity': 'Luftfeuchtigkeit',
        'wind_speed': 'Windgeschwindigkeit',
        'pressure': 'Luftdruck',
        # ... more translations
    },
}
```

## Translation Keys

### UI Elements

```python
{
    'search_placeholder': 'Search for a city...',
    'current_location': 'Current Location',
    'settings': 'Settings',
    'favorites': 'Favorites',
    'add_to_favorites': 'Add to Favorites',
    'remove_from_favorites': 'Remove from Favorites',
    'refresh': 'Refresh',
    'close': 'Close',
    'save': 'Save',
    'cancel': 'Cancel',
}
```

### Weather Data

```python
{
    'feels_like': 'Feels like',
    'wind': 'Wind',
    'precipitation': 'Precipitation',
    'visibility': 'Visibility',
    'uv_index': 'UV Index',
    'sunrise': 'Sunrise',
    'sunset': 'Sunset',
    'moon_phase': 'Moon Phase',
    'air_quality': 'Air Quality',
    'humidity': 'Humidity',
}
```

### Weather Conditions

```python
{
    'weather_clear': 'Clear',
    'weather_clouds': 'Clouds',
    'weather_rain': 'Rain',
    'weather_snow': 'Snow',
    'weather_thunderstorm': 'Thunderstorm',
    'weather_drizzle': 'Drizzle',
    'weather_mist': 'Mist',
    'weather_fog': 'Fog',
    'weather_tornado': 'Tornado',
}
```

### Days and Months

```python
{
    'monday': 'Monday',
    'tuesday': 'Tuesday',
    'wednesday': 'Wednesday',
    'thursday': 'Thursday',
    'friday': 'Friday',
    'saturday': 'Saturday',
    'sunday': 'Sunday',
    
    'january': 'January',
    'february': 'February',
    # ... other months
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

## Translation Tools

- [Poedit](https://poedit.net/): Popular translation editor
- [Transifex](https://www.transifex.com/): Collaborative translation platform
- [Crowdin](https://crowdin.com/): Localization management platform

## Troubleshooting

### Common Issues

- **Missing Translations**: Fall back to English
- **Text Overflow**: Adjust UI elements or shorten translations
- **RTL Issues**: Check the `rtl.py` module and CSS styles
- **Special Characters**: Ensure proper encoding and font support

## Getting Help

For translation-related questions or issues:
1. Check the [GitHub Issues](https://github.com/Nsfr750/weather/issues)
2. Join our [Discord](https://discord.gg/ryqNeuRYjD)
3. Contact the maintainers
