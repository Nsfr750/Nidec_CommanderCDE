"""
About Dialog for Nidec CommanderCDE

This module provides the About dialog that displays information about the application,
including version, author, and license information.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
import os
from pathlib import Path

class AboutDialog(QDialog):
    """About dialog that displays application information."""
    
    def __init__(self, parent=None, language_manager=None):
        """Initialize the About dialog.
        
        Args:
            parent: Parent widget
            language_manager: Instance of SimpleLanguageManager for translations
        """
        super().__init__(parent)
        self.language_manager = language_manager
        self.setWindowTitle(self.tr("About Nidec CommanderCDE"))
        self.setMinimumSize(400, 300)
        
        # Set window icon if available
        icon_path = Path("script/assets/icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Application icon/logo
        logo_path = Path("script/assets/logo.png")
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)
        
        # Application title and version
        title_label = QLabel("Nidec CommanderCDE")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        version_label = QLabel("Version 0.0.5")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel(
            "A GUI application for controlling and monitoring\nNidec Commander CDE series motor drives.\n\n\n\n"
            "© Copyright 2024-2025 Nsfr750 - All rights reserved"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        layout.addStretch()
        layout.addLayout(button_layout)
        
    def tr(self, text):
        """Translate text using the language manager if available."""
        if self.language_manager:
            return self.language_manager.tr(text, default=text)
        return text
