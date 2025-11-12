"""
About Dialog for Nidec CommanderCDE

This module provides the About dialog that displays information about the application,
including version, author, and license information.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
import os
import sys
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
        self.setup_ui()
        
        # Set window icon after setup_ui to ensure paths are resolved
        icon_path = self.get_resource_path("script/assets/icon.ico")
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Application icon/logo
        logo_path = self.get_resource_path("script/assets/logo.png")
        if logo_path and os.path.exists(logo_path):
            try:
                logo_label = QLabel()
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.addWidget(logo_label)
                else:
                    print(f"Warning: Failed to load logo from {logo_path}")
            except Exception as e:
                print(f"Error loading logo: {e}")
        
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
        
    def get_resource_path(self, relative_path):
        """Get the correct path to a resource file, whether running as script or frozen executable."""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            return os.path.join(base_path, relative_path)
        else:
            # Running as script
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            return os.path.join(script_dir, relative_path)
