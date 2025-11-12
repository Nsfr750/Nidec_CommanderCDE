import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QApplication, QMenuBar, QMenu, 
                            QStatusBar, QWidget, QVBoxLayout, QLabel, QMessageBox,
                            QHBoxLayout, QPushButton, QDoubleSpinBox, QComboBox, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont

def get_resource_path(relative_path):
    """Get the correct path to a resource file, whether running as script or frozen executable."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        return os.path.join(base_path, relative_path)
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(script_dir, relative_path)

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add paths to sys.path in a way that works for both development and compiled versions
paths_to_add = [
    project_root,
    script_dir,
    os.path.join(project_root, 'script'),
    os.path.join(project_root, 'script', 'utils')
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import simulator components
try:
    from script.utils.inverter_sim import InverterSimulato
    from script.utils.serial_handler import SerialHandler
except ImportError as e:
    # If import fails, try direct import (for compiled version)
    try:
        from utils.inverter_sim import InverterSimulato
        from utils.serial_handler import SerialHandler
    except ImportError as e2:
        print(f"Error importing simulator components: {e}")
        print(f"Second attempt error: {e2}")
        print(f"Python path: {sys.path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Script directory: {script_dir}")
        print(f"Project root: {project_root}")
        raise

class SimulatorWidget(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.lang = 'en'  # Default language
            self.setWindowTitle('Nidec Commander Simulator')
            self.setMinimumSize(1024, 768)
            
            # Initialize UI
            self.init_ui()
            
            # Initialize simulator components
            self.inverter = InverterSimulato()
            self.serial_handler = SerialHandler(self.inverter)
            self.setup_connections()
            self.setup_timer()
            
            # Show status in status bar
            self.statusBar().showMessage('Ready')
            
        except Exception as e:
            print(f"Error initializing simulator: {e}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
            raise
        
    def init_ui(self):
        # Set window icon
        icon_path = get_resource_path("script/assets/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        
        # Content area with horizontal layout
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content_widget)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Control group
        control_group = QGroupBox("Controllo")
        control_layout = QVBoxLayout()
        
        # Control buttons
        self.btn_start = QPushButton("AVVIA")
        self.btn_stop = QPushButton("FERMA")
        self.btn_reset = QPushButton("RESET")
        self.btn_start.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_stop.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_reset.setStyleSheet("background-color: #2196F3; color: white;")
        
        # Direction
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["AVANTI", "INDIETRO"])
        
        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_stop)
        control_layout.addWidget(self.btn_reset)
        control_layout.addWidget(QLabel("Direction:"))
        control_layout.addWidget(self.direction_combo)
        control_group.setLayout(control_layout)
        
        # Parameters group
        param_group = QGroupBox("Parametri")
        param_layout = QVBoxLayout()
        
        # Frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Frequenza (Hz):"))
        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(0.0, 400.0)
        self.freq_spin.setValue(50.0)
        self.freq_spin.setDecimals(1)
        freq_layout.addWidget(self.freq_spin)
        
        # Voltage
        volt_layout = QHBoxLayout()
        volt_layout.addWidget(QLabel("Voltaggio (V):"))
        self.volt_label = QLabel("0.0")
        volt_layout.addWidget(self.volt_label)
        
        # Current
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("Corrente (A):"))
        self.current_label = QLabel("0.0")
        current_layout.addWidget(self.current_label)
        
        # Speed
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Velocità (RPM):"))
        self.speed_label = QLabel("0")
        speed_layout.addWidget(self.speed_label)
        
        param_layout.addLayout(freq_layout)
        param_layout.addLayout(volt_layout)
        param_layout.addLayout(current_layout)
        param_layout.addLayout(speed_layout)
        param_group.setLayout(param_layout)
        
        left_layout.addWidget(control_group)
        left_layout.addWidget(param_group)
        left_layout.addStretch()
        
        # Right panel - Status and alarms
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Status
        status_group = QGroupBox("Stato")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("PRONTO")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        status_layout.addWidget(self.status_label)
        
        # Alarms
        self.alarm_label = QLabel("Nessun Allarme")
        self.alarm_label.setStyleSheet("color: #f44336;")
        status_layout.addWidget(self.alarm_label)
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperatura (°C):"))
        self.temp_label = QLabel("25")
        temp_layout.addWidget(self.temp_label)
        status_layout.addLayout(temp_layout)
        
        status_group.setLayout(status_layout)
        
        # Serial log
        log_group = QGroupBox("Log dei Comandi")
        log_layout = QVBoxLayout()
        self.log_text = QLabel()
        self.log_text.setWordWrap(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        right_layout.addWidget(status_group)
        right_layout.addWidget(log_group)
        
        # Add panels to main layout
        content_layout.addWidget(left_panel, stretch=1)
        content_layout.addWidget(right_panel, stretch=1)
        
        # Setup connections
        self.setup_connections()
    
    def setup_connections(self):
        self.btn_start.clicked.connect(self.start_inverter)
        self.btn_stop.clicked.connect(self.stop_inverter)
        self.btn_reset.clicked.connect(self.reset_inverter)
        self.freq_spin.valueChanged.connect(self.update_frequency)
        self.direction_combo.currentTextChanged.connect(self.change_direction)
    
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(200)  # Update UI every 200ms
    
    def update_ui(self):
        # Update UI with simulator data
        self.freq_spin.blockSignals(True)
        self.freq_spin.setValue(self.inverter.frequenza_uscita)
        self.freq_spin.blockSignals(False)
        
        self.volt_label.setText(f"{self.inverter.tensione_uscita:.1f}")
        self.current_label.setText(f"{self.inverter.corrente_uscita:.2f}")
        self.speed_label.setText(f"{int(self.inverter.velocita_motore)}")
        self.temp_label.setText(f"{self.inverter.temperatura}")
        
        # Update status
        if self.inverter.allarme_attivo:
            self.status_label.setText("ALLARME")
            self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f44336;")
            self.alarm_label.setText(self.inverter.descrizione_allarme)
        elif self.inverter.in_marcia:
            self.status_label.setText("IN MARCIA")
            self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
            self.alarm_label.setText("No alarms")
        else:
            self.status_label.setText("PRONTO")
            self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
            self.alarm_label.setText("No alarms")
            
        # Update direction
        self.direction_combo.blockSignals(True)
        self.direction_combo.setCurrentText("AVANTI" if self.inverter.direzione == 1 else "INDIETRO")
        self.direction_combo.blockSignals(False)
    
    def start_inverter(self):
        self.inverter.avvia()
        self.log_serial("Command: AVVIA")
        
    def stop_inverter(self):
        print(f"DEBUG - Before ferma() - in_marcia: {self.inverter.in_marcia}, stato: {self.inverter.stato}")
        self.inverter.ferma()
        print(f"DEBUG - After ferma() - in_marcia: {self.inverter.in_marcia}, stato: {self.inverter.stato}")
        self.log_serial("Command: FERMA")
        
    def reset_inverter(self):
        self.inverter.reset()
        self.log_serial("Command: RESET")
        
    def update_frequency(self, freq):
        self.inverter.imposta_frequenza(freq)
        self.log_serial(f"Frequenza impostata: {freq} Hz")
        
    def change_direction(self, direction):
        dir_value = 1 if direction == "AVANTI" else -1
        self.inverter.cambia_direzione(dir_value)
        self.log_serial(f"Direzione cambaiata a: {direction}")
    
    def log_serial(self, message):
        if hasattr(self, 'log_text'):
            current_text = self.log_text.text()
            self.log_text.setText(f"{message}\n{current_text}")
            
    def show_serial_connection(self):
        """Show the serial connection dialog."""
        # TODO: Implement serial connection dialog
        self.statusBar().showMessage("Opening serial connection...")
        
    def disconnect_serial(self):
        """Disconnect from the serial port."""
        # TODO: Implement serial disconnection
        self.statusBar().showMessage("Disconnected from serial port")
        
    def closeEvent(self, event):
        """Handle the window close event."""
        # Clean up any running threads or resources here
        if hasattr(self, 'update_thread'):
            try:
                self.update_thread.stop()
            except:
                pass
        event.accept()

def main():
    try:
        print("Starting Nidec Simulator...")
        print(f"Python path: {sys.path}")
        print(f"Current directory: {os.getcwd()}")
        
        # Create application instance
        app = QApplication(sys.argv)
        
        # Try to create and show the main window
        try:
            print("Creating main window...")
            
            # Set application style
            app.setStyle('Fusion')
            
            # Set window icon if available
            try:
                icon_path = get_resource_path("script/assets/icon.ico")
                if os.path.exists(icon_path):
                    app.setWindowIcon(QIcon(icon_path))
            except Exception as e:
                print(f"Warning: Could not set application icon: {e}")
            
            # Create and show the main window
            window = SimulatorWidget()
            print("Main window created, showing...")
            window.show()
            print("Entering application event loop...")
            return app.exec()
        except Exception as e:
            import traceback
            error_msg = f"Error in main window: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            
            # Try to show error in a message box if possible
            try:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(None, 'Fatal Error', 
                    f"Application failed to start.\n\nError: {str(e)}\n\n"
                    "Please check the application logs for more details.")
            except:
                print("Could not show error dialog", file=sys.stderr)
            
            return 1
            
    except Exception as e:
        import traceback
        error_msg = f"Fatal error in main: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        return 1

def run_simulator():
    """Run the simulator as a standalone application."""
    try:
        result = main()
        print(f"Simulator exited with code: {result}")
        return result
    except Exception as e:
        import traceback
        error_msg = f"Unhandled exception in run_simulator: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        return 1

if __name__ == '__main__':
    run_simulator()
