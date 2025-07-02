import sys
import json
import os
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QGroupBox, QLineEdit,
                             QMessageBox, QTabWidget, QFormLayout, QDoubleSpinBox, QCheckBox,
                             QSpinBox, QFileDialog, QStatusBar)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QIcon
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusException
from nidec_models import get_model_list, get_model_config, FAULT_CODES

# Import the MainWindow class from menu.py
from menu import MainWindow

class NidecCommanderGUI(MainWindow):
    def __init__(self):
        # Initialize the MainWindow parent class first
        super().__init__()
        
        # Set up our application-specific attributes
        self.client = None
        self.connected = False
        self.current_model = "CDE400"
        self.model_config = get_model_config(self.current_model)
        self.settings = QSettings("NidecCommander", "CDE_Control")
        
        # Window settings
        self.setWindowTitle("Nidec Commander CDE")
        self.setWindowIcon(QIcon("images/icon.png"))
        self.setMinimumSize(1000, 750)
        
        # Load saved settings
        self.load_settings()
        
        # Initialize the UI
        self.setup_ui()
        
        # Show the window
        self.show()
        
    def load_settings(self):
        """Load application settings"""
        self.current_model = self.settings.value("model", "CDE400")
        self.model_config = get_model_config(self.current_model)
        # Update status bar if it exists
        if hasattr(self, 'status_model'):
            self.status_model.setText(f"Model: {self.current_model}")
        
    def save_settings(self):
        """Save application settings"""
        self.settings.setValue("model", self.current_model)
        
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
        
        # Speed Control Tab
        self.create_speed_control_tab()
        
        # Parameters Tab
        self.create_parameters_tab()
        
        # Diagnostics Tab
        self.create_diagnostics_tab()
        
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
        
        # Timer for periodic updates
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_diagnostics)
        
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
        self.connection_group = QGroupBox("Connection Settings")
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
        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.clicked.connect(self.refresh_ports)
        
        # Connect/Disconnect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        # Add widgets to layout
        layout.addRow("Modbus Address:", self.modbus_addr)
        layout.addRow("Port:", self.port_combo)
        layout.addRow("Baud Rate:", self.baud_combo)
        
        # Add buttons to button layout
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.connect_btn)
        
        # Add button layout to main layout
        layout.addRow(btn_layout)
        self.connection_group.setLayout(layout)
    
    def create_speed_control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
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
        layout.addStretch()
        
        self.tabs.addTab(tab, "Control")
    
    def create_parameters_tab(self):
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
    
    def create_diagnostics_tab(self):
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
                self.update_timer.start(1000)  # Update every second
            else:
                QMessageBox.critical(self, "Error", "Failed to connect to the drive!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
    
    def disconnect_drive(self):
        if self.client:
            self.update_timer.stop()
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
                
                self.drive_status.setText(", ".join(status_text) if status_text else "Stopped")
                
                # If fault bit is set, read fault code
                if status_bits & 0x0008:
                    fault_response = self.client.read_holding_registers(address=0x2006, count=1, unit=1)
                    if not fault_response.isError():
                        fault_code = fault_response.registers[0]
                        self.fault_status.setText(f"Fault Code: {fault_code:04X}")
                    else:
                        self.fault_status.setText("Fault (unable to read code)")
                else:
                    self.fault_status.setText("No Faults")
            
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
    
    def closeEvent(self, event):
        # Clean up on application close
        if self.connected:
            self.disconnect_drive()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NidecCommanderGUI()
    window.show()
    sys.exit(app.exec_())
