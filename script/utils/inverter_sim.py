"""
Nidec Inverter Simulator

This module provides a simulated Nidec inverter for testing and development purposes.
It emulates the behavior of a real Nidec drive, including various operating states,
fault conditions, and parameter adjustments.
"""

import random
import time
import logging
import json
import os
import csv
from enum import Enum, auto
from dataclasses import dataclass, asdict, field
from typing import Dict, Optional, List, Tuple, Callable, Any
import threading
from pathlib import Path
from dataclasses_json import dataclass_json
from script.utils.logger import get_logger
logger = get_logger(__name__)
logger.info("Inverter simulator initialized")

class StatoInverter(Enum):
    SPENTO = auto()
    PRONTO = auto()
    IN_MARCIA = auto()
    ALLARME = auto()
    DECELERAZIONE = auto()
    ACCELERAZIONE = auto()

class CodiceAllarme(Enum):
    NESSUNO = 0
    SOVRACORRENTE = 1
    SOVRATENSIONE = 2
    SOTTOTENSIONE = 3
    SOVRATEMPERATURA = 4
    GUASTO_USCITA = 5
    GUASTO_INGRESSO = 6
    GUASTO_SOFTWARE = 7
    GUASTO_HARDWARE = 8
    COMUNICAZIONE = 9

@dataclass_json
@dataclass
class Allarme:
    """Class representing an alarm/error condition in the inverter."""
    codice: CodiceAllarme
    descrizione: str
    timestamp: float = field(default_factory=time.time)
    attivo: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alarm to dictionary."""
        return {
            'codice': self.codice.name,
            'descrizione': self.descrizione,
            'timestamp': self.timestamp,
            'attivo': self.attivo
        }

class InverterSimulato:
    """
    Simulates a Nidec inverter with realistic behavior including:
    - Motor control (start/stop/speed/direction)
    - Fault conditions and alarms
    - Parameter monitoring and adjustment
    - Data logging and telemetry
    """
    
    # Default configuration
    DEFAULT_CONFIG = {
        'frequenza_nominale': 50.0,    # Hz
        'tensione_nominale': 400.0,    # V
        'corrente_nominale': 10.0,     # A
        'velocita_nominale': 1500.0,   # RPM
        'temperatura_max': 80.0,       # °C
        'tensione_min': 350.0,         # V
        'tensione_max': 450.0,         # V
        'corrente_max': 15.0,          # A
        'rampa_accelerazione': 10.0,   # Hz/s
        'rampa_decelerazione': 10.0,   # Hz/s
        'fattore_potenza': 0.95,       # PF
    }
    
    def __init__(self, config: Optional[Dict[str, float]] = None):
        # Load configuration
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        
        # Operational parameters
        self.frequenza_nominale = self.config['frequenza_nominale']
        self.tensione_nominale = self.config['tensione_nominale']
        self.corrente_nominale = self.config['corrente_nominale']
        self.velocita_nominale = self.config['velocita_nominale']
        
        # Parametri operativi
        self.frequenza_uscita = 0.0    # Hz
        self.tensione_uscita = self.tensione_nominale  # Set to nominal voltage to avoid low voltage alarm
        self.corrente_uscita = 0.0     # A
        self.velocita_motore = 0.0   # RPM
        self.coppia = 0.0               # Nm
        self.potenza_uscita = 0.0       # W
        self.fattore_potenza = 0.95     # PF
        self.temperatura = 25.0         # °C
        self.tempo_attivazione = 0.0    # ore
        self.conteggio_avviamenti = 0   # n°
        
        # State and control
        self.stato = StatoInverter.PRONTO
        self.direzione = 1              # 1 = avanti, -1 = indietro
        self.comando_remoto = False
        self.rete_attiva = True
        self.in_marcia = False
        self.allarme_attivo = False
        self.descrizione_allarme = "Nessun allarme"
        self.allarmi: List[Allarme] = []
        
        # Callbacks for state changes
        self._state_change_callbacks = []
        self._alarm_callbacks = []
        
        # Ensure logs directory exists at the root of the application
        self._log_dir = Path(__file__).parent.parent.parent / "logs"
        self._log_dir.mkdir(exist_ok=True, parents=True)
        
        # Data logging
        self._log_enabled = True
        self._log_file = str(self._log_dir / "inverter_log.csv")
        self._log_interval = 1.0  # seconds
        self._last_log_time = 0
        
        # Parametri di simulazione
        self._tempo_inizio = time.time()
        self._ultimo_aggiornamento = time.time()
        self._frequenza_obiettivo = 0.0
        self._tensione_obiettivo = 0.0
        self._velocita_obiettivo = 0.0
        
        # Imposta valori iniziali coerenti
        self._frequenza_obiettivo = 0.0
        self._tensione_obiettivo = 0.0
        self._velocita_obiettivo = 0.0
        
        # Start update timer
        self._update_timer = None
        self._running = True
        self._start_update_timer()
        
        logger.info("Inverter simulator initialized")
    
    def _start_update_timer(self):
        """Start the periodic update timer"""
        def _periodic_update():
            while self._running:
                start_time = time.time()
                try:
                    self.update()
                    self._log_data()
                except Exception as e:
                    logger.error(f"Error in update loop: {e}")
                
                # Sleep to maintain approximately 10Hz update rate
                elapsed = time.time() - start_time
                sleep_time = max(0.01, 0.1 - elapsed)  # Target 10Hz (0.1s)
                time.sleep(sleep_time)
        
        self._update_timer = threading.Thread(target=_periodic_update, daemon=True)
        self._update_timer.start()
    
    def reset(self):
        """Reset the inverter to initial state"""
        self.frequenza_uscita = 0.0
        self.tensione_uscita = 0.0
        self.corrente_uscita = 0.0
        self.velocita_motore = 0.0
        self.coppia = 0.0
        self.potenza_uscita = 0.0
        self.temperatura = 25.0
        self.stato = StatoInverter.PRONTO
        self.allarme_attivo = False
        self.descrizione_allarme = "Nessun allarme"
        self.allarmi.clear()
        self._notify_state_change()
        self.potenza_uscita = 0.0
        self.temperatura = 25.0
        self.stato = StatoInverter.PRONTO
        self.direzione = 1
        self.in_marcia = False
        self.allarme_attivo = False
        self.descrizione_allarme = "Nessun allarme"
        self.allarmi.clear()
        self._frequenza_obiettivo = 0.0
        self._tensione_obiettivo = 0.0
        self._velocita_obiettivo = 0.0
    
    def ferma(self) -> bool:
        """
        Ferma l'inverter
        
        Returns:
            bool: True se l'arresto è stato avviato, False altrimenti
        """
        if self.stato in (StatoInverter.IN_MARCIA, StatoInverter.ACCELERAZIONE):
            self.stato = StatoInverter.DECELERAZIONE
            self._notify_state_change()
            logger.info("Arresto inverter avviato")
            return True
        return False
    
    def avvia(self) -> bool:
        """
        Avvia l'inverter
        
        Returns:
            bool: True se l'avvio è riuscito, False altrimenti
        """
        if self.stato == StatoInverter.PRONTO and not self.allarme_attivo:
            self.stato = StatoInverter.ACCELERAZIONE
            self.in_marcia = True
            self.conteggio_avviamenti += 1
            self._notify_state_change()
            logger.info("Inverter avviato")
            return True
        logger.warning("Impossibile avviare l'inverter: stato=%s, allarme=%s", 
                      self.stato, self.allarme_attivo)
        return False
    
    def imposta_frequenza(self, frequenza: float) -> bool:
        """
        Imposta la frequenza di uscita
        
        Args:
            frequenza: Frequenza in Hz (0-frequenza_nominale)
            
        Returns:
            bool: True se la frequenza è stata impostata, False se fuori range
        """
        if 0 <= frequenza <= self.frequenza_nominale:
            self._frequenza_obiettivo = frequenza
            logger.debug("Frequenza obiettivo impostata a %.1f Hz", frequenza)
            return True
        logger.warning("Frequenza %.1f Hz fuori range (0-%.1f)", 
                      frequenza, self.frequenza_nominale)
        return False
    
    def update(self):
        """
        Aggiorna lo stato del simulatore
        
        Questo metodo dovrebbe essere chiamato periodicamente per aggiornare
        lo stato dell'inverter in base al tempo trascorso.
        """
        now = time.time()
        dt = min(0.2, now - self._ultimo_aggiornamento)  # Limita dt per evitare salti eccessivi
        self._ultimo_aggiornamento = now
        
        try:
            # Aggiorna il tempo di attivazione
            if self.in_marcia:
                self.tempo_attivazione += dt / 3600.0  # Converti in ore
            
            # Simula il comportamento dell'inverter
            self._simulate_behavior(dt)
            
            # Aggiungi variazioni casuali per realismo
            self._simulate_random_variations()
            
            # Controlla gli allarmi
            self._check_alarms()
            
            # Aggiorna lo stato
            self._update_state()
            
        except Exception as e:
            logger.error(f"Errore durante l'aggiornamento: {e}", exc_info=True)
            # In caso di errore, metti l'inverter in stato di allarme
            if not self.allarme_attivo:
                self._add_alarm(CodiceAllarme.GUASTO_SOFTWARE, 
                              f"Errore software: {str(e)}")
    
    def _simulate_behavior(self, dt: float):
        """
        Simula il comportamento dinamico dell'inverter
        
        Args:
            dt: Tempo trascorso dall'ultimo aggiornamento (secondi)
        """
        # Aggiorna la frequenza in base allo stato
        if self.stato == StatoInverter.ACCELERAZIONE:
            # Accelerazione con rampa
            ramp_rate = self.config['rampa_accelerazione']  # Hz/s
            freq_step = ramp_rate * dt
            
            if self.frequenza_uscita < self._frequenza_obiettivo:
                self.frequenza_uscita = min(self._frequenza_obiettivo, 
                                          self.frequenza_uscita + freq_step)
            else:
                self.stato = StatoInverter.IN_MARCIA
                self._notify_state_change()
                
        elif self.stato == StatoInverter.DECELERAZIONE:
            # Decelerazione con rampa
            ramp_rate = self.config['rampa_decelerazione']  # Hz/s
            freq_step = ramp_rate * dt
            
            if self.frequenza_uscita > 0.1:  # Soglia minima
                self.frequenza_uscita = max(0, self.frequenza_uscita - freq_step)
            else:
                self.frequenza_uscita = 0
                self.stato = StatoInverter.PRONTO
                self.in_marcia = False
                self._notify_state_change()
        
        # Calcola la tensione in base alla frequenza (V/f costante)
        if self.frequenza_uscita > 0:
            v_f_ratio = self.tensione_nominale / self.frequenza_nominale
            self.tensione_uscita = self.frequenza_uscita * v_f_ratio
        else:
            # Mantieni la tensione nominale anche a frequenza 0 per evitare allarmi di bassa tensione
            self.tensione_uscita = self.tensione_nominale
        
        # Calcola la corrente in base al carico
        # Per semplicità, assumiamo un carico quadratico
        load_factor = (self.frequenza_uscita / self.frequenza_nominale) ** 2
        self.corrente_uscita = load_factor * self.corrente_nominale * (0.9 + 0.2 * random.random())
        
        # Calcola la velocità del motore
        slip = 0.02  # 2% di scorrimento a pieno carico
        sync_speed = (120 * self.frequenza_uscita) / 2  # Per un motore a 2 poli
        self.velocita_motore = sync_speed * (1 - slip * load_factor)
        
        # Calcola la coppia (semplificato)
        self.coppia = (self.potenza_uscita * 9.549) / (self.velocita_motore + 0.001)  # Evita divisione per zero
        
        # Calcola la potenza in uscita
        self.potenza_uscita = (self.tensione_uscita * self.corrente_uscita * 
                              self.fattore_potenza / 1000.0)  # kWecondi)
    
    def _check_alarms(self):
        """Controlla le condizioni di allarme"""
        # Resetta lo stato di allarme precedente
        prev_alarm = self.allarme_attivo
        self.allarme_attivo = False
        self.descrizione_allarme = "Nessun allarme"
        
        # Controlla i vari tipi di allarme
        alarms = []
        
        # Sovracorrente
        if self.corrente_uscita > self.config['corrente_max'] * 1.1:
            alarms.append((CodiceAllarme.SOVRACORRENTE, 
                         f"Sovracorrente: {self.corrente_uscita:.1f}A > {self.config['corrente_max']}A"))
        
        # Sottotensione
        if self.tensione_uscita < self.config['tensione_min'] * 0.9:
            alarms.append((CodiceAllarme.SOTTOTENSIONE,
                         f"Sottotensione: {self.tensione_uscita:.1f}V < {self.config['tensione_min']}V"))
        
        # Sovratensione
        if self.tensione_uscita > self.config['tensione_max'] * 1.1:
            alarms.append((CodiceAllarme.SOVRATENSIONE,
                         f"Sovratensione: {self.tensione_uscita:.1f}V > {self.config['tensione_max']}V"))
        
        # Sovratemperatura
        if self.temperatura > self.config['temperatura_max']:
            alarms.append((CodiceAllarme.SOVRATEMPERATURA,
                         f"Sovratemperatura: {self.temperatura:.1f}°C > {self.config['temperatura_max']}°C"))
        
        # Gestisci gli allarmi rilevati
        for code, desc in alarms:
            if not any(a.codice == code and a.attivo for a in self.allarmi):
                self._add_alarm(code, desc)
        
        # Aggiorna lo stato di allarme
        self.allarme_attivo = any(a.attivo for a in self.allarmi)
        
        # Se c'è un allarme attivo, ferma l'inverter
        if self.allarme_attivo and not prev_alarm:
            self.stato = StatoInverter.ALLARME
            self.in_marcia = False
            logger.warning("Allarme attivato: %s", self.descrizione_allarme)
            self._notify_alarm()
        elif not self.allarme_attivo and prev_alarm:
            logger.info("Tutti gli allarmi sono stati risolti")
    
    def _update_state(self):
        """Aggiorna lo stato dell'inverter in base alle condizioni attuali"""
        prev_state = self.stato
        
        # Logica di transizione di stato
        if self.allarme_attivo:
            self.stato = StatoInverter.ALLARME
        elif self.stato == StatoInverter.ALLARME and not self.allarme_attivo:
            self.stato = StatoInverter.PRONTO
        elif self.stato == StatoInverter.ACCELERAZIONE and abs(self.frequenza_uscita - self._frequenza_obiettivo) < 0.1:
            self.stato = StatoInverter.IN_MARCIA
        elif self.stato == StatoInverter.DECELERAZIONE and self.frequenza_uscita <= 0.1:
            self.stato = StatoInverter.PRONTO
            self.in_marcia = False
        
        # Notifica i listener se lo stato è cambiato
        if self.stato != prev_state:
            logger.info("Stato inverter cambiato da %s a %s", prev_state, self.stato)
            self._notify_state_change()
    
    def _add_alarm(self, code: CodiceAllarme, description: str):
        """
        Aggiunge un allarme alla lista
        
        Args:
            code: Codice dell'allarme
            description: Descrizione testuale dell'allarme
        """
        # Cerca se esiste già un allarme simile non attivo
        for alarm in self.allarmi:
            if alarm.codice == code and not alarm.attivo:
                alarm.attivo = True
                alarm.timestamp = time.time()
                alarm.descrizione = description
                break
        else:
            # Aggiungi un nuovo allarme
            alarm = Allarme(
                codice=code,
                descrizione=description,
                timestamp=time.time(),
                attivo=True
            )
            self.allarmi.append(alarm)
        
        # Aggiorna lo stato di allarme
        self.allarme_attivo = True
        self.descrizione_allarme = description
        logger.warning("Allarme: %s", description)
        
        # Notifica i listener
        self._notify_alarm()
    
    def reset_allarmi(self) -> bool:
        """
        Resetta tutti gli allarmi
        
        Returns:
            bool: True se gli allarmi sono stati resettati, False altrimenti
        """
        if not self.allarme_attivo:
            return False
            
        for allarme in self.allarmi:
            allarme.attivo = False
            
        self.allarme_attivo = False
        self.descrizione_allarme = "Nessun allarme"
        
        # Riporta l'inverter in stato di pronto se era in allarme
        if self.stato == StatoInverter.ALLARME:
            self.stato = StatoInverter.PRONTO
            
        logger.info("Tutti gli allarmi sono stati resettati")
        self._notify_state_change()
    
    def _simulate_random_variations(self):
        """Aggiunge variazioni casuali ai parametri per simulare il comportamento reale"""
        # Variazione casuale della temperatura
        temp_change = (random.random() - 0.5) * 0.1  # +/- 0.05°C
        if self.in_marcia:
            # Aumenta la temperatura quando l'inverter è in funzione
            temp_change += 0.01 * self.frequenza_uscita / self.frequenza_nominale
        self.temperatura = max(20.0, min(90.0, self.temperatura + temp_change))
        
        # Piccole variazioni casuali di tensione e corrente
        if self.tensione_uscita > 0:
            self.tensione_uscita *= (0.995 + 0.01 * random.random())
            self.corrente_uscita *= (0.98 + 0.04 * random.random())
    
    def _log_data(self):
        """Logga i dati correnti dell'inverter"""
        if not self._log_enabled:
            return
            
        now = time.time()
        if now - self._last_log_time >= self._log_interval:
            self._last_log_time = now
            
            log_entry = {
                'timestamp': now,
                'stato': self.stato.name,
                'frequenza': self.frequenza_uscita,
                'tensione': self.tensione_uscita,
                'corrente': self.corrente_uscita,
                'velocita': self.velocita_motore,
                'temperatura': self.temperatura,
                'allarme_attivo': self.allarme_attivo,
                'descrizione_allarme': self.descrizione_allarme
            }
            
            try:
                file_exists = os.path.exists(self._log_file)
                with open(self._log_file, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=log_entry.keys())
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(log_entry)
            except Exception as e:
                logger.error(f"Errore durante il salvataggio del log: {e}")
    
    def _notify_state_change(self):
        """Notifica i listener del cambiamento di stato"""
        for callback in self._state_change_callbacks:
            try:
                callback(self.stato)
            except Exception as e:
                logger.error(f"Errore nel callback di stato: {e}")
    
    def _notify_alarm(self):
        """Notifica i listener di un nuovo allarme"""
        active_alarms = [a for a in self.allarmi if a.attivo]
        for callback in self._alarm_callbacks:
            try:
                callback(active_alarms[-1] if active_alarms else None)
            except Exception as e:
                logger.error(f"Errore nel callback di allarme: {e}")
    
    def add_state_change_callback(self, callback: Callable[[StatoInverter], None]):
        """
        Aggiunge un callback per i cambiamenti di stato
        
        Args:
            callback: Funzione da chiamare quando lo stato cambia.
                     Riceve il nuovo stato come parametro.
        """
        if callback not in self._state_change_callbacks:
            self._state_change_callbacks.append(callback)
    
    def add_alarm_callback(self, callback: Callable[[Optional[Allarme]], None]):
        """
        Aggiunge un callback per i nuovi allarmi
        
        Args:
            callback: Funzione da chiamare quando viene rilevato un nuovo allarme.
                     Riceve l'oggetto Allarme come parametro, o None se tutti gli allarmi sono stati risolti.
        """
        if callback not in self._alarm_callbacks:
            self._alarm_callbacks.append(callback)
    
    def inject_fault(self, fault_type: str, description: str = None):
        """
        Inietta un guasto simulato nell'inverter.
        
        Args:
            fault_type: Tipo di guasto da iniettare (es. 'overcurrent', 'overtemp', 'undervoltage', 'overvoltage', 'communication')
            description: Descrizione opzionale del guasto
            
        Returns:
            bool: True se il guasto è stato iniettato con successo, False altrimenti
        """
        fault_type = fault_type.lower()
        
        if fault_type == 'overcurrent':
            self.corrente_uscita = self.config['corrente_max'] * 1.5  # 150% of max current
            self._add_alarm(CodiceAllarme.SOVRACORRENTE, description or "Overcurrent fault injected")
            return True
            
        elif fault_type == 'overtemp':
            self.temperatura = self.config['temperatura_max'] + 10.0  # 10°C above max
            self._add_alarm(CodiceAllarme.SOVRATEMPERATURA, description or "Overtemperature fault injected")
            return True
            
        elif fault_type == 'undervoltage':
            self.tensione_uscita = self.config['tensione_min'] * 0.8  # 20% below min
            self._add_alarm(CodiceAllarme.SOTTOTENSIONE, description or "Undervoltage fault injected")
            return True
            
        elif fault_type == 'overvoltage':
            self.tensione_uscita = self.config['tensione_max'] * 1.2  # 20% above max
            self._add_alarm(CodiceAllarme.SOVRATENSIONE, description or "Overvoltage fault injected")
            return True
            
        elif fault_type == 'communication':
            self._add_alarm(CodiceAllarme.COMUNICAZIONE, description or "Communication fault injected")
            return True
            
        elif fault_type == 'reset':
            # Reset all faults
            self.reset_allarmi()
            self.tensione_uscita = self.config['tensione_nominale']
            self.corrente_uscita = 0.0
            self.temperatura = 25.0
            return True
            
        return False
        return True
