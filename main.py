"""
Nidec CommanderCDE - Main Application Module

This module serves as the main entry point for the Nidec CommanderCDE application.
It provides a graphical user interface for controlling and monitoring Nidec motor drives.

Key Features:
- Connection management for Nidec drives
- Real-time monitoring of drive parameters
- Parameter configuration and tuning
- Fault diagnostics and logging
- Multi-language support
- Data logging and export

Dependencies:
- PyQt6: For the graphical user interface
- serial: For serial port management

Author: Nsfr750
Version: 0.0.4
"""

import sys
import os
import json
import csv
import time
from datetime import datetime
import serial.tools.list_ports
from pathlib import Path
from typing import Optional

# Add the script directory to the Python path
script_dir = Path(__file__).parent / 'script'
sys.path.insert(0, str(script_dir))

# PyQt6 imports for GUI components
from PyQt6.QtCore import QTimer, QSettings, QDateTime, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QGroupBox, QLineEdit,
    QMessageBox, QTabWidget, QFormLayout, QDoubleSpinBox, QCheckBox,
    QSpinBox, QFileDialog, QStatusBar, QTableWidget, QTableWidgetItem, 
    QHeaderView, QGridLayout
)

# No sip import needed for PyQt6
from PyQt6.QtGui import QIcon

# Local imports
from nidec_models import get_model_list, get_model_config, FAULT_CODES
from menu import MainWindow  # Main application window with menu bar
from lang.lang_manager import SimpleLanguageManager  # Language manager for internationalization

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
    return language_manager.tr(key, default or key, lang_code=language)

class NidecCommanderGUI(MainWindow):
    """
    Main application window for Nidec Commander CDE.
    
    This class extends the MainWindow class from menu.py and implements the core
    functionality of the application, including:
    - Drive connection management
    - Real-time monitoring
    - Parameter configuration
    - Fault diagnostics
    - Data logging
    
    Attributes:
        client: Nidec drive client instance for communication
        connected: Boolean indicating connection status
        current_model: Currently selected drive model
        current_language: Current UI language
        model_config: Configuration for the current drive model
        settings: QSettings instance for persistent storage
        logging_enabled: Flag for data logging status
    """
    
    def __init__(self):
        """Initialize the NidecCommanderGUI application."""
        # Initialize the MainWindow parent class first
        super().__init__()
        
        # Set up our application-specific attributes
        self.client = None
        self.connected = False
        self.current_model = "CDE400"
        self.model_config = get_model_config(self.current_model, self.current_language)
        self.settings = QSettings("NidecCommander", "CDE_Control")
        
        # Connect language change signal to update UI
        self.languageChanged = self.language_changed
        
        # Data logging attributes
        self.logging_enabled = False
        self.log_file = None
        self.csv_writer = None
        self.log_start_time = None
        self.log_entries = []
        self.log_interval = 1000  # Logging interval in ms
        self.last_log_time = 0
        
        # Window settings
        self.setWindowTitle(t('app_title', self.current_language))
        self.setWindowIcon(QIcon("images/icon.png"))
        self.setMinimumSize(1000, 750)
        
        # Load saved settings
        self.load_settings()
        
        # Initialize the UI
        self.setup_ui()
        
        # Apply translations after UI is set up
        self.retranslate_ui()
        
        # Show the window
        self.show()
        
    def load_settings(self):
        """Load application settings"""
        self.current_model = self.settings.value("model", "CDE400")
        self.current_language = self.settings.value("language", "en")
        self.model_config = get_model_config(self.current_model, self.current_language)
        
        # Load logging settings
        self.logging_enabled = self.settings.value("logging_enabled", "false").lower() == "true"
        self.log_interval = int(self.settings.value("log_interval", 1000))
        
        # Load last used directory
        self.last_used_dir = self.settings.value("last_used_dir", os.path.expanduser("~"))
        
        # Update status bar if it exists
        if hasattr(self, 'status_model'):
            self.status_model.setText(f"Model: {self.current_model}")
        
        # Update logging status if UI elements exist
        if hasattr(self, 'logging_status_label'):
            self.update_logging_status()
        
    def save_settings(self):
        """Save application settings"""
        self.settings.setValue("model", self.current_model)
        self.settings.setValue("language", self.current_language)
        self.settings.setValue("logging_enabled", str(self.logging_enabled).lower())
        self.settings.setValue("log_interval", str(self.log_interval))
        
        # Save window geometry and state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # Save last used directory
        if hasattr(self, 'last_used_dir'):
            self.settings.setValue("last_used_dir", self.last_used_dir)
            
        # Save connection settings if UI is initialized
        if hasattr(self, 'port_combo') and hasattr(self, 'baud_combo'):
            self.settings.setValue("port", self.port_combo.currentText())
            self.settings.setValue("baudrate", self.baud_combo.currentText())
        
    def setup_ui(self):
        """Initialize the main UI components"""
        # Clear the existing layout
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
            
        # Use the layout from the parent class
        layout = self.layout
        
        # Model selection
        self.create_model_selection()
        layout.addWidget(self.model_group)
        
        # Connection group
        self.create_connection_group()
        layout.addWidget(self.connection_group)
        
        # Tab widget for different control sections
        self.tabs = QTabWidget()
        
        # Dashboard tab
        self.setup_dashboard_tab()
        
        # Control tab (already included in dashboard)
        
        # Parameters Tab
        self.setup_parameters_tab()
        
        # Diagnostics Tab
        self.setup_diagnostics_tab()
        
        # Logging Tab
        self.setup_data_logging_tab()
        
        # Add dashboard as the first tab
        self.setup_dashboard_metrics_tab()
        
        layout.addWidget(self.tabs)
        
        # Create status bar with multiple sections
        self.status_bar = self.statusBar()
        
        # Create permanent widgets for the status bar
        self.status_connection = QLabel("Status: Disconnected")
        self.status_model = QLabel(f"Model: {self.current_model}")
        self.status_port = QLabel("Port: Not connected")
        
        # Add widgets to status bar
        self.status_bar.addPermanentWidget(self.status_connection)
        self.status_bar.addPermanentWidget(self.status_model, 1)
        self.status_bar.addPermanentWidget(self.status_port)
        
        # Initial status message
        self.status_bar.showMessage("Ready")
        
        # Set up timers to update dashboard and diagnostics periodically
        self.diag_timer = QTimer(self)
        self.diag_timer.timeout.connect(self.update_diagnostics)
        self.diag_timer.start(1000)  # Update every second
        
        self.dashboard_timer = QTimer(self)
        self.dashboard_timer.timeout.connect(self.update_dashboard)
        self.dashboard_timer.start(500)  # Update dashboard more frequently
        
    def create_model_selection(self):
        """Create model selection group"""
        self.model_group = QGroupBox("Drive Model")
        layout = QFormLayout()
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.addItems(get_model_list())
        self.model_combo.setCurrentText(self.current_model)
        self.model_combo.currentTextChanged.connect(self.model_changed)
        
        # Model info display
        self.model_info = QLabel()
        self.update_model_info()
        
        layout.addRow("Select Model:", self.model_combo)
        layout.addRow("Specifications:", self.model_info)
        self.model_group.setLayout(layout)
    
    def model_changed(self, model):
        """Handle model selection change"""
        self.current_model = model
        self.model_config = get_model_config(model)
        self.save_settings()
        # Update status bar
        self.status_model.setText(f"Model: {self.current_model}")
        self.status_bar.showMessage(f"Model changed to {self.current_model}", 3000)
        self.save_settings()
        
        # Update UI elements that depend on model
        if hasattr(self, 'speed_spin'):
            self.speed_spin.setMaximum(self.model_config['max_frequency'])
            self.speed_spin.setValue(0)
    
    def update_model_info(self):
        """Update model information display"""
        info = (f"Max Frequency: {self.model_config['max_frequency']} Hz\n"
                f"Max Current: {self.model_config['max_current']} A\n"
                f"Power Rating: {self.model_config['power_rating']} kW\n"
                f"Voltage: {self.model_config['voltage_rating']} V")
        self.model_info.setText(info)
    
    def create_connection_group(self):
        """Create connection settings group"""
        self.connection_group = QGroupBox(t('connection', self.current_language))
        layout = QFormLayout()
        
        # Port selection
        self.port_combo = QComboBox()
        self.refresh_ports()
        
        # Baud rate selection
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baud_combo.setCurrentText('9600')
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton(t('refresh_ports', self.current_language))
        refresh_btn.clicked.connect(self.refresh_ports)
        
        # Connect/Disconnect button
        self.connect_btn = QPushButton(t('connect', self.current_language))
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        # Add widgets to layout
        layout.addRow(f"{t('port', self.current_language)}:", self.port_combo)
        layout.addRow(f"{t('baud_rate', self.current_language)}:", self.baud_combo)
        
        # Add buttons to button layout
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.connect_btn)
        
        # Add button layout to main layout
        layout.addRow(btn_layout)
        self.connection_group.setLayout(layout)
        
        # Apply saved settings
        self.load_connection_settings()
    
    def load_connection_settings(self):
        """Load saved connection settings"""
        # Load saved port and baud rate
        saved_port = self.settings.value("port", "")
        saved_baud = self.settings.value("baudrate", "9600")
        
        # Find and select the saved port if it exists
        index = self.port_combo.findText(saved_port)
        if index >= 0:
            self.port_combo.setCurrentIndex(index)
            
        # Set the saved baud rate
        index = self.baud_combo.findText(saved_baud)
        if index >= 0:
            self.baud_combo.setCurrentIndex(index)
    
    def save_connection_settings(self):
        """Save connection settings"""
        self.settings.setValue("port", self.port_combo.currentText())
        self.settings.setValue("baudrate", self.baud_combo.currentText())
    
    def setup_dashboard_metrics_tab(self):
        """Set up the dashboard metrics tab with comprehensive monitoring."""
        dashboard_metrics_tab = QWidget()
        layout = QVBoxLayout(dashboard_metrics_tab)
        
        # Main grid for metrics
        metrics_grid = QGridLayout()
        
        # Speed Metrics Group
        speed_group = QGroupBox(t('speed_metrics', self.current_language))
        speed_layout = QFormLayout()
        
        self.output_freq_label = QLabel("0.0 Hz")
        self.output_rpm_label = QLabel("0 RPM")
        self.setpoint_freq_label = QLabel("0.0 Hz")
        
        speed_layout.addRow(f"{t('output_frequency', self.current_language)}:", self.output_freq_label)
        speed_layout.addRow(f"{t('output_speed', self.current_language)}:", self.output_rpm_label)
        speed_layout.addRow(f"{t('setpoint_frequency', self.current_language)}:", self.setpoint_freq_label)
        speed_group.setLayout(speed_layout)
        
        # Power Metrics Group
        power_group = QGroupBox(t('power_metrics', self.current_language))
        power_layout = QFormLayout()
        
        self.output_current_label = QLabel("0.0 A")
        self.dc_bus_voltage_label = QLabel("0.0 V")
        self.output_voltage_label = QLabel("0.0 V")
        self.output_power_label = QLabel("0.0 kW")
        
        power_layout.addRow(f"{t('output_current', self.current_language)}:", self.output_current_label)
        power_layout.addRow(f"{t('dc_bus_voltage', self.current_language)}:", self.dc_bus_voltage_label)
        power_layout.addRow(f"{t('output_voltage', self.current_language)}:", self.output_voltage_label)
        power_layout.addRow(f"{t('output_power', self.current_language)}:", self.output_power_label)
        power_group.setLayout(power_layout)
        
        # Status Group
        status_group = QGroupBox(t('status', self.current_language))
        status_layout = QFormLayout()
        
        self.drive_status_label = QLabel(t('stopped', self.current_language))
        self.direction_label = QLabel(t('stopped', self.current_language))
        self.temperature_label = QLabel("0.0 °C")
        self.run_time_label = QLabel("00:00:00")
        
        status_layout.addRow(f"{t('drive_status', self.current_language)}:", self.drive_status_label)
        status_layout.addRow(f"{t('direction', self.current_language)}:", self.direction_label)
        status_layout.addRow(f"{t('temperature', self.current_language)}:", self.temperature_label)
        status_layout.addRow(f"{t('run_time', self.current_language)}:", self.run_time_label)
        status_group.setLayout(status_layout)
        
        # Add groups to the grid
        metrics_grid.addWidget(speed_group, 0, 0)
        metrics_grid.addWidget(power_group, 0, 1)
        metrics_grid.addWidget(status_group, 1, 0, 1, 2)
        
        # Add stretch to push everything to the top
        layout.addLayout(metrics_grid)
        layout.addStretch()
        
        # Add the tab with translated name
        self.tabs.addTab(dashboard_metrics_tab, t('dashboard', self.current_language))
    
    def setup_dashboard_tab(self):
        """Set up the control tab with speed and direction controls."""
        control_tab = QWidget()
        layout = QVBoxLayout(control_tab)
        
        # Create a grid layout for metrics
        metrics_grid = QGridLayout()
        
        # Speed reference
        speed_group = QGroupBox("Speed Control")
        speed_layout = QFormLayout()
        
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0, self.model_config['max_frequency'])
        self.speed_spin.setSuffix(" Hz")
        self.speed_spin.setValue(0)
        self.speed_spin.setSingleStep(0.1)
        self.speed_spin.setDecimals(1)
        
        self.set_speed_btn = QPushButton("Set Speed")
        self.set_speed_btn.clicked.connect(self.set_drive_speed)
        self.set_speed_btn.setEnabled(False)
        
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.start_drive)
        self.run_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_drive)
        self.stop_btn.setEnabled(False)
        
        speed_layout.addRow("Target Speed:", self.speed_spin)
        speed_layout.addRow(self.set_speed_btn)
        speed_layout.addRow(self.run_btn)
        speed_layout.addRow(self.stop_btn)
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        # Direction control
        dir_group = QGroupBox("Direction Control")
        dir_layout = QVBoxLayout()
        
        self.fwd_btn = QPushButton("Forward")
        self.fwd_btn.clicked.connect(lambda: self.set_direction("forward"))
        self.fwd_btn.setEnabled(False)
        
        self.rev_btn = QPushButton("Reverse")
        self.rev_btn.clicked.connect(lambda: self.set_direction("reverse"))
        self.rev_btn.setEnabled(False)
        
        dir_layout.addWidget(self.fwd_btn)
        dir_layout.addWidget(self.rev_btn)
        dir_group.setLayout(dir_layout)
        
        layout.addWidget(dir_group)
        
        # Status and fault display
        status_group = QGroupBox("Status")
        status_layout = QFormLayout()
        
        # Status value label
        self.status_value = QLabel(t('disconnected', self.current_language))
        status_layout.addRow("Status:", self.status_value)
        
        # Fault value label
        self.fault_value = QLabel(t('no_faults', self.current_language))
        status_layout.addRow("Fault:", self.fault_value)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        layout.addStretch()
        self.tabs.addTab(control_tab, t('control', self.current_language))
    
    def setup_parameters_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Parameter controls
        self.param_combo = QComboBox()
        self.param_combo.addItems([
            "Acceleration Time",
            "Deceleration Time",
            "Motor Rated Current",
            "Maximum Frequency"
        ])
        
        self.param_value = QDoubleSpinBox()
        self.param_value.setRange(0, 9999)
        
        self.read_param_btn = QPushButton("Read Parameter")
        self.read_param_btn.clicked.connect(self.read_parameter)
        
        self.write_param_btn = QPushButton("Write Parameter")
        self.write_param_btn.clicked.connect(self.write_parameter)
        
        layout.addRow("Parameter:", self.param_combo)
        layout.addRow("Value:", self.param_value)
        layout.addRow(self.read_param_btn)
        layout.addRow(self.write_param_btn)
        
        self.tabs.addTab(tab, "Parameters")
    
    def setup_diagnostics_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Status indicators
        self.output_freq = QLabel("0.0 Hz")
        self.output_current = QLabel("0.0 A")
        self.dc_bus_voltage = QLabel("0.0 V")
        self.drive_status = QLabel("Stopped")
        self.fault_status = QLabel("No Faults")
        
        layout.addRow("Output Frequency:", self.output_freq)
        layout.addRow("Output Current:", self.output_current)
        layout.addRow("DC Bus Voltage:", self.dc_bus_voltage)
        layout.addRow("Drive Status:", self.drive_status)
        layout.addRow("Fault Status:", self.fault_status)
        
        # Fault reset button
        self.reset_fault_btn = QPushButton("Reset Faults")
        self.reset_fault_btn.clicked.connect(self.reset_faults)
        self.reset_fault_btn.setEnabled(False)
        
        layout.addRow(self.reset_fault_btn)
        
        self.tabs.addTab(tab, "Diagnostics")
        
    def setup_data_logging_tab(self):
        """Create the logging configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Logging settings group
        settings_group = QGroupBox("Data Logging Settings")
        settings_layout = QFormLayout()
        
        # Logging status
        self.logging_status_label = QLabel("Status: Stopped")
        settings_layout.addRow("Status:", self.logging_status_label)
        
        # Log file path
        self.log_file_path = QLineEdit()
        self.log_file_path.setReadOnly(True)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_log_file)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.log_file_path)
        path_layout.addWidget(browse_btn)
        settings_layout.addRow("Log File:", path_layout)
        
        # Logging interval
        self.log_interval_spin = QSpinBox()
        self.log_interval_spin.setRange(100, 10000)
        self.log_interval_spin.setValue(self.log_interval)
        self.log_interval_spin.setSuffix(" ms")
        self.log_interval_spin.valueChanged.connect(self.update_log_interval)
        settings_layout.addRow("Logging Interval:", self.log_interval_spin)
        
        # Start/Stop logging button
        self.toggle_logging_btn = QPushButton("Start Logging")
        self.toggle_logging_btn.clicked.connect(self.toggle_logging)
        settings_layout.addRow(self.toggle_logging_btn)
        
        # Export data button
        self.export_btn = QPushButton("Export Data...")
        self.export_btn.clicked.connect(self.export_data)
        settings_layout.addRow(self.export_btn)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Log preview table
        self.log_table = QTableWidget(0, 6)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Frequency (Hz)", "Current (A)", 
                                               "Voltage (V)", "Status", "Speed Ref"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.log_table)
        
        # Update UI based on current logging state
        self.update_logging_ui()
        
        self.tabs.addTab(tab, "Data Logging")
    
    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device, port.device)
    
    def toggle_connection(self):
        if not self.connected:
            self.connect_to_drive()
        else:
            self.disconnect_from_drive()
    
    def connect_to_drive(self):
        """Connect to the Nidec drive."""
        if self.connected:
            self.disconnect_from_drive()
            return
            
        try:
            port = self.port_combo.currentText()
            baudrate = int(self.baud_combo.currentText())
            
            # Initialize client (replace with actual communication code)
            self.client = None
            
            # Save settings
            self.save_connection_settings()
            
            # Update UI
            self.connected = True
            self.connect_btn.setText("Disconnect")
            self.statusBar().showMessage(f"Connected to {port}")
                
            # Enable controls
            self.set_speed_btn.setEnabled(True)
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.fwd_btn.setEnabled(True)
            self.rev_btn.setEnabled(True)
            self.read_param_btn.setEnabled(True)
            self.write_param_btn.setEnabled(True)
            self.reset_fault_btn.setEnabled(True)
                
            # Start diagnostics updates
            self.diag_timer.start(1000)  # Update every second
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
    
    def disconnect_from_drive(self):
        """Disconnect from the Nidec drive."""
        if self.client:
            self.diag_timer.stop()
            self.client = None
        
        self.connected = False
        self.connect_btn.setText("Connect")
        self.statusBar().showMessage("Disconnected")
        
        # Disable controls
        self.set_speed_btn.setEnabled(False)
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.fwd_btn.setEnabled(False)
        self.rev_btn.setEnabled(False)
        self.read_param_btn.setEnabled(False)
        self.write_param_btn.setEnabled(False)
        self.reset_fault_btn.setEnabled(False)
    
    def set_drive_speed(self):
        """Set the drive speed to the specified frequency."""
        if not self.connected:
            QMessageBox.warning(self, "Error", "Not connected to drive!")
            return
            
        try:
            speed = self.speed_spin.value()
            # Convert speed to drive units if needed
            drive_units = int(speed * 100)  # Example: 1.00 Hz = 100 units
            
            # TODO: Replace with actual drive communication
            # response = your_drive_interface.set_speed(drive_units)
            
            self.statusBar().showMessage(f"Speed set to {speed} Hz")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to set speed: {str(e)}")
    
    def start_drive(self):
        """Start the drive."""
        if not self.connected:
            QMessageBox.warning(self, "Error", "Not connected to drive!")
            return
            
        try:
            # TODO: Replace with actual drive communication
            # response = your_drive_interface.start()
            
            self.statusBar().showMessage("Drive started")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start drive: {str(e)}")
    
    def stop_drive(self):
        """Stop the drive."""
        if not self.connected:
            return
            
        try:
            # TODO: Replace with actual drive communication
            # response = your_drive_interface.stop()
            
            self.statusBar().showMessage("Drive stopped")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to stop drive: {str(e)}")
    
    def set_direction(self, direction):
        """Set the drive direction.
        
        Args:
            direction (str): 'forward' or 'reverse'
        """
        if not self.connected:
            QMessageBox.warning(self, "Error", "Not connected to drive!")
            return
            
        try:
            # TODO: Replace with actual drive communication
            # if direction.lower() == 'forward':
            #     response = your_drive_interface.set_forward()
            # else:
            #     response = your_drive_interface.set_reverse()
                
            self.statusBar().showMessage(f"Direction set to {direction.capitalize()}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to set direction: {str(e)}")
    
    def read_parameter(self):
        """Read a parameter from the drive."""
        if not self.connected:
            QMessageBox.warning(self, "Error", "Not connected to drive!")
            return
            
        try:
            param_name = self.param_combo.currentText()
            
            # Map parameter name to address/command
            # This is just an example - replace with your actual parameter mapping
            param_map = {
                "Acceleration Time": 0x1000,
                "Deceleration Time": 0x1001,
                "Motor Rated Current": 0x1002,
                "Maximum Frequency": 0x1003
            }
            
            address = param_map.get(param_name, 0)
            
            # TODO: Replace with actual drive communication
            # response = your_drive_interface.read_parameter(address)
            # value = response.value  # Adjust based on actual response format
            
            # For now, just show 0
            self.param_value.setValue(0)
            self.statusBar().showMessage(f"Read {param_name}: 0")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read parameter: {str(e)}")
    
    def write_parameter(self):
        """Write a parameter to the drive."""
        if not self.connected:
            QMessageBox.warning(self, "Error", "Not connected to drive!")
            return
            
        try:
            param_name = self.param_combo.currentText()
            value = self.param_value.value()
            
            # Map parameter name to address/command
            # This is just an example - replace with your actual parameter mapping
            param_map = {
                "Acceleration Time": 0x1000,
                "Deceleration Time": 0x1001,
                "Motor Rated Current": 0x1002,
                "Maximum Frequency": 0x1003
            }
            
            address = param_map.get(param_name, 0)
            
            # Convert value to drive units if needed
            if param_name in ["Acceleration Time", "Deceleration Time"]:
                drive_value = int(value * 10)  # Convert to 0.1s units
            elif param_name == "Motor Rated Current":
                drive_value = int(value * 10)  # Convert to 0.1A units
            elif param_name == "Maximum Frequency":
                drive_value = int(value * 100)  # Convert to 0.01Hz units
            else:
                drive_value = int(value)
            
            # TODO: Replace with actual drive communication
            # response = your_drive_interface.write_parameter(address, drive_value)
            
            self.statusBar().showMessage(f"Wrote {param_name}: {value}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to write parameter: {str(e)}")
    
    def update_diagnostics(self):
        """Update the diagnostic information display."""
        if not self.connected:
            return
            
        try:
            # TODO: Replace with actual drive communication
            # Example: response = your_drive_interface.get_status()
            
            # For now, just show zeros/placeholders
            self.output_freq_label.setText("0.0 Hz")
            self.output_rpm_label.setText("0 RPM")
            self.setpoint_freq_label.setText("0.0 Hz")
            self.output_current_label.setText("0.0 A")
            self.dc_bus_voltage_label.setText("0.0 V")
            self.output_voltage_label.setText("0.0 V")
            self.output_power_label.setText("0.0 kW")
            self.temperature_label.setText("0.0 °C")
            
            # Update status
            self.drive_status_label.setText("Stopped")
            self.direction_label.setText("Stopped")
            self.fault_status_label.setText("No Faults")
            
        except Exception as e:
            # Don't show error message for every failed update
            print(f"Diagnostics update error: {str(e)}")
    
    def reset_faults(self):
        """Reset drive faults."""
        if not self.connected:
            QMessageBox.warning(self, "Error", "Not connected to drive!")
            return
            
        try:
            # TODO: Replace with actual drive communication
            # response = your_drive_interface.reset_faults()
            
            self.statusBar().showMessage("Faults reset")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to reset faults: {str(e)}")
    
    def update_dashboard(self):
        """Update the dashboard with current drive metrics."""
        if not self.connected or not self.client:
            self._set_disconnected_state()
            return
            
        try:
            # Read multiple parameters in one request for efficiency
            # Read parameters from 0x2002 (output frequency) to 0x2006 (fault code)
            # response = self.client.read_holding_registers(address=0x2002, count=5, unit=1)
            # if response.isError() or len(response.registers) < 4:
            #     raise Exception("Failed to read drive parameters")
            
            # Extract values from response
            # freq_reg, current_reg, voltage_reg, status_reg = response.registers[:4]
            # fault_code = response.registers[4] if len(response.registers) > 4 else None
            
            # Update Speed Metrics
            # freq_hz = freq_reg / 100.0  # 0.01 Hz units
            # rpm = int(freq_hz * 60)  # Convert Hz to RPM (assuming 1 pole pair)
            self.output_freq_label.setText("0.0 Hz")
            self.output_rpm_label.setText("0 RPM")
            
            # Read setpoint frequency from a different register
            # setpoint_response = self.client.read_holding_registers(address=0x2001, count=1, unit=1)
            # if not setpoint_response.isError():
            #     setpoint_hz = setpoint_response.registers[0] / 100.0  # 0.01 Hz units
            self.setpoint_freq_label.setText("0.0 Hz")
            
            # Update Power Metrics
            # current_a = current_reg / 10.0  # 0.1 A units
            # voltage_v = voltage_reg / 10.0  # 0.1 V units
            # power_kw = (current_a * voltage_v) / 1000.0  # Convert to kW
            
            self.output_current_label.setText("0.0 A")
            self.dc_bus_voltage_label.setText("0.0 V")
            self.output_voltage_label.setText("0.0 V")  # Assuming same as bus voltage
            self.output_power_label.setText("0.0 kW")
            
            # Update Status Group
            # status_bits = status_reg
            # status_text = []
            # direction_text = t('stopped', self.current_language)
            
            # if status_bits & 0x0001:  # Running
            #     status_text.append(t('running', self.current_language))
            # if status_bits & 0x0002:  # Forward
            #     direction_text = t('forward', self.current_language)
            # if status_bits & 0x0004:  # Reverse
            #     direction_text = t('reverse', self.current_language)
            # if status_bits & 0x0008:  # Fault
            #     status_text.append(t('fault', self.current_language))
            
            status_str = "Stopped"
            self.drive_status_label.setText(status_str)
            self.direction_label.setText("Stopped")
            
            # Read and update temperature
            # temp_response = self.client.read_holding_registers(address=0x2010, count=1, unit=1)
            # if not temp_response.isError():
            #     temp_c = temp_response.registers[0] / 10.0  # 0.1°C units
            self.temperature_label.setText("0.0 °C")
            
            # Update run time (example implementation)
            if hasattr(self, 'start_time'):
                run_seconds = int(time.time() - self.start_time)
                hours = run_seconds // 3600
                minutes = (run_seconds % 3600) // 60
                seconds = run_seconds % 60
                self.run_time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
        except Exception as e:
            print(f"Dashboard update error: {str(e)}")
            self._set_disconnected_state()
    
    def _set_disconnected_state(self):
        """Set all dashboard fields to indicate disconnected state."""
        disconnected_text = t('disconnected', self.current_language)
        na_text = t('not_available', self.current_language)
        
        # Speed Metrics
        self.output_freq_label.setText(na_text)
        self.output_rpm_label.setText(na_text)
        self.setpoint_freq_label.setText(na_text)
        
        # Power Metrics
        self.output_current_label.setText(na_text)
        self.dc_bus_voltage_label.setText(na_text)
        self.output_voltage_label.setText(na_text)
        self.output_power_label.setText(na_text)
        
        # Status Group
        self.drive_status_label.setText(disconnected_text)
        self.direction_label.setText(disconnected_text)
        self.temperature_label.setText(na_text)
        self.run_time_label.setText("00:00:00")
        
    def retranslate_ui(self):
        """Retranslate all UI elements with the current language."""
        # Call parent's retranslate_ui first to update menu and other common elements
        super().retranslate_ui()
        
        # Update dashboard metrics tab
        if hasattr(self, 'dashboard_metrics_tab'):
            # Update group box titles
            for group in self.dashboard_metrics_tab.findChildren(QGroupBox):
                if group.title() == t('speed_metrics', 'en'):
                    group.setTitle(t('speed_metrics', self.current_language))
                elif group.title() == t('power_metrics', 'en'):
                    group.setTitle(t('power_metrics', self.current_language))
                elif group.title() == t('status', 'en'):
                    group.setTitle(t('status', self.current_language))
            
            # Update labels in the form layouts
            for form in self.dashboard_metrics_tab.findChildren(QFormLayout):
                for i in range(form.rowCount()):
                    label_item = form.itemAt(i, QFormLayout.LabelRole)
                    if label_item and label_item.widget():
                        label = label_item.widget().text()
                        if ':' in label:
                            # Extract the translation key (remove ':' and any whitespace)
                            key = label.split(':')[0].strip()
                            if key in TRANSLATIONS.get('en', {}):
                                # Update the label with the translated text
                                label_item.widget().setText(f"{t(key, self.current_language)}:")
        
        # Update other UI elements as needed
        if hasattr(self, 'tabs'):
            for i in range(self.tabs.count()):
                tab_text = self.tabs.tabText(i)
                if tab_text in [t('control', 'en'), t('diagnostics', 'en'), 
                              t('parameters', 'en'), t('dashboard', 'en')]:
                    # This is one of our main tabs
                    if tab_text == t('control', 'en'):
                        self.tabs.setTabText(i, t('control', self.current_language))
                    elif tab_text == t('diagnostics', 'en'):
                        self.tabs.setTabText(i, t('diagnostics', self.current_language))
                    elif tab_text == t('parameters', 'en'):
                        self.tabs.setTabText(i, t('parameters', self.current_language))
                    elif tab_text == t('dashboard', 'en'):
                        self.tabs.setTabText(i, t('dashboard', self.current_language))
    
    def language_changed(self, lang_code):
        """Handle language change event."""
        self.current_language = lang_code
        self.model_config = get_model_config(self.current_model, self.current_language)
        self.retranslate_ui()
        self._set_disconnected_state()
    
    def browse_log_file(self):
        """Open file dialog to select log file location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Select Log File",
            self.last_used_dir if hasattr(self, 'last_used_dir') else "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            if hasattr(self, 'log_file_path'):
                self.log_file_path.setText(file_path)
            if hasattr(self, 'last_used_dir'):
                self.last_used_dir = os.path.dirname(file_path)
    
    def update_log_interval(self, interval):
        """Update the logging interval"""
        self.log_interval = interval
    
    def toggle_logging(self):
        """Toggle logging on/off"""
        if self.logging_enabled:
            self.stop_logging()
        else:
            self.start_logging()
    
    def start_logging(self):
        """Start data logging"""
        log_file = self.log_file_path.text().strip()
        
        if not log_file:
            QMessageBox.warning(self, "Warning", "Please select a log file first.")
            return
            
        try:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            # Open file in append mode
            self.log_file = open(log_file, 'a', newline='')
            self.csv_writer = csv.writer(self.log_file)
            
            # Write header if file is empty
            if os.path.getsize(log_file) == 0:
                self.csv_writer.writerow([
                    'Timestamp', 'Frequency (Hz)', 'Current (A)', 
                    'Voltage (V)', 'Status', 'Fault Code', 'Speed Reference'
                ])
            
            self.logging_enabled = True
            self.last_log_time = time.time()
            self.update_logging_ui()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start logging: {str(e)}")
            if self.log_file:
                self.log_file.close()
                self.log_file = None
    
    def stop_logging(self):
        """Stop data logging"""
        if self.log_file:
            try:
                self.log_file.close()
            except Exception as e:
                print(f"Error closing log file: {e}")
            finally:
                self.log_file = None
                self.csv_writer = None
        
        self.logging_enabled = False
        self.update_logging_ui()
    
    def log_data(self, timestamp, freq_hz, current_a, voltage_v, status, fault_code):
        """Log data to file and update UI"""
        if not self.logging_enabled or not self.csv_writer:
            return
            
        try:
            # Get current speed reference
            speed_ref = self.speed_spin.value()
            
            # Format timestamp
            timestamp_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            
            # Write to file
            self.csv_writer.writerow([
                timestamp_str, 
                f"{freq_hz:.2f}", 
                f"{current_a:.2f}", 
                f"{voltage_v:.1f}", 
                status,
                str(fault_code) if fault_code is not None else "",
                str(speed_ref)
            ])
            self.log_file.flush()
            
            # Update table (keep last 1000 entries)
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)
            
            for col, value in enumerate([
                timestamp_str, 
                f"{freq_hz:.2f}", 
                f"{current_a:.2f}", 
                f"{voltage_v:.1f}", 
                status,
                f"{speed_ref} Hz"
            ]):
                self.log_table.setItem(row, col, QTableWidgetItem(value))
            
            # Auto-scroll to bottom
            self.log_table.scrollToBottom()
            
            # Limit to 1000 rows
            while self.log_table.rowCount() > 1000:
                self.log_table.removeRow(0)
                
        except Exception as e:
            print(f"Error logging data: {e}")
            self.stop_logging()
    
    def update_logging_ui(self):
        """Update UI elements based on logging state"""
        if self.logging_enabled:
            self.logging_status_label.setText("Status: <font color='green'>Logging</font>")
            self.toggle_logging_btn.setText("Stop Logging")
            self.export_btn.setEnabled(False)
            self.log_interval_spin.setEnabled(False)
        else:
            self.logging_status_label.setText("Status: <font color='red'>Stopped</font>")
            self.toggle_logging_btn.setText("Start Logging")
            self.export_btn.setEnabled(True)
            self.log_interval_spin.setEnabled(True)
    
    def export_data(self):
        """Export logged data to a new file"""
        if not hasattr(self, 'log_table') or self.log_table.rowCount() == 0:
            QMessageBox.information(self, "Export Data", "No data to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            os.path.join(self.last_used_dir, f"nidec_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"),
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        if not file_path.endswith('.csv'):
            file_path += '.csv'
        
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Timestamp', 'Frequency (Hz)', 'Current (A)', 
                    'Voltage (V)', 'Status', 'Speed Reference'
                ])
                
                # Write data
                for row in range(self.log_table.rowCount()):
                    writer.writerow([
                        self.log_table.item(row, col).text()
                        for col in range(self.log_table.columnCount())
                    ])
            
            QMessageBox.information(self, "Export Successful", 
                                 f"Data exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", 
                              f"Failed to export data:\n{str(e)}")
    
    # Configuration Save/Load Methods
    
    def save_configuration(self):
        """
        Save the current drive configuration to a JSON file.
        
        This method saves the current drive settings, including connection parameters,
        drive parameters, and UI state to a JSON configuration file.
        """
        if not hasattr(self, 'last_used_dir'):
            self.last_used_dir = os.path.expanduser("~/Documents")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t('save_configuration', self.current_language),
            os.path.join(self.last_used_dir, f"nidec_{self.current_model}_config.json"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return False
            
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        try:
            # Get current parameter values
            config = {
                'version': '1.1',
                'timestamp': datetime.now().isoformat(),
                'application': 'Nidec Commander CDE',
                'model': self.current_model,
                'language': self.current_language,
                'theme': self.current_theme,
                'connection': {
                    'port': self.port_combo.currentText(),
                    'baudrate': int(self.baud_combo.currentText()),
                    'timeout': 1.0,  # Default timeout in seconds
                    'parity': 'E',   # Even parity
                    'stopbits': 1,
                    'bytesize': 8
                },
                'drive_parameters': {
                    # Speed control
                    'reference_frequency': self.speed_spin.value(),
                    'acceleration_time': self.accel_time.value(),
                    'deceleration_time': self.decel_time.value(),
                    'max_frequency': self.max_freq.value(),
                    'min_frequency': 0.0,  # Default min frequency
                    # Motor parameters
                    'motor_rated_current': self.motor_current.value(),
                    'motor_rated_voltage': 400.0,  # Default for 400V drives
                    'motor_pole_pairs': 2,  # Default for most AC motors
                    # Control mode settings
                    'control_mode': 'V/F',  # Default control mode
                    'torque_boost': 0.0,    # Default torque boost
                    'slip_compensation': 0.0  # Default slip compensation
                },
                'io_settings': {
                    'analog_input1_min': 0.0,
                    'analog_input1_max': 10.0,
                    'analog_input2_min': 0.0,
                    'analog_input2_max': 10.0,
                    'relay1_function': 'Run',
                    'relay2_function': 'Fault'
                },
                'monitoring': {
                    'update_interval': 1000,  # ms
                    'log_interval': self.log_interval if hasattr(self, 'log_interval') else 1000,
                    'show_tooltips': True,
                    'show_status_bar': True
                },
                'ui_state': {
                    'window_geometry': self.saveGeometry().toHex().data().decode(),
                    'window_state': self.saveState().toHex().data().decode(),
                    'selected_tab': self.tabs.currentIndex() if hasattr(self, 'tabs') else 0
                }
            }
            
            # Add logging settings if available
            if hasattr(self, 'logging_enabled'):
                config['monitoring']['logging_enabled'] = self.logging_enabled
                if hasattr(self, 'log_file_path') and self.log_file_path.text():
                    config['monitoring']['log_file'] = self.log_file_path.text()
            
            # Save the configuration file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # Update last used directory
            self.last_used_dir = os.path.dirname(file_path)
            self.settings.setValue("last_used_dir", self.last_used_dir)
            
            # Show success message
            QMessageBox.information(
                self,
                t('save_success', self.current_language),
                f"{t('configuration_saved', self.current_language)}:\n{file_path}"
            )
            
            return True
            
        except Exception as e:
            error_msg = f"{t('save_failed', self.current_language)}:\n{str(e)}"
            QMessageBox.critical(self, t('error', self.current_language), error_msg)
            return False
    
    def load_configuration(self):
        """
        Load configuration from a JSON file and apply settings.
        
        This method loads a previously saved configuration file and applies
        the settings to the application. It handles different versions of
        configuration files and provides appropriate error messages.
        """
        if not hasattr(self, 'last_used_dir'):
            self.last_used_dir = os.path.expanduser("~/Documents")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t('load_configuration', self.current_language),
            self.last_used_dir,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path or not os.path.exists(file_path):
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check configuration version
            config_version = config.get('version', '1.0')
            
            # Update last used directory
            self.last_used_dir = os.path.dirname(file_path)
            self.settings.setValue("last_used_dir", self.last_used_dir)
            
            # Apply model if different
            if 'model' in config and config['model'] != self.current_model:
                self.model_combo.setCurrentText(config['model'])
            
            # Apply language if different
            if 'language' in config and config['language'] != self.current_language:
                self.current_language = config['language']
                self.retranslate_ui()
            
            # Apply theme if different
            if 'theme' in config and config['theme'] != self.current_theme:
                self.apply_theme(config['theme'])
            
            # Apply connection settings
            if 'connection' in config:
                conn = config['connection']
                if 'port' in conn and conn['port'] in [self.port_combo.itemText(i) for i in range(self.port_combo.count())]:
                    self.port_combo.setCurrentText(conn['port'])
                if 'baudrate' in conn:
                    baud = str(conn['baudrate'])
                    if baud in [self.baud_combo.itemText(i) for i in range(self.baud_combo.count())]:
                        self.baud_combo.setCurrentText(baud)
            
            # Apply drive parameters
            if 'drive_parameters' in config:
                params = config['drive_parameters']
                
                # Speed control
                if 'reference_frequency' in params:
                    self.speed_spin.setValue(float(params['reference_frequency']))
                if 'acceleration_time' in params and hasattr(self, 'accel_time'):
                    self.accel_time.setValue(float(params['acceleration_time']))
                if 'deceleration_time' in params and hasattr(self, 'decel_time'):
                    self.decel_time.setValue(float(params['deceleration_time']))
                if 'max_frequency' in params and hasattr(self, 'max_freq'):
                    self.max_freq.setValue(float(params['max_frequency']))
                if 'motor_rated_current' in params and hasattr(self, 'motor_current'):
                    self.motor_current.setValue(float(params['motor_rated_current']))
            
            # Apply monitoring settings
            if 'monitoring' in config:
                monitor = config['monitoring']
                if 'log_interval' in monitor and hasattr(self, 'log_interval'):
                    self.log_interval = int(monitor['log_interval'])
                    if hasattr(self, 'log_interval_spin'):
                        self.log_interval_spin.setValue(self.log_interval)
                if 'logging_enabled' in monitor and hasattr(self, 'logging_enabled'):
                    self.logging_enabled = bool(monitor['logging_enabled'])
                if 'log_file' in monitor and hasattr(self, 'log_file_path'):
                    self.log_file_path.setText(monitor['log_file'])
            
            # Apply UI state
            if 'ui_state' in config:
                ui = config['ui_state']
                if 'window_geometry' in ui:
                    try:
                        self.restoreGeometry(QByteArray.fromHex(ui['window_geometry'].encode()))
                    except:
                        pass
                if 'window_state' in ui:
                    try:
                        self.restoreState(QByteArray.fromHex(ui['window_state'].encode()))
                    except:
                        pass
                if 'selected_tab' in ui and hasattr(self, 'tabs') and 0 <= ui['selected_tab'] < self.tabs.count():
                    self.tabs.setCurrentIndex(ui['selected_tab'])
            
            # Show success message
            QMessageBox.information(
                self,
                t('load_success', self.current_language),
                f"{t('configuration_loaded', self.current_language)}:\n{file_path}"
            )
            
            return True
            
        except json.JSONDecodeError as e:
            error_msg = f"{t('invalid_config_file', self.current_language)}:\n{str(e)}"
            QMessageBox.critical(self, t('error', self.current_language), error_msg)
            return False
            
        except Exception as e:
            error_msg = f"{t('load_failed', self.current_language)}:\n{str(e)}"
            QMessageBox.critical(self, t('error', self.current_language), error_msg)
            return False
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Stop all timers
        if hasattr(self, 'dashboard_timer') and self.dashboard_timer.isActive():
            self.dashboard_timer.stop()
        if hasattr(self, 'diag_timer') and self.diag_timer.isActive():
            self.diag_timer.stop()
            
        # Disconnect from the drive if connected
        if self.connected and hasattr(self, 'client') and self.client:
            try:
                self.disconnect_from_drive()
            except Exception as e:
                print(f"Error disconnecting from drive: {str(e)}")
                
        # Save settings
        self.save_settings()
        
        # Accept the close event
        event.accept()
    
    def retranslate_ui(self):
        """Retranslate all UI elements with the current language."""
        # Call parent's retranslate_ui first to update menus
        super().retranslate_ui()
        
        # Update window title
        self.setWindowTitle(t('app_title', self.current_language))
        
        # Update group boxes
        if hasattr(self, 'connection_group'):
            self.connection_group.setTitle(t('connection', self.current_language))
        if hasattr(self, 'control_group'):
            self.control_group.setTitle(t('control', self.current_language))
        if hasattr(self, 'parameters_group'):
            self.parameters_group.setTitle(t('parameters', self.current_language))
        if hasattr(self, 'diagnostics_group'):
            self.diagnostics_group.setTitle(t('diagnostics', self.current_language))
            
        # Update labels and buttons
        if hasattr(self, 'connect_btn'):
            self.connect_btn.setText(t('connect', self.current_language) if not self.connected else t('disconnect', self.current_language))
        if hasattr(self, 'run_btn'):
            self.run_btn.setText(t('run', self.current_language))
        if hasattr(self, 'stop_btn'):
            self.stop_btn.setText(t('stop', self.current_language))
        if hasattr(self, 'forward_btn'):
            self.forward_btn.setText(t('forward', self.current_language))
        if hasattr(self, 'reverse_btn'):
            self.reverse_btn.setText(t('reverse', self.current_language))
            
        # Update tab names
        if hasattr(self, 'tabs'):
            for i in range(self.tabs.count()):
                tab_text = self.tabs.tabText(i)
                if tab_text in [t('control', 'en'), t('parameters', 'en'), 
                               t('diagnostics', 'en'), t('data_logging', 'en')]:
                    if tab_text == t('control', 'en'):
                        self.tabs.setTabText(i, t('control', self.current_language))
                    elif tab_text == t('parameters', 'en'):
                        self.tabs.setTabText(i, t('parameters', self.current_language))
                    elif tab_text == t('diagnostics', 'en'):
                        self.tabs.setTabText(i, t('diagnostics', self.current_language))
                    elif tab_text == t('data_logging', 'en'):
                        self.tabs.setTabText(i, t('data_logging', self.current_language))
    
    def closeEvent(self, event):
        # Clean up on application close
        if self.connected:
            self.disconnect_from_drive()
            
        # Stop logging if active
        if self.logging_enabled:
            self.stop_logging()
            
        # Save settings
        self.save_settings()
        event.accept()

if __name__ == "__main__":
    """
    Main entry point for the Nidec Commander CDE application.
    
    This block is executed when the script is run directly (not imported as a module).
    It creates the QApplication instance and the main window, then starts the event loop.
    """
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Nidec CommanderCDE")
    app.setOrganizationName("Tuxxle")
    app.setApplicationVersion("0.0.4")
    
    # Create and show the main window
    window = NidecCommanderGUI()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())
