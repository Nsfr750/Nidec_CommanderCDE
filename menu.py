"""
Nidec Commander CDE - Main Window and Menu System

This module implements the main application window with a menu bar and handles
application-wide functionality such as language selection, help, and updates.

Key Features:
- Main application window with menu bar
- Language selection and switching
- Help system integration
- About and sponsor dialogs
- Update checking functionality

Dependencies:
- PyQt5: For GUI components
- script/*: Helper modules for various features
- lang.translations: For internationalization support

Author: [Your Name]
Version: 1.0.0
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add the script directory to the Python path
script_dir = Path(__file__).parent / 'script'
sys.path.insert(0, str(script_dir))

# PyQt5 imports
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QMenuBar, QMenu, 
    QAction, QMessageBox, QWidget, QVBoxLayout, QActionGroup
)
from PyQt5.QtGui import QKeySequence, QCloseEvent, QColor, QPalette
from PyQt5.QtCore import Qt, QSettings, QObject, pyqtSignal

# Local application imports
from help import HelpWindow
from about import About
from sponsor import Sponsor
from updates import check_for_updates

# Import translations
from lang.translations import TRANSLATIONS, t

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Main application window with menu bar and core functionality.
    
    This class represents the main window of the Nidec Commander CDE application.
    It provides the main menu, handles language switching, and manages application
    state and settings.
    
    Attributes:
        settings: QSettings instance for persistent storage
        current_language: Currently selected language code (e.g., 'en', 'it')
        help_window: Reference to the help window (lazily created)
        about_dialog: Reference to the about dialog (lazily created)
        sponsor_dialog: Reference to the sponsor dialog (lazily created)
    """
    
    def __init__(self):
        """Initialize the main window and set up the UI."""
        super().__init__()
        
        # Set up the main window
        self.setWindowTitle("Nidec Commander CDE")
        self.setGeometry(100, 100, 1000, 750)
        
        # Initialize settings and application state
        self.settings = QSettings("NidecCommander", "CDE_Control")
        
        # Set default language if not set
        self.current_language = self.settings.value("language", "en")
        
        # Set default theme if not set (system, light, or dark)
        self.current_theme = self.settings.value("theme", "system")
        
        # Create the menu bar
        self.create_menu_bar()
        
        # Apply the saved theme
        self.apply_theme(self.current_theme)
        
        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # This will be populated by the child class
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(t('file_menu', self.current_language))
        
        # Save Configuration
        save_config_action = QAction(t('save_config', self.current_language), self)
        save_config_action.setShortcut(QKeySequence.Save)
        save_config_action.triggered.connect(self.save_configuration)
        file_menu.addAction(save_config_action)
        
        # Load Configuration
        load_config_action = QAction(t('load_config', self.current_language), self)
        load_config_action.setShortcut(QKeySequence.Open)
        load_config_action.triggered.connect(self.load_configuration)
        file_menu.addAction(load_config_action)
        
        file_menu.addSeparator()
        
        # Export Data
        export_data_action = QAction(t('export_data', self.current_language), self)
        export_data_action.triggered.connect(self.export_data)
        file_menu.addAction(export_data_action)
        
        file_menu.addSeparator()
        
        # Add Check for Updates to File menu
        update_action = QAction(t('check_for_updates', self.current_language), self)
        update_action.triggered.connect(self.check_for_updates)
        file_menu.addAction(update_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(t('exit', self.current_language), self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu (for cur/copy/paste)
        tools_menu = menubar.addMenu(t('tools_menu', self.current_language))
        
        cut_action = QAction(t('cut', self.current_language), self)
        cut_action.setShortcut(QKeySequence.Cut)
        tools_menu.addAction(cut_action)
        
        copy_action = QAction(t('copy', self.current_language), self)
        copy_action.setShortcut(QKeySequence.Copy)
        tools_menu.addAction(copy_action)
        
        paste_action = QAction(t('paste', self.current_language), self)
        paste_action.setShortcut(QKeySequence.Paste)
        tools_menu.addAction(paste_action)
                
        # Language menu
        language_menu = menubar.addMenu(t('language_menu', self.current_language))
        
        # Create a language group for exclusive selection
        self.language_group = QActionGroup(self)
        self.language_group.setExclusive(True)
        
        # Add available languages
        for lang_code, lang_data in TRANSLATIONS.items():
            lang_name = lang_data.get('language_name', lang_code.upper())
            action = QAction(lang_name, self, checkable=True)
            action.setData(lang_code)
            action.triggered.connect(self.change_language)
            language_menu.addAction(action)
            self.language_group.addAction(action)
            
            # Check the current language
            if lang_code == self.current_language:
                action.setChecked(True)
        
        # Theme menu
        theme_menu = menubar.addMenu(t('theme_menu', self.current_language))
        
        # Create a theme group for exclusive selection
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        
        # Available themes
        themes = [
            (t('system_theme', self.current_language), 'system'),
            (t('light_theme', self.current_language), 'light'),
            (t('dark_theme', self.current_language), 'dark')
        ]
        
        # Add theme options
        for theme_name, theme_id in themes:
            action = QAction(theme_name, self, checkable=True)
            action.setData(theme_id)
            action.triggered.connect(lambda checked, t=theme_id: self.change_theme(t))
            theme_menu.addAction(action)
            self.theme_group.addAction(action)
            
            # Check the current theme
            if theme_id == self.current_theme:
                action.setChecked(True)
        
        # Help menu
        help_menu = menubar.addMenu(t('help_menu', self.current_language))
        
        # Help -> Documentation
        help_action = QAction(t('documentation', self.current_language), self)
        help_action.triggered.connect(lambda: self.show_help())
        help_menu.addAction(help_action)
        
        help_menu.addSeparator()
        
        # Help -> About
        about_action = QAction(t('about', self.current_language), self)
        about_action.triggered.connect(lambda: self.show_about())
        help_menu.addAction(about_action)
        
        # Help -> Sponsor
        sponsor_action = QAction(t('sponsor', self.current_language), self)
        sponsor_action.triggered.connect(lambda: self.show_sponsor())
        help_menu.addAction(sponsor_action)
    
    def show_help(self):
        from script.help import HelpWindow
        self.help_window = HelpWindow(self, self.current_language)
        self.help_window.show()
    
    def show_about(self):
        from script.about import About
        About.show_about(self, self.current_language)
    
    def show_sponsor(self):
        from script.sponsor import Sponsor
        Sponsor.show_sponsor(parent=self, lang=self.current_language)
        
    def change_theme(self, theme_id):
        """Change the application theme.
        
        Args:
            theme_id (str): The theme to apply ('system', 'light', or 'dark')
        """
        self.current_theme = theme_id
        self.settings.setValue("theme", theme_id)
        self.apply_theme(theme_id)
    
    def apply_theme(self, theme_id):
        """Apply the specified theme to the application.
        
        Args:
            theme_id (str): The theme to apply ('system', 'light', or 'dark')
        """
        # Determine which palette to use
        if theme_id == 'dark' or (theme_id == 'system' and self.is_dark_system_theme()):
            self.set_dark_theme()
        else:
            self.set_light_theme()
    
    def is_dark_system_theme(self):
        """Check if the system is using a dark theme.
        
        Returns:
            bool: True if the system is using a dark theme, False otherwise
        """
        # Try to detect system dark mode
        try:
            import ctypes
            if hasattr(ctypes, 'windll'):  # Windows
                # This checks the Windows 10/11 theme setting
                try:
                    import winreg
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
                    value = winreg.QueryValueEx(key, 'AppsUseLightTheme')[0]
                    return value == 0
                except (WindowsError, OSError):
                    return False
            # Add detection for other platforms here if needed
        except Exception as e:
            logger.warning(f"Could not detect system theme: {e}")
            return False
        
        return False
    
    def set_dark_theme(self):
        """Apply a dark theme to the application."""
        # Set the Fusion style for consistent theming across platforms
        app = QApplication.instance()
        app.setStyle('Fusion')
        
        # Create a dark palette
        dark_palette = app.palette()
        
        # Base colors
        dark_palette.setColor(dark_palette.Window, QColor(53, 53, 53))
        dark_palette.setColor(dark_palette.WindowText, Qt.white)
        dark_palette.setColor(dark_palette.Base, QColor(35, 35, 35))
        dark_palette.setColor(dark_palette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(dark_palette.ToolTipBase, Qt.white)
        dark_palette.setColor(dark_palette.ToolTipText, Qt.white)
        dark_palette.setColor(dark_palette.Text, Qt.white)
        dark_palette.setColor(dark_palette.Button, QColor(53, 53, 53))
        dark_palette.setColor(dark_palette.ButtonText, Qt.white)
        dark_palette.setColor(dark_palette.BrightText, Qt.red)
        dark_palette.setColor(dark_palette.Link, QColor(42, 130, 218))
        dark_palette.setColor(dark_palette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(dark_palette.HighlightedText, Qt.white)
        
        # Disabled colors
        dark_palette.setColor(dark_palette.Disabled, dark_palette.Text, QColor(127, 127, 127))
        dark_palette.setColor(dark_palette.Disabled, dark_palette.ButtonText, QColor(127, 127, 127))
        
        # Apply the palette
        app.setPalette(dark_palette)
        
        # Update style to ensure the theme is applied
        app.setStyleSheet("""
            QToolTip { 
                color: #ffffff; 
                background-color: #2a82da; 
                border: 1px solid white; 
            }
            QMenu::item:selected { 
                background-color: #2a82da; 
            }
            QTabBar::tab:selected { 
                background: #2a82da; 
                color: white; 
            }
        """)
    
    def set_light_theme(self):
        """Apply a light theme to the application."""
        # Set the Fusion style for consistent theming across platforms
        app = QApplication.instance()
        app.setStyle('Fusion')
        
        # Reset to default palette
        app.setPalette(app.style().standardPalette())
        
        # Update style to ensure the theme is applied
        app.setStyleSheet("""
            QToolTip { 
                border: 1px solid #2a82da; 
                padding: 2px; 
                border-radius: 3px; 
                opacity: 240; 
            }
            QMenu::item:selected { 
                background-color: #2a82da; 
                color: white;
            }
        """)
    
    def change_language(self, lang_code=None):
        """Change the application language and update the UI immediately."""
        if lang_code is None:
            action = self.sender()
            if not action or not action.isChecked():
                return
            lang_code = action.data()
            
        if lang_code != self.current_language:
            self.current_language = lang_code
            self.settings.setValue("language", lang_code)
            
            # Update all UI elements with the new language
            self.retranslate_ui()
            
            # Update the language menu check state
            if hasattr(self, 'language_group'):
                for action in self.language_group.actions():
                    action.setChecked(action.data() == lang_code)
    
    def retranslate_ui(self):
        """Retranslate all UI elements with the current language."""
        # Update window title
        self.setWindowTitle(t('app_title', self.current_language))
        
        # Update menu bar
        if hasattr(self, 'menuBar'):
            for menu in self.menuBar().findChildren(QMenu):
                if menu.title() in [t('file_menu', 'en'), t('tools_menu', 'en'), 
                                 t('language_menu', 'en'), t('help_menu', 'en')]:
                    # This is one of our main menus
                    if menu.title() == t('file_menu', 'en'):
                        menu.setTitle(t('file_menu', self.current_language))
                    elif menu.title() == t('tools_menu', 'en'):
                        menu.setTitle(t('tools_menu', self.current_language))
                    elif menu.title() == t('language_menu', 'en'):
                        menu.setTitle(t('language_menu', self.current_language))
                    elif menu.title() == t('help_menu', 'en'):
                        menu.setTitle(t('help_menu', self.current_language))
                else:
                    # This is a submenu or action
                    for action in menu.actions():
                        if not action.isSeparator() and action.text():
                            # Find the translation key for this action's text
                            for key, value in TRANSLATIONS['en'].items():
                                if value == action.text() and key in TRANSLATIONS.get(self.current_language, {}):
                                    action.setText(TRANSLATIONS[self.current_language][key])
                                    break
    
    def check_for_updates(self):
        """Check for application updates."""
        try:
            # Show a message that we're checking for updates
            QMessageBox.information(
                self,
                t('checking_updates', self.current_language),
                t('checking_updates_message', self.current_language)
            )
            
            # Call the update check function
            check_for_updates(self, self.current_language)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                t('update_error', self.current_language),
                f"{t('update_error_message', self.current_language)}: {str(e)}"
            )
    
    def show_sponsor(self):
        """Show the sponsor dialog."""
        Sponsor.show_sponsor(parent=self, lang=self.current_language)

if __name__ == "__main__":
    """
    Entry point for the Nidec Commander CDE application.
    
    This block is executed when the script is run directly (not imported as a module).
    It creates the QApplication instance and the main window, then starts the event loop.
    """
    try:
        # Create the Qt application
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName("Nidec Commander CDE")
        app.setOrganizationName("Nidec")
        app.setApplicationVersion("1.0.0")
        
        # Create and show the main window
        window = MainWindow()
        window.show()
        
        # Start the application event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        # Log any unhandled exceptions
        logger.critical("Unhandled exception in main thread", exc_info=True)
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"An unexpected error occurred: {str(e)}\n\n"
            "The application will now exit.\n\n"
            "Please check the log file for more details."
        )
        sys.exit(1)
