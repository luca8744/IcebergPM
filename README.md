# IcebergPM

IcebergPM è un sistema di gestione progetti progettato per risolvere il problema della condivisione selettiva dei dati con i clienti. Permette di gestire progetti complessi internamente mantenendo una vista semplificata e protetta per il cliente finale.

## Stato del Progetto

Fino ad ora sono stati implementati i seguenti componenti core:

### Backend (FastAPI)
- **Architettura Robust**: Struttura a moduli (routers, models, schemas, core).
- **Database**: Integrazione con SQLAlchemy (default SQLite) e migrazione automatica delle tabelle.
- **Autenticazione**: Sistema basato su JWT (JSON Web Tokens) con hashing delle password (bcrypt).
- **Gestione Ruoli**: Supporto per Admin, Team e Client.
- **API REST**: Endpoint per la gestione di Progetti e Item (attività/costi) con logica di visibilità "public/internal".
- **Versioning**: Sistema di revisione integrato (v0.1.0) visibile in tutta la UI.

### Frontend (Static HTML/JS)
- **Vanilla Stack**: HTML5, CSS3 e Javascript puro per massima velocità e zero dipendenze pesanti.
- **Autenticazione**: Pagine di login e gestione del token nel browser.
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

## Versione Portable (Windows)

Se non vuoi installare Python o gestire virtualenv, puoi usare la versione pre-compilata:

1. Entra nella cartella `dist/IcebergPM`.
2. Assicurati che il file `.env` sia presente nella stessa cartella dell'eseguibile.
3. Lancia **`IcebergPM.exe`**.
4. Accedi a [http://localhost:8000](http://localhost:8000).

---

## Struttura delle Cartelle

- `backend/`: Contiene il codice Python (FastAPI, SQLAlchemy).
- `frontend/`: Contiene i file statici (HTML, JS, CSS).
- `run.py`: Script di utilità per avviare il server uvicorn.
- `seed_client.py`: Script per popolare il database con dati di test.
