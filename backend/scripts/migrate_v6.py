import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Aggiungi la cartella radice al path per importare i modelli se necessario
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
    print(f"Migrating database: {DATABASE_URL} (V6)...")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        inspector = inspect(engine)
        
        # Check columns in 'items' table
        items_columns = [c['name'] for c in inspector.get_columns('items')]
        
        new_columns = [
            ("rev_finding", "VARCHAR(255)"),
            ("rev_released", "VARCHAR(255)"),
            ("submodule", "VARCHAR(255)")
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in items_columns:
                print(f"Adding '{col_name}' column to 'items'...")
                conn.execute(text(f"ALTER TABLE items ADD COLUMN {col_name} {col_type}"))
            else:
                print(f"Column '{col_name}' already exists in 'items'.")
        
        print("Migration V6 completed successfully.")

if __name__ == "__main__":
    migrate()
