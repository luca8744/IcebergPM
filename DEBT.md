# Bug e Debiti Tecnici - IcebergPM

Questo documento censisce i bug noti, i debiti tecnici e le fragilità architetturali dell'applicazione IcebergPM, ordinati per severità.

> [!NOTE]
> Questo registro è complementare a [ADVERSARIAL.MD](ADVERSARIAL.MD) (vulnerabilità di sicurezza) e [IMPROVEMENTS.md](IMPROVEMENTS.md) (funzionalità pianificate). Qui ci concentriamo su **difetti nel codice esistente** e **scelte tecniche da sanare**.

---

## 🐛 Bug Noti

### [B-01] `datetime.utcnow` usato come valore di default nei modelli SQLAlchemy
- **File**: `backend/app/models/models.py` (righe 43, 77, 78, 100)
- **Descrizione**: I campi `created_at`, `updated_at` e `timestamp` usano `default=datetime.utcnow` (senza parentesi), il che è corretto in SQLAlchemy. Tuttavia, `datetime.utcnow()` è deprecato in Python 3.12+ a favore di `datetime.now(timezone.utc)`. Inoltre l'app non gestisce in nessun punto la timezone, generando ambiguità tra timestamp naive e aware.
- **Impatto**: **Medio** — Potenziali inconsistenze con database PostgreSQL timezone-aware; warning di deprecazione sulle versioni recenti di Python.

### [B-02] L'export DB via URL invia il token come query parameter
- **File**: `frontend/dashboard.html` (riga 1023)
- **Descrizione**: La funzione `exportDatabase()` passa il JWT come parametro URL (`?token=...`), ma il backend `/api/admin/db/export` utilizza l'header `Authorization` via `Depends(get_current_active_user)`. Il download non funziona correttamente perché il token nel query string non viene letto dal middleware FastAPI/OAuth2.
- **Impatto**: **Alto** — L'export del database è di fatto **non funzionante** per via dell'autenticazione; l'utente riceverà un 401.

### [B-03] `auth.fetch()` non gestisce il caso `response = undefined`
- **File**: `frontend/js/auth.js` (righe 51-58)
- **Descrizione**: Se la risposta è un 401, il metodo `auth.fetch()` chiama `this.logout()` e poi `return;` (cioè `undefined`). Tutti i caller (`loadProjects`, `loadProjectDetail`, ecc.) chiamano immediatamente `await res.json()` senza verificare che `res` non sia `undefined`, causando un `TypeError: Cannot read properties of undefined (reading 'json')`.
- **Impatto**: **Medio** — Crash silenzioso del frontend quando la sessione scade.

### [B-04] XSS potenziale via interpolazione HTML non sanitizzata
- **File**: `frontend/dashboard.html`, `frontend/client.html`
- **Descrizione**: I nomi dei progetti, titoli degli item, note interne, descrizioni, nomi tag e username vengono inseriti nel DOM via template literal (`${item.title}`, `${p.name}`, ecc.) senza escape HTML. Un attaccante (o un input accidentale con caratteri `<script>`) può iniettare markup arbitrario.
- **Impatto**: **Alto** — Cross-Site Scripting (XSS) stored.

### [B-05] Nomi progetto con apice singolo rompono l'onclick
- **File**: `frontend/dashboard.html` (riga 489), `frontend/client.html` (riga 176)
- **Descrizione**: `onclick="loadProjectDetail(${p.id}, '${p.name}')"` — se `p.name` contiene un apostrofo (es. `Progetto dell'anno`), l'attributo HTML si rompe causando un errore JavaScript.
- **Impatto**: **Medio** — Crash del click su progetti con nomi contenenti apici.

### [B-06] Il campo Tag nel client.html non è funzionale
- **File**: `frontend/client.html` (riga 122, 289)
- **Descrizione**: Il form del client ha un campo testo `itemTag` che viene letto come `item.tag` (proprietà inesistente) e non è mai inviato al backend. Il backend si aspetta `tag_ids` (array di interi), mentre il frontend client non lo manda mai. Il sistema di tag multi-selezionabili è implementato solo nella dashboard admin.
- **Impatto**: **Basso** — Feature non funzionante nel frontend client.

### [B-07] Eliminazione tag non protetta da errori di integrità
- **File**: `backend/app/routers/tags.py` (righe 34-49)
- **Descrizione**: L'endpoint `DELETE /api/tags/{tag_id}` esegue `db.delete(db_tag)` senza gestire `IntegrityError`. Se il tag è associato a molti item tramite `item_tags`, la cancellazione potrebbe fallire in modo imprevedibile a seconda del database (SQLite è più permissivo, PostgreSQL no). Corrisponde a **[A-12]** in ADVERSARIAL.MD.
- **Impatto**: **Medio** — Possibile errore 500 non gestito.

### [B-08] Il ruolo INTERNAL non ha accesso all'area Sistema
- **File**: `backend/app/routers/admin.py` (tutti gli endpoint)
- **Descrizione**: Tutti gli endpoint admin controllano `current_user.role != models.UserRole.ADMIN`, escludendo gli utenti INTERNAL. Tuttavia la dashboard frontend mostra il pulsante "Sistema" anche per gli utenti INTERNAL, che vedranno solo errori 403 al click.
- **Impatto**: **Basso** — UX confusa per gli utenti INTERNAL.

---

## 🏗️ Debiti Tecnici

### [D-01] Frontend monolitico con inline JavaScript (~1100 righe in dashboard.html)
- **File**: `frontend/dashboard.html`
- **Descrizione**: Tutta la logica applicativa (gestione stato, chiamate API, rendering DOM, gestione modal, drag-and-drop) è contenuta in un unico blocco `<script>` inline. Non esiste separazione tra logica, presentazione e stato.
- **Remediation**: Estrarre la logica in file `.js` separati (es. `dashboard.js`, `api.js`, `components.js`) e adottare un pattern MVC/MVP minimo.
- **Priorità**: Alta

### [D-02] Stili CSS inline pervasivi
- **File**: `frontend/dashboard.html`, `frontend/client.html`
- **Descrizione**: La maggior parte degli elementi ha stili scritti direttamente nell'attributo `style=""`, rendendo impossibile la manutenzione, il theming e l'override coerente. Molti stili sono duplicati tra le due pagine (badge-tag, layout grid, spaziature).
- **Remediation**: Centralizzare tutti gli stili in `css/style.css` usando classi semantiche.
- **Priorità**: Media

### [D-03] Duplicazione del codice tra dashboard.html e client.html
- **File**: `frontend/dashboard.html`, `frontend/client.html`
- **Descrizione**: Le due pagine condividono componenti identici: `renderItems()`, `getPriorityColor()`, `applyFilters()`, `resetFilters()`, struttura dei badge, layout degli item. Ogni modifica va replicata manualmente in entrambi i file.
- **Remediation**: Estrarre i componenti condivisi in un modulo JS comune (es. `js/shared.js`).
- **Priorità**: Alta

### [D-04] Assenza totale di test (unitari, integrazione, e2e)
- **Descrizione**: Il progetto non ha alcun framework di test configurato né alcun test scritto. Nessun `pytest.ini`, nessuna cartella `tests/`, nessun file `*_test.py`.
- **Remediation**: Aggiungere `pytest` + `httpx` per test API, e opzionalmente Playwright/Cypress per test e2e.
- **Priorità**: **Critica**

### [D-05] Sistema di migrazioni database non strutturato
- **File**: `backend/scripts/migrate_v1.py` ... `migrate_v4.py`
- **Descrizione**: Le migrazioni sono script Python standalone eseguiti manualmente. Non esiste un sistema di tracking delle migrazioni applicate (nessuna tabella `alembic_version` o equivalente). Se uno script viene eseguito due volte o nell'ordine sbagliato, il risultato è imprevedibile. Corrisponde a **[I-35]** in IMPROVEMENTS.md.
- **Remediation**: Adottare **Alembic** per migrazioni versionabili e tracciabili.
- **Priorità**: Alta

### [D-06] Mancanza di gestione errori globale nel backend
- **File**: `backend/app/main.py`
- **Descrizione**: Non esiste un exception handler globale per `Exception`, `SQLAlchemyError` o `ValidationError`. Errori non catturati producono risposte 500 in formato HTML (stacktrace di Starlette), che il frontend non sa parsare. Corrisponde a **[I-34]** e **[A-11]** nei documenti correlati.
- **Remediation**: Aggiungere `@app.exception_handler(Exception)` per restituire sempre JSON.
- **Priorità**: **Critica**

### [D-07] `declarative_base()` deprecato
- **File**: `backend/app/database.py` (riga 29)
- **Descrizione**: L'import `from sqlalchemy.ext.declarative import declarative_base` è deprecato da SQLAlchemy 2.0. Il path moderno è `from sqlalchemy.orm import DeclarativeBase`.
- **Remediation**: Migrare a `DeclarativeBase` e aggiornare tutti i modelli.
- **Priorità**: Bassa

### [D-08] `on_event("startup")` deprecato in FastAPI
- **File**: `backend/app/main.py` (riga 40)
- **Descrizione**: `@app.on_event("startup")` è deprecato a favore dei lifecycle handler con `@asynccontextmanager`. La funzione `create_initial_data` usa inoltre `next(get_db())` per ottenere una sessione, bypassando il contesto di dependency injection.
- **Remediation**: Usare `lifespan` context manager di FastAPI.
- **Priorità**: Bassa

### [D-09] Dipendenze non pinnate in requirements.txt
- **File**: `backend/requirements.txt`
- **Descrizione**: Nessuna dipendenza ha un vincolo di versione (es. `fastapi[all]` senza `==x.y.z`). Ogni `pip install` potrebbe portare a versioni diverse e incompatibili.
- **Remediation**: Pinnare le versioni esatte (o usare `pip freeze > requirements.txt` dopo aver verificato la compatibilità). Alternativamente, adottare `pyproject.toml` con `pip-tools` o `uv`.
- **Priorità**: Alta

### [D-10] Nessuna validazione di input avanzata sugli schema Pydantic
- **File**: `backend/app/schemas/schemas.py`
- **Descrizione**: I campi `username` e `password` in `UserCreate` sono semplici `str` senza vincoli di lunghezza minima/massima, regex per caratteri ammessi, o complessità password. Un utente può creare un account con username vuoto (`""`) o password di un solo carattere.
- **Remediation**: Aggiungere `Field(min_length=..., max_length=..., pattern=...)` ai campi sensibili.
- **Priorità**: Media

### [D-11] Mancano le policy `ondelete` sulle ForeignKey
- **File**: `backend/app/models/models.py`
- **Descrizione**: Le chiavi esterne (`Project.client_id → users.id`, `Item.project_id → projects.id`, `item_tags`, `AuditLog.user_id → users.id`) non dichiarano `ondelete`. Il comportamento è delegato interamente a SQLAlchemy a livello applicativo, il che è fragile e non protegge in caso di operazioni dirette sul DB. Corrisponde a **[A-12]** e **[I-35]**.
- **Remediation**: Aggiungere `ForeignKey("users.id", ondelete="CASCADE")` o `SET NULL` dove appropriato, tramite migrazione Alembic.
- **Priorità**: Alta

### [D-12] Nessun endpoint per la modifica/eliminazione dei progetti
- **File**: `backend/app/routers/projects.py`
- **Descrizione**: Esistono solo `GET /` (lista), `POST /` (creazione) e `GET /{id}` (dettaglio). Mancano `PUT/PATCH /{id}` (modifica) e `DELETE /{id}` (eliminazione). I progetti non sono eliminabili dall'applicazione.
- **Remediation**: Implementare endpoint CRUD completi per i progetti.
- **Priorità**: Media

### [D-13] L'endpoint `/api/items/` non ha un metodo GET per la lista
- **File**: `backend/app/routers/items.py`
- **Descrizione**: Gli item sono accessibili solo attraverso il dettaglio di un progetto (`GET /projects/{id}` restituisce `items` embedded). Non esiste un `GET /api/items/` per recuperare la lista degli item con filtri lato server (paginazione, ricerca, stato, ecc.). Tutto il filtraggio avviene lato client.
- **Impatto**: Problemi di performance con grandi volumi di dati.
- **Priorità**: Media

### [D-14] Mancanza di paginazione
- **File**: `backend/app/routers/projects.py`, `backend/app/routers/admin.py`
- **Descrizione**: Le query restituiscono tutti i risultati senza alcun meccanismo di paginazione (`offset`/`limit`), fatta eccezione per l'audit log che ha un `limit(100)` hardcoded. Con centinaia di progetti/item, la performance degrada.
- **Remediation**: Aggiungere parametri `skip` e `limit` a tutti gli endpoint di lista.
- **Priorità**: Media

### [D-15] Duplicazione del caricamento `.env`
- **File**: `backend/app/database.py` (riga 18), `backend/app/core/security.py` (riga 8)
- **Descrizione**: `load_dotenv()` viene chiamato sia in `database.py` (con path esplicito) che in `security.py` (senza path, quindi cerca nel cwd). Se il cwd è diverso dalla root del progetto, `security.py` potrebbe leggere un `.env` diverso o nessuno.
- **Remediation**: Centralizzare il caricamento del `.env` in un modulo `config.py` unico.
- **Priorità**: Bassa

### [D-16] Nessun meccanismo di logging applicativo
- **Descrizione**: L'applicazione non configura alcun logger Python (`logging`). Gli errori vengono gestiti solo con `print()` o `console.error()` sul frontend. Non esiste un log file per il debug in produzione.
- **Remediation**: Configurare il modulo `logging` con formattazione e rotazione dei file.
- **Priorità**: Media

### [D-17] Il commit nell'audit log è separato dal commit dell'operazione principale
- **File**: `backend/app/core/audit.py` (riga 26)
- **Descrizione**: La funzione `log_action()` esegue un `db.commit()` proprio. Se il log viene chiamato dopo il commit dell'operazione principale, e il commit del log fallisce, l'operazione è già stata salvata ma il log no. Se il log viene chiamato prima del commit principale e fallisce, l'operazione intera può risultare in uno stato inconsistente.
- **Remediation**: Rimuovere il `commit()` da `log_action()` e gestire il commit in modo transazionale nel caller.
- **Priorità**: Media

### [D-18] Tipo `Optional[Optional[str]]` ridondante nello schema
- **File**: `backend/app/schemas/schemas.py` (riga 65)
- **Descrizione**: `internal_notes: Optional[Optional[str]] = None` è un tipo annidato ridondante. Equivale a `Optional[str]` ma è probabilmente un errore di copia/incolla.
- **Remediation**: Correggere in `Optional[str] = None`.
- **Priorità**: Bassa

### [D-19] Credenziali database esposte nel .env e visibili via API
- **File**: `.env`, `backend/app/routers/admin.py` (endpoint `/db/status` e `/db/config`)
- **Descrizione**: La stringa di connessione al database (contenente host, username e password in chiaro) viene salvata nel file `.env` senza cifratura ed è leggibile da chiunque abbia accesso al filesystem. Inoltre, l'endpoint `GET /api/admin/db/status` restituisce la URL completa del database nella risposta JSON, e `POST /api/admin/db/config` permette di scriverla. Se un account admin viene compromesso (ricordando che le credenziali di default sono `admin/admin123`, vedi **[A-07]**), l'attaccante ottiene accesso diretto e completo al database esterno.
- **Rischi concreti**:
  - Un admin (o chiunque ne rubi la sessione) può leggere host + user + password del DB dalla UI
  - Il file `.env` sul disco è leggibile da qualsiasi processo/utente del sistema
  - Se il `.env` viene accidentalmente incluso in un pacchetto distribuito, le credenziali sono compromesse
- **Remediation**:
  - Mascherare la password nella risposta di `/db/status` (es. `postgresql://user:****@host/db`)
  - In produzione, usare **variabili d'ambiente di sistema** o un **secret manager** (AWS Secrets Manager, Azure Key Vault, Docker Secrets) al posto del file `.env`
  - Separare l'accesso alla configurazione DB dal ruolo admin (es. richiedere una master password aggiuntiva)
  - Mai includere il `.env` nel pacchetto distribuibile
- **Priorità**: **Alta**

---

## 📋 Riepilogo per Priorità

| Priorità | ID | Tipo | Titolo breve |
|---|---|---|---|
| 🔴 Critica | D-04 | Debito | Nessun test |
| 🔴 Critica | D-06 | Debito | Nessun error handler globale |
| 🟠 Alta | B-02 | Bug | Export DB non funzionante |
| 🟠 Alta | B-04 | Bug | XSS stored |
| 🟠 Alta | D-01 | Debito | Frontend monolitico |
| 🟠 Alta | D-03 | Debito | Duplicazione codice frontend |
| 🟠 Alta | D-05 | Debito | Migrazioni non strutturate |
| 🟠 Alta | D-09 | Debito | Dipendenze non pinnate |
| 🟠 Alta | D-11 | Debito | Mancano policy ondelete |
| 🟡 Medio | B-01 | Bug | datetime.utcnow deprecato |
| 🟡 Medio | B-03 | Bug | auth.fetch() undefined |
| 🟡 Medio | B-05 | Bug | Apice singolo rompe onclick |
| 🟡 Medio | B-07 | Bug | Delete tag senza IntegrityError |
| 🟡 Medio | D-02 | Debito | CSS inline |
| 🟡 Medio | D-10 | Debito | Validazione input mancante |
| 🟡 Medio | D-12 | Debito | CRUD progetti incompleto |
| 🟡 Medio | D-13 | Debito | Nessun GET /items/ |
| 🟡 Medio | D-14 | Debito | Nessuna paginazione |
| 🟡 Medio | D-16 | Debito | Nessun logging |
| 🟡 Medio | D-17 | Debito | Commit audit separato |
| 🟠 Alta | D-19 | Debito | Credenziali DB esposte via .env/API |
| 🟢 Basso | B-06 | Bug | Campo tag client non funzionale |
| 🟢 Basso | B-08 | Bug | INTERNAL vede pulsante Sistema |
| 🟢 Basso | D-07 | Debito | declarative_base deprecato |
| 🟢 Basso | D-08 | Debito | on_event deprecato |
| 🟢 Basso | D-15 | Debito | Duplicazione load_dotenv |
| 🟢 Basso | D-18 | Debito | Optional[Optional[str]] |

---

## 🔗 Cross-reference con altri documenti

| DEPT.md | ADVERSARIAL.MD | IMPROVEMENTS.md |
|---|---|---|
| B-04 (XSS) | A-08 (Info Leakage) | — |
| B-07 / D-11 | A-12 (item_tags ondelete) | I-35 (Refactoring integrità) |
| D-06 | A-11 (Errori integrità globali) | I-34 (Middleware errori) |
| D-10 | A-07 (Credenziali default) | I-31 (Rate Limiting) |
| D-19 (Credenziali DB esposte) | A-03 (Data Exfiltration), A-05 (SECRET_KEY), A-07 (Credenziali default) | — |
