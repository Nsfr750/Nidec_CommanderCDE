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
- PyQt6: For GUI components
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
from typing import Optional

# Add the script directory to the Python path
script_dir = Path(__file__).parent / 'script'
sys.path.insert(0, str(script_dir))

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# PyQt6 imports
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QMenuBar, QMenu, 
    QMessageBox, QWidget, QVBoxLayout
)
from PyQt6.QtGui import QCloseEvent, QColor, QPalette, QAction, QKeySequence, QActionGroup
from PyQt6.QtCore import Qt, QSettings, QObject, pyqtSignal, QProcess, QProcessEnvironment

# Local application imports
from script.UI.help import HelpWindow
from script.UI.about import AboutDialog
from script.UI.sponsor import SponsorDialog
from script.utils.updates import check_updates

# Import language manager
from script.lang.lang_manager import SimpleLanguageManager

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
        
        # Initialize language manager
        from script.lang.lang_manager import SimpleLanguageManager
        self.language_manager = SimpleLanguageManager()
        
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
        save_config_action.setShortcut(QKeySequence.StandardKey.Save)
        save_config_action.triggered.connect(self.save_configuration)
        file_menu.addAction(save_config_action)
        
        # Load Configuration
        load_config_action = QAction(t('load_config', self.current_language), self)
        load_config_action.setShortcut(QKeySequence.StandardKey.Open)
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
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu(t('tools_menu', self.current_language))
        
        # Cut/Copy/Paste actions
        cut_action = QAction(t('cut', self.current_language), self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        tools_menu.addAction(cut_action)
        
        copy_action = QAction(t('copy', self.current_language), self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        tools_menu.addAction(copy_action)
        
        paste_action = QAction(t('paste', self.current_language), self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        tools_menu.addAction(paste_action)
        
        tools_menu.addSeparator()
        
        # Simulator action
        simulator_action = QAction(t('open_simulator', self.current_language, 'Open Simulator'), self)
        simulator_action.triggered.connect(self.open_simulator)
        tools_menu.addAction(simulator_action)
                
        # Language menu
        language_menu = menubar.addMenu(t('language_menu', self.current_language))
        
        # Create a language group for exclusive selection
        self.language_group = QActionGroup(self)
        self.language_group.setExclusive(True)
        
        # Add available languages
        for lang_info in language_manager.get_available_languages():
            lang_code = lang_info['code']
            lang_name = lang_info['name']
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
        help_action.setShortcut(QKeySequence("F1"))  # F1 is commonly used for Help
        help_menu.addAction(help_action)
        
        # Help -> Wiki
        wiki_action = QAction(t('wiki', self.current_language, "Wiki"), self)
        wiki_action.triggered.connect(self.open_wiki)
        help_menu.addAction(wiki_action)
        
        help_menu.addSeparator()
        
        # Help -> About
        about_action = QAction(t('about', self.current_language), self)
        about_action.triggered.connect(lambda: self.show_about())
        about_action.setShortcut(QKeySequence("F2"))  # F2 is commonly used for About
        help_menu.addAction(about_action)
        
        # Help -> Sponsor
        sponsor_action = QAction(t('sponsor', self.current_language), self)
        sponsor_action.triggered.connect(lambda: self.show_sponsor())
        sponsor_action.setShortcut(QKeySequence("F3"))  # F3 is commonly used for Sponsor
        help_menu.addAction(sponsor_action) 
    
    def show_help(self):
        from script.UI.help import HelpWindow
        self.help_window = HelpWindow(self, self.current_language)
        self.help_window.show()
        
    def open_wiki(self):
        """Open the project wiki in the default web browser."""
        wiki_url = "https://github.com/Nsfr750/Nidec_CommanderCDE/wiki"
        try:
            import webbrowser
            webbrowser.open(wiki_url)
        except Exception as e:
            logger.error(f"Failed to open wiki: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Could not open the wiki page.\n\n"
                f"Please visit: {wiki_url}"
            )
    
    def show_about(self):
        """Show the about dialog."""
        if not hasattr(self, 'about_dialog') or not self.about_dialog:
            self.about_dialog = AboutDialog(self)
        self.about_dialog.exec()
        
    def show_sponsor(self):
        """Show the sponsor dialog."""
        from script.UI.sponsor import SponsorDialog
        sponsor_dialog = SponsorDialog(self, self.language_manager)
        sponsor_dialog.exec()
        
    def get_resource_path(self, relative_path):
        """Get the correct path to a resource file, whether running as script or frozen executable."""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            return os.path.join(base_path, relative_path)
        else:
            # Running as script
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(script_dir, relative_path)
            
    def open_simulator(self):
        """Open the Nidec Commander Simulator window."""
        try:
            # Check if simulator window is already open
            if hasattr(self, 'simulator_window') and self.simulator_window.isVisible():
                self.simulator_window.activateWindow()
                self.simulator_window.raise_()
                return
                
            # Import and create the simulator window
            from script.UI.simulator import SimulatorWidget
            self.simulator_window = SimulatorWidget()
            self.simulator_window.setWindowTitle(t('open_simulator', self.current_language, 'Nidec Commander Simulator'))
            self.simulator_window.show()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                t('error', self.current_language, 'Error'),
                t('error_launching_simulator', self.current_language, 
                  'Error launching simulator: {}').format(str(e))
            )
    
    def on_simulator_finished(self, exit_code, exit_status):
        """Handle simulator process finished event."""
        if exit_code != 0 or exit_status != QProcess.ExitStatus.NormalExit:
            QMessageBox.warning(
                self,
                t('warning', self.current_language, 'Warning'),
                t('simulator_crashed', self.current_language, 
                  'The simulator has crashed or was closed with an error. Exit code: {}').format(exit_code)
            )
    
    def on_simulator_error(self, error):
        """Handle simulator process error event."""
        QMessageBox.critical(
            self,
            t('error', self.current_language, 'Error'),
            t('simulator_error', self.current_language, 
              'Simulator error: {}').format(self._simulator_process.errorString())
        )
    
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
        
        # Base colors - using PyQt6 color roles
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.Base, QColor(35, 35, 35))
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(dark_palette.ColorGroup.Active, dark_palette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        # Apply the same colors to Inactive and Disabled states
        for group in [dark_palette.ColorGroup.Inactive, dark_palette.ColorGroup.Disabled]:
            dark_palette.setColor(group, dark_palette.ColorRole.Window, QColor(53, 53, 53))
            dark_palette.setColor(group, dark_palette.ColorRole.WindowText, Qt.GlobalColor.gray)
            dark_palette.setColor(group, dark_palette.ColorRole.Base, QColor(35, 35, 35))
            dark_palette.setColor(group, dark_palette.ColorRole.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(group, dark_palette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            dark_palette.setColor(group, dark_palette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            dark_palette.setColor(group, dark_palette.ColorRole.Text, Qt.GlobalColor.gray)
            dark_palette.setColor(group, dark_palette.ColorRole.Button, QColor(53, 53, 53))
            dark_palette.setColor(group, dark_palette.ColorRole.ButtonText, Qt.GlobalColor.gray)
            dark_palette.setColor(group, dark_palette.ColorRole.BrightText, Qt.GlobalColor.red)
            dark_palette.setColor(group, dark_palette.ColorRole.Link, QColor(42, 130, 218))
            dark_palette.setColor(group, dark_palette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(group, dark_palette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        # Apply the palette
        app.setPalette(dark_palette)
        
        # Apply additional styling
        app.setStyleSheet("""
            QToolTip {
                color: #ffffff;
                background-color: #2a82da;
                border: 1px solid white;
            }
            QMenu::item:selected {
                background-color: #2a82da;
                color: white;
            }
        """)
    
    def change_language(self, checked):
        """Change the application language.
        
        Args:
            checked: Boolean indicating if the action is checked (from the triggered signal)
        """
        # Get the action that triggered this slot
        action = self.sender()
        if not action or not isinstance(action, QAction) or not action.isChecked():
            return
            
        lang_code = action.data()
        if lang_code != self.current_language:
            self.current_language = lang_code
            self.settings.setValue("language", lang_code)
            
            # Update the language menu check state
            if hasattr(self, 'language_group'):
                for action in self.language_group.actions():
                    action.setChecked(action.data() == lang_code)
            
            # Retranslate the UI
            self.retranslate_ui()
    
    def retranslate_ui(self):
        """Retranslate all UI elements with the current language."""
        # Update window title
        self.setWindowTitle(t('app_title', self.current_language))
        
        # Update menu bar
        if hasattr(self, 'menuBar'):
            menubar = self.menuBar()
            
            # Update main menus
            for menu in menubar.findChildren(QMenu):
                # Store the original title if not already stored
                if not hasattr(menu, '_original_title'):
                    menu._original_title = menu.title()
                
                # Update menu title based on original title
                if menu._original_title in [t('file_menu', 'en'), t('tools_menu', 'en'), 
                                         t('language_menu', 'en'), t('help_menu', 'en'),
                                         t('theme_menu', 'en')]:
                    if menu._original_title == t('file_menu', 'en'):
                        menu.setTitle(t('file_menu', self.current_language))
                    elif menu._original_title == t('tools_menu', 'en'):
                        menu.setTitle(t('tools_menu', self.current_language))
                    elif menu._original_title == t('language_menu', 'en'):
                        menu.setTitle(t('language_menu', self.current_language))
                    elif menu._original_title == t('help_menu', 'en'):
                        menu.setTitle(t('help_menu', self.current_language))
                    elif menu._original_title == t('theme_menu', 'en'):
                        menu.setTitle(t('theme_menu', self.current_language))
                
                # Update menu actions
                for action in menu.actions():
                    if not action.isSeparator() and action.text():
                        # Skip language and theme actions as they are handled separately
                        if action in self.language_group.actions() or action in self.theme_group.actions():
                            continue
                            
                        # Store original text if not already stored
                        if not hasattr(action, '_original_text'):
                            action._original_text = action.text()
                        
                        # Get the translation for the original text in the current language
                        # We'll use the original text as the key and fallback to the original text
                        translated_text = language_manager.tr(action._original_text, lang_code=self.current_language, default=action._original_text)
                        action.setText(translated_text)
    
    def check_for_updates(self):
        """Check for application updates."""
        try:
            # Show a message that we're checking for updates
            QMessageBox.information(
                self,
                t('checking_updates', self.current_language),
                t('checking_updates_message', self.current_language)
            )
            
            # Import the check_updates function from the updates module
            from script.utils.updates import check_updates
            
            # Call the update check function with the current version
            update_available, message, update_info = check_updates("0.0.5")  # Replace with actual version
            
            # Show the result to the user
            QMessageBox.information(
                self,
                t('update_check_complete', self.current_language, 'Update Check Complete'),
                message
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                t('update_error', self.current_language, 'Update Error'),
                f"{t('update_error_message', self.current_language, 'An error occurred while checking for updates:')}: {str(e)}"
            )
    
    def show_sponsor(self):
        """Show the sponsor dialog."""
        sponsor_dialog = SponsorDialog(parent=self, language_manager=self.language_manager)
        sponsor_dialog.exec()

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
        app.setApplicationVersion("0.0.5")
        
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
