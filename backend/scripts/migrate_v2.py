import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Determinazione del percorso base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

# Caricamento .env
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    default_db_path = os.path.join(BASE_DIR, "iceberg_pm.db")
    DATABASE_URL = f"sqlite:///{default_db_path}"

def migrate():
    print(f"Migrating database: {DATABASE_URL} (V2)...")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        inspector = inspect(engine)
        existing_columns = [c['name'] for c in inspector.get_columns('users')]
        
        if 'reference_client' not in existing_columns:
            print("Adding column 'reference_client' to 'users' table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN reference_client VARCHAR(255)"))
        else:
            print("Column 'reference_client' already exists.")

    print("Migration V2 completed.")

if __name__ == "__main__":
    migrate()
