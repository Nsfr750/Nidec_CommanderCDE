import random
import time
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional, List
import threading

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

@dataclass
class Allarme:
    codice: CodiceAllarme
    descrizione: str
    timestamp: float
    attivo: bool = True

class InverterSimulato:
    def __init__(self):
        # Parametri di configurazione
        self.frequenza_nominale = 50.0  # Hz
        self.tensione_nominale = 400.0  # V
        self.corrente_nominale = 10.0   # A
        self.velocità_nominale = 1500.0  # RPM
        
        # Parametri operativi
        self.frequenza_uscita = 0.0    # Hz
        self.tensione_uscita = 0.0    # V
        self.corrente_uscita = 0.0     # A
        self.velocita_motore = 0.0   # RPM
        self.coppia = 0.0               # Nm
        self.potenza_uscita = 0.0       # W
        self.fattore_potenza = 0.95     # PF
        self.temperatura = 25.0         # °C
        self.tempo_attivazione = 0.0    # ore
        self.conteggio_avviamenti = 0   # n°
        
        # Stato e controllo
        self.stato = StatoInverter.PRONTO
        self.direzione = 1              # 1 = avanti, -1 = indietro
        self.comando_remoto = False
        self.rete_attiva = True
        self.in_marcia = False
        self.allarme_attivo = False
        self.descrizione_allarme = "Nessun allarme"
        self.allarmi: List[Allarme] = []
        
        # Parametri di simulazione
        self._tempo_inizio = time.time()
        self._ultimo_aggiornamento = time.time()
        self._frequenza_obiettivo = 0.0
        self._tensione_obiettivo = 0.0
        self._velocita_obiettivo = 0.0
        
        # Inizializza i parametri di default
        self.reset()
        
        # Imposta valori iniziali coerenti
        self._frequenza_obiettivo = 0.0
        self._tensione_obiettivo = 0.0
        self._velocita_obiettivo = 0.0
        
        # Avvia il timer per l'aggiornamento periodico
        self._aggiorna_timer = None
        self._avvia_timer_aggiornamento()
    
    def _avvia_timer_aggiornamento(self):
        """Avvia il timer per l'aggiornamento periodico dello stato"""
        def _aggiorna_periodicamente():
            while True:
                self.aggiorna()
                time.sleep(0.1)  # Aggiorna ogni 100ms
        
        self._aggiorna_timer = threading.Thread(target=_aggiorna_periodicamente, daemon=True)
        self._aggiorna_timer.start()
    
    def reset(self):
        """Resetta l'inverter allo stato di pronto"""
        self.frequenza_uscita = 0.0
        self.tensione_uscita = 0.0
        self.corrente_uscita = 0.0
        self.velocita_motore = 0.0
        self.coppia = 0.0
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
    
    def avvia(self):
        """Avvia l'inverter"""
        if not self.allarme_attivo and self.stato == StatoInverter.PRONTO:
            self.stato = StatoInverter.ACCELERAZIONE
            self._frequenza_obiettivo = self.frequenza_nominale
            self._tensione_obiettivo = self.tensione_nominale
            # Usare la frequenza nominale invece di frequenza_uscita per il calcolo iniziale
            self._velocita_obiettivo = self.velocità_nominale * (self._frequenza_obiettivo / self.frequenza_nominale)
            self.in_marcia = True
            self.conteggio_avviamenti += 1
            return True
        return False
    
    def ferma(self):
        """Ferma l'inverter"""
        print(f"DEBUG - ferma() called. Current state: {self.stato}, in_marcia: {self.in_marcia}")
        if self.stato in [StatoInverter.IN_MARCIA, StatoInverter.ACCELERAZIONE, StatoInverter.DECELERAZIONE]:
            print(f"DEBUG - Setting state to DECELERAZIONE and targets to 0")
            self.stato = StatoInverter.DECELERAZIONE
            self._frequenza_obiettivo = 0.0
            self._tensione_obiettivo = 0.0
            self._velocita_obiettivo = 0.0
            # Don't set in_marcia to False here, let it be handled by the state machine
            print(f"DEBUG - After ferma() - state: {self.stato}, in_marcia: {self.in_marcia}")
            return True
        print(f"DEBUG - ferma() did nothing, current state is {self.stato}")
        return False
    
    def imposta_frequenza(self, frequenza: float):
        """Imposta la frequenza di uscita"""
        if 0 <= frequenza <= 400:  # Limiti tipici per un inverter
            self._frequenza_obiettivo = min(frequenza, self.frequenza_nominale)
            self._velocita_obiettivo = self.velocità_nominale * (self._frequenza_obiettivo / self.frequenza_nominale)
            self._tensione_obiettivo = self.tensione_nominale * (self._frequenza_obiettivo / self.frequenza_nominale)
            
            if self.stato == StatoInverter.IN_MARCIA and frequenza > 0:
                self.stato = StatoInverter.ACCELERAZIONE
            elif self.stato == StatoInverter.IN_MARCIA and frequenza == 0:
                self.stato = StatoInverter.DECELERAZIONE
    
    def cambia_direzione(self, direzione: int):
        """Cambia la direzione di rotazione (1 = avanti, -1 = indietro)"""
        if direzione in [-1, 1]:
            self.direzione = direzione
            if self.in_marcia and self.frequenza_uscita > 0:
                self.ferma()
                time.sleep(1)  # Breve pausa prima di cambiare direzione
                self.avvia()
    
    def aggiorna(self):
        """Aggiorna lo stato del simulatore"""
        now = time.time()
        dt = now - self._ultimo_aggiornamento
        self._ultimo_aggiornamento = now
        
        # Aggiorna il tempo di attivazione
        if self.in_marcia:
            self.tempo_attivazione += dt / 3600.0  # Converti in ore
        
        # Simula il comportamento dinamico
        self._simula_comportamento(dt)
        
        # Aggiorna i parametri di uscita
        self._aggiorna_parametri_uscita()
        
        # Simula variazioni casuali
        self._simula_variazioni_casuali()
        
        # Controlla condizioni di allarme
        self._controlla_allarmi()
        
        # Aggiorna lo stato
        self._aggiorna_stato()
    
    def _simula_comportamento(self, dt: float):
        """Simula il comportamento dinamico dell'inverter"""
        # Costanti di tempo per la simulazione (in secondi)
        TAU_FREQUENZA = 0.5  # Costante di tempo per la variazione di frequenza
        TAU_TENSIONE = 0.3   # Costante di tempo per la variazione di tensione
        TAU_VELOCITA = 1.0   # Costante di tempo per la variazione di velocità
        
        # Aggiornamento esponenziale verso il valore obiettivo
        alpha_f = 1.0 - (1.0 / (1.0 + dt / TAU_FREQUENZA))
        alpha_v = 1.0 - (1.0 / (1.0 + dt / TAU_VELOCITA))
        
        # Aggiorna frequenza
        self.frequenza_uscita += alpha_f * (self._frequenza_obiettivo - self.frequenza_uscita)
        
        # Aggiorna tensione (V/f costante)
        self.tensione_uscita = self.tensione_nominale * (self.frequenza_uscita / self.frequenza_nominale)
        
        # Aggiorna velocità del motore
        rapporto_carico = 0.7  # Simula un carico costante
        velocita_teorica = self.velocità_nominale * (self.frequenza_uscita / self.frequenza_nominale)
        self.velocita_motore = velocita_teorica * (1 - 0.2 * rapporto_carico)  # Scorrimento del 20% a pieno carico
        
        # Aggiorna corrente e coppia in base al carico
        if self.frequenza_uscita > 0.1:  # Soglia per evitare divisioni per zero
            if self.stato == StatoInverter.ACCELERAZIONE:
                # Durante l'accelerazione, aumenta gradualmente la corrente
                rapporto_carico = min(1.0, 0.2 + 0.8 * (self.frequenza_uscita / self.frequenza_nominale))
                self.corrente_uscita = min(
                    self.corrente_nominale * rapporto_carico,
                    self.corrente_nominale * 1.2  # Limita la corrente massima al 120% del nominale
                )
            else:
                # A regime, mantieni la corrente al valore nominale
                rapporto_carico = min(1.0, 0.2 + 0.8 * (self.frequenza_uscita / self.frequenza_nominale))
                self.corrente_uscita = self.corrente_nominale * rapporto_carico
                
            # Calcola la coppia solo se la velocità è sufficientemente alta
            if self.velocita_motore > 0.1:
                self.coppia = (self.potenza_uscita * 60) / (2 * 3.14159 * self.velocita_motore)
            else:
                self.coppia = 0.0
        else:
            self.corrente_uscita = 0.0
            self.coppia = 0.0
        
        # Aggiorna potenza in uscita (solo se l'inverter è in funzione)
        if self.in_marcia:
            self.potenza_uscita = self.tensione_uscita * self.corrente_uscita * self.fattore_potenza
        else:
            self.potenza_uscita = 0.0
        
        # Aggiorna temperatura (aumenta con la potenza, si raffredda a riposo)
        delta_temp = (self.potenza_uscita / 1000.0) * dt - (self.temperatura - 25.0) * 0.001 * dt
        self.temperatura = max(25.0, min(90.0, self.temperatura + delta_temp))
    
    def _aggiorna_parametri_uscita(self):
        """Aggiorna i parametri di uscita in base allo stato attuale"""
        # Nessuna azione necessaria qui, gestito in _simula_comportamento
        pass
    
    def _simula_variazioni_casuali(self):
        """Aggiunge piccole variazioni casuali per simulare il comportamento reale"""
        if self.in_marcia:
            # Piccole variazioni casuali
            self.frequenza_uscita += random.uniform(-0.05, 0.05)
            self.tensione_uscita += random.uniform(-0.5, 0.5)
            self.corrente_uscita += random.uniform(-0.01, 0.01) * self.corrente_nominale
            self.velocita_motore += random.uniform(-1.0, 1.0)
            
            # Limita i valori entro limiti ragionevoli
            self.frequenza_uscita = max(0, min(self.frequenza_nominale, self.frequenza_uscita))
            self.tensione_uscita = max(0, min(self.tensione_nominale * 1.1, self.tensione_uscita))
            self.corrente_uscita = max(0, min(self.corrente_nominale * 1.5, self.corrente_uscita))
            self.velocita_motore = max(0, self.velocita_motore)
    
    def _controlla_allarmi(self):
        """Controlla le condizioni di allarme"""
        # Se l'inverter è spento o in stato di pronto, non controllare gli allarmi
        if self.stato == StatoInverter.SPENTO or self.stato == StatoInverter.PRONTO:
            self.allarme_attivo = False
            self.descrizione_allarme = "Nessun allarme"
            return
            
        # Resetta lo stato di allarme prima di verificare le condizioni
        self.allarme_attivo = False
        
        # Debug: Stampa i valori attuali per il debug
        print(f"DEBUG - Stato: {self.stato}, In marcia: {self.in_marcia}, Corrente: {self.corrente_uscita}, Max: {self.corrente_nominale * 1.5}")
        
        # Controlla sovracorrente (solo se l'inverter è in funzione)
        if self.in_marcia and self.corrente_uscita > self.corrente_nominale * 1.5:
            print(f"DEBUG - Allarme sovracorrente: {self.corrente_uscita} > {self.corrente_nominale * 1.5}")
            self._aggiungi_allarme(CodiceAllarme.SOVRACORRENTE, "Sovracorrente rilevata")
        
        # Controlla sovratensione (solo se l'inverter è in funzione)
        if self.in_marcia and self.tensione_uscita > self.tensione_nominale * 1.15:  # +15%
            print(f"DEBUG - Allarme sovratensione: {self.tensione_uscita} > {self.tensione_nominale * 1.15}")
            self._aggiungi_allarme(CodiceAllarme.SOVRATENSIONE, "Sovratensione rilevata")
            
        # Controlla sottotensione (solo se l'inverter è in funzione)
        tensione_attesa = self.tensione_nominale * (self.frequenza_uscita / self.frequenza_nominale)
        if self.in_marcia and self.frequenza_uscita > 5:  # Solo se la frequenza è significativa
            if self.tensione_uscita < tensione_attesa * 0.8:  # -20% dalla tensione attesa
                print(f"DEBUG - Allarme sottotensione: {self.tensione_uscita} < {tensione_attesa * 0.8} (attesa: {tensione_attesa})")
                self._aggiungi_allarme(CodiceAllarme.SOTTOTENSIONE, "Sottotensione rilevata")
            
        # Controlla sovratemperatura (sempre attivo)
        if self.temperatura > 80.0:  # °C
            print(f"DEBUG - Allarme sovratemperatura: {self.temperatura} > 80.0")
            self._aggiungi_allarme(CodiceAllarme.SOVRATEMPERATURA, "Sovratemperatura rilevata")
            
        # Controlla guasto rete (sempre attivo)
        if not self.rete_attiva:
            print("DEBUG - Allarme rete")
            self._aggiungi_allarme(CodiceAllarme.GUASTO_INGRESSO, "Guasto rete di alimentazione")
            
        # Se ci sono allarmi attivi, aggiorna lo stato
        if any(allarme.attivo for allarme in self.allarmi):
            self.allarme_attivo = True
            self.descrizione_allarme = ", ".join(allarme.descrizione 
                                              for allarme in self.allarmi 
                                              if allarme.attivo)
            print(f"DEBUG - Allarme attivato: {self.descrizione_allarme}")
    
    def _aggiorna_stato(self):
        """Aggiorna lo stato dell'inverter in base alle condizioni attuali"""
        old_state = self.stato
        old_in_marcia = self.in_marcia
        
        if self.allarme_attivo:
            self.stato = StatoInverter.ALLARME
            if old_state != self.stato:
                print(f"DEBUG - State changed from {old_state} to {self.stato} (ALARM)")
            return
        
        # Update in_marcia based on frequency and target frequency
        if abs(self.frequenza_uscita) < 0.1 and abs(self._frequenza_obiettivo) < 0.1:
            new_state = StatoInverter.PRONTO
            self.in_marcia = False
        elif self.stato == StatoInverter.DECELERAZIONE:
            if abs(self.frequenza_uscita) > 0.1:
                new_state = StatoInverter.DECELERAZIONE
            else:
                new_state = StatoInverter.PRONTO
                self.in_marcia = False
        elif self.in_marcia:
            if abs(self.frequenza_uscita - self._frequenza_obiettivo) < 0.1:
                new_state = StatoInverter.IN_MARCIA
            else:
                new_state = StatoInverter.ACCELERAZIONE
        else:
            # If we're not in_marcia but frequency is > 0, we should be decelerating
            if abs(self.frequenza_uscita) > 0.1:
                new_state = StatoInverter.DECELERAZIONE
            else:
                new_state = StatoInverter.PRONTO
        
        # Log state changes
        if old_state != new_state or old_in_marcia != self.in_marcia:
            print(f"DEBUG - State: {old_state}->{new_state}, in_marcia: {old_in_marcia}->{self.in_marcia}, "
                  f"freq: {self.frequenza_uscita:.1f}, target: {self._frequenza_obiettivo:.1f}")
        
        self.stato = new_state
    
    def _aggiungi_allarme(self, codice: CodiceAllarme, descrizione: str):
        """Aggiunge un allarme alla lista"""
        # Verifica se l'allarme è già presente
        for allarme in self.allarmi:
            if allarme.codice == codice and allarme.attivo:
                return  # Allarme già presente
        
        # Aggiunge il nuovo allarme
        self.allarmi.append(Allarme(
            codice=codice,
            descrizione=descrizione,
            timestamp=time.time(),
            attivo=True
        ))
        
        # Se è un allarme grave, ferma l'inverter
        if codice != CodiceAllarme.NESSUNO:
            self.ferma()
    
    def reset_allarmi(self):
        """Resetta tutti gli allarmi"""
        self.allarmi = [a for a in self.allarmi if not a.attivo]
        self.allarme_attivo = False
        self.descrizione_allarme = "Nessun allarme"
