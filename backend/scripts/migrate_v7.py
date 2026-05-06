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
    print(f"Migrating database: {DATABASE_URL} (V7)...")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if "item_notes" not in tables:
            print("Creating 'item_notes' table...")
            
            # Determina se usare SERIAL o AUTOINCREMENT
            is_postgres = "postgres" in DATABASE_URL
            id_column = "id SERIAL PRIMARY KEY" if is_postgres else "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
            datetime_type = "TIMESTAMP" if is_postgres else "DATETIME"
            
            conn.execute(text(f"""
                CREATE TABLE item_notes (
                    {id_column},
                    item_id INTEGER NOT NULL,
                    user_id INTEGER,
                    content TEXT NOT NULL,
                    created_at {datetime_type} DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE CASCADE,
                    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
                )
            """))
            print("Table 'item_notes' created successfully.")
            
            # Optional: migrate existing internal_notes to item_notes
            # We will create a note for any task that has internal_notes
            print("Migrating existing internal_notes...")
            # Use raw sql to insert into item_notes
            # We don't have a reliable user_id, so we'll set it to null
            conn.execute(text("""
                INSERT INTO item_notes (item_id, user_id, content, created_at)
                SELECT id, NULL, 'Nota preesistente: ' || internal_notes, CURRENT_TIMESTAMP
                FROM items
                WHERE internal_notes IS NOT NULL AND internal_notes != ''
            """))
            print("Existing internal_notes migrated successfully.")
        else:
            print("Table 'item_notes' already exists, running data migration if needed...")
            # Run the migration just in case it failed before
            try:
                conn.execute(text("""
                    INSERT INTO item_notes (item_id, user_id, content, created_at)
                    SELECT id, NULL, 'Nota preesistente: ' || internal_notes, CURRENT_TIMESTAMP
                    FROM items
                    WHERE internal_notes IS NOT NULL AND internal_notes != ''
                      AND NOT EXISTS (SELECT 1 FROM item_notes WHERE item_notes.item_id = items.id)
                """))
                print("Existing internal_notes migrated successfully.")
            except Exception as e:
                print(f"Data migration skipped or failed: {e}")
        
        print("Migration V7 completed successfully.")

if __name__ == "__main__":
    migrate()
