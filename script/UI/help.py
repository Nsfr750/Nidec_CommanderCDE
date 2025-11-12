"""
Help System for Nidec CommanderCDE

This module provides the help system for the application, including the help dialog
and documentation viewer with dark theme support.
"""

import os
import sys
from typing import Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, 
                            QPushButton, QLabel, QApplication, QWidget, QFrame)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QPalette, QColor

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import language manager
from script.lang.lang_manager import SimpleLanguageManager

class HelpWindow(QDialog):
    """Help window that displays application documentation with dark theme."""
    
    @staticmethod
    def show_help(parent=None, lang='en'):
        """Static method to show the help window.
        
        Args:
            parent: Parent widget
            lang: Language code ('en' or 'it')
        """
        dialog = HelpWindow(parent, lang)
        dialog.exec()
    
    def __init__(self, parent=None, lang='en'):
        """Initialize the help window.
        
        Args:
            parent: Parent widget
            lang: Language code ('en' or 'it')
        """
        super().__init__(parent)
        self.lang = lang if lang in ['en', 'it'] else 'en'
        self.setWindowTitle("Nidec CommanderCDE - Help" if lang == 'en' else "Nidec CommanderCDE - Aiuto")
        self.setMinimumSize(900, 700)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Apply dark theme
        self.set_dark_theme()
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a frame for the content
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_frame.setStyleSheet("""
            #contentFrame {
                background-color: #1e1e2e;
                border: 1px solid #44475a;
                border-radius: 8px;
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        
        # Language buttons
        en_btn = QPushButton("English")
        it_btn = QPushButton("Italiano")
        
        # Style language buttons
        btn_style = """
            QPushButton {
                background-color: #44475a;
                color: #f8f8f2;
                border: 1px solid #6272a4;
                border-radius: 4px;
                padding: 5px 15px;
                margin: 0 5px;
            }
            QPushButton:hover {
                background-color: #6272a4;
            }
            QPushButton:checked {
                background-color: #bd93f9;
                color: #282a36;
                font-weight: bold;
            }
        """
        
        en_btn.setStyleSheet(btn_style)
        it_btn.setStyleSheet(btn_style)
        en_btn.setCheckable(True)
        it_btn.setCheckable(True)
        
        if self.lang == 'en':
            en_btn.setChecked(True)
        else:
            it_btn.setChecked(True)
        
        en_btn.clicked.connect(lambda: self.change_language('en'))
        it_btn.clicked.connect(lambda: self.change_language('it'))
        
        lang_layout.addWidget(en_btn)
        lang_layout.addWidget(it_btn)
        content_layout.addLayout(lang_layout)
        
        # Help content
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setStyleSheet("""
            QTextBrowser {
                background-color: #282a36;
                color: #f8f8f2;
                border: 1px solid #44475a;
                border-radius: 6px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
            a {
                color: #8be9fd;
                text-decoration: none;
            }
            a:hover {
                color: #50fa7b;
                text-decoration: underline;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #f8f8f2;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            .note {
                background-color: #44475a75;
                border-left: 4px solid #8be9fd;
                padding: 12px 15px;
                margin: 15px 0;
                border-radius: 4px;
            }
            .warning {
                background-color: #ffb86c22;
                border-left: 4px solid #ffb86c;
                padding: 12px 15px;
                margin: 15px 0;
                border-radius: 4px;
            }
            code {
                background-color: #44475a;
                color: #f1fa8c;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
            }
        """)
        
        self.browser.setHtml(self.get_help_content())
        content_layout.addWidget(self.browser)
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.close_btn = QPushButton("Close" if lang == 'en' else "Chiudi")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5555;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 25px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #ff6e6e;
            }
            QPushButton:pressed {
                background-color: #ff3d3d;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)
        content_layout.addLayout(btn_layout)
        
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)
    
    def set_dark_theme(self):
        """Apply dark theme to the application."""
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 45))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(248, 248, 242))
        palette.setColor(QPalette.ColorRole.Base, QColor(40, 42, 54))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 52, 64))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(40, 42, 54))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(248, 248, 242))
        palette.setColor(QPalette.ColorRole.Text, QColor(248, 248, 242))
        palette.setColor(QPalette.ColorRole.Button, QColor(68, 71, 90))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(248, 248, 242))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(139, 233, 253))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(189, 147, 249))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(40, 42, 54))
        self.setPalette(palette)
    
    def change_language(self, new_lang):
        """Change the current language.
        
        Args:
            new_lang: New language code ('en' or 'it')
        """
        if new_lang != self.lang:
            self.lang = new_lang
            self.browser.setHtml(self.get_help_content())
            self.close_btn.setText("Close" if new_lang == 'en' else "Chiudi")
            self.setWindowTitle("Nidec CommanderCDE - Help" if new_lang == 'en' else "Nidec CommanderCDE - Aiuto")
    
    def get_help_content(self):
        """Get the help content in the current language."""
        if self.lang == 'it':
            return self.get_italian_help()
        return self.get_english_help()
    
    def get_english_help(self):
        """Return English help content."""
        return """
        <h1>Nidec CommanderCDE Help</h1>
        
        <div class="note">
            <h4>Welcome to Nidec CommanderCDE</h4>
            <p>This application allows you to control and monitor Nidec CDE series motor drives.</p>
        </div>
        
        <h2>Getting Started</h2>
        <ol>
            <li>Connect your Nidec drive to your computer using the appropriate interface</li>
            <li>Select the correct COM port from the connection menu</li>
            <li>Click the <strong>Connect</strong> button to establish communication</li>
        </ol>
        
        <h2>Features</h2>
        <ul>
            <li><strong>Real-time Monitoring:</strong> View current drive parameters</li>
            <li><strong>Parameter Configuration:</strong> Adjust drive settings</li>
            <li><strong>Fault Diagnostics:</strong> View and clear drive faults</li>
            <li><strong>Data Logging:</strong> Record and export drive data</li>
        </ul>
        
        <div class="warning">
            <h4>Important Safety Notice</h4>
            <p>Always follow proper safety procedures when working with motor drives. Ensure the drive is properly grounded and all connections are secure before powering on.</p>
        </div>
        
        <h2>Keyboard Shortcuts</h2>
        <ul>
            <li><code>Ctrl+O</code>: Open connection dialog</li>
            <li><code>Ctrl+D</code>: Disconnect from drive</li>
            <li><code>F1</code>: Show this help</li>
            <li><code>Esc</code>: Close dialogs</li>
        </ul>
        
        """
    
    def get_italian_help(self):
        """Return Italian help content."""
        return """
        <h1>Guida di Nidec CommanderCDE</h1>
        
        <div class="note">
            <h4>Benvenuti in Nidec CommanderCDE</h4>
            <p>Questa applicazione ti permette di controllare e monitorare gli azionamenti Nidec serie CDE.</p>
        </div>
        
        <h2>Per Iniziare</h2>
        <ol>
            <li>Collega il tuo azionamento Nidec al computer utilizzando l'interfaccia appropriata</li>
            <li>Seleziona la porta COM corretta dal menu di connessione</li>
            <li>Clicca sul pulsante <strong>Connetti</strong> per stabilire la comunicazione</li>
        </ol>
        
        <h2>Funzionalità</h2>
        <ul>
            <li><strong>Monitoraggio in Tempo Reale:</strong> Visualizza i parametri correnti dell'azionamento</li>
            <li><strong>Configurazione Parametri:</strong> Modifica le impostazioni dell'azionamento</li>
            <li><strong>Diagnostica Guasti:</strong> Visualizza e cancella i guasti dell'azionamento</li>
            <li><strong>Registrazione Dati:</strong> Registra ed esporta i dati dell'azionamento</li>
        </ul>
        
        <div class="warning">
            <h4>Avviso di Sicurezza Importante</h4>
            <p>Segui sempre le corrette procedure di sicurezza quando lavori con gli azionamenti. Assicurati che l'azionamento sia correttamente messo a terra e che tutti i collegamenti siano sicuri prima di accenderlo.</p>
        </div>
        
        <h2>Scorciatoie da Tastiera</h2>
        <ul>
            <li><code>Ctrl+O</code>: Apri la finestra di connessione</li>
            <li><code>Ctrl+D</code>: Disconnetti dall'azionamento</li>
            <li><code>F1</code>: Mostra questa guida</li>
            <li><code>Esc</code>: Chiudi le finestre di dialogo</li>
        </ul>
        
        """
