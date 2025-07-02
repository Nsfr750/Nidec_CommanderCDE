from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QWidget, QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from lang.translations import t

# Sponsor Class
class Sponsor(QDialog):
    @staticmethod
    def show_sponsor(parent=None, lang='en'):
        dialog = Sponsor(parent, lang)
        dialog.exec()
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(t('sponsor', lang))
        self.setMinimumSize(600, 200)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(t('support_development', self.lang))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Button container
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(10, 0, 10, 0)
        
        # Sponsor buttons
        buttons = [
            (t('sponsor_on_github', self.lang), "https://github.com/sponsors/Nsfr750"),
            (t('join_discord', self.lang), "https://discord.gg/BvvkUEP9"),
            (t('buy_me_a_coffee', self.lang), "https://paypal.me/3dmega"),
            (t('join_the_patreon', self.lang), "https://www.patreon.com/Nsfr750")
        ]
        
        for text, url in buttons:
            btn = QPushButton(text, self)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px;
                    margin: 2px;
                    background-color: #1976D2;  /* Blue background */
                    color: white;              /* White text */
                    border: 1px solid #1565C0;  /* Slightly darker blue border */
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2196F3;  /* Lighter blue on hover */
                    border-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;  /* Darker blue when pressed */
                }
            """)
            btn.clicked.connect(lambda checked, u=url: self.open_url(u))
            btn_layout.addWidget(btn)
        
        layout.addWidget(btn_container)
        
        # Close button
        close_btn = QPushButton(t('close', self.lang))
        close_btn.setFixedSize(100, 30)
        close_btn.clicked.connect(self.close)
        
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        layout.addStretch()
        layout.addWidget(btn_container)
    
    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))
