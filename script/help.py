import os
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, 
                            QPushButton, QLabel, QApplication, QWidget, QScrollArea)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lang.translations import TRANSLATIONS, t

class HelpWindow(QDialog):
    @staticmethod
    def show_help(parent=None, lang='en'):
        dialog = HelpWindow(parent, lang)
        dialog.exec_()
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(f"{t('app_title', lang)} - {t('help_menu', lang)}")
        self.setMinimumSize(800, 600)
        self.setWindowModality(Qt.ApplicationModal)
        
        main_layout = QVBoxLayout()
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel(t('language_menu', lang))
        lang_layout.addWidget(lang_label)
        
        # Language buttons
        for lang_code in ['en', 'it', 'es', 'pt', 'de', 'fr', 'nl', 'ru', 'zh', 'jp', 'ar']:
            btn = QPushButton(t(lang_code, lang_code))
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
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Help content
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setHtml(self.get_help_content())
        main_layout.addWidget(self.browser)
        
        # Close button
        close_btn = QPushButton(t('close', self.lang))
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        self.setLayout(main_layout)
    
    def change_language(self, new_lang):
        self.close()
        HelpWindow.show_help(self.parent(), new_lang)
    
    def get_help_content(self):
        # Get the appropriate help content based on language
        help_content = self.get_localized_help_content()
        
        # Use double curly braces for literal curly braces in the CSS
        return """
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                h2 {{ color: #3498db; margin-top: 20px; }}
                h3 {{ color: #7f8c8d; }}
                ul, ol {{ margin: 10px 0 10px 20px; }}
                li {{ margin: 5px 0; }}
                .note {{ 
                    background-color: #f8f9fa; 
                    padding: 10px 15px;
                    border-left: 4px solid #3498db; 
                    margin: 15px 0;
                    border-radius: 4px;
                }}
                .warning {{ 
                    background-color: #fff3cd; 
                    padding: 10px 15px;
                    border-left: 4px solid #ffc107; 
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
                .lang-btn {{ 
                    margin: 2px;
                    padding: 2px 8px;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    background: #f8f9fa;
                    cursor: pointer;
                }}
                .lang-btn.active {{ 
                    background: #3498db;
                    color: white;
                    border-color: #2980b9;
                }}
            </style>
        </head>
        <body>
            <div class="note">
                <h2>{getting_started}</h2>
                <p>{welcome_message}</p>
            </div>
            
            <h2>{basic_usage}</h2>
            <ul>
                <li>{connect_device_help}</li>
                <li>{send_commands_help}</li>
                <li>{monitor_status_help}</li>
            </ul>
            
            <div class="warning">
                <h3>{need_help}</h3>
                <p>{visit_github} <a href="https://github.com/NsNsfr750/nidec-commander">GitHub</a>.</p>
            </div>
            
            {help_content}
        </body>
        </html>
        """.format(
            getting_started=t('getting_started', self.lang),
            welcome_message=t('welcome_message', self.lang),
            basic_usage=t('basic_usage', self.lang),
            connect_device_help=t('connect_device_help', self.lang),
            send_commands_help=t('send_commands_help', self.lang),
            monitor_status_help=t('monitor_status_help', self.lang),
            need_help=t('need_help', self.lang),
            visit_github=t('visit_github', self.lang),
            help_content=help_content
        )
    
    def get_localized_help_content(self):
        """Return help content specific to the current language"""
        # Help content for all supported languages
        help_texts = {
            'en': """ """,
            'it': """ """,
            'es': """ """,
            'pt': """ """,
            'de': """ """,
            'fr': """ """,
            'nl': """ """,
            'ru': """ """,
            'zh': """ """,
            'jp': """ """,
            'ar': """ """,
        }
        # Return the help text for the current language, defaulting to English if not found
        return help_texts.get(self.lang, help_texts['en'])
