from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
import sqlite3
from typing import Optional
from pydantic import BaseModel

from ..database import get_db, SQLALCHEMY_DATABASE_URL, BASE_DIR
from ..models import models
from .auth import get_current_active_user

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
async def update_db_config(config: DBConfigRequest, current_user: models.User = Depends(get_current_active_user)):
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
            
        return {"message": "Configurazione salvata. Riavvia l'applicazione per applicare i cambiamenti."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante il salvataggio della configurazione: {str(e)}")
