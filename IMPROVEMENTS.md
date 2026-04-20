# Miglioramenti Futuri - IcebergPM

Questo documento elenca le funzionalità e le ottimizzazioni pianificate per le prossime versioni di IcebergPM.

## ✅ Completato: Gestione Database & Portabilità
- **Backup & Restore**: Implementata funzione di esportazione ed importazione sicura del database SQLite locale.
- **Configurazione Dinamica**: Possibilità di cambiare la stringa di connessione al database (es. migrazione a PostgreSQL) direttamente dall'interfaccia Admin.
- **Versioning**: Tracciamento della versione del software nell'interfaccia e gestione del DB.

## 📊 Prossimi Passi: Funzionalità Core & UX
- **Import/Export Excel/JSON**: Caricamento rapido di liste di task e costi da file Excel (Struttura già discussa).
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
