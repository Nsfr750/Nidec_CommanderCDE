import os
import sys
from typing import Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, 
                            QPushButton, QLabel, QApplication, QWidget, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add script directory to Python path
script_dir = os.path.join(project_root, 'script')
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from lang.lang_manager import SimpleLanguageManager

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
    return language_manager.tr(key, default or key)

class HelpWindow(QDialog):
    @staticmethod
    def show_help(parent=None, lang='en'):
        dialog = HelpWindow(parent, lang)
        dialog.exec()
    
    def __init__(self, parent=None, lang='en'):
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
        for lang_code in ['en', 'it']:
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
                h1 {{ color: white; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                h2 {{ color: white; margin-top: 20px; }}
                h3 {{ color: white; }}
                ul, ol {{ margin: 10px 0 10px 20px; }}
                li {{ margin: 5px 0; }}
                .note {{ 
                    background-color: #1976D2; 
                    color: white;
                    padding: 12px 16px;
                    border-radius: 4px;
                    margin: 15px 0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
                }}
                .note h4 {{
                    color: white;
                    margin-top: 0;
                    margin-bottom: 10px;
                    font-size: 1.1em;
                }}
                .warning {{ 
                    background-color: blue; 
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
                <h4>{getting_started}</h4>
                <p>{welcome_message}</p>
            </div>
            
            <h2>{basic_usage}</h2>
            <ul>
                <li>{connect_device_help}</li>
                <li>{send_commands_help}</li>
                <li>{monitor_status_help}</li>
            </ul>
            
            <div class="warning">
                <h2>{need_help}</h2>
                <p>{visit_github} <a href="https://github.com/Nsfr750/Nidec_CommanderCDE">GitHub</a>.</p>
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
        """Return help content specific to the current language
        
        Returns:
            str: HTML formatted help content for the current language
        """
        # Help content for all supported languages
        help_texts = {
            'en': """
            <h2>Getting Started</h2>
            <p>Welcome to Nidec CommanderCDE. This application allows you to control and monitor Nidec motor drives.</p>
            
            <h3>Connecting to a Drive</h3>
            <ol>
                <li>Select your drive model from the dropdown menu</li>
                <li>Choose the correct COM port from the list</li>
                <li>Set the appropriate baud rate and other connection parameters</li>
                <li>Click 'Connect' to establish communication</li>
            </ol>
            
            <h3>Basic Controls</h3>
            <ul>
                <li>Use the 'Start' and 'Stop' buttons to control the motor</li>
                <li>Adjust the speed using the slider or input field</li>
                <li>Change direction using the direction control buttons</li>
            </ul>
            
            <h3>Monitoring</h3>
            <p>The dashboard displays real-time information about the drive status, including:</p>
            <ul>
                <li>Output frequency</li>
                <li>Output current</li>
                <li>DC bus voltage</li>
                <li>Drive status and fault information</li>
            </ul>
            
            <div class="note">
                <h4>Note</h4>
                <p>Ensure the drive is properly connected and powered before attempting to control it.</p>
            </div>
            """,
            
            'it': """
            <h2>Per iniziare</h2>
            <p>Benvenuto in Nidec CommanderCDE. Questa applicazione ti consente di controllare e monitorare gli azionamenti Nidec.</p>
            
            <h3>Connessione all'azionamento</h3>
            <ol>
                <li>Seleziona il modello del tuo azionamento dal menu a discesa</li>
                <li>Scegli la porta COM corretta dall'elenco</li>
                <li>Imposta la velocità di trasmissione e gli altri parametri di connessione</li>
                <li>Fai clic su 'Connetti' per stabilire la comunicazione</li>
            </ol>
            
            <h3>Controlli di base</h3>
            <ul>
                <li>Usa i pulsanti 'Avvia' e 'Ferma' per controllare il motore</li>
                <li>Regola la velocità usando il cursore o il campo di inserimento</li>
                <li>Cambia direzione usando i pulsanti di controllo della direzione</li>
            </ul>
            
            <h3>Monitoraggio</h3>
            <p>La dashboard mostra informazioni in tempo reale sullo stato dell'azionamento, tra cui:</p>
            <ul>
                <li>Frequenza di uscita</li>
                <li>Corrente di uscita</li>
                <li>Tensione del bus CC</li>
                <li>Stato dell'azionamento e informazioni sugli errori</li>
            </ul>
            
            <div class="note">
                <h4>Nota</h4>
                <p>Assicurati che l'azionamento sia correttamente collegato e alimentato prima di tentare di controllarlo.</p>
            </div>
            """,
        }
        
        # For languages not yet translated, use English as fallback
        return help_texts.get(self.lang, help_texts['en'])
