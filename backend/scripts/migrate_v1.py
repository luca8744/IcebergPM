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
    print(f"Migrating database: {DATABASE_URL} (V1)...")
    engine = create_engine(DATABASE_URL)
    
    columns_to_add = [
        ("hlr", "TEXT"),
        ("srs", "TEXT"),
        ("tp", "TEXT"),
        ("external_id", "VARCHAR(255)"),
        ("unique_id", "VARCHAR(255)")
    ]

    with engine.begin() as conn:
        inspector = inspect(engine)
        existing_columns = [c['name'] for c in inspector.get_columns('items')]
        
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"Adding column {col_name}...")
                conn.execute(text(f"ALTER TABLE items ADD COLUMN {col_name} {col_type}"))
            else:
                print(f"Column {col_name} already exists.")

    print("Migration V1 completed.")

if __name__ == "__main__":
    migrate()
