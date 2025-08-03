"""
translations_utils.py
Utility class for managing translations and language switching in a modular way.
"""

class TranslationsManager:
    def __init__(self, translations_dict, default_lang='IT'):
        # Convert all language codes to uppercase for consistency
        self.translations = {k.upper(): v for k, v in translations_dict.items()}
        self.default_lang = default_lang.upper()

    def t(self, key, lang=None):
        lang = (lang or self.default_lang).upper()
        return self.translations.get(lang, {}).get(key, self.translations.get(self.default_lang, {}).get(key, key))

    def available_languages(self):
        return list(self.translations.keys())

    def set_default_lang(self, lang):
        self.default_lang = lang.upper()

    def set_language(self, lang):
        """Alias for set_default_lang for better code readability."""
        self.set_default_lang(lang)
