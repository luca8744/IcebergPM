from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys
from dotenv import load_dotenv

# Determinazione del percorso base (cartella dell'eseguibile se frozen, altrimenti root del progetto)
if getattr(sys, 'frozen', False):
    # Eseguibile PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Modalità sviluppo
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carichiamo il .env dalla cartella base
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

# Se non esiste un DATABASE_URL nel .env, usiamo SQLite nella cartella base
default_db_path = os.path.join(BASE_DIR, "iceberg_pm.db")
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
