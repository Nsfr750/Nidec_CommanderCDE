"""
Update System for Nidec CommanderCDE

This module handles checking for and applying updates to the application.
"""

import sys
import json
import urllib.request
import platform
import os
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta

# Import language manager for translations
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
    return language_manager.tr(key, default=default or key, lang_code=language)

class UpdateChecker:
    """Class to handle update checking and downloading."""
    
    # GitHub repository information
    REPO_OWNER = "Nsfr750"
    REPO_NAME = "Nidec_CommanderCDE"
    CONFIG_FILE = Path(__file__).parent.parent.parent / "config" / "updates.json"
    
    def __init__(self, current_version: str):
        """Initialize the update checker.
        
        Args:
            current_version: Current version of the application
        """
        self.current_version = current_version
        self.latest_version = None
        self.release_notes = ""
        self.download_url = None
        
        # Ensure config directory exists
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the update configuration from file.
        
        Returns:
            Dict: The loaded configuration
        """
        default_config = {
            "last_checked": "",
            "last_version": None,
            "dont_ask_until": None
        }
        
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Ensure all required keys exist
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    return config
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading update config: {e}")
            
        return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save the update configuration to file.
        
        Args:
            config: The configuration to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            logger.error(f"Error saving update config: {e}")
            return False
    
    def should_check_for_updates(self) -> bool:
        """Check if we should check for updates based on the last check time.
        
        Returns:
            bool: True if we should check for updates, False otherwise
        """
        config = self._load_config()
        
        # If we have a "don't ask until" date in the future, don't check
        if config["dont_ask_until"]:
            try:
                dont_ask_until = datetime.fromisoformat(config["dont_ask_until"])
                if datetime.now() < dont_ask_until:
                    return False
            except (ValueError, TypeError):
                pass
                
        # If we've never checked or it's been more than a day since last check
        if not config["last_checked"]:
            return True
            
        try:
            last_checked = datetime.fromisoformat(config["last_checked"])
            return (datetime.now() - last_checked) > timedelta(days=1)
        except (ValueError, TypeError):
            return True
    
    def update_last_checked(self, dont_ask_until: str = None) -> None:
        """Update the last checked timestamp in the config.
        
        Args:
            dont_ask_until: Optional ISO format datetime string to not ask again until
        """
        config = self._load_config()
        config["last_checked"] = datetime.now().isoformat()
        if dont_ask_until:
            config["dont_ask_until"] = dont_ask_until
        self._save_config(config)
    
    def check_for_updates(self, force: bool = False) -> Tuple[bool, str]:
        """Check if a newer version is available.
        
        Args:
            force: If True, force a check even if we recently checked
            
        Returns:
            Tuple[bool, str]: (update_available, message)
        """
        # Check if we should skip the update check
        if not force and not self.should_check_for_updates():
            config = self._load_config()
            if config["last_version"] and self._compare_versions(
                self.current_version, config["last_version"]) < 0:
                return True, t('update_available', 'en', 
                            f'Version {config["last_version"]} is available!')
            return False, t('no_updates', 'en', 'You are using the latest version')
        
        try:
            # Get the latest release information from GitHub
            api_url = f"https://api.github.com/repos/{self.REPO_OWNER}/{self.REPO_NAME}/releases/latest"
            
            with urllib.request.urlopen(api_url) as response:
                if response.status != 200:
                    return False, t('update_check_failed', 'en', 'Failed to check for updates')
                
                data = json.loads(response.read().decode())
                self.latest_version = data.get('tag_name', '').lstrip('v')
                self.release_notes = data.get('body', '')
                
                # Check if we have any assets to download
                if 'assets' in data and len(data['assets']) > 0:
                    self.download_url = data['assets'][0].get('browser_download_url')
                
                # Save the latest version to config
                config = self._load_config()
                config["last_checked"] = datetime.now().isoformat()
                config["last_version"] = self.latest_version
                self._save_config(config)
                
                # Compare versions
                if self._compare_versions(self.current_version, self.latest_version) < 0:
                    return True, t('update_available', 'en', f'Version {self.latest_version} is available!')
                else:
                    return False, t('no_updates', 'en', 'You are using the latest version')
                    
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return False, t('update_check_error', 'en', f'Error checking for updates: {str(e)}')
    
    def download_update(self, download_dir: str = None) -> Tuple[bool, str]:
        """Download the latest update.
        
        Args:
            download_dir: Directory to save the downloaded file
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.download_url:
            return False, t('no_download_url', 'en', 'No download URL available')
        
        try:
            # Determine the download directory
            if not download_dir:
                download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            
            # Create the directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)
            
            # Extract the filename from the URL
            filename = os.path.basename(self.download_url)
            filepath = os.path.join(download_dir, filename)
            
            # Download the file
            urllib.request.urlretrieve(self.download_url, filepath)
            
            return True, t('download_complete', 'en', f'Downloaded to: {filepath}')
            
        except Exception as e:
            return False, t('download_failed', 'en', f'Download failed: {str(e)}')
    
    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int:
        """Compare two version strings.
        
        Args:
            v1: First version string (e.g., '1.2.3')
            v2: Second version string (e.g., '1.3.0')
            
        Returns:
            int: -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2
        """
        def parse_version(version: str) -> Tuple[int, ...]:
            # Handle None or empty strings
            if not version:
                return (0, 0, 0)
                
            # Remove any 'v' prefix and split by dots
            version = str(version).lstrip('v')
            parts = version.split('.')
            
            # Convert to integers, defaulting to 0 for missing parts
            return tuple(int(part) if part.isdigit() else 0 for part in parts)
        
        v1_parts = parse_version(v1)
        v2_parts = parse_version(v2)
        
        # Compare each part
        for v1_part, v2_part in zip(v1_parts, v2_parts):
            if v1_part < v2_part:
                return -1
            elif v1_part > v2_part:
                return 1
        
        # If all parts are equal but one version has more parts
        return (len(v1_parts) > len(v2_parts)) - (len(v1_parts) < len(v2_parts))


def check_updates(current_version: str) -> Tuple[bool, str, Dict]:
    """Check for updates and return the result.
    
    Args:
        current_version: Current version of the application
        
    Returns:
        Tuple[bool, str, Dict]: (update_available, message, update_info)
    """
    checker = UpdateChecker(current_version)
    update_available, message = checker.check_for_updates()
    
    update_info = {
        'current_version': current_version,
        'latest_version': checker.latest_version,
        'release_notes': checker.release_notes,
        'download_url': checker.download_url
    }
    
    return update_available, message, update_info
