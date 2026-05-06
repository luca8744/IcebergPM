# Schema Database IcebergPM 🧊

Questo documento illustra l'architettura dei dati dell'applicazione IcebergPM, evidenziando le entità principali e le loro interconnessioni.

## Diagramma Entità-Relazione (ER)

```mermaid
erDiagram
    USER ||--o{ PROJECT : "manages"
    USER ||--o{ AUDIT_LOG : "performs"
    PROJECT ||--o{ ITEM : "contains"
    ITEM }|--|{ TAG : "labeled with"
    ITEM ||--o{ ITEM_NOTE : "has notes"
    USER ||--o{ ITEM_NOTE : "writes"
    
    USER {
        int id PK
        string username
        string hashed_password
        Enum role "ADMIN, INTERNAL, CLIENT"
        string reference_client
        bool is_active
    }

    PROJECT {
        int id PK
        string name
        string description
        int client_id FK
        datetime created_at
    }

    ITEM {
        int id PK
        string title
        string description
        Enum status "OPEN, IN_PROGRESS, DONE, CLOSED"
        int project_id FK
        datetime created_at
        datetime updated_at
        datetime completed_at
        string internal_notes
        Enum internal_priority "LOW, MEDIUM, HIGH, CRITICAL"
        bool is_private
        string hlr "High Level Requirements"
        string srs "Software Requirements Spec"
        string tp "Test Plan"
        string external_id
        string unique_id
        string rev_finding
        string rev_released
        string submodule
    }

    TAG {
        int id PK
        string name
        string color
    }

    ITEM_NOTE {
        int id PK
        int item_id FK
        int user_id FK
        string content
        datetime created_at
    }

    AUDIT_LOG {
        int id PK
        datetime timestamp
        int user_id FK
        string username
        string action
        string entity_type
        int entity_id
        string details
    }
```

## Descrizione delle Entità

### 👤 Users
Gestisce l'autenticazione e l'autorizzazione.
- **Ruoli**: Determinano l'accesso alle funzionalità (es. gli utenti `CLIENT` vedono solo i propri progetti).
- **Reference Client**: Un campo opzionale per raggruppare gli utenti sotto uno specifico cliente.

### 📂 Projects
Contenitori logici per i task. Ogni progetto è assegnato a un "cliente" (User).

### 📋 Items (Tasks)
L'entità centrale dell'applicazione. Supporta:
- **Lifecycle**: Tracciamento tramite `created_at`, `updated_at` e `completed_at`.
- **Tracciabilità**: Campi specifici per requisiti tecnici (`hlr`, `srs`, `tp`).
- **Privacy**: Flag `is_private` per nascondere i dettagli tecnici agli utenti esterni.

### 🏷️ Tags
Etichette colorate che possono essere applicate a più Item per facilitare il filtraggio. La relazione è molti-a-molti tramite la tabella `item_tags`.

### 💬 Item Notes
Conversazioni e annotazioni relative a un task. Permettono la tracciabilità degli aggiornamenti con l'indicazione dell'autore e dell'orario di inserimento.

### 🛡️ Audit Logs
Registro immutabile di tutte le operazioni critiche (creazione, modifica, eliminazione) per garantire la sicurezza e la tracciabilità delle modifiche.

> [!NOTE]
> Lo schema è implementato utilizzando **SQLAlchemy** su **SQLite** in modalità sviluppo. I timestamp sono gestiti automaticamente per garantire precisione e integrità.
