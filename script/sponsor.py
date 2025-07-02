from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from lang.translations import t

# Sponsor Class
class Sponsor(QDialog):
    @staticmethod
    def show_sponsor(parent=None, lang='en'):
        dialog = Sponsor(parent, lang)
        dialog.exec_()
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(t('sponsor', lang))
        self.setMinimumSize(600, 200)
        self.setWindowModality(Qt.ApplicationModal)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(t('support_development', self.lang))
        title.setAlignment(Qt.AlignCenter)
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
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px;
                    margin: 2px;
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border-color: #999;
                }
            """)
            btn.clicked.connect(lambda checked, u=url: self.open_url(u))
            btn_layout.addWidget(btn)
        
        layout.addWidget(btn_container)
        
        # Close button
        close_btn = QPushButton(t('close', self.lang))
        close_btn.clicked.connect(self.close)
        close_btn.setMaximumWidth(100)
        
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        
        layout.addStretch()
        layout.addWidget(btn_container)
    
    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))
