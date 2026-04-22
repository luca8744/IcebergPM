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
    print(f"Migrating database: {DATABASE_URL} (V4)...")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        inspector = inspect(engine)
        existing_columns = [c['name'] for c in inspector.get_columns('items')]
        
        if 'completed_at' not in existing_columns:
            print("Adding column 'completed_at' to 'items' table...")
            conn.execute(text("ALTER TABLE items ADD COLUMN completed_at TIMESTAMP"))
        else:
            print("Column 'completed_at' already exists.")

    print("Migration V4 completed.")

if __name__ == "__main__":
    migrate()
