# Translation Guide

This guide explains how to add or modify translations in the Weather App.

## Overview

The application uses a translation system that supports multiple languages. All translations are stored in `script/translations.py`.

## Available Languages

- English (EN)
- Italian (IT)
- Spanish (ES)
- Portuguese (PT)
- German (DE)
- French (FR)
- Russian (RU)
- Arabic (AR)
- Japanese (JA)

## Adding a New Language

1. Open `script/translations.py`
2. Add a new language dictionary with the language code (ISO 639-1) as the key
3. Copy all translation keys from the English dictionary
4. Translate each value to the target language
5. Update the `available_languages` list in the `TranslationsManager` class

### Example:

```python
'FR': {  # French
    'city': 'Ville:',
    'search': 'Rechercher',
    # ... other translations
}
```

## Translation Keys

Each key in the translation dictionary corresponds to a UI element or message. The keys are organized by functionality:

### UI Elements
- `city`: City input label
- `search`: Search button text
- `theme`: Theme selection label
- `favorites`: Favorites menu label
- `current_weather`: Current weather section header
- `forecast`: Forecast section header

### Messages
- `invalid_city_warning`: Invalid city name message
- `settings_saved`: Confirmation when settings are saved
- `could_not_fetch`: Error when weather data cannot be retrieved

### Help System
- `help_title`: Help window title
- `help_usage_text`: Main help text
- `help_features_text`: Features description
- `help_tips_text`: Tips and troubleshooting

## Best Practices

1. **Consistency**: Use consistent terminology throughout the translation
2. **Context**: Maintain the same level of formality as the original text
3. **Variables**: Preserve any variables (like `{0}`, `{1}`) in their original positions
4. **Special Characters**: Ensure proper encoding for special characters
5. **Length**: Be mindful of text expansion/contraction in different languages

## Testing Translations

1. After adding or modifying translations, test the application in the target language
2. Check for:
   - Text overflow in UI elements
   - Proper alignment of right-to-left (RTL) languages like Arabic
   - Correct display of special characters
   - Proper date/number formatting

## Right-to-Left (RTL) Support

For RTL languages like Arabic and Hebrew:

1. The application automatically detects RTL languages
2. UI elements are mirrored for RTL languages
3. Text alignment is set to right-aligned

## Contributing Translations

1. Fork the repository
2. Add or update translations
3. Submit a pull request with a clear description of the changes
4. Include the language code in the PR title (e.g., "[FR] Update French translations")

## Troubleshooting

### Common Issues

- **Missing Translations**: If a key is missing, the English text will be shown
- **Encoding Issues**: Ensure the file is saved with UTF-8 encoding
- **Special Characters**: Use proper Unicode characters for accented letters and symbols

### Debugging

To see which translation keys are being used:

1. Set the log level to DEBUG
2. Look for log messages containing "Translation key"
3. Missing keys will be logged as warnings

## Translation Tools

Consider using these tools for managing translations:

- [Poedit](https://poedit.net/) - Translation editor
- [OmegaT](https://omegat.org/) - Computer-assisted translation tool
- [Crowdin](https://crowdin.com/) - Cloud-based localization platform

## License

By contributing translations, you agree to license your work under the same [GPLv3 license](LICENSE) as the rest of the project.
