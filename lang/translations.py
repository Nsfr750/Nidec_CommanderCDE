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

from typing import Dict, Any, Optional

# Translation dictionary
# 
# Structure:
# {
#   'language_code': {
#       'key': 'translated_string',
#       ...
#   },
#   ...
# }
#
# Each language should have translations for all keys to ensure consistent UI.
# If a translation is missing for a key in a language, the English version will be used.

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'en': {
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
    },
    # Add more languages as needed
    'it': {
        'app_title': 'Nidec Commander CDE',
        'welcome_message': 'Benvenuto in Nidec Commander CDE',
        'language_name': 'Italiano',
        'file_menu': 'File',
        'tools_menu': 'Strumenti',
        'language_menu': 'Lingua',
        'theme_menu': 'Tema',
        'system_theme': 'Sistema',
        'light_theme': 'Chiaro',
        'dark_theme': 'Scuro',
        'help_menu': 'Aiuto',
        'about': 'Informazioni',
        'sponsor': 'Supporta',
        'documentation': 'Documentazione',
        'exit': 'Esci',
        'close': 'Chiudi',
        'copy': 'Copia',
        'paste': 'Incolla',
        'cut': 'Taglia',
        'support_development': 'Supporta lo Sviluppo',
        'sponsor_on_github': 'Supporta su GitHub',
        'join_discord': 'Unisciti a Discord',
        'buy_me_a_coffee': 'Offrimi un caffè',
        'join_the_patreon': 'Diventa un Patreon',
        'check_for_updates': 'Controlla aggiornamenti',
        'language_menu': 'Lingua',
        'english': 'Inglese',
        'italian': 'Italiano',
        'version': 'Versione',
        'about_text': 'Un\'applicazione per il controllo dei Nidec Commander CDE',
        'getting_started': 'Per Iniziare',
        'basic_usage': 'Utilizzo di Base',
        'connect_device_help': 'Connetti il dispositivo utilizzando il menu di connessione',
        'send_commands_help': 'Invia comandi utilizzando il pannello di controllo',
        'monitor_status_help': 'Monitora lo stato del dispositivo nel pannello di stato',
        'need_help': 'Hai bisogno di aiuto?',
        'visit_github': 'Visita il nostro repository GitHub per maggiori informazioni:',
        'checking_updates': 'Controllo aggiornamenti',
        'checking_updates_message': 'Controllo degli aggiornamenti disponibili...',
        'update_available': 'Aggiornamento Disponibile',
        'update_available_message': 'È disponibile una nuova versione {version}. Vuoi scaricarla ora?',
        'no_updates': 'Nessun Aggiornamento',
        'no_updates_message': 'Stai utilizzando l\'ultima versione dell\'applicazione.',
        'update_error': 'Errore di Aggiornamento',
        'update_error_message': 'Si è verificato un errore durante il controllo degli aggiornamenti',
        'download_update': 'Scarica Aggiornamento',
        'remind_me_later': 'Ricordamelo più tardi',
        'restart_required': 'Riavvio richiesto',
        'restart_message': 'Riavviare l\'applicazione per applicare le modifiche alla lingua.',
       
        # Language / About / Missing
        'language_name': 'Italiano',
        'save_config': 'Salva Configurazione',
        'load_config': 'Carica Configurazione',
        'export_data': 'Esporta Dati',
        'about_text': 'Un\'applicazione per il controllo dei Nidec CommanderCDE',
        'en': 'Inglese',
        'it': 'Italiano',

        # Connection
        'connection': 'Impostazioni Connessione',
        'connect': 'Collegati',
        'disconnect': 'Scollegati',
        'port': 'Porta',
        'baud_rate': 'Velovità Baud',
        'modbus_address': 'Indirizzo Modbus',
        'refresh_ports': 'Aggiorna Porte',
        'connected': 'Connesso',
        'disconnected': 'Disconnesso',
        'connection_status': 'Stato Connessione',
        
        # Control
        'control': 'Controlla',
        'run': 'Avvia',
        'stop': 'Ferma',
        'forward': 'Avanti',
        'reverse': 'Indietro',
        'set_speed': 'Imposta Velocità',
        'speed_control': 'Controllo Velocità',
        'direction_control': 'Controllo Direzione',
        'target_speed': 'Velocità di Riferimento',
        
        # Parameters
        'parameters': 'Parametri',
        'parameter': 'Parametri',
        'value': 'Valore',
        'read_parameter': 'Leggi Parametro',
        'write_parameter': 'Scrivi Parametro',
        'acceleration_time': 'Tempo di Accelerazione',
        'deceleration_time': 'Tempo di Decelerazione',
        'motor_rated_current': 'Corrente di Riferimento',
        'maximum_frequency': 'Frequenza Massima',
        
        # Diagnostics
        'diagnostics': 'Diagnostica',
        'output_frequency': 'Frequenza di Output',
        'output_current': 'Corrente di Output',
        'dc_bus_voltage': 'Voltaggio DC Bus',
        'drive_status': 'Stato del Drive',
        'fault_status': 'Stato dei Fault',
        'reset_faults': 'Reset dei Fault',
        'no_faults': 'Nessun Guasto',
        'fault_detected': 'Guasto Rilevato',
        
        # Data Logging
        'data_logging': 'Logging Dati',
        'start_logging': 'Avvia Logging',
        'stop_logging': 'Ferma Logging',
        'log_file': 'Log File',
        'browse': 'Sfoglia...',
        'logging_interval': 'Intervallo Logging',
        'export': 'Esporta',
        'status': 'Stato',
        'logging': 'Logging',
        'stopped': 'Fermato',
        'select_log_file': 'Seleziona File di Log',
        'csv_files': 'CSV Files (*.csv)',
        'all_files': 'Tutti i Files (*)',
        
        # Dashboard
        'dashboard': 'Cruscotto',
        'speed_metrics': 'Metriche di Velocità',
        'power_metrics': 'Metriche di Potenza',
        'status': 'Stato',
        'output_frequency': 'Frequenza Uscita',
        'output_speed': 'Velocità Uscita',
        'setpoint_frequency': 'Frequenza Impostata',
        'output_current': 'Corrente Uscita',
        'dc_bus_voltage': 'Tensione Bus CC',
        'output_voltage': 'Tensione Uscita',
        'output_power': 'Potenza Uscita',
        'drive_status': 'Stato Azionamento',
        'direction': 'Direzione',
        'run_time': 'Tempo di Funzionamento',
        'current': 'Corrente',
        'voltage': 'Tensione',
        'power': 'Potenza',
        'temperature': 'Temperatura',
        'rpm': 'RPM',
        'running': 'Avviato',
        'stopped': 'Fermato',
        'forward': 'Avanti',
        'reverse': 'Indietro',
        'not_available': 'N/D',
        
        # Messages
        'config_saved': 'Configurazione salvata con successo',
        'config_loaded': 'Configurazione caricata con successo',
        'data_exported': 'Dati esportati con successo',
        'config_error': 'Errore salvataggio/caricamento configurazione',
        'save_config': 'Salva Configurazione',
        'load_config': 'Carica Configurazione',
        'export_data': 'Esporta Dati',
        
        # Model Parameters
        'frequency_reference': 'Frequenza di Riferimento',
        'run_command': 'Comando di Avvio',
        'direction_control': 'Controllo Direzione',
        'output_frequency': 'Frequenza di Output',
        'output_current': 'Corrente di Output',
        'dc_bus_voltage': 'Voltaggio DC Bus',
        'status_register': 'Register di Stato',
        'fault_register': 'Registro Guasti',
        'accel_time': 'Tempo di Accelerazione',
        'decel_time': 'Tempo di Decelerazione',
        'motor_rated_current': 'Corrente di Riferimento',
        'max_frequency_reg': 'Frequenza Massima',
        'motor_rated_voltage': 'Tensione di Riferimento',
        
        # Fault Codes
        'no_fault': 'Nessun Guasto',
        'overcurrent': 'Sovracorrente',
        'overvoltage': 'Sovravoltaggio',
        'undervoltage': 'Sottovoltaggio',
        'inverter_overheat': 'Surriscaldamento Inverter',
        'motor_overload': 'Sovraccarico Motore',
        'input_phase_loss': 'Perdita in fase di ingresso',
        'output_phase_loss': 'Perdita in fase di uscita',
        'external_fault': 'Guasto Esternoi',
        'eeprom_error': 'Errore EEPROM',
        'cpu_error': 'Errore CPU',
        'overload': 'Sovraccarico',
        'braking_resistor_overload': 'Sovraccarico Resistenza Frenata',
        'motor_stall_prevention': 'Prevenzione Stallo del Motore',
        'communication_error': 'Errore di Comunicazione',   

        # CDE400
        'model_CDE400_description': 'Modello CDE400',
        'model_CDE400_frequency': 'Frequenza',
        'model_CDE400_current': 'Corrente',
        'model_CDE400_voltage': 'Tensione',
        'model_CDE400_power': 'Potenza',
        'model_CDE400_temperature': 'Temperatura',
        'model_CDE400_rpm': 'RPM',
        'model_CDE400_running': 'In Esecuzione',
        'model_CDE400_stopped': 'Fermo',
        'model_CDE400_not_available': 'N/D',
        'model_CDE400_frequency_reference': 'Frequenza di Riferimento',
        'model_CDE400_run_command': 'Comando di Avvio',
        'model_CDE400_direction_control': 'Controllo Direzione',
        'model_CDE400_output_frequency': 'Frequenza di Output',
        'model_CDE400_output_current': 'Corrente di Output',
        'model_CDE400_dc_bus_voltage': 'Voltaggio DC Bus',
        'model_CDE400_status_register': 'Register di Stato',
        'model_CDE400_fault_register': 'Registro Guasti',
        'model_CDE400_accel_time': 'Tempo di Accelerazione',
        'model_CDE400_decel_time': 'Tempo di Decelerazione',
        'model_CDE400_motor_rated_current': 'Corrente di Riferimento',
        'model_CDE400_max_frequency_reg': 'Frequenza Massima',
        'model_CDE400_motor_rated_voltage': 'Tensione di Riferimento',

        # CDE550
        'model_CDE550_description': 'Modello CDE550',
        'model_CDE550_frequency': 'Frequenza',
        'model_CDE550_current': 'Corrente',
        'model_CDE550_voltage': 'Tensione',
        'model_CDE550_power': 'Potenza',
        'model_CDE550_temperature': 'Temperatura',
        'model_CDE550_rpm': 'RPM',
        'model_CDE550_running': 'In Esecuzione',
        'model_CDE550_stopped': 'Fermo',
        'model_CDE550_not_available': 'N/D',
        'model_CDE550_frequency_reference': 'Frequenza di Riferimento',
        'model_CDE550_run_command': 'Comando di Avvio',
        'model_CDE550_direction_control': 'Controllo Direzione',
        'model_CDE550_output_frequency': 'Frequenza di Output',
        'model_CDE550_output_current': 'Corrente di Output',
        'model_CDE550_dc_bus_voltage': 'Voltaggio DC Bus',
        'model_CDE550_status_register': 'Register di Stato',
        'model_CDE550_fault_register': 'Registro Guasti',
        'model_CDE550_accel_time': 'Tempo di Accelerazione',
        'model_CDE550_decel_time': 'Tempo di Decelerazione',
        'model_CDE550_motor_rated_current': 'Corrente di Riferimento',
        'model_CDE550_max_frequency_reg': 'Frequenza Massima',
        'model_CDE550_motor_rated_voltage': 'Tensione di Riferimento',

        # CDE750
        'model_CDE750_description': 'Modello CDE750',
        'model_CDE750_frequency': 'Frequenza',
        'model_CDE750_current': 'Corrente',
        'model_CDE750_voltage': 'Tensione',
        'model_CDE750_power': 'Potenza',
        'model_CDE750_temperature': 'Temperatura',
        'model_CDE750_rpm': 'RPM',
        'model_CDE750_running': 'In Esecuzione',
        'model_CDE750_stopped': 'Fermo',
        'model_CDE750_not_available': 'N/D',
        'model_CDE750_frequency_reference': 'Frequenza di Riferimento',
        'model_CDE750_run_command': 'Comando di Avvio',
        'model_CDE750_direction_control': 'Controllo Direzione',
        'model_CDE750_output_frequency': 'Frequenza di Output',
        'model_CDE750_output_current': 'Corrente di Output',
        'model_CDE750_dc_bus_voltage': 'Voltaggio DC Bus',
        'model_CDE750_status_register': 'Register di Stato',
        'model_CDE750_fault_register': 'Registro Guasti',
        'model_CDE750_accel_time': 'Tempo di Accelerazione',
        'model_CDE750_decel_time': 'Tempo di Decelerazione',
        'model_CDE750_motor_rated_current': 'Corrente di Riferimento',
        'model_CDE750_max_frequency_reg': 'Frequenza Massima',
        'model_CDE750_motor_rated_voltage': 'Tensione di Riferimento',

        # CDE1100S
        'model_CDE1100S_description': 'Modello CDE1100S',
        'model_CDE1100S_frequency': 'Frequenza',
        'model_CDE1100S_current': 'Corrente',
        'model_CDE1100S_voltage': 'Tensione',
        'model_CDE1100S_power': 'Potenza',
        'model_CDE1100S_temperature': 'Temperatura',
        'model_CDE1100S_rpm': 'RPM',
        'model_CDE1100S_running': 'In Esecuzione',
        'model_CDE1100S_stopped': 'Fermo',
        'model_CDE1100S_not_available': 'N/D',
        'model_CDE1100S_frequency_reference': 'Frequenza di Riferimento',
        'model_CDE1100S_run_command': 'Comando di Avvio',
        'model_CDE1100S_direction_control': 'Controllo Direzione',
        'model_CDE1100S_output_frequency': 'Frequenza di Output',
        'model_CDE1100S_output_current': 'Corrente di Output',
        'model_CDE1100S_dc_bus_voltage': 'Voltaggio DC Bus',
        'model_CDE1100S_status_register': 'Register di Stato',
        'model_CDE1100S_fault_register': 'Registro Guasti',
        'model_CDE1100S_accel_time': 'Tempo di Accelerazione',
        'model_CDE1100S_decel_time': 'Tempo di Decelerazione',
        'model_CDE1100S_motor_rated_current': 'Corrente di Riferimento',
        'model_CDE1100S_max_frequency_reg': 'Frequenza Massima',
        'model_CDE1100S_motor_rated_voltage': 'Tensione di Riferimento',
    },
 }

def t(key: str, lang: str = 'en', **kwargs: Any) -> str:
    """
    Retrieve a translated string for the given key and language.
    
    This function looks up the provided key in the translations dictionary for the
    specified language. If the key is not found in the specified language, it falls
    back to English. If the key is not found in English, it returns the key itself.
    
    The function also supports string formatting using Python's string format syntax.
    Any additional keyword arguments will be used to format the translated string.
    
    Args:
        key: The translation key to look up
        lang: Two-letter language code (e.g., 'en', 'it'). Defaults to 'en'.
        **kwargs: Format arguments that will be substituted into the translated string
        
    Returns:
        str: The translated and formatted string, or the original key if translation fails
        
    Example:
        # Basic usage
        >>> t('app_title', 'en')
        'Nidec Commander CDE'
        
        # With string formatting
        >>> t('welcome_message', 'en', username='Admin')
        'Welcome, Admin!'
        
        # Fallback to English
        >>> t('nonexistent_key', 'fr')
        'nonexistent_key'
    """
    try:
        # Ensure key is a string
        key = str(key)
        
        # Try to get the translation for the specified language
        translation = TRANSLATIONS.get(lang, {}).get(key, '')
        
        # If not found in the specified language, try English
        if not translation and lang != 'en':
            translation = TRANSLATIONS.get('en', {}).get(key, '')
        
        # If still not found, use the key itself
        if not translation:
            # Log missing translation
            if key and not key.startswith('_'):  # Don't log internal keys
                print(f"Warning: Missing translation for key '{key}' in language '{lang}'")
            return key
            
        # Format the string if there are any kwargs
        if kwargs:
            try:
                return str(translation).format(**kwargs)
            except (KeyError, ValueError) as e:
                # If formatting fails, log the error and return the unformatted string
                print(f"Warning: Failed to format translation for key '{key}': {str(e)}")
                return str(translation)
                
        return str(translation)
        
    except Exception as e:
        # In case of any error, log the error and return the key
        print(f"Error in translation for key '{key}' in language '{lang}': {str(e)}")
        return str(key)
        return key
