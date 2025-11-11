"""
Update checking functionality for the Nidec Commander application.
"""
import logging
from typing import Optional, Tuple, Dict, Any
import requests
import json
from pathlib import Path
import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QProgressBar, QHBoxLayout, QMessageBox, QWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject

# Get the application directory
APP_DIR = Path(__file__).parent.parent
UPDATES_FILE = APP_DIR / 'updates.json'

# Add the script directory to the Python path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Import language manager
from lang.lang_manager import SimpleLanguageManager

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

# Configure logger
logger = logging.getLogger(__name__)

class UpdateChecker(QObject):
    """Handles checking for application updates."""
    
    update_available = pyqtSignal(bool, str, str)  # success, version, url
    
    def __init__(self, current_version: str, lang: str = 'en', parent: Optional[QWidget] = None):
        """Initialize the update checker.
        
        Args:
            current_version: The current version of the application.
            lang: Language code for translations.
            parent: Parent widget for dialogs.
        """
        super().__init__(parent)
        self.current_version = current_version
        self.lang = lang
        self.config_path = UPDATES_FILE
        self.config = self._load_config()
        self.update_url = "https://api.github.com/repos/Nsfr750/Nidec_CommanderCDE/releases/latest"
    
    def _load_config(self) -> dict:
        """Load the update configuration."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading update config: {e}")
        return {
            'last_checked': None,
            'last_version': None,
            'dont_ask_until': None
        }
    
    def _save_config(self) -> None:
        """Save the update configuration."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving update config: {e}")
    
    def check_for_updates(self, force_check: bool = False) -> None:
        """Check for updates.
        
        Args:
            force_check: If True, skip the cache and force a check.
        """
        # Check if we should skip the update check
        if not force_check and not self._should_check_for_updates():
            self.update_available.emit(False, "", "")
            return
            
        try:
            response = requests.get(self.update_url, timeout=10)
            response.raise_for_status()
            latest_release = response.json()
            
            # Save the last check time
            self.config['last_checked'] = self._get_current_time()
            self._save_config()
            
            # Compare versions
            latest_version = latest_release.get('tag_name', '').lstrip('v')
            if self._is_newer_version(latest_version, self.current_version):
                self.update_available.emit(
                    True,
                    latest_version,
                    latest_release.get('html_url', '')
                )
            else:
                self.update_available.emit(False, "", "")
            
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            self.update_available.emit(False, "", "")
    
    def _should_check_for_updates(self) -> bool:
        """Check if we should check for updates."""
        # Implement logic to check if we should skip the update check
        return True
    
    def _get_current_time(self) -> str:
        """Get the current time."""
        # Implement logic to get the current time
        return ""
    
    def _is_newer_version(self, v1: str, v2: str) -> bool:
        """Compare two version strings.
        
        Returns:
            True if v1 is newer than v2, False otherwise
        """
        def parse_version(v: str) -> list:
            return [int(x) for x in v.split('.')]
            
        try:
            v1_parts = parse_version(v1)
            v2_parts = parse_version(v2)
            
            # Pad with zeros if versions have different lengths
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts += [0] * (max_len - len(v1_parts))
            v2_parts += [0] * (max_len - len(v2_parts))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return True
                elif v1_parts[i] < v2_parts[i]:
                    return False
            return False
            
        except (ValueError, AttributeError):
            # Fallback to string comparison if version format is invalid
            return v1 > v2


class UpdateCheckThread(QThread):
    """Thread for checking updates in the background."""
    
    update_available = pyqtSignal(bool, str, str)  # success, version, url
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, current_version: str, lang: str = 'en', force_check: bool = False, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.current_version = current_version
        self.lang = lang
        self.force_check = force_check
        self.checker = UpdateChecker(current_version, lang, parent)
        
    def run(self):
        """Run the update check in a separate thread."""
        self.checker.update_available.connect(self._on_update_available)
        self.checker.check_for_updates(force_check=self.force_check)
    
    def _on_update_available(self, has_update: bool, version: str, url: str) -> None:
        """Forward the update available signal."""
        self.update_available.emit(has_update, version, url)


def check_for_updates(parent: Optional[QWidget] = None, lang: str = 'en', 
                     current_version: str = "1.0.0", force_check: bool = False) -> None:
    """Check for application updates and show a dialog if an update is available.
    
    Args:
        parent: Parent window for dialogs.
        lang: Language code for translations.
        current_version: Current application version.
        force_check: If True, skip the cache and force a check.
    """
    def show_update_dialog(version: str, url: str) -> None:
        """Show the update available dialog."""
        dialog = QDialog(parent)
        dialog.setWindowTitle(t('update_available', lang))
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Message
        msg = QLabel(t('update_available_message', lang).format(version=version))
        msg.setWordWrap(True)
        layout.addWidget(msg)
        
        # Buttons
        btn_box = QHBoxLayout()
        
        def open_download():
            from PyQt6.QtGui import QDesktopServices
            from PyQt6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl(url))
            dialog.accept()
        
        download_btn = QPushButton(t('download_update', lang))
        download_btn.clicked.connect(open_download)
        btn_box.addWidget(download_btn)
        
        later_btn = QPushButton(t('remind_me_later', lang))
        later_btn.clicked.connect(dialog.reject)
        btn_box.addWidget(later_btn)
        
        layout.addLayout(btn_box)
        
        dialog.exec_()
    
    # Create and start the update check thread
    thread = UpdateCheckThread(current_version, lang, force_check, parent)
    
    def on_update_available(has_update: bool, version: str, url: str) -> None:
        if has_update:
            show_update_dialog(version, url)
        elif force_check:
            QMessageBox.information(
                parent,
                t('no_updates', lang),
                t('no_updates_message', lang)
            )
    
    thread.update_available.connect(on_update_available)
    thread.start()
    
    def on_error(error: str) -> None:
        QMessageBox.critical(
            parent,
            t('update_error', lang),
            t('update_error_message', lang).format(error=error)
        )
    
    thread.error_occurred.connect(on_error)
