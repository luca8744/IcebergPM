# Miglioramenti Futuri - IcebergPM

Questo documento elenca le funzionalità e le ottimizzazioni pianificate per le prossime versioni di IcebergPM.

## 🚀 Priorità Alta: Gestione Database (Setup Wizard)
Implementazione di una procedura guidata al primo avvio ("First Run Experience") per configurare l'origine dei dati.

- **Opzioni di Configurazione Iniziale:**
  - **Crea da zero**: Inizializza un nuovo database SQLite locale pulito.
  - **Importa da DB esistente**: Carica un file `.db` o un dump esistente per migrare i dati.
  - **Connetti DB esterno**: Permette l'inserimento di una stringa di connessione (es. PostgreSQL su database remoto/cloud).
- **Gestione Continua:**
  - Possibilità di cambiare la sorgente dati dalle impostazioni in qualsiasi momento.
  - Funzione di **Esportazione** completa della struttura e dei dati per portabilità.

## 📊 Funzionalità Core & UX
- **Import/Export Excel/JSON**: Caricamento rapido di liste di task e costi da file Excel.
- **Allegati**: Possibilità di caricare documenti, preventivi o immagini direttamente sugli Item (attività).
- **Filtri Avanzati**: Vista filtrata per priorità, stato e visibilità (pubblico vs interno).
- **Log Attività**: Tracciamento di chi ha modificato cosa e quando (Audit Log).

## 🎨 Interfaccia & Estetica
- **Dark Mode**: Supporto nativo per il tema scuro.
- **Micro-interazioni**: Animazioni fluide per la transizione tra Dashboard Admin e Vista Cliente.
- **Reportistica Grafica**: Grafici a torta e barre per visualizzare lo stato di avanzamento dei costi e dei tempi.

## 🔒 Sicurezza & Infrastruttura
- **Backup Automatici**: Creazione di snapshot periodici del database.
- **MFA (Multi-Factor Authentication)**: Autenticazione a due fattori per gli account Admin.
- **Dockerization**: Containerizzazione dell'app per un deployment facilitato su server esterni.
