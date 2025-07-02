import sys
import os
import json
from pathlib import Path

# Add the script directory to the Python path
script_dir = Path(__file__).parent / 'script'
sys.path.insert(0, str(script_dir))

from PyQt5.QtWidgets import (QMainWindow, QApplication, QMenuBar, QMenu, 
                           QAction, QMessageBox, QWidget, QVBoxLayout, QActionGroup)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QSettings

# Import the modules we need
from help import HelpWindow
from about import About
from sponsor import Sponsor
from updates import check_for_updates

# Import translations
from lang.translations import TRANSLATIONS, t

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nidec Commander Control")
        self.setGeometry(100, 100, 1000, 750)
        
        # Initialize settings
        self.settings = QSettings("NidecCommander", "CDE_Control")
        
        # Set default language if not set
        self.current_language = self.settings.value("language", "en")
        
        # Create the menu bar
        self.create_menu_bar()
        
        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # This will be populated by the child class
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(t('file_menu', self.current_language))
        
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
        
        # Help menu
        help_menu = menubar.addMenu(t('help_menu', self.current_language))
        
        # Help -> Documentation
        help_action = QAction(t('documentation', self.current_language), self)
        help_action.triggered.connect(lambda: self.show_help())
        help_menu.addAction(help_action)
        
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
        Sponsor.show_sponsor(self, self.current_language)
    
    def change_language(self):
        """Change the application language."""
        action = self.sender()
        if action and action.isChecked():
            new_lang = action.data()
            if new_lang != self.current_language:
                self.current_language = new_lang
                self.settings.setValue("language", new_lang)
                # Restart the application to apply language changes
                QMessageBox.information(
                    self,
                    t('restart_required', self.current_language),
                    t('restart_message', self.current_language)
                )
                # Note: The actual language change will take effect after restart
    
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
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
