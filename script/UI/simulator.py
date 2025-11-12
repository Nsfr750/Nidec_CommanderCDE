"""
Nidec Commander CDE Simulator

This module provides a comprehensive simulator for testing the Nidec Commander CDE application
without requiring actual hardware. It emulates the behavior of a Nidec drive with a user-friendly
interface for monitoring and controlling the simulated inverter.
"""

import sys
import os
import json
import csv
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple, Callable

# Import the logger utility
from script.utils.logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
script_dir = Path(__file__).parent

# Add paths to sys.path in a way that works for both development and compiled versions
paths_to_add = [
    str(project_root),
    str(script_dir),
    str(project_root / 'script'),
    str(project_root / 'script' / 'utils')
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QPushButton, QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox,
        QCheckBox, QTabWidget, QTextEdit, QStatusBar, QMessageBox, QFileDialog,
        QSlider, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
        QSplitter, QToolBar, QStyle, QFileDialog, QDialog, QLineEdit, QFormLayout,
        QDialogButtonBox, QListWidget, QListWidgetItem, QAbstractItemView
    )
    from PyQt6.QtCore import Qt, QTimer, QSize, QDateTime, QPoint, QRectF
    from PyQt6.QtGui import (
        QIcon, QFont, QTextCursor, QPalette, QColor, QPainter, QPen, QBrush,
        QLinearGradient, QFontMetrics, QAction, QKeySequence
    )
    from script.utils.inverter_sim import InverterSimulato, StatoInverter, CodiceAllarme
    from script.utils.serial_handler import SerialHandler
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise

def get_resource_path(relative_path: str) -> str:
    """
    Get the correct path to a resource file, whether running as script or frozen executable.
    
    Args:
        relative_path: Path relative to the project root
        
    Returns:
        str: Absolute path to the resource
    """
    try:
        # Running as compiled executable
        if getattr(sys, 'frozen', False):
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            return os.path.join(base_path, relative_path)
        
        # Running as script
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_path, relative_path)
    except Exception as e:
        logger.error(f"Error getting resource path for {relative_path}: {e}")
        return relative_path

class LedIndicator(QWidget):
    """A simple LED indicator widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(15, 15)
        self._color = QColor('gray')
        self._state = False
        
    def set_state(self, state: bool):
        """Set the LED state (on/off)."""
        if self._state != state:
            self._state = state
            self.update()
            
    def set_color(self, color: str):
        """Set the LED color."""
        new_color = QColor(color)
        if self._color != new_color:
            self._color = new_color
            self.update()
    
    def paintEvent(self, event):
        """Paint the LED."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw the outer circle (border)
        pen = QPen(Qt.GlobalColor.black, 1)
        painter.setPen(pen)
        
        # Draw the inner circle (LED)
        if self._state:
            # Gradient for the lit LED
            gradient = QLinearGradient(3, 3, 12, 12)
            gradient.setColorAt(0, Qt.GlobalColor.white)
            gradient.setColorAt(1, self._color)
            brush = QBrush(gradient)
        else:
            brush = QBrush(QColor(100, 100, 100))
            
        painter.setBrush(brush)
        painter.drawEllipse(2, 2, 11, 11)


class ParameterWidget(QWidget):
    """A widget to display a parameter with name, value, and unit."""
    def __init__(self, name: str, unit: str = "", parent=None):
        super().__init__(parent)
        self.name = name
        self.unit = unit
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(2)
        
        # Name label
        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-weight: bold;")
        
        # Value label
        self.value_label = QLabel("0.00")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("font-size: 14px;")
        
        # Unit label
        self.unit_label = QLabel(self.unit)
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_label.setStyleSheet("color: gray;")
        
        # Add widgets to layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.unit_label)
        
    def set_value(self, value, decimals: int = 2):
        """Set the parameter value."""
        if isinstance(value, (int, float)):
            self.value_label.setText(f"{value:.{decimals}f}")
        else:
            self.value_label.setText(str(value))


class SimulatorWidget(QMainWindow):
    """
    Main simulator window for Nidec Commander CDE.
    
    This class provides a comprehensive graphical interface to simulate and monitor
    the behavior of a Nidec drive for testing purposes.
    """
    
    def __init__(self, parent=None):
        """Initialize the simulator window."""
        super().__init__(parent)
        self.setWindowTitle('Nidec Commander Simulator')
        self.setMinimumSize(1000, 700)
        
        # Initialize simulator components
        self.inverter = InverterSimulato()
        self.serial_handler = None
        self.update_timer = QTimer()
        self.log_timer = QTimer()
        self.status_timer = QTimer()
        
        # Apply optimized dark theme for better readability
        self.setStyleSheet("""
            /* Base colors */
            QMainWindow, QDialog, QWidget, QTabWidget::pane, QTabBar::tab:selected {
                background-color: #1e1e1e;  /* Slightly darker background for better contrast */
                color: #f0f0f0;  /* Brighter text for better readability */
                selection-background-color: #3d6e94;  /* Blue selection color */
                selection-color: #ffffff;
            }
            
            /* Text elements */
            QLabel, QCheckBox, QRadioButton, QGroupBox, QLabel#titleLabel {
                color: #f0f0f0;  /* Brighter text */
                font-size: 9pt;  /* Slightly larger font */
            }
            
            /* Group boxes */
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                margin-top: 1.5em;  /* More spacing above group boxes */
                padding: 10px 5px 5px 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4db8ff;  /* Light blue for group titles */
                font-weight: bold;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #2d2d2d;
                color: #f0f0f0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 6px 16px;
                min-width: 90px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
            QPushButton:disabled {
                background-color: #252525;
                color: #6a6a6a;
                border-color: #2d2d2d;
            }
            
            /* Input fields */
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
                background-color: #252525;  /* Slightly lighter than main background */
                color: #f0f0f0;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 5px 8px;
                selection-background-color: #3d6e94;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #4a90d9;  /* Highlight focused fields */
            }
            
            /* Progress bars */
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                background-color: #252525;
                text-align: center;
                color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4a90d9;  /* Brighter blue for better visibility */
                width: 10px;
                margin: 0.5px;
                border-radius: 2px;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                top: 1px;
                padding: 5px;
            }
            QTabBar::tab {
                background: #2d2d2d;
                color: #a0a0a0;
                border: 1px solid #3a3a3a;
                border-bottom: none;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: #1e1e1e;
                color: #4db8ff;  /* Light blue for selected tab text */
                border-bottom: 2px solid #4a90d9;  /* Blue underline for active tab */
                font-weight: 500;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            
            /* Status bar */
            QStatusBar {
                background-color: #252525;
                color: #a0a0a0;
                border-top: 1px solid #3a3a3a;
                padding: 5px;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                border: none;
                background: #252525;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3a3a3a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            /* Tables */
            QTableView, QTableWidget {
                background-color: #252525;
                gridline-color: #3a3a3a;
                color: #f0f0f0;
                selection-background-color: #3d6e94;
                selection-color: #ffffff;
                border: 1px solid #3a3a3a;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #f0f0f0;
                padding: 5px;
                border: none;
                border-right: 1px solid #3a3a3a;
                border-bottom: 1px solid #3a3a3a;
            }
        """)
        
        # Ensure logs directory exists at the root of the application
        self._log_dir = Path(__file__).parent.parent.parent / "logs"
        self._log_dir.mkdir(exist_ok=True, parents=True)
        
        # Data logging
        self.log_file = str(self._log_dir / "simulator_log.csv")
        self.log_interval = 1.0  # seconds
        self.last_log_time = 0
        
        # Setup UI
        self.init_ui()
        self.setup_connections()
        
        # Start timers
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # 10 Hz update rate
        
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(500)  # 2 Hz update rate
        
        self.log_timer.timeout.connect(self.log_data)
        self.log_timer.start(1000)  # 1 Hz logging
        
        # Set initial button states
        self.stop_btn.setEnabled(False)
    
    def init_ui(self):
        """Initialize the user interface."""
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Use a splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout = QHBoxLayout(main_widget)
        main_layout.addWidget(splitter)
        
        # Left panel - Control and status
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Right panel - Tabs for different views
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        # Left panel - Control and status
        self.setup_control_panel(left_layout)
        
        # Right panel - Tabs for different views
        self.setup_tabbed_interface(right_layout)
        
        # Status bar
        self.setup_status_bar()
        
        # Set window icon
        self.setWindowIcon(QIcon(get_resource_path("script/assets/icon.ico")))
        
        # Apply styles
        self.apply_styles()
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New action
        new_action = QAction("&New Simulation", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_simulation)
        file_menu.addAction(new_action)
        
        # Open log action
        open_log_action = QAction("&Open Log...", self)
        open_log_action.triggered.connect(self.open_log)
        file_menu.addAction(open_log_action)
        
        # Save log action
        save_log_action = QAction("&Save Log As...", self)
        save_log_action.triggered.connect(self.save_log_as)
        file_menu.addAction(save_log_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Toggle fullscreen
        toggle_fullscreen = QAction("Toggle &Full Screen", self)
        toggle_fullscreen.setShortcut(QKeySequence.StandardKey.FullScreen)
        toggle_fullscreen.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(toggle_fullscreen)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Fault injection
        inject_fault_action = QAction("Inject &Fault...", self)
        inject_fault_action.triggered.connect(self.show_fault_injection_dialog)
        tools_menu.addAction(inject_fault_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Add common actions to toolbar
        start_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.start_action = QAction(start_icon, "Start", self)
        self.start_action.triggered.connect(self.start_inverter)
        
        stop_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
        self.stop_action = QAction(stop_icon, "Stop", self)
        self.stop_action.triggered.connect(self.stop_inverter)
        
        reset_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        reset_action = QAction(reset_icon, "Reset", self)
        reset_action.triggered.connect(self.reset_inverter)
        
        # Add separator
        toolbar.addSeparator()
        
        # Add actions to toolbar
        toolbar.addAction(self.start_action)
        toolbar.addAction(self.stop_action)
        toolbar.addAction(reset_action)
        
        # Add frequency control
        toolbar.addSeparator()
        freq_label = QLabel("Frequency (Hz):")
        toolbar.addWidget(freq_label)
        
        self.freq_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_slider.setRange(0, int(self.inverter.frequenza_nominale * 10))  # 0.1 Hz resolution
        self.freq_slider.setValue(0)
        self.freq_slider.valueChanged.connect(self.on_freq_slider_changed)
        self.freq_slider.setFixedWidth(200)
        toolbar.addWidget(self.freq_slider)
        
        self.freq_display = QLabel("0.0")
        self.freq_display.setFixedWidth(40)
        toolbar.addWidget(self.freq_display)
    
    def setup_control_panel(self, layout):
        """Set up the control panel in the left panel."""
        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        
        # State indicator
        state_group = QGroupBox("State")
        state_layout = QHBoxLayout()
        
        self.state_led = LedIndicator()
        self.state_label = QLabel("Ready")
        state_layout.addWidget(self.state_led)
        state_layout.addWidget(self.state_label, 1)
        state_group.setLayout(state_layout)
        
        # Alarms indicator
        alarm_group = QGroupBox("Alarms")
        alarm_layout = QVBoxLayout()
        
        self.alarm_led = LedIndicator()
        self.alarm_led.set_color("red")
        self.alarm_label = QLabel("No Alarms")
        self.alarm_label.setWordWrap(True)
        
        alarm_status = QHBoxLayout()
        alarm_status.addWidget(self.alarm_led)
        alarm_status.addWidget(QLabel("Status:"))
        alarm_status.addWidget(self.alarm_label, 1)
        
        self.alarm_list = QListWidget()
        self.alarm_list.setMaximumHeight(100)
        
        alarm_layout.addLayout(alarm_status)
        alarm_layout.addWidget(self.alarm_list)
        alarm_group.setLayout(alarm_layout)
        
        # Add to status layout
        status_layout.addWidget(state_group)
        status_layout.addWidget(alarm_group)
        status_group.setLayout(status_layout)
        
        # Control group
        control_group = QGroupBox("Control")
        control_layout = QVBoxLayout()
        
        # Start/Stop buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start")
        self.start_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.start_btn.clicked.connect(self.start_inverter)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_btn.clicked.connect(self.stop_inverter)
        self.stop_btn.setEnabled(False)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        
        # Frequency control
        freq_control = QGroupBox("Frequency Control")
        freq_layout = QVBoxLayout()
        
        # Frequency slider
        self.freq_slider_main = QSlider(Qt.Orientation.Horizontal)
        self.freq_slider_main.setRange(0, int(self.inverter.frequenza_nominale * 10))  # 0.1 Hz resolution
        self.freq_slider_main.setValue(0)
        self.freq_slider_main.valueChanged.connect(self.on_freq_slider_changed)
        
        # Frequency display
        freq_display_layout = QHBoxLayout()
        self.freq_display_main = QLabel("0.0")
        self.freq_display_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.freq_display_main.setStyleSheet("font-size: 16px; font-weight: bold;")
        freq_unit = QLabel("Hz")
        
        freq_display_layout.addStretch()
        freq_display_layout.addWidget(self.freq_display_main)
        freq_display_layout.addWidget(freq_unit)
        freq_display_layout.addStretch()
        
        freq_layout.addLayout(freq_display_layout)
        freq_layout.addWidget(self.freq_slider_main)
        freq_control.setLayout(freq_layout)
        
        # Add to control layout
        control_layout.addLayout(btn_layout)
        control_layout.addWidget(freq_control)
        
        # Preset frequencies
        presets_group = QGroupBox("Preset Frequencies")
        presets_layout = QGridLayout()
        
        presets = [
            ("10 Hz", 10), ("20 Hz", 20), ("30 Hz", 30),
            ("40 Hz", 40), ("50 Hz", 50), ("60 Hz", 60)
        ]
        
        for i, (label, freq) in enumerate(presets):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, f=freq: self.set_frequency(f))
            presets_layout.addWidget(btn, i // 3, i % 3)
        
        presets_group.setLayout(presets_layout)
        control_layout.addWidget(presets_group)
        
        # Add to main layout
        layout.addWidget(status_group)
        layout.addWidget(control_group)
        layout.addStretch()
        
        # Set the control panel as the left panel content
        control_group.setLayout(control_layout)
    
    def setup_tabbed_interface(self, layout):
        """Set up the tabbed interface in the right panel."""
        self.tabs = QTabWidget()
        
        # Dashboard tab
        self.dashboard_tab = QWidget()
        self.setup_dashboard_ui()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        
        # Parameters tab
        self.parameters_tab = QWidget()
        self.setup_parameters_ui()
        self.tabs.addTab(self.parameters_tab, "Parameters")
        
        # Log tab
        self.log_tab = QWidget()
        self.setup_log_ui()
        self.tabs.addTab(self.log_tab, "Log")
        
        # Add tabs to layout
        layout.addWidget(self.tabs)
    
    def setup_dashboard_ui(self):
        """Set up the dashboard tab."""
        layout = QVBoxLayout(self.dashboard_tab)
        
        # Top row - Key parameters
        top_row = QHBoxLayout()
        
        # Speed gauge
        speed_group = QGroupBox("Motor Speed")
        speed_layout = QVBoxLayout()
        
        self.speed_gauge = QLabel("0")
        self.speed_gauge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_gauge.setStyleSheet("font-size: 36px; font-weight: bold;")
        
        speed_unit = QLabel("RPM")
        speed_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        speed_layout.addWidget(self.speed_gauge)
        speed_layout.addWidget(speed_unit)
        speed_group.setLayout(speed_layout)
        
        # Frequency display
        freq_group = QGroupBox("Output Frequency")
        freq_layout = QVBoxLayout()
        
        self.freq_value = QLabel("0.00")
        self.freq_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.freq_value.setStyleSheet("font-size: 36px; font-weight: bold;")
        
        freq_unit = QLabel("Hz")
        freq_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        freq_layout.addWidget(self.freq_value)
        freq_layout.addWidget(freq_unit)
        freq_group.setLayout(freq_layout)
        
        # Current display
        current_group = QGroupBox("Output Current")
        current_layout = QVBoxLayout()
        
        self.current_value = QLabel("0.00")
        self.current_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_value.setStyleSheet("font-size: 36px; font-weight: bold;")
        
        current_unit = QLabel("A")
        current_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        current_layout.addWidget(self.current_value)
        current_layout.addWidget(current_unit)
        current_group.setLayout(current_layout)
        
        # Add to top row
        top_row.addWidget(speed_group)
        top_row.addWidget(freq_group)
        top_row.addWidget(current_group)
        
        # Middle row - Status indicators
        mid_row = QHBoxLayout()
        
        # Voltage
        voltage_group = QGroupBox("Voltage")
        voltage_layout = QVBoxLayout()
        
        self.voltage_value = QLabel("0.0")
        self.voltage_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voltage_value.setStyleSheet("font-size: 24px;")
        
        voltage_unit = QLabel("V")
        voltage_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        voltage_layout.addWidget(self.voltage_value)
        voltage_layout.addWidget(voltage_unit)
        voltage_group.setLayout(voltage_layout)
        
        # Power
        power_group = QGroupBox("Power")
        power_layout = QVBoxLayout()
        
        self.power_value = QLabel("0.00")
        self.power_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.power_value.setStyleSheet("font-size: 24px;")
        
        power_unit = QLabel("kW")
        power_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        power_layout.addWidget(self.power_value)
        power_layout.addWidget(power_unit)
        power_group.setLayout(power_layout)
        
        # Temperature
        temp_group = QGroupBox("Temperature")
        temp_layout = QVBoxLayout()
        
        self.temp_value = QLabel("25.0")
        self.temp_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_value.setStyleSheet("font-size: 24px;")
        
        temp_unit = QLabel("°C")
        temp_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        temp_layout.addWidget(self.temp_value)
        temp_layout.addWidget(temp_unit)
        temp_group.setLayout(temp_layout)
        
        # Add to middle row
        mid_row.addWidget(voltage_group)
        mid_row.addWidget(power_group)
        mid_row.addWidget(temp_group)
        
        # Add to main layout
        layout.addLayout(top_row)
        layout.addLayout(mid_row)
        layout.addStretch()
    
    def setup_parameters_ui(self):
        """Set up the parameters tab."""
        layout = QVBoxLayout(self.parameters_tab)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QVBoxLayout()
        
        # Create parameter widgets
        self.param_widgets = []
        for name, unit in [
            ("Frequency", "Hz"),
            ("Voltage", "V"),
            ("Current", "A"),
            ("Power", "kW"),
            ("Temperature", "°C")
        ]:
            widget = ParameterWidget(name, unit)
            params_layout.addWidget(widget)
            self.param_widgets.append(widget)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
    
    def setup_log_ui(self):
        """Set up the log tab."""
        layout = QVBoxLayout(self.log_tab)
        
        # Log group
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        
        # Log controls
        controls_layout = QHBoxLayout()
        
        # Log level filter
        log_level_label = QLabel("Filter by level:")
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")  # Default to showing INFO and above
        
        # Add controls to layout
        controls_layout.addWidget(log_level_label)
        controls_layout.addWidget(self.log_level_combo)
        controls_layout.addStretch()
        
        # Log table
        self.log_table = QTableWidget()
        self.log_table.setRowCount(0)
        self.log_table.setColumnCount(4)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Level", "Source", "Message"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Add widgets to log layout
        log_layout.addLayout(controls_layout)
        log_layout.addWidget(self.log_table)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status indicators
        self.status_indicators = {
            'connected': (QLabel("Disconnected"), QLabel("")),
            'error': (QLabel("No Errors"), QLabel("")),
            'state': (QLabel("Ready"), QLabel("")),
            'uptime': (QLabel("00:00:00"), QLabel(""))
        }
        
        for label, value in self.status_indicators.values():
            self.status_bar.addPermanentWidget(label)
            self.status_bar.addPermanentWidget(value)
    
    def apply_styles(self):
        """Apply styles to the UI."""
        # Set font
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Connect inverter state change callbacks
        self.inverter.add_state_change_callback(self.on_inverter_state_changed)
        self.inverter.add_alarm_callback(self.on_inverter_alarm)
        
        # Connect UI controls
        self.start_btn.clicked.connect(self.start_inverter)
        self.stop_btn.clicked.connect(self.stop_inverter)
        
        # Log level filter
        self.log_level_combo.currentTextChanged.connect(self.filter_log)
        
        # Set up periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # 10 Hz update rate
    
    def on_inverter_state_changed(self, state):
        """Handle inverter state changes.
        
        Args:
            state: The new state of the inverter (StatoInverter enum)
        """
        # Update UI based on inverter state
        self.update_ui()
        
        # Log state change
        self.log_message(f"Inverter state changed to {state.name}", "INFO")
    
    def on_inverter_alarm(self, alarm):
        """Handle inverter alarms.
        
        Args:
            alarm: The alarm object or None if all alarms are cleared
        """
        # Update alarm list
        self.update_alarm_list()
        
        if alarm is not None:
            # Log the alarm
            self.log_message(f"ALARM: {alarm.descrizione}", "ERROR")
            
            # Show error message to user
            QMessageBox.critical(self, "Inverter Alarm", alarm.descrizione)
        else:
            self.log_message("All alarms cleared", "INFO")
    
    def update_ui(self):
        """Update the UI with current inverter state."""
        try:
            # Update dashboard values
            self.speed_gauge.setText(f"{int(self.inverter.velocita_motore)}")
            self.freq_value.setText(f"{self.inverter.frequenza_uscita:.2f}")
            self.current_value.setText(f"{self.inverter.corrente_uscita:.2f}")
            self.voltage_value.setText(f"{self.inverter.tensione_uscita:.1f}")
            self.power_value.setText(f"{self.inverter.potenza_uscita:.2f}")
            self.temp_value.setText(f"{self.inverter.temperatura:.1f}")
            
            # Update state indicator
            state_text = self.inverter.stato.name.replace('_', ' ').title()
            self.state_label.setText(state_text)
            
            # Update state LED
            if self.inverter.stato == StatoInverter.IN_MARCIA:
                self.state_led.set_color("green")
                self.state_led.set_state(True)
            elif self.inverter.stato == StatoInverter.ALLARME:
                self.state_led.set_color("red")
                self.state_led.set_state(True)
            elif self.inverter.stato == StatoInverter.ACCELERAZIONE:
                self.state_led.set_color("yellow")
                self.state_led.set_state(True)
            elif self.inverter.stato == StatoInverter.DECELERAZIONE:
                self.state_led.set_color("yellow")
                self.state_led.set_state(True)
            else:
                self.state_led.set_color("gray")
                self.state_led.set_state(False)
            
            # Update alarm indicator
            if self.inverter.allarme_attivo:
                self.alarm_led.set_state(True)
                self.alarm_label.setText(self.inverter.descrizione_allarme)
                self.alarm_label.setStyleSheet("color: red;")
            else:
                self.alarm_led.set_state(False)
                self.alarm_label.setText("No Alarms")
                self.alarm_label.setStyleSheet("")
            
            # Update control buttons
            is_running = self.inverter.stato in [StatoInverter.IN_MARCIA, StatoInverter.ACCELERAZIONE]
            self.start_btn.setEnabled(not is_running and not self.inverter.allarme_attivo)
            self.stop_btn.setEnabled(is_running and not self.inverter.allarme_attivo)
            
            # Update frequency slider if not being dragged
            if not self.freq_slider.isSliderDown():
                self.freq_slider.setValue(int(self.inverter.frequenza_uscita * 10))
                self.freq_display.setText(f"{self.inverter.frequenza_uscita:.1f}")
            
            # Update status bar
            self.update_status()
            
        except Exception as e:
            self.log_message(f"Error updating UI: {str(e)}", "ERROR")
    
    def update_status(self):
        """Update the status bar with current information."""
        try:
            # Update connection status
            is_connected = self.serial_handler is not None and self.serial_handler.connected
            self.status_indicators['connected'][1].setText("Connected" if is_connected else "Disconnected")
            self.status_indicators['connected'][1].setStyleSheet(
                "color: green;" if is_connected else "color: red;"
            )
            
            # Update error status
            if self.inverter.allarme_attivo:
                self.status_indicators['error'][1].setText("Alarm Active")
                self.status_indicators['error'][1].setStyleSheet("color: red;")
            else:
                self.status_indicators['error'][1].setText("OK")
                self.status_indicators['error'][1].setStyleSheet("color: green;")
            
            # Update state
            state_text = self.inverter.stato.name.replace('_', ' ').title()
            self.status_indicators['state'][1].setText(state_text)
            
            # Update uptime
            uptime = time.time() - self.inverter._tempo_inizio
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            self.status_indicators['uptime'][1].setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
        except Exception as e:
            self.log_message(f"Error updating status: {str(e)}", "ERROR")
    
    def update_alarm_list(self):
        """Update the alarm list with current alarms."""
        self.alarm_list.clear()
        for alarm in sorted(self.inverter.allarmi, key=lambda x: x.timestamp, reverse=True):
            if alarm.attivo:
                timestamp = datetime.fromtimestamp(alarm.timestamp).strftime("%H:%M:%S")
                item = QListWidgetItem(f"[{timestamp}] {alarm.descrizione}")
                item.setForeground(QColor("red"))
                self.alarm_list.addItem(item)
    
    def log_message(self, message: str, level: str = "INFO"):
        """
        Add a message to the log.
        
        Args:
            message: The message to log
            level: The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Add to log table
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)
            
            # Create items
            time_item = QTableWidgetItem(timestamp)
            level_item = QTableWidgetItem(level)
            source_item = QTableWidgetItem("Simulator")
            msg_item = QTableWidgetItem(message)
            
            # Set text alignment
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            level_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            source_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            # Set text color based on level
            if level == "ERROR" or level == "CRITICAL":
                level_item.setForeground(QColor("red"))
                msg_item.setForeground(QColor("red"))
            elif level == "WARNING":
                level_item.setForeground(QColor("orange"))
                msg_item.setForeground(QColor("orange"))
            elif level == "DEBUG":
                level_item.setForeground(QColor("gray"))
                msg_item.setForeground(QColor("gray"))
            
            # Add items to table
            self.log_table.setItem(row, 0, time_item)
            self.log_table.setItem(row, 1, level_item)
            self.log_table.setItem(row, 2, source_item)
            self.log_table.setItem(row, 3, msg_item)
            
            # Auto-scroll to bottom
            self.log_table.scrollToBottom()
            
            # Also log to console
            logger.log(getattr(logging, level), message)
            
        except Exception as e:
            print(f"Error logging message: {e}")
    
    def filter_log(self, level: str):
        """
        Filter the log by level.
        
        Args:
            level: The minimum log level to show
        """
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        min_level = levels.index(level) if level in levels else 1  # Default to INFO
        
        for row in range(self.log_table.rowCount()):
            level_item = self.log_table.item(row, 1)
            if level_item:
                level_text = level_item.text()
                row_level = levels.index(level_text) if level_text in levels else 1
                self.log_table.setRowHidden(row, row_level < min_level)
    
    def clear_log(self):
        """Clear the log."""
        self.log_table.setRowCount(0)
        self.log_message("Log cleared", "INFO")
    
    def save_log(self):
        """Save the log to a file."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Log", "", "CSV Files (*.csv);;All Files (*)"
            )
            
            if filename:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow(["Timestamp", "Level", "Source", "Message"])
                    
                    # Write rows
                    for row in range(self.log_table.rowCount()):
                        if not self.log_table.isRowHidden(row):
                            row_data = []
                            for col in range(self.log_table.columnCount()):
                                item = self.log_table.item(row, col)
                                row_data.append(item.text() if item else "")
                            writer.writerow(row_data)
                
                self.log_message(f"Log saved to {filename}", "INFO")
                
        except Exception as e:
            self.log_message(f"Error saving log: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Failed to save log: {str(e)}")
    
    def log_data(self):
        """Log current data to file."""
        try:
            now = time.time()
            if now - self.last_log_time >= self.log_interval:
                self.last_log_time = now
                
                # Prepare data row
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                data = [
                    timestamp,
                    self.inverter.frequenza_uscita,
                    self.inverter.tensione_uscita,
                    self.inverter.corrente_uscita,
                    self.inverter.velocita_motore,
                    self.inverter.temperatura,
                    self.inverter.stato.name,
                    "1" if self.inverter.allarme_attivo else "0"
                ]
                
                # Write to file
                file_exists = os.path.isfile(self.log_file)
                with open(self.log_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow([
                            "timestamp", "frequency_hz", "voltage_v", "current_a",
                            "speed_rpm", "temperature_c", "state", "alarm"
                        ])
                    writer.writerow(data)
                    
        except Exception as e:
            self.log_message(f"Error logging data: {str(e)}", "ERROR")
    
    def start_inverter(self):
        """Start the inverter."""
        try:
            if self.inverter.avvia():
                self.log_message("Inverter started", "INFO")
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
            else:
                self.log_message("Failed to start inverter: Invalid state", "WARNING")
        except Exception as e:
            self.log_message(f"Error starting inverter: {str(e)}", "ERROR")
    
    def stop_inverter(self):
        """Stop the inverter."""
        try:
            if self.inverter.ferma():
                self.log_message("Inverter stop initiated", "INFO")
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(False)
            else:
                self.log_message("Failed to stop inverter: Invalid state", "WARNING")
        except Exception as e:
            self.log_message(f"Error stopping inverter: {str(e)}", "ERROR")
    
    def reset_inverter(self):
        """Reset the inverter."""
        try:
            self.inverter.reset()
            self.log_message("Inverter reset", "INFO")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        except Exception as e:
            self.log_message(f"Error resetting inverter: {str(e)}", "ERROR")
    
    def set_frequency(self, frequency: float):
        """
        Set the inverter frequency.
        
        Args:
            frequency: The frequency to set in Hz
        """
        try:
            if self.inverter.imposta_frequenza(frequency):
                self.log_message(f"Frequency set to {frequency} Hz", "INFO")
            else:
                self.log_message(f"Invalid frequency: {frequency} Hz", "WARNING")
        except Exception as e:
            self.log_message(f"Error setting frequency: {str(e)}", "ERROR")
    
    def on_freq_slider_changed(self, value):
        """Handle frequency slider changes."""
        frequency = value / 10.0  # Convert from 0.1 Hz steps to Hz
        self.freq_display.setText(f"{frequency:.1f}")
        self.freq_display_main.setText(f"{frequency:.1f}")
        
        # Only update inverter if running
        if self.inverter.stato in [StatoInverter.IN_MARCIA, StatoInverter.ACCELERAZIONE]:
            self.set_frequency(frequency)
    
    def show_fault_injection_dialog(self):
        """Show the fault injection dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Inject Fault")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        # Fault type selection
        form_layout = QFormLayout()
        
        fault_type_combo = QComboBox()
        for fault in CodiceAllarme:
            if fault != CodiceAllarme.NESSUNO:
                fault_type_combo.addItem(fault.name.replace('_', ' ').title(), fault)
        
        description_edit = QLineEdit("Simulated fault")
        
        form_layout.addRow("Fault Type:", fault_type_combo)
        form_layout.addRow("Description:", description_edit)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            fault_type = fault_type_combo.currentData()
            description = description_edit.text().strip()
            
            try:
                self.inverter.inject_fault(fault_type, description)
                self.log_message(f"Injected fault: {fault_type.name}", "WARNING")
            except Exception as e:
                self.log_message(f"Error injecting fault: {str(e)}", "ERROR")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_about_dialog(self):
        """Show the about dialog."""
        about_text = """
        <h2>Nidec Commander CDE Simulator</h2>
        <p>Version 1.0.0</p>
        <p> 2024 Nidec Corporation. All rights reserved.</p>
        <p>This is a simulation tool for testing Nidec Commander CDE applications
        without requiring actual hardware.</p>
        """
        
        QMessageBox.about(self, "About Nidec Commander Simulator", about_text)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop timers
        self.update_timer.stop()
        self.status_timer.stop()
        self.log_timer.stop()
        
        # Stop the inverter
        if hasattr(self, 'inverter'):
            self.inverter.ferma()
        
        # Stop serial handler if running
        if hasattr(self, 'serial_handler') and self.serial_handler:
            self.serial_handler.disconnect()
        
        # Accept the close event
        event.accept()
    
    def new_simulation(self):
        """Start a new simulation."""
        # Stop the current simulation
        self.stop_inverter()
        
        # Reset the inverter
        self.inverter = InverterSimulato()
        
        # Reset the UI
        self.update_ui()
        self.update_status()
        self.clear_log()
        
        # Log the new simulation
        self.log_message("New simulation started", "INFO")
        
        # Update button states
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.reset_btn.setEnabled(True)
        
        # Reset frequency slider
        self.freq_slider.setValue(0)
        self.freq_display.setText("0.0")
        self.freq_display_main.setText("0.0")
    
    def open_log(self):
        """Open a log file and display its contents."""
        # Open file dialog to select a log file
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Log File",
            "",
            "Log Files (*.log *.txt);;All Files (*)"
        )
        
        if not file_name:
            return  # User cancelled
        
        try:
            # Read the log file
            with open(file_name, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Create a dialog to display the log
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Log Viewer - {os.path.basename(file_name)}")
            dialog.setMinimumSize(800, 600)
            
            layout = QVBoxLayout(dialog)
            
            # Add a text edit to display the log
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            text_edit.setFont(QFont("Courier New", 10))
            text_edit.setPlainText(log_content)
            
            # Add a close button
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            button_box.rejected.connect(dialog.reject)
            
            layout.addWidget(text_edit)
            layout.addWidget(button_box)
            
            # Scroll to the bottom
            text_edit.verticalScrollBar().setValue(text_edit.verticalScrollBar().maximum())
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open log file: {str(e)}")
    
    def save_log_as(self):
        """Save the current log to a file with a custom name and location."""
        # Open file dialog to select save location
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log As",
            "inverter_log.txt",
            "Text Files (*.txt);;Log Files (*.log);;All Files (*)"
        )
        
        if not file_name:
            return  # User cancelled
        
        try:
            # Get the current log content from the log table
            log_data = []
            for row in range(self.log_table.rowCount()):
                timestamp = self.log_table.item(row, 0).text()
                level = self.log_table.item(row, 1).text()
                source = self.log_table.item(row, 2).text()
                message = self.log_table.item(row, 3).text()
                log_data.append(f"{timestamp} - {level} - {source} - {message}")
            
            # Write to the selected file
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write("\n".join(log_data))
            
            QMessageBox.information(self, "Success", f"Log saved to {file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save log file: {str(e)}")

def run_simulator():
    """
    Run the simulator as a standalone application.
    
    This function initializes the application, creates the main window,
    and starts the event loop.
    """
    try:
        # Create application instance
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Set application information
        app.setApplicationName("Nidec Commander CDE Simulator")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Nidec Corporation")
        
        # Create and show the main window
        window = SimulatorWidget()
        window.show()
        
        # Keep a reference to the window to prevent garbage collection
        app._window = window
        
        # Log startup
        window.log_message("Simulator started", "INFO")
        
        # Start the event loop
        return app.exec()
        
    except Exception as e:
        # Log any unhandled exceptions
        logger.critical("Unhandled exception in simulator", exc_info=True)
        
        # Show error message
        error_msg = f"A critical error occurred while starting the simulator:\n{str(e)}\n\nPlease check the log file for details."
        QMessageBox.critical(None, "Critical Error", error_msg)
        return 1

if __name__ == '__main__':
    # Ensure the application doesn't close immediately
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        simulator = SimulatorWidget()
        simulator.show()
        app._window = simulator  # Keep reference to prevent garbage collection
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
