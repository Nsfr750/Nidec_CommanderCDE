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

logger = logging.getLogger(__name__)

class SimpleLanguageManager:
    """
    A simple language manager that loads translations from JSON files.
    
    The manager looks for translation files in the 'lang' directory.
    Translation files should be named in the format 'lang_XX.json' where XX is the language code.
    """
    
    def __init__(self, lang_dir=None):
        """
        Initialize the language manager.
        
        Args:
            lang_dir (str, optional): Path to the directory containing language modules.
                                    If not provided, defaults to 'lang' in the current directory.
        """
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
            # Import the language modules
            
            # Look for Python language modules in the lang directory, excluding lang_manager.py
            lang_files = [f for f in self.lang_dir.glob('lang_*.py') 
                         if f.name not in ['lang_manager.py', '__init__.py']]
            
            if not lang_files:
                logger.warning(f"No language modules found in {self.lang_dir}")
                return
                
            for lang_file in lang_files:
                # Extract language code from filename (e.g., 'en' from 'lang_en.py')
                lang_code = lang_file.stem.split('_', 1)[1]
                module_name = f"lang.lang_{lang_code}"
                
                try:
                    # Dynamically import the module
                    spec = importlib.util.spec_from_file_location(module_name, lang_file)
                    if spec is None or spec.loader is None:
                        raise ImportError(f"Could not load spec for {module_name}")
                        
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    
                    # Get the TRANSLATIONS dictionary from the module
                    if hasattr(module, 'TRANSLATIONS'):
                        self.translations[lang_code] = module.TRANSLATIONS
                        self.available_languages.append({
                            'code': lang_code,
                            'name': self.translations[lang_code].get('language_name', lang_code.upper())
                        })
                        logger.info(f"Loaded language: {lang_code}")
                    else:
                        logger.error(f"No TRANSLATIONS dictionary found in {lang_file}")
                        
                except Exception as e:
                    logger.error(f"Error loading language module {lang_file}: {e}")
                    
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
        
    def tr(self, key, default=None):
        """
        Get a translated string for the given key.
        
        Args:
            key (str): The translation key
            default (str, optional): Default value if key is not found
            
        Returns:
            str: The translated string or the default value if not found
        """
        return self.translations.get(key, default)
