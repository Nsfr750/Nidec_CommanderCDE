"""
Nidec Commander CDE - Main Application Module

This module serves as the main entry point for the Nidec Commander CDE application.
It provides a graphical user interface for controlling and monitoring Nidec motor drives.

Key Features:
- Connection management for Modbus RTU devices
- Real-time monitoring of drive parameters
- Parameter configuration and tuning
- Fault diagnostics and logging
- Multi-language support
- Data logging and export

Dependencies:
- PyQt5: For the graphical user interface
- pymodbus: For Modbus RTU communication
- serial: For serial port management

Author: [Your Name]
Version: 1.0.0
"""

import sys
import json
import os
import csv
import time
from datetime import datetime
import serial.tools.list_ports

# PyQt5 imports for GUI components
from PyQt5.QtCore import QTimer, QSettings, QDateTime, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QGroupBox, QLineEdit,
    QMessageBox, QTabWidget, QFormLayout, QDoubleSpinBox, QCheckBox,
    QSpinBox, QFileDialog, QStatusBar, QTableWidget, QTableWidgetItem, 
    QHeaderView, QGridLayout
)
from PyQt5.QtGui import QIcon

# Modbus communication
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusException

# Local imports
from nidec_models import get_model_list, get_model_config, FAULT_CODES
from menu import MainWindow  # Main application window with menu bar
from lang.translations import t  # Translation function for internationalization

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
        client: Modbus client instance for communication
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
        self.current_language = 'en'  # Default language
        self.model_config = get_model_config(self.current_model, self.current_language)
        self.settings = QSettings("NidecCommander", "CDE_Control")
        
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
        if hasattr(self, 'port_combo') and hasattr(self, 'baud_combo') and hasattr(self, 'modbus_addr'):
            self.settings.setValue("port", self.port_combo.currentText())
            self.settings.setValue("baudrate", self.baud_combo.currentText())
            self.settings.setValue("modbus_addr", self.modbus_addr.value())
        
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
        
        # Modbus address
        self.modbus_addr = QSpinBox()
        self.modbus_addr.setRange(1, 247)
        self.modbus_addr.setValue(1)
        
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
        layout.addRow(f"{t('modbus_address', self.current_language)}:", self.modbus_addr)
        layout.addRow(f"{t('port', self.current_language)}:", self.port_combo)
        layout.addRow(f"{t('baud_rate', self.current_language)}:", self.baud_combo)
        
        # Add buttons to button layout
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.connect_btn)
        
        # Add button layout to main layout
        layout.addRow(btn_layout)
        self.connection_group.setLayout(layout)
    
    def setup_dashboard_metrics_tab(self):
        """Set up the dashboard metrics tab."""
        dashboard_metrics_tab = QWidget()
        layout = QVBoxLayout(dashboard_metrics_tab)
        
        # Add your dashboard metrics widgets here
        metrics_label = QLabel("Metriche del cruscotto")
        layout.addWidget(metrics_label)
        
        # Add more dashboard widgets as needed
        
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
        self.set_speed_btn.clicked.connect(self.set_speed)
        self.set_speed_btn.setEnabled(False)
        
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run_drive)
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
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
            self.disconnect_drive()
    
    def connect_to_drive(self):
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "Error", "No port selected!")
            return
        
        try:
            # Get connection parameters
            baudrate = int(self.baud_combo.currentText())
            modbus_addr = self.modbus_addr.value()
            
            # Configure Modbus RTU client
            self.client = ModbusClient(
                method='rtu',
                port=port,
                baudrate=baudrate,
                bytesize=8,
                parity='E',  # Even parity (common for Nidec drives)
                stopbits=1,
                timeout=1
            )
            
            # Save settings
            self.settings.setValue("port", port)
            self.settings.setValue("baudrate", baudrate)
            self.settings.setValue("modbus_addr", modbus_addr)
            
            # Try to connect
            if self.client.connect():
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
            else:
                QMessageBox.critical(self, "Error", "Failed to connect to the drive!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
    
    def disconnect_drive(self):
        if self.client:
            self.diag_timer.stop()
            self.client.close()
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
    
    def set_speed(self):
        if not self.connected:
            return
            
        speed = self.speed_spin.value()
        # Convert Hz to drive units if needed (0.01 Hz units is common)
        drive_units = int(speed * 100)
        
        try:
            # Write to holding register for frequency reference
            # Note: Register addresses may need adjustment based on the drive's documentation
            response = self.client.write_register(address=0x1000, value=drive_units, unit=1)
            if response.isError():
                raise Exception("Failed to set speed")
                
            self.statusBar().showMessage(f"Speed set to {speed} Hz")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to set speed: {str(e)}")
    
    def run_drive(self):
        if not self.connected:
            return
            
        try:
            # Write run command to control register
            # Note: The exact command value depends on the drive's protocol
            response = self.client.write_register(address=0x2000, value=0x0001, unit=1)
            if response.isError():
                raise Exception("Failed to start drive")
                
            self.statusBar().showMessage("Drive started")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start drive: {str(e)}")
    
    def stop_drive(self):
        if not self.connected:
            return
            
        try:
            # Write stop command to control register
            response = self.client.write_register(address=0x2000, value=0x0000, unit=1)
            if response.isError():
                raise Exception("Failed to stop drive")
                
            self.statusBar().showMessage("Drive stopped")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to stop drive: {str(e)}")
    
    def set_direction(self, direction):
        if not self.connected:
            return
            
        try:
            # 0x0001 = Forward, 0x0002 = Reverse (may vary by drive model)
            value = 0x0001 if direction == "forward" else 0x0002
            
            # Write direction command to control register
            # Note: The exact register and values depend on the drive's protocol
            response = self.client.write_register(address=0x2001, value=value, unit=1)
            if response.isError():
                raise Exception("Failed to set direction")
                
            self.statusBar().showMessage(f"Direction set to {direction.capitalize()}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to set direction: {str(e)}")
    
    def read_parameter(self):
        if not self.connected:
            return
            
        param_name = self.param_combo.currentText()
        
        # Map parameter names to register addresses
        param_map = {
            "Acceleration Time": 0x3000,
            "Deceleration Time": 0x3001,
            "Motor Rated Current": 0x3002,
            "Maximum Frequency": 0x3003
        }
        
        address = param_map.get(param_name, 0x3000)
        
        try:
            # Read parameter from drive
            response = self.client.read_holding_registers(address=address, count=1, unit=1)
            if response.isError():
                raise Exception("Failed to read parameter")
                
            # Convert from drive units to display units
            value = response.registers[0]
            if param_name in ["Acceleration Time", "Deceleration Time"]:
                value /= 10.0  # Convert to seconds
            elif param_name == "Motor Rated Current":
                value /= 10.0  # Convert to Amps
            elif param_name == "Maximum Frequency":
                value /= 100.0  # Convert to Hz
            
            self.param_value.setValue(value)
            self.statusBar().showMessage(f"Read {param_name}: {value}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read parameter: {str(e)}")
    
    def write_parameter(self):
        if not self.connected:
            return
            
        param_name = self.param_combo.currentText()
        value = self.param_value.value()
        
        # Map parameter names to register addresses
        param_map = {
            "Acceleration Time": 0x3000,
            "Deceleration Time": 0x3001,
            "Motor Rated Current": 0x3002,
            "Maximum Frequency": 0x3003
        }
        
        address = param_map.get(param_name, 0x3000)
        
        # Convert from display units to drive units
        if param_name in ["Acceleration Time", "Deceleration Time"]:
            drive_value = int(value * 10)  # Convert from seconds to 0.1s units
        elif param_name == "Motor Rated Current":
            drive_value = int(value * 10)  # Convert from Amps to 0.1A units
        elif param_name == "Maximum Frequency":
            drive_value = int(value * 100)  # Convert from Hz to 0.01Hz units
        else:
            drive_value = int(value)
        
        try:
            # Write parameter to drive
            response = self.client.write_register(address=address, value=drive_value, unit=1)
            if response.isError():
                raise Exception("Failed to write parameter")
                
            self.statusBar().showMessage(f"Wrote {param_name}: {value}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to write parameter: {str(e)}")
    
    def update_diagnostics(self):
        if not self.connected:
            return
            
        try:
            # Read multiple parameters in one request if possible
            # Note: Addresses and scaling factors may need adjustment
            response = self.client.read_holding_registers(address=0x2002, count=4, unit=1)
            if not response.isError() and len(response.registers) >= 4:
                # Get current timestamp
                current_time = time.time()
                
                # Update output frequency (0.01 Hz units)
                freq_hz = response.registers[0] / 100.0
                self.output_freq.setText(f"{freq_hz:.2f} Hz")
                
                # Update output current (0.1 A units)
                current_a = response.registers[1] / 10.0
                self.output_current.setText(f"{current_a:.1f} A")
                
                # Update DC bus voltage (0.1 V units)
                voltage_v = response.registers[2] / 10.0
                self.dc_bus_voltage.setText(f"{voltage_v:.1f} V")
                
                # Update drive status
                status_bits = response.registers[3]
                status_text = []
                if status_bits & 0x0001:
                    status_text.append("Running")
                if status_bits & 0x0002:
                    status_text.append("Forward")
                if status_bits & 0x0004:
                    status_text.append("Reverse")
                if status_bits & 0x0008:
                    status_text.append("Fault")
                
                status_str = ", ".join(status_text) if status_text else "Stopped"
                self.drive_status.setText(status_str)
                
                # If fault bit is set, read fault code
                fault_code = None
                if status_bits & 0x0008:
                    fault_response = self.client.read_holding_registers(address=0x2006, count=1, unit=1)
                    if not fault_response.isError():
                        fault_code = fault_response.registers[0]
                        self.fault_status.setText(f"Fault Code: {fault_code:04X}")
                    else:
                        self.fault_status.setText("Fault (unable to read code)")
                else:
                    self.fault_status.setText("No Faults")
                
                # Log data if logging is enabled and enough time has passed
                if self.logging_enabled and (current_time - self.last_log_time) * 1000 >= self.log_interval:
                    self.log_data(current_time, freq_hz, current_a, voltage_v, status_str, fault_code)
                    self.last_log_time = current_time
            
        except Exception as e:
            # Don't show error message for every failed update
            pass
    
    def reset_faults(self):
        if not self.connected:
            return
            
        try:
            # Write reset command to control register
            # Note: The exact command value depends on the drive's protocol
            response = self.client.write_register(address=0x2000, value=0x0080, unit=1)
            if response.isError():
                raise Exception("Failed to reset faults")
                
            self.statusBar().showMessage("Faults reset")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to reset faults: {str(e)}")
    
    def update_dashboard(self):
        """Update the dashboard with current drive metrics."""
        if not self.connected or not self.client:
            if hasattr(self, 'status_value'):
                self.status_value.setText(t('disconnected', self.current_language))
            if hasattr(self, 'fault_value'):
                self.fault_value.setText(t('not_available', self.current_language))
            return
            
        try:
            # Read speed (RPM)
            speed = self.client.read_holding_registers(0x1000, 1)
            if not speed.isError():
                self.speed_value.setText(f"{speed.registers[0]} {t('rpm', self.current_language)}")
                
            # Read current and voltage
            current = self.client.read_holding_registers(0x2000, 1)
            voltage = self.client.read_holding_registers(0x2001, 1)
            
            if not current.isError():
                current_val = current.registers[0] / 10.0
                self.current_value.setText(f"{current_val:.1f} A")
                
            if not voltage.isError():
                voltage_val = voltage.registers[0] / 10.0
                self.voltage_value.setText(f"{voltage_val:.1f} V")
                
                # Calculate power if both current and voltage are available
                if not current.isError():
                    power = current_val * voltage_val
                    self.power_value.setText(f"{power:.1f} W")
            
            # Read status and fault codes
            status = self.client.read_holding_registers(0x3000, 1)
            if not status.isError():
                status_code = status.registers[0]
                self.status_value.setText(t('running' if status_code == 1 else 'stopped', self.current_language))
                
                # Check for faults (simplified)
                if status_code & 0x8000:
                    self.fault_value.setText(t('fault_detected', self.current_language))
                else:
                    self.fault_value.setText(t('no_fault', self.current_language))
            
            # Read temperature
            temp = self.client.read_holding_registers(0x4000, 1)
            if not temp.isError():
                self.temp_value.setText(f"{temp.registers[0]}°C")
                
        except Exception as e:
            print(f"Error updating dashboard: {e}")
    
    # Logging and Configuration Methods
    
    def browse_log_file(self):
        """Open file dialog to select log file location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Select Log File",
            self.last_used_dir,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            self.log_file_path.setText(file_path)
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
        """Save current configuration to a file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            os.path.join(self.last_used_dir, "nidec_config.json"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
            
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        try:
            config = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'model': self.current_model,
                'connection': {
                    'port': self.port_combo.currentText(),
                    'baudrate': int(self.baud_combo.currentText()),
                    'modbus_address': self.modbus_addr.value()
                },
                'parameters': {
                    'speed_reference': self.speed_spin.value(),
                    'acceleration_time': self.get_parameter_value('Acceleration Time'),
                    'deceleration_time': self.get_parameter_value('Deceleration Time'),
                    'max_frequency': self.get_parameter_value('Maximum Frequency')
                },
                'logging': {
                    'enabled': self.logging_enabled,
                    'log_file': self.log_file_path.text(),
                    'log_interval': self.log_interval
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=4)
                
            QMessageBox.information(self, "Save Successful", 
                                 f"Configuration saved to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", 
                              f"Failed to save configuration:\n{str(e)}")
    
    def load_configuration(self):
        """Load configuration from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            self.last_used_dir,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path or not os.path.exists(file_path):
            return
            
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Apply model if different
            if 'model' in config and config['model'] != self.current_model:
                self.model_combo.setCurrentText(config['model'])
            
            # Apply connection settings
            if 'connection' in config:
                conn = config['connection']
                port_idx = self.port_combo.findText(conn.get('port', ''))
                if port_idx >= 0:
                    self.port_combo.setCurrentIndex(port_idx)
                
                baud_idx = self.baud_combo.findText(str(conn.get('baudrate', '9600')))
                if baud_idx >= 0:
                    self.baud_combo.setCurrentIndex(baud_idx)
                
                self.modbus_addr.setValue(conn.get('modbus_address', 1))
            
            # Apply parameters
            if 'parameters' in config:
                params = config['parameters']
                self.speed_spin.setValue(params.get('speed_reference', 0))
                self.set_parameter_value('Acceleration Time', params.get('acceleration_time', 10.0))
                self.set_parameter_value('Deceleration Time', params.get('deceleration_time', 10.0))
                self.set_parameter_value('Maximum Frequency', params.get('max_frequency', 60.0))
            
            # Apply logging settings
            if 'logging' in config and hasattr(self, 'logging_enabled'):
                log_cfg = config['logging']
                self.log_file_path.setText(log_cfg.get('log_file', ''))
                self.log_interval_spin.setValue(log_cfg.get('log_interval', 1000))
            
            QMessageBox.information(self, "Load Successful", 
                                 f"Configuration loaded from:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Load Failed", 
                              f"Failed to load configuration:\n{str(e)}")
    
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
            self.disconnect_drive()
            
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
    app.setApplicationName("Nidec Commander CDE")
    app.setOrganizationName("Nidec")
    app.setApplicationVersion("1.0.0")
    
    # Create and show the main window
    window = NidecCommanderGUI()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())
