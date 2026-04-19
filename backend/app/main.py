from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from .database import engine, Base, get_db
from .models import models
from .routers import auth, projects, items
from .core.security import get_password_hash

APP_VERSION = "0.1.0"

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="IcebergPM API", version=APP_VERSION)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])

@app.get("/api/version")
async def get_version():
    return {"version": APP_VERSION}

# Create initial admin user if not exists
@app.on_event("startup")
def create_initial_data():
    db = next(get_db())
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        admin_user = models.User(
            username="admin",
            hashed_password=get_password_hash("admin123"), # Change this!
            role=models.UserRole.ADMIN
        )
        db.add(admin_user)
        db.commit()
    db.close()

# Serve Frontend
# Make sure the directory exists
import sys

if getattr(sys, 'frozen', False):
    # Se siamo in un eseguibile PyInstaller, i file statici sono estratti in sys._MEIPASS
    root_path = sys._MEIPASS
    frontend_path = os.path.join(root_path, "frontend")
else:
    # In modalità sviluppo, cerchiamo la cartella frontend nella root del progetto
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    frontend_path = os.path.join(root_path, "frontend")

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
