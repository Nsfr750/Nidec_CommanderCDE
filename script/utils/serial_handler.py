import serial
import serial.tools.list_ports
import threading
import time
import re
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

@dataclass
class ComandoSeriale:
    comando: str
    risposta: str
    descrizione: str
    handler: Optional[Callable[[str], str]] = None

class SerialHandler:
    def __init__(self, inverter, port: str = None, baudrate: int = 9600):
        self.inverter = inverter
        self.port = port
        self.baudrate = baudrate
        self.serial_port: Optional[serial.Serial] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Mappa dei comandi supportati (comando: risposta o handler)
        self.comandi: Dict[str, ComandoSeriale] = {
            "RUN": ComandoSeriale(
                "RUN", 
                "OK\r\n", 
                "Avvia l'inverter",
                self._handle_run
            ),
            "STOP": ComandoSeriale(
                "STOP", 
                "OK\r\n", 
                "Ferma l'inverter",
                self._handle_stop
            ),
            "RST": ComandoSeriale(
                "RST", 
                "OK\r\n", 
                "Resetta gli allarmi",
                self._handle_reset
            ),
            "FREQ": ComandoSeriale(
                r"FREQ (\d+\.?\d*)", 
                "OK\r\n", 
                "Imposta la frequenza (es: FREQ 50.0)",
                self._handle_freq
            ),
            "DIR": ComandoSeriale(
                r"DIR ([+-]?1)", 
                "OK\r\n", 
                "Imposta la direzione (1=avanti, -1=indietro)",
                self._handle_dir
            ),
            "STATUS": ComandoSeriale(
                "STATUS", 
                "", 
                "Restituisce lo stato dell'inverter",
                self._handle_status
            ),
            "HELP": ComandoSeriale(
                "HELP", 
                "", 
                "Mostra l'elenco dei comandi disponibili",
                self._handle_help
            )
        }
        
        # Se non è specificata una porta, cerca una porta COM disponibile
        if not self.port:
            self._trova_porta_com()
    
    def _trova_porta_com(self):
        """Cerca una porta COM disponibile"""
        ports = serial.tools.list_ports.comports()
        if ports:
            # Prendi la prima porta COM disponibile
            self.port = ports[0].device
        else:
            # Se non ci sono porte COM, usa una porta virtuale (solo per testing)
            self.port = "COM3"  # Modifica se necessario
    
    def start(self):
        """Avvia il gestore della porta seriale"""
        if self.running:
            return
            
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                xonxoff=0,
                rtscts=0
            )
            
            self.running = True
            self.thread = threading.Thread(target=self._read_serial, daemon=True)
            self.thread.start()
            print(f"Serial handler avviato su {self.port} a {self.baudrate} baud")
            
        except Exception as e:
            print(f"Errore nell'apertura della porta seriale {self.port}: {e}")
            self.running = False
    
    def stop(self):
        """Ferma il gestore della porta seriale"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
    
    def _read_serial(self):
        """Legge i dati dalla porta seriale e li elabora"""
        buffer = ""
        
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                # Leggi i dati disponibili
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting).decode('ascii', errors='ignore')
                    buffer += data
                    
                    # Elabora i comandi completi (terminati da \r\n)
                    while '\r\n' in buffer:
                        command, buffer = buffer.split('\r\n', 1)
                        command = command.strip()
                        
                        if command:  # Ignora righe vuote
                            self._process_command(command)
                
                # Aggiorna periodicamente lo stato
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Errore nella lettura seriale: {e}")
                time.sleep(1)  # Evita loop di errore
    
    def _process_command(self, command: str):
        """Elabora un comando ricevuto"""
        print(f"Comando ricevuto: {command}")
        
        # Cerca un comando corrispondente
        for cmd, handler in self.comandi.items():
            # Se il comando è una regex, prova a fare il match
            if hasattr(handler, 'pattern'):
                match = re.fullmatch(handler.pattern, command, re.IGNORECASE)
                if match:
                    if handler.handler:
                        response = handler.handler(command)
                        self._send_response(response)
                    else:
                        self._send_response(handler.risposta)
                    return
            # Altrimenti confronta direttamente le stringhe
            elif command.upper() == cmd.upper():
                if handler.handler:
                    response = handler.handler(command)
                    self._send_response(response)
                else:
                    self._send_response(handler.risposta)
                return
        
        # Se nessun comando corrisponde, rispondi con errore
        self._send_response("ERR: Comando non riconosciuto\r\n")
    
    def _send_response(self, response: str):
        """Invia una risposta sulla porta seriale"""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(response.encode('ascii'))
                self.serial_port.flush()
            except Exception as e:
                print(f"Errore nell'invio della risposta: {e}")
    
    # ===== Gestori dei comandi =====
    
    def _handle_run(self, command: str) -> str:
        """Gestisce il comando RUN"""
        if self.inverter.avvia():
            return "OK\r\n"
        else:
            return "ERR: Impossibile avviare l'inverter\r\n"
    
    def _handle_stop(self, command: str) -> str:
        """Gestisce il comando STOP"""
        if self.inverter.ferma():
            return "OK\r\n"
        else:
            return "ERR: Impossibile fermare l'inverter\r\n"
    
    def _handle_reset(self, command: str) -> str:
        """Gestisce il comando RST (reset allarmi)"""
        self.inverter.reset_allarmi()
        return "OK\r\n"
    
    def _handle_freq(self, command: str) -> str:
        """Gestisce il comando FREQ <valore>"""
        try:
            # Estrai il valore numerico dal comando
            match = re.match(r"FREQ\s+(\d+(?:\.\d+)?)", command, re.IGNORECASE)
            if match:
                freq = float(match.group(1))
                self.inverter.imposta_frequenza(freq)
                return f"OK: Frequenza impostata a {freq} Hz\r\n"
            else:
                return "ERR: Formato non valido. Usa: FREQ <valore>\r\n"
        except ValueError:
            return "ERR: Valore non valido\r\n"
    
    def _handle_dir(self, command: str) -> str:
        """Gestisce il comando DIR <1|-1>"""
        try:
            match = re.match(r"DIR\s+([+-]?1)", command, re.IGNORECASE)
            if match:
                direzione = int(match.group(1))
                self.inverter.cambia_direzione(direzione)
                dir_str = "avanti" if direzione == 1 else "indietro"
                return f"OK: Direzione impostata a {dir_str}\r\n"
            else:
                return "ERR: Formato non valido. Usa: DIR 1 (avanti) o DIR -1 (indietro)\r\n"
        except ValueError:
            return "ERR: Valore non valido\r\n"
    
    def _handle_status(self, command: str) -> str:
        """Gestisce il comando STATUS"""
        stato = {
            "stato": self.inverter.stato.name,
            "frequenza": f"{self.inverter.frequenza_uscita:.1f} Hz",
            "tensione": f"{self.inverter.tensione_uscita:.1f} V",
            "corrente": f"{self.inverter.corrente_uscita:.2f} A",
            "velocita": f"{int(self.inverter.velocita_motore)} RPM",
            "temperatura": f"{self.inverter.temperatura:.1f} °C",
            "direzione": "AVANTI" if self.inverter.direzione == 1 else "INDIETRO",
            "allarme": self.inverter.descrizione_allarme if self.inverter.allarme_attivo else "Nessuno"
        }
        
        # Costruisci la risposta formattata
        response = "\r\n=== STATO INVERTER ===\r\n"
        for key, value in stato.items():
            response += f"{key.upper()}: {value}\r\n"
        response += "===================\r\n"
        
        return response
    
    def _handle_help(self, command: str) -> str:
        """Gestisce il comando HELP"""
        help_text = "\r\n=== COMANDI DISPONIBILI ===\r\n"
        for cmd, handler in self.comandi.items():
            if not hasattr(handler, 'pattern'):  # Mostra solo i comandi base, non le regex
                help_text += f"{cmd}: {handler.descrizione}\r\n"
        help_text += "\r\nEsempi:\r\n"
        help_text += "  RUN       - Avvia l'inverter\r\n"
        help_text += "  STOP      - Ferma l'inverter\r\n"
        help_text += "  FREQ 50.0 - Imposta la frequenza a 50.0 Hz\r\n"
        help_text += "  DIR 1     - Imposta la direzione in avanti\r\n"
        help_text += "  STATUS    - Mostra lo stato corrente\r\n"
        help_text += "  HELP      - Mostra questo aiuto\r\n"
        help_text += "=========================\r\n"
        return help_text
