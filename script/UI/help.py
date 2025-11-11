"""
Help System for Nidec CommanderCDE

This module provides the help system for the application, including the help dialog
and documentation viewer.
"""

import os
import sys
from typing import Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, 
                            QPushButton, QLabel, QApplication, QWidget, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import language manager
from script.lang.lang_manager import SimpleLanguageManager

# Initialize language manager
language_manager = SimpleLanguageManager()

def t(key: str, language: str = 'en', default: Optional[str] = None) -> str:
    """Translation helper function for backward compatibility.
    
    Args:
        key: Translation key
        language: Language code (default: 'en')
        default: Default value if key is not found
        
    Returns:
        str: Translated string or default value
    """
    return language_manager.tr(key, default=default or key, lang_code=language)

class HelpWindow(QDialog):
    """Help window that displays application documentation."""
    
    @staticmethod
    def show_help(parent=None, lang='en'):
        """Static method to show the help window.
        
        Args:
            parent: Parent widget
            lang: Language code
        """
        dialog = HelpWindow(parent, lang)
        dialog.exec()
    
    def __init__(self, parent=None, lang='en'):
        """Initialize the help window.
        
        Args:
            parent: Parent widget
            lang: Language code
        """
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(f"{t('app_title', lang)} - {t('help_menu', lang)}")
        self.setMinimumSize(800, 600)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        main_layout = QVBoxLayout()
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel(t('language_menu', lang))
        lang_layout.addWidget(lang_label)
        
        # Language buttons
        for lang_info in language_manager.get_available_languages():
            lang_code = lang_info['code']
            btn = QPushButton(t(lang_code, lang_code))  # Use lang_code for both key and language
            btn.clicked.connect(lambda checked, l=lang_code: self.change_language(l))
            lang_layout.addWidget(btn)
        
        lang_layout.addStretch()
        main_layout.addLayout(lang_layout)
        
        # Title
        title = QLabel(f"{t('app_title', lang)} - {t('help_menu', lang)}")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Help content
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setHtml(self.get_help_content())
        main_layout.addWidget(self.browser)
        
        # Close button
        close_btn = QPushButton(t('close', self.lang))
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(main_layout)
    
    def change_language(self, new_lang):
        """Change the current language.
        
        Args:
            new_lang: New language code
        """
        self.lang = new_lang
        self.browser.setHtml(self.get_help_content())
        
    def get_help_content(self):
        """Get the help content in the current language.
        
        Returns:
            str: HTML formatted help content
        """
        # Use the language manager to get translated content
        return self.get_localized_help_content()
    
    def get_localized_help_content(self):
        """Return help content specific to the current language.
        
        Returns:
            str: HTML formatted help content for the current language
        """
        # This is a simplified version - in a real app, you might load this from files
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                h2 {{ color: #3498db; margin-top: 20px; }}
                h3 {{ color: #2c3e50; }}
                ul, ol {{ margin: 10px 0 10px 20px; }}
                li {{ margin: 5px 0; }}
                .note {{ 
                    background-color: #e7f4ff; 
                    border-left: 4px solid #3498db; 
                    padding: 10px 15px;
                    margin: 15px 0;
                    border-radius: 4px;
                }}
                .warning {{ 
                    background-color: #fff3cd; 
                    border-left: 4px solid #ffc107; 
                    padding: 10px 15px;
                    margin: 15px 0;
                    border-radius: 4px;
                }}
                code {{ 
                    background-color: #f8f9fa; 
                    padding: 2px 5px; 
                    border-radius: 3px; 
                    font-family: monospace;
                }}
                a {{ 
                    color: #3498db; 
                    text-decoration: none; 
                }}
                a:hover {{ 
                    text-decoration: underline; 
                }}
            </style>
        </head>
        <body>
            <h1>{t('help_menu', self.lang)}</h1>
            
            <div class="note">
                <h4>{t('help_note', self.lang, 'Note')}</h4>
                <p>{t('help_note_text', self.lang, 'This is the help documentation for Nidec CommanderCDE.')}</p>
            </div>
            
            <h2>{t('getting_started', self.lang, 'Getting Started')}</h2>
            <p>{t('getting_started_text', self.lang, 'To get started with Nidec CommanderCDE, follow these steps:')}</p>
            <ol>
                <li>{t('step_1', self.lang, 'Connect your Nidec drive to your computer')}</li>
                <li>{t('step_2', self.lang, 'Select the correct COM port and baud rate')}</li>
                <li>{t('step_3', self.lang, 'Click the "Connect" button')}</li>
            </ol>
            
            <h2>{t('features', self.lang, 'Features')}</h2>
            <ul>
                <li>{t('feature_1', self.lang, 'Real-time monitoring of drive parameters')}</li>
                <li>{t('feature_2', self.lang, 'Parameter configuration')}</li>
                <li>{t('feature_3', self.lang, 'Fault diagnostics')}</li>
                <li>{t('feature_4', self.lang, 'Data logging')}</li>
            </ul>
            
            <div class="warning">
                <h4>{t('warning', self.lang, 'Warning')}</h4>
                <p>{t('warning_text', self.lang, 'Always ensure proper safety measures when working with motor drives.')}</p>
            </div>
            
            <h2>{t('support', self.lang, 'Support')}</h2>
            <p>{t('support_text', self.lang, 'For additional help, please contact:')} 
               <a href="mailto:nsfr750@yandex.com">nsfr750@yandex.com</a></p>
        </body>
        </html>
        """
