"""
translations_utils.py
Utility class for managing translations and language switching in a modular way.
"""
from PyQt6.QtCore import QObject, pyqtSignal

class TranslationsManager(QObject):
    # Signal emitted when language is changed
    language_changed = pyqtSignal(str)
    
    def __init__(self, translations_dict, default_lang='EN'):
        super().__init__()
        # Convert all language codes to uppercase for consistency
        self.translations = {k.upper(): v for k, v in translations_dict.items()}
        self.default_lang = default_lang.upper()
        self._current_lang = self.default_lang

    def t(self, key, lang=None):
        lang = (lang or self._current_lang).upper()
        return self.translations.get(lang, {}).get(key, self.translations.get(self.default_lang, {}).get(key, key))

    def available_languages(self):
        return list(self.translations.keys())

    def set_default_lang(self, lang):
        lang = lang.upper()
        if lang != self._current_lang and lang in self.translations:
            self._current_lang = lang
            self.language_changed.emit(lang)
            return True
        return False

    def set_language(self, lang):
        """Set the current language and emit signal if changed."""
        return self.set_default_lang(lang)
        
    def get_current_language(self):
        """Get the current language code."""
        return self._current_lang
