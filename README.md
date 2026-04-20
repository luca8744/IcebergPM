# IcebergPM

IcebergPM è un sistema di gestione progetti progettato per risolvere il problema della condivisione selettiva dei dati con i clienti. Permette di gestire progetti complessi internamente mantenendo una vista semplificata e protetta per il cliente finale.

## Stato del Progetto

Fino ad ora sono stati implementati i seguenti componenti core:

### Backend (FastAPI)
- **Architettura Robust**: Struttura a moduli (routers, models, schemas, core).
- **Database**: Integrazione con SQLAlchemy (default SQLite) e migrazione automatica delle tabelle.
- **Autenticazione**: Sistema basato su JWT (JSON Web Tokens) con hashing delle password (bcrypt).
- **Gestione Utenti**: Gestione completa di Admin e Clienti con permessi granulari.
- **API REST**: Endpoint per la gestione di Progetti, Item (attività/costi) e Tag. Logica di visibilità "public/internal".
- **Gestione Database**: Strumenti per backup (export), restore (import) e configurazione remota (DATABASE_URL) direttamente dall'app.
- **Audit Log**: Tracciamento delle operazioni critiche (creazione/eliminazione utenti, progetti, cambi configurazione).
- **Versioning**: Sistema di revisione integrato (v0.1.1) visibile in tutta la UI.

### Frontend (Static HTML/JS)
- **Vanilla Stack**: HTML5, CSS3 e Javascript puro per massima velocità e zero dipendenze pesanti.
- **UI Moderna**: Design pulito con icone (🗑️, 👁️), glassmorphism e micro-interazioni.
- **Filtri Avanzati**: Barra di ricerca contestuale e filtri per stato, priorità e tag con funzione di reset.
- **Dashboard**: Vista dei progetti per l'admin e vista dedicata per il cliente.
- **Integrazione**: Il frontend è servito direttamente dal backend FastAPI.

---

## Requisiti

- Python 3.8+
- [Opzionale] Virtualenv

## Installazione

1. **Crea un ambiente virtuale (consigliato):**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Su Windows
   source venv/bin/activate  # Su Linux/Mac
   ```

2. **Installa le dipendenze:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configurazione ambiente:**
   Il sistema utilizza un file `.env` per le variabili di configurazione. Puoi crearne uno partendo dal template incluso:
   ```bash
   cp .env.example .env  # Su Linux/Mac
   copy .env.example .env # Su Windows
   ```
   Poi apri il file `.env` e personalizza la `SECRET_KEY`.

---

## Come Avviare l'Applicazione

Per lanciare l'intero sistema (Backend + Frontend), basta eseguire lo script di avvio nella root del progetto:

```bash
python run.py
```

L'applicazione sarà disponibile all'indirizzo:
**[http://localhost:8000](http://localhost:8000)**

### Credenziali Iniziali
Al primo avvio, viene creato un utente amministratore predefinito:
- **Username:** `admin`
- **Password:** `admin123`

---

## Utility e Migrazioni

Il progetto include una serie di script di supporto in `backend/scripts/`:

- `migrate_v3.py`: Gestisce l'aggiunta di campi (es. `is_private`) al database esistente.
- `cleanup_database.py`: Utility per la pulizia dei dati.
- `import_csv.py`: Script per l'importazione massiva di dati.

---

## Struttura delle Cartelle

- `backend/`: Contiene il codice Python (FastAPI, SQLAlchemy).
  - `app/`: Logica core dell'applicazione.
  - `scripts/`: Script di migrazione e utilità.
- `frontend/`: Contiene i file statici (HTML, JS, CSS).
- `run.py`: Script principale per avviare il server.
- `build_windows.py`: Script per generare la versione portable .exe.

