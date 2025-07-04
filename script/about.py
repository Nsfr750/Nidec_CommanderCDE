from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QApplication)
from PyQt6.QtCore import Qt
from app_struct.version import get_version
from lang.translations import t

class About(QDialog):
    @staticmethod
    def show_about(parent=None, lang='en'):
        dialog = About(parent, lang)
        dialog.exec()
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(t('about', lang))
        self.setFixedSize(400, 300)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Nidec Commander CDE')
        title.setStyleSheet('font-size: 16px; font-weight: bold;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Version
        version = QLabel(f"{t('version', self.lang)} {get_version()}")
        layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Description
        description = QLabel(t('about_text', self.lang))
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        # Copyright
        copyright = QLabel('© 2025 Nsfr750')
        layout.addWidget(copyright, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Close button
        close_btn = QPushButton(t('close', self.lang))
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
