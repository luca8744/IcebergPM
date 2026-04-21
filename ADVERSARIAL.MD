# Analisi Adversarial (Red Team) - IcebergPM

Questo documento elenca le debolezze, le vulnerabilità e le criticità di sicurezza identificate nell'attuale architettura e implementazione di IcebergPM.

## 🛡️ Sintesi della Valutazione
L'applicazione presenta diverse criticità tipiche di un prototipo in fase iniziale, con particolare enfasi sulla mancanza di controlli di throttling (rate limiting) e policy di rete eccessivamente aperte.

---

## 🚩 Vulnerabilità Identificate

### [A-01] Attacchi Brute-Force sul Login
- **Descrizione**: L'endpoint `/api/auth/login` non implementa alcun meccanismo di rate-limiting o blocco dell'account dopo tentativi falliti. 
- **Rischio**: Un attaccante può automatizzare migliaia di tentativi di accesso per indovinare le password degli utenti (in particolare dell'utente `admin`).
- **Impatto**: **Alto** - Compromissione totale degli account.

### [A-02] Politica CORS Eccessivamente Permissiva
- **Descrizione**: Il backend è configurato con `allow_origins=["*"]` in `main.py`.
- **Rischio**: Qualsiasi sito web malevolo visitato da un utente autenticato può inviare richieste API al backend di IcebergPM.
- **Impatto**: **Medio** - Rischio di Cross-Site Request Forgery (CSRF).

### [A-03] Esportazione Database via API (Data Exfiltration)
- **Descrizione**: L'endpoint `/api/admin/db/export` permette il download diretto del file `.db`.
- **Rischio**: Se un account Admin viene compromesso (anche tramite session hijacking), l'attaccante può scaricare istantaneamente l'intero database contenente tutti i progetti, i task e gli hash delle password.
- **Impatto**: **Critico** - Perdita totale della riservatezza dei dati.

### [A-04] Validazione File Insufficiente in Import DB
- **Descrizione**: `/api/admin/db/import` accetta file basandosi esclusivamente sull'estensione `.db`.
- **Rischio**: Un utente malintenzionato con permessi admin potrebbe caricare file corrotti o appositamente manipolati per causare Denial of Service (DoS) o tentare di sfruttare vulnerabilità nel motore SQLite3 sottostante.
- **Impatto**: **Alto** - Integrità e disponibilità del sistema a rischio.

### [A-05] Gestione Insicura della SECRET_KEY
- **Descrizione**: La chiave per la firma dei JWT ha un valore di fallback hardcoded in `security.py`.
- **Rischio**: Se l'utente non configura correttamente il file `.env`, l'applicazione utilizzerà una chiave pubblica nota, permettendo a chiunque di falsificare token JWT con privilegi di amministratore.
- **Impatto**: **Critico** - Bypass completo dell'autenticazione.

### [A-06] Sessioni JWT a Lunga Durata
- **Descrizione**: I token hanno una validità predefinita di 8 ore (`ACCESS_TOKEN_EXPIRE_MINUTES = 480`).
- **Rischio**: Se un token viene intercettato o rubato, non esiste un meccanismo di revoca (blacklist). L'attaccante può utilizzare il token per l'intera durata della sua validità.
- **Impatto**: **Medio** - Finestra di attacco prolungata in caso di compromissione del token.

### [A-07] Credenziali Admin di Default Hardcoded
- **Descrizione**: `main.py` crea un utente `admin` con password `admin123` se non presente.
- **Rischio**: Molte installazioni potrebbero mantenere queste credenziali. Il sistema non forza il cambio della password al primo accesso.
- **Impatto**: **Critico** - Accesso non autorizzato garantito su installazioni non configurate.

### [A-08] Possibile Information Leakage nei Messaggi di Errore
- **Descrizione**: Alcune eccezioni del database o del sistema vengono restituite direttamente al client tramite `HTTPException`.
- **Rischio**: I messaggi possono contenere nomi di tabelle, colonne o percorsi di sistema (es. errori SQL o di file system), fornendo informazioni utili per mappare la superficie di attacco.
- **Impatto**: **Basso/Medio** - Supporto alla ricognizione per un attaccante.

### [A-09] Log di Audit: Rischio di Log Injection / Sensitive Data
- **Descrizione**: Il campo `details` nel registro di audit riceve stringhe arbitrarie.
- **Rischio**: Se dati sensibili (come parti di chiavi API o note private) vengono loggati durante un'operazione, rimangono permanentemente nel database in chiaro, accessibili a qualsiasi amministratore.
- **Impatto**: **Basso** - Potenziale esposizione accidentale di segreti.

### [A-10] Mancanza di Protezione CSRF (Cross-Site Request Forgery)
- **Descrizione**: Poiché l'autenticazione è basata su token inviati via `Authorization` header, il rischio è mitigato, ma se il frontend dovesse passare all'uso di cookie per la sessione, l'assenza di un middleware CSRF dedicato diventerebbe una vulnerabilità critica.
- **Impatto**: **Basso** (Attuale) / **Alto** (In caso di cambio gestione sessione).

### [A-11] Errori di Integrità Non Gestiti (Globali)
- **Descrizione**: Molti endpoint (es. eliminazione Item o Tag) non catturano errori di database (`SQLAlchemyError`).
- **Rischio**: Se un'operazione viola un vincolo di integrità (es. elimino un tag usato in 1000 task), il server restituisce un errore 500 HTML invece di JSON.
- **Impatto**: **Medio** - Causa il crash della UI (errore di parsing JSON) e possibile leakage di informazioni strutturali del DB.

### [A-12] Inconsistenza nelle Relazioni Many-to-Many
- **Descrizione**: La tabella di associazione `item_tags` non ha politiche di `ondelete` esplicite nel modello.
- **Rischio**: Deletion instabili o errori di database se SQLAlchemy non gestisce correttamente la rimozione automatica dei legami durante l'eliminazione di un Item o di un Tag.
- **Impatto**: **Basso/Medio** - Corruzione dell'integrità referenziale.
