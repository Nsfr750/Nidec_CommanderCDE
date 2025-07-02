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
        self.setWindowTitle("Nidec Commander CDE")
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
        Sponsor.show_sponsor(self, self.current_language)
    
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
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
