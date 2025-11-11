try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError as e:
    SERIAL_AVAILABLE = False
    print(f"Errore durante l'importazione di pyserial: {e}")
    print("Per favore installa pyserial con: pip install pyserial")

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QPushButton, QDialogButtonBox, QMessageBox)

class SerialDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Connessione Seriale')
        self.setMinimumWidth(400)
        
        self.port = None
        self.baudrate = 9600
        
        self.init_ui()
        if SERIAL_AVAILABLE:
            self.populate_ports()
        else:
            QMessageBox.critical(
                self,
                'Errore',
                'Il modulo pyserial non è installato.\nPer favore installalo con: pip install pyserial'
            )
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Port selection
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel('Porta COM:'))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        port_layout.addWidget(self.port_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton('Aggiorna')
        self.refresh_btn.clicked.connect(self.populate_ports)
        port_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(port_layout)
        
        # Baud rate selection
        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel('Velocità (baud):'))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baud_combo.setCurrentText('9600')
        baud_layout.addWidget(self.baud_combo)
        
        layout.addLayout(baud_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def populate_ports(self):
        """Populate the COM port dropdown with available ports."""
        if not SERIAL_AVAILABLE:
            QMessageBox.critical(
                self,
                'Errore',
                'Impossibile elencare le porte: pyserial non disponibile'
            )
            return
            
        self.port_combo.clear()
        try:
            ports = serial.tools.list_ports.comports()
            
            if not ports:
                self.port_combo.addItem('Nessuna porta disponibile')
                return
                
            for port in sorted(ports):
                self.port_combo.addItem(port.device, port.device)
        except Exception as e:
            QMessageBox.critical(
                self,
                'Errore',
                f'Errore durante il rilevamento delle porte: {str(e)}'
            )
    
    def get_port(self):
        """Get the selected port."""
        return self.port_combo.currentData()
    
    def get_baudrate(self):
        """Get the selected baud rate."""
        return int(self.baud_combo.currentText())
    
    def accept(self):
        """Validate and accept the dialog."""
        if not self.port_combo.currentData():
            QMessageBox.warning(
                self, 
                'Errore', 
                'Selezionare una porta COM valida'
            )
            return
            
        self.port = self.get_port()
        self.baudrate = self.get_baudrate()
        super().accept()
