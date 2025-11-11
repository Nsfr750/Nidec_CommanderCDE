"""
Language management for Nidec Commander CDE application.

This module provides language management functionality including loading translations
and managing the current application language.
"""

import os
import json
import importlib
import sys
from pathlib import Path
import logging
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class SimpleLanguageManager(QObject):
    """A simple language manager that loads translations from Python modules.
    
    The manager looks for translation files in the 'lang' directory.
    Translation files should be named in the format 'lang_XX.py' where XX is the language code.
    Each module should contain a TRANSLATIONS dictionary with the translations.
    """
    language_changed = pyqtSignal()  # Signal emitted when language is changed
    """
    A simple language manager that loads translations from JSON files.
    
    The manager looks for translation files in the 'lang' directory.
    Translation files should be named in the format 'lang_XX.json' where XX is the language code.
    """
    
    def __init__(self, lang_dir=None, parent=None):
        """
        Initialize the language manager.
        
        Args:
            lang_dir (str, optional): Path to the directory containing language modules.
                                    If not provided, defaults to 'lang' in the current directory.
            parent (QObject, optional): Parent QObject for this manager.
        """
        super().__init__(parent)  # Initialize QObject
        self.lang_dir = Path(lang_dir) if lang_dir else Path(__file__).parent
        self.translations = {}
        self.available_languages = []
        self.current_language = 'en'  # Default language
        self._load_languages()
        
        # Load default language
        self.load_language(self.current_language)
    
    def _load_languages(self):
        """Load all available language modules."""
        try:
            # In development, __file__ is the .py file, in compiled it's in a different location
            if getattr(sys, 'frozen', False):
                # Running in compiled mode with PyInstaller or Nuitka
                base_path = Path(sys._MEIPASS if hasattr(sys, '_MEIPASS') else sys.executable).parent
                lang_dir = base_path / 'script' / 'lang'
            else:
                # Running in development mode
                lang_dir = self.lang_dir
            
            # Look for Python language modules in the lang directory
            lang_files = [f for f in lang_dir.glob('lang_*.py') 
                         if f.name not in ['lang_manager.py', '__init__.py']]
            
            if not lang_files:
                # Try alternative path for compiled version
                if lang_dir != self.lang_dir:
                    lang_dir = self.lang_dir
                    lang_files = [f for f in lang_dir.glob('lang_*.py') 
                                if f.name not in ['lang_manager.py', '__init__.py']]
                
                if not lang_files:
                    logger.warning(f"No language modules found in {lang_dir}")
                    return
            
            for lang_file in lang_files:
                try:
                    # Extract language code from filename (e.g., 'en' from 'lang_en.py')
                    lang_code = lang_file.stem.split('_', 1)[1]
                    
                    # Read the file content
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract the TRANSLATIONS dictionary using a simple approach
                    translations = {}
                    if 'TRANSLATIONS' in content:
                        # This is a simple approach - for more complex cases, consider using ast.literal_eval
                        # or a proper parser
                        start = content.find('TRANSLATIONS = {') + len('TRANSLATIONS = ')
                        end = content.rfind('}') + 1
                        if start > 0 and end > 0:
                            try:
                                # Use a safe way to evaluate the dictionary
                                import ast
                                translations = ast.literal_eval(content[start:end])
                            except (SyntaxError, ValueError) as e:
                                logger.error(f"Error parsing translations in {lang_file}: {e}")
                                continue
                    
                    if translations:
                        self.translations[lang_code] = translations
                        self.available_languages.append({
                            'code': lang_code,
                            'name': translations.get('language_name', lang_code.upper())
                        })
                        logger.info(f"Loaded language: {lang_code}")
                    else:
                        logger.error(f"No valid translations found in {lang_file}")
                        
                except Exception as e:
                    logger.error(f"Error loading language file {lang_file}: {e}")
            
            if not self.translations:
                logger.error("No valid language modules found")
                return
                
            # Set default language if available
            if 'en' in self.translations:
                self.current_language = 'en'
            else:
                self.current_language = next(iter(self.translations.keys()))
                
        except Exception as e:
            logger.error(f"Error initializing language manager: {e}")
    
    def load_language(self, lang_code):
        """
        Load translations for the specified language code.
        
        Args:
            lang_code (str): Language code (e.g., 'en', 'es')
            
        Returns:
            bool: True if the language was loaded successfully, False otherwise
        """
        if lang_code not in self.translations:
            logger.warning(f"Language not available: {lang_code}")
            return False
            
        self.current_language = lang_code
        logger.info(f"Loaded language: {lang_code}")
        self.language_changed.emit()  # Emit signal when language changes
        return True
    
    def get_text(self, key, default=None):
        """
        Get a translated text by key.
        
        Args:
            key (str): The translation key
            default: Default value to return if key is not found
            
        Returns:
            The translated text or the default value if not found
        """
        return self.translations.get(key, default)
    
    def get_available_languages(self):
        """
        Get a list of available language codes.
        
        Returns:
            list: List of available language codes
        """
        return self.available_languages
    
    def get_current_language(self):
        """
        Get the current language code.
        
        Returns:
            str: Current language code
        """
        return self.current_language
        
    def tr(self, key, default=None, lang_code=None):
        """
        Get a translated string for the given key.
        
        Args:
            key (str): The translation key
            default (str, optional): Default value if key is not found
            lang_code (str, optional): Language code to use for translation. 
                                     If not provided, uses the current language.
            
        Returns:
            str: The translated string or the default value if not found
        """
        target_lang = lang_code if lang_code else self.current_language
        if target_lang in self.translations and key in self.translations[target_lang]:
            return self.translations[target_lang][key]
        return default if default is not None else key
