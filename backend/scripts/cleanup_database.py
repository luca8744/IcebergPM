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
    print(f"Cleaning database: {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        inspector = inspect(engine)
        existing_columns = [c['name'] for c in inspector.get_columns('items')]
        
        for col_name in ['estimated_hours', 'actual_hours']:
            if col_name in existing_columns:
                print(f"Removing column '{col_name}' from 'items' table...")
                try:
                    conn.execute(text(f"ALTER TABLE items DROP COLUMN {col_name}"))
                except Exception as e:
                    print(f"Error removing {col_name}: {e}")
            else:
                print(f"Column '{col_name}' does not exist.")

    print("Cleanup finished.")

if __name__ == "__main__":
    migrate()
