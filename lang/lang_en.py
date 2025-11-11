"""
Nidec Commander CDE - Internationalization Module

This module provides a comprehensive internationalization (i18n) system for the Nidec
Commander CDE application. It includes translations for all user-facing strings in
multiple languages, allowing the application to be easily localized for different regions.

Key Features:
- Centralized string management for all UI elements
- Support for multiple languages (English, Italian, Spanish, etc.)
- Simple key-based string lookup with fallback to English
- Support for string formatting with dynamic values

Usage:
    # Get a translated string
    from lang.translations import t
    
    # Basic usage
    message = t('app_title', 'en')  # Returns 'Nidec Commander CDE'
    
    # With string formatting
    message = t('welcome_message', 'en', username='Admin')  # Returns 'Welcome, Admin!'

Adding a New Language:
1. Add a new language code (e.g., 'fr' for French) to the TRANSLATIONS dictionary
2. Provide translations for all keys in the new language
3. Ensure all special characters are properly encoded in UTF-8

Note: Always use UTF-8 encoding when editing this file to ensure proper handling
of special characters in different languages.

Author: [Nsfr750]
Version: 1.0.0
"""

TRANSLATIONS = {
        'app_title': 'Nidec Commander CDE',
        'welcome_message': 'Welcome to Nidec Commander CDE', 
        'file_menu': 'File',
        'tools_menu': 'Tools',
        'language_menu': 'Language',
        'theme_menu': 'Theme',
        'system_theme': 'System',
        'light_theme': 'Light',
        'dark_theme': 'Dark',
        'help_menu': 'Help',
        'about': 'About',
        'sponsor': 'Sponsor',
        'documentation': 'Documentation',
        'exit': 'Exit',
        'close': 'Close',
        'copy': 'Copy',
        'paste': 'Paste',
        'cut': 'Cut',
        'support_development': 'Support Development',
        'sponsor_on_github': 'Sponsor on GitHub',
        'join_discord': 'Join Discord',
        'buy_me_a_coffee': 'Buy Me a Coffee',
        'join_the_patreon': 'Become a Patron',
        'language_menu': 'Language',
        'check_for_updates': 'Check for Updates',
        'english': 'English',
        'italian': 'Italian',
        'version': 'Version:',
        'getting_started': 'Getting Started',
        'basic_usage': 'Basic Usage',
        'connect_device_help': 'Connect to your device using the connection menu',
        'send_commands_help': 'Send commands using the control panel',
        'monitor_status_help': 'Monitor device status in the status panel',
        'need_help': 'Need Help?',
        'visit_github': 'Visit our GitHub repository for more information:',
        'save_config': 'Save Configuration',
        'save_configuration': 'Save Configuration',
        'load_config': 'Load Configuration',
        'load_configuration': 'Load Configuration',
        'export_data': 'Export Data',
        'config_saved': 'Configuration saved successfully',
        'configuration_saved': 'Configuration saved',
        'configuration_loaded': 'Configuration loaded',
        'save_success': 'Success',
        'load_success': 'Success',
        'save_failed': 'Failed to save configuration',
        'load_failed': 'Failed to load configuration',
        'invalid_config_file': 'Invalid configuration file',
        'json_files': 'JSON Files (*.json)',
        'config_loaded': 'Configuration loaded successfully',
        'data_exported': 'Data exported successfully',
        'config_error': 'Error saving/loading configuration',
        'checking_updates': 'Checking for Updates',
        'checking_updates_message': 'Checking for available updates...',
        'update_available': 'Update Available',
        'update_available_message': 'A new version {version} is available. Would you like to download it now?',
        'no_updates': 'No Updates',
        'no_updates_message': 'You are using the latest version of the application.',
        'update_error': 'Update Error',
        'update_error_message': 'An error occurred while checking for updates',
        'restart_required': 'Restart Required',
        'restart_message': 'Please restart the application to apply the language changes.',
        
        # Language / About / Missing
        'language_name': 'English',
        'save_config': 'Save Configurarion',
        'load_config': 'Load Configuration',
        'export_data': 'Export Data',
        'about_text': 'A application to control Nidec CommanderCDE',
        'en': 'English',
        'it': 'Italian',
        
        # Connection
        'connection': 'Connection Settings',
        'connect': 'Connect',
        'disconnect': 'Disconnect',
        'port': 'Port',
        'baud_rate': 'Baud Rate',
        'modbus_address': 'Modbus Address',
        'refresh_ports': 'Refresh Ports',
        'connected': 'Connected',
        'disconnected': 'Disconnected',
        'connection_status': 'Connection Status',
        
        # Control
        'control': 'Control',
        'run': 'Run',
        'stop': 'Stop',
        'forward': 'Forward',
        'reverse': 'Reverse',
        'set_speed': 'Set Speed',
        'speed_control': 'Speed Control',
        'direction_control': 'Direction Control',
        'target_speed': 'Target Speed',
        
        # Parameters
        'parameters': 'Parameters',
        'parameter': 'Parameter',
        'value': 'Value',
        'read_parameter': 'Read Parameter',
        'write_parameter': 'Write Parameter',
        'acceleration_time': 'Acceleration Time',
        'deceleration_time': 'Deceleration Time',
        'motor_rated_current': 'Motor Rated Current',
        'maximum_frequency': 'Maximum Frequency',
        
        # Diagnostics
        'diagnostics': 'Diagnostics',
        'output_frequency': 'Output Frequency',
        'output_current': 'Output Current',
        'dc_bus_voltage': 'DC Bus Voltage',
        'drive_status': 'Drive Status',
        'fault_status': 'Fault Status',
        'reset_faults': 'Reset Faults',
        'no_faults': 'No Faults',
        'fault_detected': 'Fault Detected',
        
        # Data Logging
        'data_logging': 'Data Logging',
        'start_logging': 'Start Logging',
        'stop_logging': 'Stop Logging',
        'log_file': 'Log File',
        'browse': 'Browse...',
        'logging_interval': 'Logging Interval',
        'export': 'Export',
        'status': 'Status',
        'logging': 'Logging',
        'stopped': 'Stopped',
        'select_log_file': 'Select Log File',
        'csv_files': 'CSV Files (*.csv)',
        'all_files': 'All Files (*)',
        
        # Dashboard
        'dashboard': 'Dashboard',
        'speed_metrics': 'Speed Metrics',
        'power_metrics': 'Power Metrics',
        'current': 'Current',
        'voltage': 'Voltage',
        'power': 'Power',
        'temperature': 'Temperature',
        'rpm': 'RPM',
        'running': 'Running',
        'stopped': 'Stopped',
        'not_available': 'N/A',
        
        # Messages
        'config_saved': 'Configuration saved successfully',
        'config_loaded': 'Configuration loaded successfully',
        'data_exported': 'Data exported successfully',
        'config_error': 'Error saving/loading configuration',
        'save_config': 'Save Configuration',
        'load_config': 'Load Configuration',
        'export_data': 'Export Data',
        
        # Model Parameters
        'frequency_reference': 'Frequency Reference',
        'run_command': 'Run Command',
        'direction_control': 'Direction Control',
        'output_frequency': 'Output Frequency',
        'output_current': 'Output Current',
        'dc_bus_voltage': 'DC Bus Voltage',
        'status_register': 'Status Register',
        'fault_register': 'Fault Register',
        'accel_time': 'Acceleration Time',
        'decel_time': 'Deceleration Time',
        'motor_rated_current': 'Motor Rated Current',
        'max_frequency_reg': 'Maximum Frequency',
        'motor_rated_voltage': 'Motor Rated Voltage',
        
        # Fault Codes
        'no_fault': 'No Fault',
        'overcurrent': 'Overcurrent',
        'overvoltage': 'Overvoltage',
        'undervoltage': 'Undervoltage',
        'inverter_overheat': 'Inverter Overheat',
        'motor_overload': 'Motor Overload',
        'input_phase_loss': 'Input Phase Loss',
        'output_phase_loss': 'Output Phase Loss',
        'external_fault': 'External Fault',
        'eeprom_error': 'EEPROM Error',
        'cpu_error': 'CPU Error',
        'overload': 'Overload',
        'braking_resistor_overload': 'Braking Resistor Overload',
        'motor_stall_prevention': 'Motor Stall Prevention',
        'communication_error': 'Communication Error',

        # CDE400
        'model_CDE400_description': 'Model CDE400',
        'model_CDE400_frequency': 'Frequency',
        'model_CDE400_current': 'Current',
        'model_CDE400_voltage': 'Voltage',
        'model_CDE400_power': 'Power',
        'model_CDE400_temperature': 'Temperature',
        'model_CDE400_rpm': 'RPM',
        'model_CDE400_running': 'Rnning',
        'model_CDE400_stopped': 'Stopped',
        'model_CDE400_not_available': 'N/A',
        'model_CDE400_frequency_reference': 'Frequency Reference',
        'model_CDE400_run_command': 'Run Command',
        'model_CDE400_direction_control': 'Direction Control',
        'model_CDE400_output_frequency': 'Output Frequency',
        'model_CDE400_output_current': 'Output Current',
        'model_CDE400_dc_bus_voltage': 'DC Bus Voltage',
        'model_CDE400_status_register': 'Status Register',
        'model_CDE400_fault_register': 'Fault Register',
        'model_CDE400_accel_time': 'Acceleration Time',
        'model_CDE400_decel_time': 'Deceleration Time',
        'model_CDE400_max_frequency_reg': 'Maximum Frequency',
        'model_CDE400_motor_rated_voltage': 'Motor Rated Voltage',

        # CDE550
        'model_CDE550_description': 'Model CDE550',
        'model_CDE550_frequency': 'Frequency',
        'model_CDE550_current': 'Current',
        'model_CDE550_voltage': 'Voltage',
        'model_CDE550_power': 'Power',
        'model_CDE550_temperature': 'Temperature',
        'model_CDE550_rpm': 'RPM',
        'model_CDE550_running': 'Rnning',
        'model_CDE550_stopped': 'Stopped',
        'model_CDE550_not_available': 'N/A',
        'model_CDE550_frequency_reference': 'Frequency Reference',
        'model_CDE550_run_command': 'Run Command',
        'model_CDE550_direction_control': 'Direction Control',
        'model_CDE550_output_frequency': 'Output Frequency',
        'model_CDE550_output_current': 'Output Current',
        'model_CDE550_dc_bus_voltage': 'DC Bus Voltage',
        'model_CDE550_status_register': 'Status Register',
        'model_CDE550_fault_register': 'Fault Register',
        'model_CDE550_accel_time': 'Acceleration Time',
        'model_CDE550_decel_time': 'Deceleration Time',
        'model_CDE550_max_frequency_reg': 'Maximum Frequency',
        'model_CDE550_motor_rated_voltage': 'Motor Rated Voltage',

        # CDE750
        'model_CDE750_description': 'Model CDE750',
        'model_CDE750_frequency': 'Frequency',
        'model_CDE750_current': 'Current',
        'model_CDE750_voltage': 'Voltage',
        'model_CDE750_power': 'Power',
        'model_CDE750_temperature': 'Temperature',
        'model_CDE750_rpm': 'RPM',
        'model_CDE750_running': 'Rnning',
        'model_CDE750_stopped': 'Stopped',
        'model_CDE750_not_available': 'N/A',
        'model_CDE750_frequency_reference': 'Frequency Reference',
        'model_CDE750_run_command': 'Run Command',
        'model_CDE750_direction_control': 'Direction Control',
        'model_CDE750_output_frequency': 'Output Frequency',
        'model_CDE750_output_current': 'Output Current',
        'model_CDE750_dc_bus_voltage': 'DC Bus Voltage',
        'model_CDE750_status_register': 'Status Register',
        'model_CDE750_fault_register': 'Fault Register',
        'model_CDE750_accel_time': 'Acceleration Time',
        'model_CDE750_decel_time': 'Deceleration Time',
        'model_CDE750_max_frequency_reg': 'Maximum Frequency',
        'model_CDE750_motor_rated_voltage': 'Motor Rated Voltage',

        # CDE1100S
        'model_CDE1100S_description': 'Model CDE1100S',
        'model_CDE1100S_frequency': 'Frequency',
        'model_CDE1100S_current': 'Current',
        'model_CDE1100S_voltage': 'Voltage',
        'model_CDE1100S_power': 'Power',
        'model_CDE1100S_temperature': 'Temperature',
        'model_CDE1100S_rpm': 'RPM',
        'model_CDE1100S_running': 'Rnning',
        'model_CDE1100S_stopped': 'Stopped',
        'model_CDE1100S_not_available': 'N/A',
        'model_CDE1100S_frequency_reference': 'Frequency Reference',
        'model_CDE1100S_run_command': 'Run Command',
        'model_CDE1100S_direction_control': 'Direction Control',
        'model_CDE1100S_output_frequency': 'Output Frequency',
        'model_CDE1100S_output_current': 'Output Current',
        'model_CDE1100S_dc_bus_voltage': 'DC Bus Voltage',
        'model_CDE1100S_status_register': 'Status Register',
        'model_CDE1100S_fault_register': 'Fault Register',
        'model_CDE1100S_accel_time': 'Acceleration Time',
        'model_CDE1100S_decel_time': 'Deceleration Time',
        'model_CDE1100S_max_frequency_reg': 'Maximum Frequency',
        'model_CDE1100S_motor_rated_voltage': 'Motor Rated Voltage',
    }