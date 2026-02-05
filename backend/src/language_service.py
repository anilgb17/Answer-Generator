"""Language Service for managing multi-language support."""
from typing import List, Optional
from src.models import LanguageConfig
from src.exceptions import LanguageNotSupportedError


class LanguageService:
    """Service for managing language configurations and translations."""
    
    # Supported languages with their configurations
    _SUPPORTED_LANGUAGES = {
        'en': LanguageConfig(
            code='en',
            name='English',
            native_name='English',
            font_family='Arial, Helvetica, sans-serif',
            rtl=False
        ),
        'es': LanguageConfig(
            code='es',
            name='Spanish',
            native_name='Español',
            font_family='Arial, Helvetica, sans-serif',
            rtl=False
        ),
        'fr': LanguageConfig(
            code='fr',
            name='French',
            native_name='Français',
            font_family='Arial, Helvetica, sans-serif',
            rtl=False
        ),
        'de': LanguageConfig(
            code='de',
            name='German',
            native_name='Deutsch',
            font_family='Arial, Helvetica, sans-serif',
            rtl=False
        ),
        'zh': LanguageConfig(
            code='zh',
            name='Chinese',
            native_name='中文',
            font_family='SimSun, Microsoft YaHei, sans-serif',
            rtl=False
        ),
        'ja': LanguageConfig(
            code='ja',
            name='Japanese',
            native_name='日本語',
            font_family='MS Gothic, Yu Gothic, sans-serif',
            rtl=False
        ),
        'hi': LanguageConfig(
            code='hi',
            name='Hindi',
            native_name='हिन्दी',
            font_family='Noto Sans Devanagari, Mangal, sans-serif',
            rtl=False
        ),
        'ar': LanguageConfig(
            code='ar',
            name='Arabic',
            native_name='العربية',
            font_family='Arial, Tahoma, sans-serif',
            rtl=True
        ),
        'pt': LanguageConfig(
            code='pt',
            name='Portuguese',
            native_name='Português',
            font_family='Arial, Helvetica, sans-serif',
            rtl=False
        ),
        'ru': LanguageConfig(
            code='ru',
            name='Russian',
            native_name='Русский',
            font_family='Arial, Helvetica, sans-serif',
            rtl=False
        )
    }
    
    def get_supported_languages(self) -> List[LanguageConfig]:
        """
        Get list of all supported languages.
        
        Returns:
            List of LanguageConfig objects for all supported languages
        """
        return list(self._SUPPORTED_LANGUAGES.values())
    
    def get_language_config(self, language_code: str) -> LanguageConfig:
        """
        Get configuration for a specific language.
        
        Args:
            language_code: ISO 639-1 language code (e.g., 'en', 'es')
            
        Returns:
            LanguageConfig object for the specified language
            
        Raises:
            LanguageNotSupportedError: If the language code is not supported
        """
        if not self.is_supported(language_code):
            supported_codes = list(self._SUPPORTED_LANGUAGES.keys())
            raise LanguageNotSupportedError(
                language_code,
                supported_codes
            )
        return self._SUPPORTED_LANGUAGES[language_code]
    
    def is_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language_code: ISO 639-1 language code to check
            
        Returns:
            True if the language is supported, False otherwise
        """
        return language_code in self._SUPPORTED_LANGUAGES
