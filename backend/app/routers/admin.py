from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os
import shutil
import sqlite3
from typing import Optional
from pydantic import BaseModel

from ..database import get_db, SQLALCHEMY_DATABASE_URL, BASE_DIR
from ..models import models
from ..schemas import schemas
from ..core.security import get_password_hash
from .auth import get_current_active_user
from ..core.audit import log_action

router = APIRouter()

class DBConfigRequest(BaseModel):
    database_url: str

@router.get("/db/status")
async def get_db_status(current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono accedere a questa funzione")
    
    is_sqlite = "sqlite" in SQLALCHEMY_DATABASE_URL
    return {
        "url": SQLALCHEMY_DATABASE_URL if not is_sqlite else "SQLite Locale",
        "is_sqlite": is_sqlite
    }

@router.get("/db/export")
async def export_db(current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono accedere a questa funzione")
    
    if "sqlite" not in SQLALCHEMY_DATABASE_URL:
        raise HTTPException(status_code=400, detail="L'esportazione è supportata solo per database SQLite locale")
    
    db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="File database non trovato")
        
    return FileResponse(db_path, filename="iceberg_pm_backup.db", media_type="application/x-sqlite3")

@router.post("/db/import")
async def import_db(file: UploadFile = File(...), current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono accedere a questa funzione")
    
    if "sqlite" not in SQLALCHEMY_DATABASE_URL:
        raise HTTPException(status_code=400, detail="L'importazione è supportata solo per database SQLite locale")

    db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
    temp_path = db_path + ".tmp"
    
    try:
        # Salva il file caricato temporaneamente
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Usa l'API di backup di sqlite3 per sovrascrivere il DB attivo in modo sicuro
        src_conn = sqlite3.connect(temp_path)
        dest_conn = sqlite3.connect(db_path)
        
        src_conn.backup(dest_conn)
        
        src_conn.close()
        dest_conn.close()
        
        return {"message": "Database ripristinato con successo"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante il ripristino: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/db/config")
async def update_db_config(
    config: DBConfigRequest, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono accedere a questa funzione")
    
    dotenv_path = os.path.join(BASE_DIR, ".env")
    
    try:
        # Leggi il file .env esistente o crealo
        lines = []
        if os.path.exists(dotenv_path):
            with open(dotenv_path, "r") as f:
                lines = f.readlines()
        
        # Aggiorna o aggiungi DATABASE_URL
        found = False
        new_line = f"DATABASE_URL={config.database_url}\n"
        for i, line in enumerate(lines):
            if line.startswith("DATABASE_URL="):
                lines[i] = new_line
                found = True
                break
        
        if not found:
            lines.append(new_line)
            
        # Scrivi il nuovo .env
        with open(dotenv_path, "w") as f:
            f.writelines(lines)
            
        log_action(db, current_user.id, current_user.username, "UPDATE", "DB", None, f"Changed DB URL to: {config.database_url}")
            
        return {"message": "Configurazione salvata. Riavvia l'applicazione per applicare i cambiamenti."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante il salvataggio della configurazione: {str(e)}")

@router.post("/db/test")
async def test_db_connection(config: DBConfigRequest, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    try:
        # Tenta di creare un engine e connettersi
        # Usiamo un timeout breve per non bloccare il server
        temp_engine = create_engine(
            config.database_url, 
            connect_args={"connect_timeout": 5} if "postgresql" in config.database_url or "mysql" in config.database_url else {}
        )
        with temp_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"message": "Connessione riuscita correttamente!"}
    except Exception as e:
        # Ritorna un errore dettagliato
        error_msg = str(e)
        if "driver" in error_msg.lower():
            error_msg = "Driver database mancante o non supportato. Verifica la stringa di connessione."
        raise HTTPException(status_code=400, detail=f"Connessione fallita: {error_msg}")

@router.get("/audit", response_model=list[schemas.AuditLogResponse])
async def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(100).all()

# --- User Management ---

@router.get("/users/", response_model=list[schemas.UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    return db.query(models.User).all()

@router.post("/users/", response_model=schemas.UserResponse)
async def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Check if username exists
    existing = db.query(models.User).filter(models.User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username già esistente")
    
    # Role Logic: Use provided role, or determine from reference_client
    role = user_in.role
    if user_in.reference_client and user_in.reference_client.strip():
        role = models.UserRole.CLIENT
    elif not role:
        role = models.UserRole.ADMIN
    
    new_user = models.User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        role=role,
        reference_client=user_in.reference_client
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    log_action(db, current_user.id, current_user.username, "CREATE", "USER", new_user.id, f"Created user: {new_user.username} ({new_user.role})")
    
    return new_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Non puoi cancellare te stesso")
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    username_del = db_user.username
    db.delete(db_user)
    db.commit()
    
    log_action(db, current_user.id, current_user.username, "DELETE", "USER", user_id, f"Deleted user: {username_del}")
    
    return {"message": "Utente eliminato correttamente"}
